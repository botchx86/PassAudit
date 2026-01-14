"""
Example: Basic Password Analysis
Demonstrates simple password analysis using PassAudit CLI functions
"""

import sys
import os

# Add parent directory to path to import PassAudit modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.patterns import DetectPatterns
from analyzer.strength import CalculateStrength, GetStrengthCategory
from analyzer.entropy import CalculateEntropy
from analyzer.common_passwords import IsCommonPassword
from analyzer.feedback import GenerateFeedback


def analyze_single_password(password: str) -> None:
    """Analyze a single password and print results"""
    print(f"\n{'='*60}")
    print(f"Analyzing password: {'*' * len(password)}")
    print(f"{'='*60}\n")

    # Step 1: Detect patterns
    patterns = DetectPatterns(password)
    print("1. Pattern Detection:")
    for pattern_type, items in patterns.items():
        if items:
            print(f"   - {pattern_type.replace('_', ' ').title()}: {', '.join(str(x) for x in items)}")
    if not any(patterns.values()):
        print("   - No patterns detected")
    print()

    # Step 2: Calculate strength score
    strength_score = CalculateStrength(password, patterns)
    strength_category = GetStrengthCategory(strength_score)
    print(f"2. Strength Analysis:")
    print(f"   - Score: {strength_score:.1f}/100")
    print(f"   - Category: {strength_category}")
    print()

    # Step 3: Calculate entropy
    entropy = CalculateEntropy(password)
    print(f"3. Entropy Analysis:")
    print(f"   - Shannon Entropy: {entropy:.2f} bits")
    if entropy < 28:
        print("   - Level: Very Low (easily crackable)")
    elif entropy < 36:
        print("   - Level: Low (weak)")
    elif entropy < 60:
        print("   - Level: Medium (acceptable)")
    elif entropy < 128:
        print("   - Level: High (strong)")
    else:
        print("   - Level: Very High (very strong)")
    print()

    # Step 4: Check if common
    is_common = IsCommonPassword(password)
    print(f"4. Common Password Check:")
    print(f"   - Is Common: {'YES [WARNING]' if is_common else 'NO [OK]'}")
    print()

    # Step 5: Generate feedback
    feedback = GenerateFeedback(password, strength_score, patterns, is_common)
    print(f"5. Recommendations:")
    if feedback:
        for idx, suggestion in enumerate(feedback, 1):
            print(f"   {idx}. {suggestion}")
    else:
        print("   - No recommendations. Password is strong!")
    print()


def main():
    """Main function demonstrating basic usage"""
    print("\n" + "="*60)
    print("PassAudit - Basic Usage Example")
    print("="*60)

    # Example 1: Weak password
    print("\n### Example 1: Weak Password ###")
    analyze_single_password("password123")

    # Example 2: Medium password
    print("\n### Example 2: Medium Password ###")
    analyze_single_password("MyP@ss2023")

    # Example 3: Strong password
    print("\n### Example 3: Strong Password ###")
    analyze_single_password("xK9#mQ2$pL7!vN5@")

    # Example 4: Password with patterns
    print("\n### Example 4: Password with Patterns ###")
    analyze_single_password("qwertyuiop1234")

    # Example 5: Leetspeak password
    print("\n### Example 5: Leetspeak Password ###")
    analyze_single_password("p@ssw0rd!")

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
