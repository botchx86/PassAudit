from analyzer.entropy import CalculateEntropy
from typing import Dict, List, Optional, Any

def CalculateStrength(password: str, patterns: Optional[Dict[str, List[str]]] = None) -> float:
    """
    Calculate password strength score (0-100)

    Factors weighted:
    - Length (30%): Base 8 chars, bonus up to 20+ chars
    - Character diversity (25%): Lowercase, uppercase, numbers, symbols
    - Entropy (25%): Shannon entropy calculation
    - Pattern penalties (20%): Sequences, repeats, keyboard walks
    """
    if not password:
        return 0

    score = 0

    # Length scoring (0-30 points)
    score += CalculateLengthScore(password)

    # Character diversity (0-25 points)
    score += CalculateCharacterDiversity(password)

    # Entropy (0-25 points)
    score += CalculateEntropyScore(password)

    # Pattern penalties (subtract up to 20 points)
    if patterns:
        pattern_penalty = CalculatePatternPenalty(patterns)
        score -= pattern_penalty

    return max(0, min(100, score))  # Clamp to 0-100

def CalculateLengthScore(password: str) -> float:
    """
    Calculate score based on password length (0-30 points)
    - < 8 chars: 0-10 points (proportional)
    - 8-12 chars: 10-20 points
    - 13-16 chars: 20-25 points
    - 17+ chars: 25-30 points
    """
    length = len(password)

    if length < 8:
        return min(10, length * 1.25)  # Proportional up to 10
    elif length < 13:
        return 10 + (length - 8) * 2  # 10-20 points
    elif length < 17:
        return 20 + (length - 12) * 1.25  # 20-25 points
    else:
        return min(30, 25 + (length - 16) * 0.5)  # 25-30 points

def CalculateCharacterDiversity(password: str) -> int:
    """
    Calculate score based on character type diversity (0-25 points)
    - 1 type (all lowercase): 5 points
    - 2 types (lower + numbers): 10 points
    - 3 types (lower + upper + numbers): 18 points
    - 4 types (all categories): 25 points
    """
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_symbols = any(not c.isalnum() for c in password)

    type_count = sum([has_lowercase, has_uppercase, has_digits, has_symbols])

    if type_count == 1:
        return 5
    elif type_count == 2:
        return 10
    elif type_count == 3:
        return 18
    else:  # type_count == 4
        return 25

def CalculateEntropyScore(password: str) -> float:
    """
    Calculate score based on Shannon entropy (0-25 points)
    Normalized from entropy value
    """
    entropy = CalculateEntropy(password)

    # Normalize entropy to 0-25 scale
    # Typical strong passwords have 50-80 bits of entropy
    # We'll map 0-80 bits to 0-25 points
    score = min(25, (entropy / 80) * 25)

    return round(score, 1)

def CalculatePatternPenalty(patterns: Dict[str, List[str]]) -> int:
    """
    Calculate penalty based on detected patterns (up to 30 points)
    - Sequential chars: -5 points
    - Repeated chars: -5 points
    - Keyboard walks: -10 points (increased from -8)
    - Date patterns: -5 points
    - Common words: -3 points per word (max -9)
    - Leetspeak: -6 points
    - Context patterns: -4 points per pattern (max -8)
    """
    penalty = 0

    if patterns.get('sequences'):
        penalty += 5

    if patterns.get('repeated_chars'):
        penalty += 5

    if patterns.get('keyboard_walks'):
        penalty += 10  # Increased from 8

    if patterns.get('dates'):
        penalty += 5

    if patterns.get('common_words'):
        # Penalize up to 3 common words
        word_count = min(3, len(patterns['common_words']))
        penalty += word_count * 3

    if patterns.get('leetspeak'):
        # Leetspeak is a weak obfuscation attempt
        penalty += 6

    if patterns.get('context_patterns'):
        # Penalize up to 2 context patterns
        pattern_count = min(2, len(patterns['context_patterns']))
        penalty += pattern_count * 4

    return min(30, penalty)  # Cap at 30 points (increased from 20)

def GetStrengthCategory(score: float) -> str:
    """Convert numerical score to category"""
    if score >= 80:
        return "Very Strong"
    if score >= 60:
        return "Strong"
    if score >= 40:
        return "Medium"
    if score >= 20:
        return "Weak"
    return "Very Weak"
