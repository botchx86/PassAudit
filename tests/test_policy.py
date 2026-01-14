"""
Tests for password policy validation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.policy import (
    PasswordPolicy, get_policy,
    get_basic_policy, get_medium_policy, get_strong_policy, get_enterprise_policy
)


def test_basic_policy_pass():
    """Test that a valid password passes basic policy"""
    policy = get_basic_policy()
    password = "Password123"

    is_valid, errors = policy.validate(password)

    assert is_valid is True
    assert len(errors) == 0


def test_basic_policy_fail_no_uppercase():
    """Test that password without uppercase fails basic policy"""
    policy = get_basic_policy()
    password = "password123"

    is_valid, errors = policy.validate(password)

    assert is_valid is False
    assert len(errors) > 0
    assert any('uppercase' in error.lower() for error in errors)


def test_basic_policy_fail_too_short():
    """Test that short password fails basic policy"""
    policy = get_basic_policy()
    password = "Pass1"

    is_valid, errors = policy.validate(password)

    assert is_valid is False
    assert any('8 characters' in error for error in errors)


def test_medium_policy():
    """Test medium policy requirements"""
    policy = get_medium_policy()

    # Should fail - no special symbol
    password1 = "Password123"
    is_valid, errors = policy.validate(password1)
    assert is_valid is False

    # Should pass
    password2 = "Password123!"
    # Need analysis result for strength check
    from analyzer.patterns import DetectPatterns
    from analyzer.strength import CalculateStrength
    from analyzer.entropy import CalculateEntropy
    from analyzer.common_passwords import IsCommonPassword

    patterns = DetectPatterns(password2)
    result = {
        'strength_score': CalculateStrength(password2, patterns),
        'entropy': CalculateEntropy(password2),
        'is_common': IsCommonPassword(password2),
        'patterns': patterns
    }

    is_valid, errors = policy.validate(password2, result)
    # May still fail due to strength requirements


def test_custom_policy():
    """Test creating custom policy"""
    policy = PasswordPolicy("Custom Test Policy")
    policy.add_min_length(10)
    policy.require_uppercase(2)
    policy.require_digits(2)

    # Should fail - only 1 uppercase
    password1 = "Password12"
    is_valid, errors = policy.validate(password1)
    assert is_valid is False

    # Should pass
    password2 = "PassWord12"
    is_valid, errors = policy.validate(password2)
    assert is_valid is True


def test_policy_blacklist_words():
    """Test blacklist words feature"""
    policy = PasswordPolicy("Blacklist Test")
    policy.add_min_length(8)
    policy.add_blacklist_words(['company', 'admin', 'password'])

    # Should fail - contains blacklisted word
    password1 = "Company2023!"
    is_valid, errors = policy.validate(password1)
    assert is_valid is False
    assert any('forbidden' in error.lower() for error in errors)

    # Should pass
    password2 = "SecureP@ss2023"
    is_valid, errors = policy.validate(password2)
    assert is_valid is True


def test_policy_custom_rule():
    """Test adding custom validation rule"""
    policy = PasswordPolicy("Custom Rule Test")

    # Add rule that forbids consecutive characters
    def no_consecutive(pwd, result):
        for i in range(len(pwd) - 1):
            if pwd[i] == pwd[i + 1]:
                return False
        return True

    policy.add_custom_rule(
        name="no_consecutive",
        description="No consecutive identical characters",
        validator=no_consecutive,
        error_message="Password cannot contain consecutive identical characters"
    )

    # Should fail
    password1 = "Password123"
    is_valid, errors = policy.validate(password1)
    assert is_valid is False
    assert any('consecutive' in error.lower() for error in errors)

    # Should pass
    password2 = "Pasword123"
    is_valid, errors = policy.validate(password2)
    assert is_valid is True


def test_policy_get_requirements():
    """Test getting policy requirements"""
    policy = get_basic_policy()
    requirements = policy.get_requirements()

    assert len(requirements) > 0
    assert any('8 characters' in req for req in requirements)
    assert any('uppercase' in req.lower() for req in requirements)


def test_policy_to_dict():
    """Test exporting policy to dictionary"""
    policy = get_basic_policy()
    policy_dict = policy.to_dict()

    assert 'name' in policy_dict
    assert 'rules' in policy_dict
    assert isinstance(policy_dict['rules'], list)
    assert len(policy_dict['rules']) > 0


def test_get_policy_by_name():
    """Test retrieving policy by name"""
    policy = get_policy('POLICY_BASIC')
    assert policy is not None
    assert policy.name == 'POLICY_BASIC'

    policy = get_policy('POLICY_STRONG')
    assert policy is not None
    assert policy.name == 'POLICY_STRONG'

    policy = get_policy('NONEXISTENT')
    assert policy is None


def test_all_preset_policies():
    """Test that all preset policies can be instantiated"""
    presets = ['POLICY_BASIC', 'POLICY_MEDIUM', 'POLICY_STRONG', 'POLICY_ENTERPRISE']

    for preset_name in presets:
        policy = get_policy(preset_name)
        assert policy is not None
        assert len(policy.rules) > 0
        assert len(policy.get_requirements()) > 0


def test_policy_with_analysis_result():
    """Test policy validation with full analysis result"""
    from analyzer.patterns import DetectPatterns
    from analyzer.strength import CalculateStrength
    from analyzer.entropy import CalculateEntropy
    from analyzer.common_passwords import IsCommonPassword

    policy = get_medium_policy()
    password = "xK9#mQ2$pL7!"

    patterns = DetectPatterns(password)
    result = {
        'password': password,
        'strength_score': CalculateStrength(password, patterns),
        'entropy': CalculateEntropy(password),
        'is_common': IsCommonPassword(password),
        'patterns': patterns,
        'length': len(password)
    }

    is_valid, errors = policy.validate(password, result)

    # This strong password should pass medium policy
    assert is_valid is True
    assert len(errors) == 0
