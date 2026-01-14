"""
Example: Custom Pattern Detection
Demonstrates how to work with and extend pattern detection capabilities
"""

import sys
import os
import re
from typing import List, Dict

# Add parent directory to path to import PassAudit modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.patterns import DetectPatterns, LoadCommonWords
from analyzer.strength import CalculateStrength


def example_basic_patterns():
    """Example 1: Understanding basic pattern detection"""
    print("\n" + "="*60)
    print("Example 1: Basic Pattern Detection")
    print("="*60 + "\n")

    test_passwords = [
        ("abc123def", "Sequences"),
        ("qwertyuiop", "Keyboard walks"),
        ("password!!!!", "Repeated characters"),
        ("MyBirthday1990", "Date patterns"),
        ("p@ssw0rd", "Leetspeak"),
        ("GoogleAmazon", "Context patterns (brands)")
    ]

    for password, expected in test_passwords:
        patterns = DetectPatterns(password)
        print(f"\nPassword: {password}")
        print(f"Expected: {expected}")
        print(f"Detected patterns:")
        for pattern_type, items in patterns.items():
            if items:
                print(f"  - {pattern_type}: {items}")


def example_sequence_detection():
    """Example 2: Sequence pattern detection"""
    print("\n" + "="*60)
    print("Example 2: Sequence Detection")
    print("="*60 + "\n")

    test_cases = [
        "abc123",      # Alphabetic and numeric sequences
        "xyz890",      # Reverse sequences
        "defghi",      # Longer alphabetic sequence
        "54321",       # Reverse numeric sequence
        "abcXYZ123"    # Multiple sequences
    ]

    for password in test_cases:
        patterns = DetectPatterns(password)
        sequences = patterns.get('sequences', [])
        print(f"{password:15} | Sequences: {sequences if sequences else 'None'}")


def example_keyboard_patterns():
    """Example 3: Keyboard walk detection"""
    print("\n" + "="*60)
    print("Example 3: Keyboard Walk Detection")
    print("="*60 + "\n")

    test_cases = [
        "qwerty",       # Top row
        "asdfgh",       # Home row
        "zxcvbn",       # Bottom row
        "qazwsx",       # Vertical columns
        "1q2w3e4r",     # Diagonal pattern
        "poiuyt",       # Reverse top row
        "789456123"     # Numpad pattern
    ]

    for password in test_cases:
        patterns = DetectPatterns(password)
        walks = patterns.get('keyboard_walks', [])
        print(f"{password:15} | Keyboard walks: {walks if walks else 'None'}")


def example_leetspeak_detection():
    """Example 4: Leetspeak detection"""
    print("\n" + "="*60)
    print("Example 4: Leetspeak Detection")
    print("="*60 + "\n")

    test_cases = [
        ("p@ssw0rd", "password"),
        ("3l1t3", "elite"),
        ("h4ck3r", "hacker"),
        ("l33tsp34k", "leetspeak"),
        ("adm1n!", "admin")
    ]

    for password, expected_word in test_cases:
        patterns = DetectPatterns(password)
        leetspeak = patterns.get('leetspeak', [])
        detected = expected_word in leetspeak if leetspeak else False
        status = "[OK]" if detected else "[FAIL]"
        print(f"{status} {password:15} | Expected: {expected_word:10} | Detected: {leetspeak}")


def example_date_detection():
    """Example 5: Date pattern detection"""
    print("\n" + "="*60)
    print("Example 5: Date Pattern Detection")
    print("="*60 + "\n")

    test_cases = [
        "MyPass1990",      # Year (19XX)
        "Birth2023",       # Year (20XX)
        "Jan2023Pass",     # Month + year
        "Pass01012000",    # Date (DDMMYYYY)
        "December1995"     # Month name + year
    ]

    for password in test_cases:
        patterns = DetectPatterns(password)
        dates = patterns.get('dates', [])
        print(f"{password:20} | Dates: {dates if dates else 'None'}")


def example_context_patterns():
    """Example 6: Context-specific pattern detection"""
    print("\n" + "="*60)
    print("Example 6: Context Pattern Detection")
    print("="*60 + "\n")

    test_cases = [
        ("GooglePass123", "Tech brand"),
        ("PythonRocks!", "Programming language"),
        ("Lakers2023", "Sports team"),
        ("StarWars99", "Pop culture"),
        ("AmazonPrime1", "Service/brand")
    ]

    for password, context in test_cases:
        patterns = DetectPatterns(password)
        context_patterns = patterns.get('context_patterns', [])
        print(f"{password:20} | Context: {context:20} | Detected: {context_patterns}")


