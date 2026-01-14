"""
Password Policy Validator
Configurable password policy enforcement with preset policies
"""

from typing import List, Tuple, Dict, Any, Optional, Set
import json
import re


class PolicyRule:
    """Individual password policy rule"""

    def __init__(self, name: str, description: str, validator, error_message: str):
        """
        Initialize a policy rule

        Args:
            name: Rule name
            description: Rule description
            validator: Validation function that takes password and returns bool
            error_message: Error message when validation fails
        """
        self.name = name
        self.description = description
        self.validator = validator
        self.error_message = error_message

    def validate(self, password: str, analysis_result: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Validate password against this rule

        Args:
            password: Password to validate
            analysis_result: Optional analysis result from PassAudit

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            is_valid = self.validator(password, analysis_result)
            return (is_valid, "" if is_valid else self.error_message)
        except Exception as e:
            return (False, f"Validation error: {str(e)}")


class PasswordPolicy:
    """Password policy with configurable rules"""

    def __init__(self, name: str = "Custom Policy"):
        """
        Initialize password policy

        Args:
            name: Policy name
        """
        self.name = name
        self.rules: List[PolicyRule] = []

    def add_rule(self, rule: PolicyRule):
        """Add a rule to the policy"""
        self.rules.append(rule)

    def add_min_length(self, min_length: int):
        """Add minimum length requirement"""
        rule = PolicyRule(
            name=f"min_length_{min_length}",
            description=f"Minimum {min_length} characters",
            validator=lambda pwd, _: len(pwd) >= min_length,
            error_message=f"Password must be at least {min_length} characters long"
        )
        self.add_rule(rule)
        return self

    def add_max_length(self, max_length: int):
        """Add maximum length requirement"""
        rule = PolicyRule(
            name=f"max_length_{max_length}",
            description=f"Maximum {max_length} characters",
            validator=lambda pwd, _: len(pwd) <= max_length,
            error_message=f"Password must not exceed {max_length} characters"
        )
        self.add_rule(rule)
        return self

    def require_uppercase(self, min_count: int = 1):
        """Require uppercase letters"""
        rule = PolicyRule(
            name=f"require_uppercase_{min_count}",
            description=f"At least {min_count} uppercase letter(s)",
            validator=lambda pwd, _: sum(1 for c in pwd if c.isupper()) >= min_count,
            error_message=f"Password must contain at least {min_count} uppercase letter(s)"
        )
        self.add_rule(rule)
        return self

    def require_lowercase(self, min_count: int = 1):
        """Require lowercase letters"""
        rule = PolicyRule(
            name=f"require_lowercase_{min_count}",
            description=f"At least {min_count} lowercase letter(s)",
            validator=lambda pwd, _: sum(1 for c in pwd if c.islower()) >= min_count,
            error_message=f"Password must contain at least {min_count} lowercase letter(s)"
        )
        self.add_rule(rule)
        return self

    def require_digits(self, min_count: int = 1):
        """Require digits"""
        rule = PolicyRule(
            name=f"require_digits_{min_count}",
            description=f"At least {min_count} digit(s)",
            validator=lambda pwd, _: sum(1 for c in pwd if c.isdigit()) >= min_count,
            error_message=f"Password must contain at least {min_count} digit(s)"
        )
        self.add_rule(rule)
        return self

    def require_symbols(self, min_count: int = 1):
        """Require special symbols"""
        rule = PolicyRule(
            name=f"require_symbols_{min_count}",
            description=f"At least {min_count} special symbol(s)",
            validator=lambda pwd, _: sum(1 for c in pwd if not c.isalnum()) >= min_count,
            error_message=f"Password must contain at least {min_count} special symbol(s)"
        )
        self.add_rule(rule)
        return self

    def add_min_entropy(self, min_entropy: float):
        """Add minimum entropy requirement"""
        rule = PolicyRule(
            name=f"min_entropy_{min_entropy}",
            description=f"Minimum {min_entropy} bits entropy",
            validator=lambda pwd, result: result and result.get('entropy', 0) >= min_entropy if result else True,
            error_message=f"Password must have at least {min_entropy} bits of entropy"
        )
        self.add_rule(rule)
        return self

    def add_min_strength(self, min_strength: float):
        """Add minimum strength score requirement"""
        rule = PolicyRule(
            name=f"min_strength_{min_strength}",
            description=f"Minimum strength score {min_strength}/100",
            validator=lambda pwd, result: result and result.get('strength_score', 0) >= min_strength if result else True,
            error_message=f"Password must have a strength score of at least {min_strength}/100"
        )
        self.add_rule(rule)
        return self

    def forbid_common_passwords(self):
        """Forbid common passwords"""
        rule = PolicyRule(
            name="forbid_common",
            description="Must not be a common password",
            validator=lambda pwd, result: not result.get('is_common', False) if result else True,
            error_message="Password is too common and easily guessable"
        )
        self.add_rule(rule)
        return self

    def forbid_patterns(self, pattern_types: Optional[List[str]] = None):
        """
        Forbid specific pattern types

        Args:
            pattern_types: List of pattern types to forbid (e.g., ['sequences', 'keyboard_walks'])
                         If None, forbids all patterns
        """
        if pattern_types is None:
            pattern_types = ['sequences', 'keyboard_walks', 'repeated_chars', 'dates', 'common_words', 'leetspeak']

        def has_forbidden_patterns(pwd, result):
            if not result or 'patterns' not in result:
                return True
            patterns = result['patterns']
            for ptype in pattern_types:
                if patterns.get(ptype):
                    return False
            return True

        rule = PolicyRule(
            name="forbid_patterns",
            description=f"Must not contain patterns: {', '.join(pattern_types)}",
            validator=has_forbidden_patterns,
            error_message=f"Password contains forbidden patterns"
        )
        self.add_rule(rule)
        return self

    def require_hibp_check(self):
        """Require password not be found in HIBP database"""
        rule = PolicyRule(
            name="require_hibp_check",
            description="Must not appear in data breaches",
            validator=lambda pwd, result: not result.get('hibp_pwned', False) if result else True,
            error_message="Password has been exposed in known data breaches"
        )
        self.add_rule(rule)
        return self

    def add_blacklist_words(self, words: List[str]):
        """Add blacklisted words that cannot appear in password"""
        words_lower = [w.lower() for w in words]

        def contains_blacklisted(pwd, result):
            pwd_lower = pwd.lower()
            for word in words_lower:
                if word in pwd_lower:
                    return False
            return True

        rule = PolicyRule(
            name="blacklist_words",
            description=f"Must not contain blacklisted words",
            validator=contains_blacklisted,
            error_message=f"Password contains forbidden words"
        )
        self.add_rule(rule)
        return self

    def add_custom_rule(self, name: str, description: str, validator, error_message: str):
        """
        Add a custom validation rule

        Args:
            name: Rule name
            description: Rule description
            validator: Function that takes (password, analysis_result) and returns bool
            error_message: Error message when validation fails
        """
        rule = PolicyRule(name, description, validator, error_message)
        self.add_rule(rule)
        return self

    def validate(self, password: str, analysis_result: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
        """
        Validate password against all policy rules

        Args:
            password: Password to validate
            analysis_result: Optional analysis result from PassAudit API

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for rule in self.rules:
            is_valid, error_msg = rule.validate(password, analysis_result)
            if not is_valid:
                errors.append(error_msg)

        return (len(errors) == 0, errors)

    def get_requirements(self) -> List[str]:
        """Get list of policy requirements"""
        return [rule.description for rule in self.rules]

    def to_dict(self) -> Dict[str, Any]:
        """Export policy to dictionary"""
        return {
            'name': self.name,
            'rules': [
                {
                    'name': rule.name,
                    'description': rule.description,
                    'error_message': rule.error_message
                }
                for rule in self.rules
            ]
        }

    def to_json(self) -> str:
        """Export policy to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


# Preset Policies

def get_basic_policy() -> PasswordPolicy:
    """
    Basic password policy
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    policy = PasswordPolicy("POLICY_BASIC")
    policy.add_min_length(8)
    policy.require_uppercase(1)
    policy.require_lowercase(1)
    policy.require_digits(1)
    return policy


def get_medium_policy() -> PasswordPolicy:
    """
    Medium password policy
    - At least 10 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special symbol
    - Must not be a common password
    - Minimum strength score of 40
    """
    policy = PasswordPolicy("POLICY_MEDIUM")
    policy.add_min_length(10)
    policy.require_uppercase(1)
    policy.require_lowercase(1)
    policy.require_digits(1)
    policy.require_symbols(1)
    policy.forbid_common_passwords()
    policy.add_min_strength(40)
    return policy


def get_strong_policy() -> PasswordPolicy:
    """
    Strong password policy
    - At least 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special symbol
    - Must not be a common password
    - Minimum entropy of 50 bits
    - Minimum strength score of 60
    - Must not contain sequences or keyboard walks
    """
    policy = PasswordPolicy("POLICY_STRONG")
    policy.add_min_length(12)
    policy.require_uppercase(1)
    policy.require_lowercase(1)
    policy.require_digits(1)
    policy.require_symbols(1)
    policy.forbid_common_passwords()
    policy.add_min_entropy(50)
    policy.add_min_strength(60)
    policy.forbid_patterns(['sequences', 'keyboard_walks'])
    return policy


def get_enterprise_policy() -> PasswordPolicy:
    """
    Enterprise password policy
    - At least 14 characters
    - At least 2 uppercase letters
    - At least 2 lowercase letters
    - At least 2 digits
    - At least 2 special symbols
    - Must not be a common password
    - Minimum entropy of 60 bits
    - Minimum strength score of 70
    - Must not contain any patterns
    - Must not be in HIBP database
    """
    policy = PasswordPolicy("POLICY_ENTERPRISE")
    policy.add_min_length(14)
    policy.require_uppercase(2)
    policy.require_lowercase(2)
    policy.require_digits(2)
    policy.require_symbols(2)
    policy.forbid_common_passwords()
    policy.add_min_entropy(60)
    policy.add_min_strength(70)
    policy.forbid_patterns()  # Forbid all patterns
    policy.require_hibp_check()
    return policy


# Policy registry
POLICY_PRESETS = {
    'POLICY_BASIC': get_basic_policy,
    'POLICY_MEDIUM': get_medium_policy,
    'POLICY_STRONG': get_strong_policy,
    'POLICY_ENTERPRISE': get_enterprise_policy
}


def get_policy(name: str) -> Optional[PasswordPolicy]:
    """
    Get a policy by name

    Args:
        name: Policy name (e.g., 'POLICY_BASIC', 'POLICY_STRONG')

    Returns:
        PasswordPolicy instance or None if not found
    """
    if name in POLICY_PRESETS:
        return POLICY_PRESETS[name]()
    return None


def load_policy_from_json(json_string: str) -> PasswordPolicy:
    """
    Load policy from JSON string

    Note: This only loads metadata. Custom validators cannot be serialized.
    Use this for displaying policy information, not for validation.

    Args:
        json_string: JSON string representation of policy

    Returns:
        PasswordPolicy with metadata only
    """
    data = json.loads(json_string)
    policy = PasswordPolicy(data['name'])
    # Note: Rules with validators cannot be fully restored from JSON
    # This is primarily for display purposes
    return policy


def validate_password_with_policy(password: str, policy: PasswordPolicy,
                                  analysis_result: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate password against a policy

    Args:
        password: Password to validate
        policy: PasswordPolicy instance
        analysis_result: Optional PassAudit analysis result

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    return policy.validate(password, analysis_result)
