"""
Example: Using PassAudit as a Python Library
Demonstrates how to use the PassAudit API in your own Python applications
"""

import sys
import os

# Add parent directory to path to import PassAudit modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import PassAuditAPI


def example_basic_analysis():
    """Example 1: Basic password analysis"""
    print("\n" + "="*60)
    print("Example 1: Basic Password Analysis")
    print("="*60 + "\n")

    # Initialize API
    api = PassAuditAPI()

    # Analyze a single password
    password = "MySecureP@ss2023"
    result = api.analyze_password(password)

    print(f"Password: {'*' * len(password)}")
    print(f"Strength Score: {result['strength_score']:.1f}/100")
    print(f"Category: {result['strength_category']}")
    print(f"Entropy: {result['entropy']:.1f} bits")
    print(f"Is Common: {result['is_common']}")

    if result['patterns']:
        print("\nPatterns detected:")
        for pattern_type, items in result['patterns'].items():
            if items:
                print(f"  - {pattern_type}: {items}")


def example_batch_analysis():
    """Example 2: Batch password analysis"""
    print("\n" + "="*60)
    print("Example 2: Batch Password Analysis")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # List of passwords to analyze
    passwords = [
        "password123",
        "qwerty",
        "MyS3cur3P@ss!",
        "admin",
        "Tr0ub4dor&3"
    ]

    # Analyze batch
    results = api.analyze_batch(passwords)

    print(f"Analyzed {len(results)} passwords:\n")
    for idx, result in enumerate(results, 1):
        masked = '*' * len(passwords[idx-1])
        score = result['strength_score']
        category = result['strength_category']
        print(f"{idx}. {masked:15} | Score: {score:5.1f} | {category}")


def example_password_generation():
    """Example 3: Generate secure passwords"""
    print("\n" + "="*60)
    print("Example 3: Password Generation")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Generate a single password
    password = api.generate_password(length=16)
    print(f"Generated password: {password}")

    # Analyze it
    result = api.analyze_password(password)
    print(f"Strength: {result['strength_score']:.1f}/100 ({result['strength_category']})")

    # Generate multiple passwords
    print("\nGenerating 5 passwords:")
    passwords = api.generate_batch(count=5, length=20)
    for idx, pwd in enumerate(passwords, 1):
        print(f"{idx}. {pwd}")


def example_quick_checks():
    """Example 4: Quick convenience methods"""
    print("\n" + "="*60)
    print("Example 4: Quick Checks")
    print("="*60 + "\n")

    api = PassAuditAPI()

    test_passwords = [
        "password123",
        "MyS3cur3P@ss!",
        "qwerty"
    ]

    for password in test_passwords:
        masked = password[:3] + '*' * (len(password) - 3)
        strength = api.check_strength(password)
        is_common = api.check_common(password)

        print(f"\nPassword: {masked}")
        print(f"  Strength: {strength:.1f}/100")
        print(f"  Is Common: {'YES [WARNING]' if is_common else 'NO [OK]'}")


def example_with_configuration():
    """Example 5: Using custom configuration"""
    print("\n" + "="*60)
    print("Example 5: Custom Configuration")
    print("="*60 + "\n")

    # Custom configuration
    custom_config = {
        'security': {
            'check_hibp': False,
            'cache_enabled': True
        },
        'logging': {
            'level': 'WARNING',
            'console_output': False
        }
    }

    # Initialize API with custom config
    api = PassAuditAPI(config=custom_config)

    password = "TestPassword123"
    result = api.analyze_password(password)

    print(f"Password: {'*' * len(password)}")
    print(f"Strength: {result['strength_score']:.1f}/100")
    print(f"Category: {result['strength_category']}")


def example_feedback_system():
    """Example 6: Getting actionable feedback"""
    print("\n" + "="*60)
    print("Example 6: Password Feedback System")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Weak password
    password = "password123"
    feedback = api.get_feedback(password)

    print(f"Password: {password}")
    print("\nFeedback:")
    for idx, suggestion in enumerate(feedback, 1):
        print(f"  {idx}. {suggestion}")


def example_integration():
    """Example 7: Integration in user registration"""
    print("\n" + "="*60)
    print("Example 7: User Registration Integration")
    print("="*60 + "\n")

    api = PassAuditAPI()

    def validate_password(password: str, min_strength: float = 60.0) -> tuple[bool, str]:
        """
        Validate password meets minimum requirements

        Returns:
            Tuple of (is_valid, message)
        """
        # Check basic requirements
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        # Analyze strength
        result = api.analyze_password(password)

        if result['is_common']:
            return False, "This password is too common. Please choose a more unique password."

        if result['strength_score'] < min_strength:
            feedback = result['feedback']
            return False, f"Password too weak. {feedback[0] if feedback else 'Please make it stronger.'}"

        return True, "Password accepted!"

    # Test passwords
    test_cases = [
        "pass",           # Too short
        "password",       # Common
        "MyP@ss2023",     # Acceptable
        "xK9#mQ2$pL7!"   # Strong
    ]

    for password in test_cases:
        is_valid, message = validate_password(password)
        status = "[OK]" if is_valid else "[FAIL]"
        print(f"{status} {password:20} | {message}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*15 + "PassAudit API Usage Examples")
    print("="*70)

    example_basic_analysis()
    example_batch_analysis()
    example_password_generation()
    example_quick_checks()
    example_with_configuration()
    example_feedback_system()
    example_integration()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