def example_pattern_impact():
    """Example 7: How patterns affect strength score"""
    print("\n" + "="*60)
    print("Example 7: Pattern Impact on Strength")
    print("="*60 + "\n")

    # Similar passwords with and without patterns
    test_pairs = [
        ("RandomXyZ!@#", "RandomXyZ123"),      # Random vs sequence
        ("Tr0ub4dor&3", "Troubador&3"),        # Leetspeak vs normal
        ("MySecure!Pass", "MySecure!1990"),     # No date vs date
        ("ComplexPass!", "qwerty12345!")        # Complex vs keyboard walk
    ]

    for password1, password2 in test_pairs:
        patterns1 = DetectPatterns(password1)
        patterns2 = DetectPatterns(password2)

        score1 = CalculateStrength(password1, patterns1)
        score2 = CalculateStrength(password2, patterns2)

        print(f"\nComparison:")
        print(f"  {password1:20} | Score: {score1:5.1f} | Patterns: {sum(len(v) for v in patterns1.values())}")
        print(f"  {password2:20} | Score: {score2:5.1f} | Patterns: {sum(len(v) for v in patterns2.values())}")
        print(f"  Difference: {abs(score1-score2):.1f} points")


def example_custom_word_check():
    """Example 8: Checking against custom word lists"""
    print("\n" + "="*60)
    print("Example 8: Custom Word List Checking")
    print("="*60 + "\n")

    # Load common words
    common_words = LoadCommonWords()

    # Custom organization-specific words
    custom_words = {
        'companyname', 'productname', 'departmentname',
        'projectalpha', 'projectbeta'
    }

    # Combine word sets
    all_words = common_words.union(custom_words)

    test_passwords = [
        "CompanyName2023!",
        "ProductName@123",
        "MySecurePass!",
        "ProjectAlpha99"
    ]

    print("Checking passwords against custom word list...")
    for password in test_passwords:
        password_lower = password.lower()
        found_words = [word for word in all_words if word in password_lower]

        print(f"\n{password}")
        if found_words:
            print(f"  Contains words: {', '.join(found_words)}")
            print(f"  Status: [WARNING] WEAK - Contains known words")
        else:
            print(f"  Contains words: None")
            print(f"  Status: [OK] OK - No known words found")


def example_pattern_statistics():
    """Example 9: Analyzing pattern frequency across multiple passwords"""
    print("\n" + "="*60)
    print("Example 9: Pattern Statistics")
    print("="*60 + "\n")

    from analyzer.generator import GeneratePasswords

    # Analyze common patterns in weak passwords
    weak_passwords = [
        "password123", "qwerty123", "admin2023", "letmein!",
        "welcome1", "monkey123", "dragon99", "master123",
        "sunshine1", "princess2023", "password!", "123456789"
    ]

    print(f"Analyzing {len(weak_passwords)} weak passwords...\n")

    # Count pattern types
    pattern_counts = {
        'sequences': 0,
        'keyboard_walks': 0,
        'repeated_chars': 0,
        'dates': 0,
        'common_words': 0,
        'leetspeak': 0,
        'context_patterns': 0
    }

    for password in weak_passwords:
        patterns = DetectPatterns(password)
        for pattern_type in pattern_counts:
            if patterns.get(pattern_type):
                pattern_counts[pattern_type] += 1

    # Display statistics
    print("Pattern Frequency:")
    total = len(weak_passwords)
    for pattern_type, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {pattern_type:20} | {bar:25} {count:2d}/{total:2d} ({percentage:5.1f}%)")


def example_building_strong_password():
    """Example 10: Building a password without common patterns"""
    print("\n" + "="*60)
    print("Example 10: Building Strong Passwords")
    print("="*60 + "\n")

    def build_and_test(password: str, description: str):
        """Test a password and show results"""
        patterns = DetectPatterns(password)
        score = CalculateStrength(password, patterns)
        pattern_count = sum(len(v) for v in patterns.values())

        status = "[OK]" if score >= 70 and pattern_count == 0 else "[WARNING]"
        print(f"{status} {description}")
        print(f"   Password: {'*' * len(password)} (len={len(password)})")
        print(f"   Score: {score:.1f}/100")
        print(f"   Patterns detected: {pattern_count}")
        if patterns:
            for ptype, items in patterns.items():
                if items:
                    print(f"     - {ptype}: {items}")
        print()

    print("Evolution of password strength:\n")

    build_and_test("password", "1. Common word")
    build_and_test("password123", "2. Added sequence")
    build_and_test("p@ssw0rd123", "3. Added leetspeak (still weak)")
    build_and_test("MyP@ssw0rd", "4. Mixed case + special")
    build_and_test("Tr0ub4dor&3", "5. Famous XKCD example")
    build_and_test("xK9#mQ2$pL7!", "6. Random characters (strong!)")
    build_and_test("correct-horse-battery-staple", "7. Passphrase (strong!)")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*15 + "PassAudit Custom Pattern Examples")
    print("="*70)

    example_basic_patterns()
    example_sequence_detection()
    example_keyboard_patterns()
    example_leetspeak_detection()
    example_date_detection()
    example_context_patterns()
    example_pattern_impact()
    example_custom_word_check()
    example_pattern_statistics()
    example_building_strong_password()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
