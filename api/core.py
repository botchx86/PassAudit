"""
PassAudit Core API
Provides a clean, object-oriented interface for password analysis and generation
"""

from typing import Dict, List, Optional, Any
from analyzer.patterns import DetectPatterns
from analyzer.strength import CalculateStrength, GetStrengthCategory
from analyzer.entropy import CalculateEntropy, CalculateCharacterPoolEntropy
from analyzer.feedback import GenerateFeedback
from analyzer.common_passwords import IsCommonPassword
from analyzer.hibp import CheckHIBP
from analyzer.generator import GeneratePassword, GeneratePasswords as GenPasswords
from utils.config import LoadConfig


class PassAuditAPI:
    """
    Main API class for PassAudit password analysis and generation

    Usage:
        api = PassAuditAPI()
        result = api.analyze_password("mypassword")
        passwords = api.generate_password(length=20, count=5)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PassAudit API

        Args:
            config: Optional configuration dictionary. If None, loads from config file.
        """
        self.config = config if config is not None else LoadConfig()

    def analyze_password(self, password: str, check_hibp: bool = False) -> Dict[str, Any]:
        """
        Analyze a single password

        Args:
            password: The password to analyze
            check_hibp: Whether to check Have I Been Pwned database

        Returns:
            Dictionary containing analysis results:
            - password: The analyzed password
            - strength_score: Numerical score (0-100)
            - strength_category: Category (Very Weak to Very Strong)
            - is_common: Whether password is in common password database
            - entropy: Shannon entropy in bits
            - pool_entropy: Character pool entropy in bits
            - length: Password length
            - patterns: Dictionary of detected patterns
            - feedback: List of recommendations
            - hibp_pwned: (optional) Whether found in breaches
            - hibp_count: (optional) Number of times breached
        """
        # Perform pattern detection
        patterns = DetectPatterns(password)

        # Check if common password
        is_common = IsCommonPassword(password)

        # Check HIBP if requested
        hibp_pwned = False
        hibp_count = 0
        if check_hibp:
            timeout = self.config.get('security', {}).get('hibp_timeout', 5)
            hibp_pwned, hibp_count = CheckHIBP(password, timeout=timeout)
            if hibp_pwned is None:
                hibp_pwned = False
                hibp_count = -1  # Indicates check failed

        # Calculate strength metrics
        strength_score = CalculateStrength(password, patterns)
        strength_category = GetStrengthCategory(strength_score)
        entropy = CalculateEntropy(password)
        pool_entropy = CalculateCharacterPoolEntropy(password)

        # Generate feedback
        feedback = GenerateFeedback(password, strength_score, patterns, is_common)

        # Compile results
        result = {
            'password': password,
            'strength_score': strength_score,
            'strength_category': strength_category,
            'is_common': is_common,
            'entropy': entropy,
            'pool_entropy': pool_entropy,
            'length': len(password),
            'patterns': patterns,
            'feedback': feedback
        }

        # Add HIBP data if checked
        if check_hibp:
            result['hibp_pwned'] = hibp_pwned
            result['hibp_count'] = hibp_count

        return result

    def analyze_batch(self, passwords: List[str], check_hibp: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze multiple passwords

        Args:
            passwords: List of passwords to analyze
            check_hibp: Whether to check Have I Been Pwned database

        Returns:
            List of analysis result dictionaries
        """
        results = []
        for password in passwords:
            result = self.analyze_password(password, check_hibp=check_hibp)
            results.append(result)
        return results

    def generate_password(
        self,
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True
    ) -> str:
        """
        Generate a single secure password

        Args:
            length: Password length (default: 16)
            use_uppercase: Include uppercase letters
            use_lowercase: Include lowercase letters
            use_digits: Include digits
            use_symbols: Include symbols

        Returns:
            Generated password string
        """
        return GeneratePassword(
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols
        )

    def generate_batch(
        self,
        count: int = 1,
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True
    ) -> List[str]:
        """
        Generate multiple secure passwords

        Args:
            count: Number of passwords to generate (1-100)
            length: Password length (default: 16)
            use_uppercase: Include uppercase letters
            use_lowercase: Include lowercase letters
            use_digits: Include digits
            use_symbols: Include symbols

        Returns:
            List of generated passwords
        """
        return GenPasswords(
            count=count,
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols
        )

    def check_strength(self, password: str) -> float:
        """
        Quick strength check without full analysis

        Args:
            password: Password to check

        Returns:
            Strength score (0-100)
        """
        patterns = DetectPatterns(password)
        return CalculateStrength(password, patterns)

    def check_common(self, password: str) -> bool:
        """
        Check if password is in common password database

        Args:
            password: Password to check

        Returns:
            True if password is common
        """
        return IsCommonPassword(password)

    def check_breached(self, password: str) -> tuple:
        """
        Check if password has been in data breaches

        Args:
            password: Password to check

        Returns:
            Tuple of (is_breached, breach_count)
            is_breached: True if found in breaches, False if not, None if check failed
            breach_count: Number of times found, 0 if not found, -1 if check failed
        """
        timeout = self.config.get('security', {}).get('hibp_timeout', 5)
        return CheckHIBP(password, timeout=timeout)

    def get_feedback(self, password: str) -> List[str]:
        """
        Get recommendations for improving password

        Args:
            password: Password to analyze

        Returns:
            List of recommendation strings
        """
        patterns = DetectPatterns(password)
        strength_score = CalculateStrength(password, patterns)
        is_common = IsCommonPassword(password)
        return GenerateFeedback(password, strength_score, patterns, is_common)
