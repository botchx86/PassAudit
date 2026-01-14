import math
from collections import Counter
from typing import Optional

def CalculateEntropy(password: str) -> float:
    """
    Calculate Shannon entropy: H = -Σ(p(x) * log2(p(x)))
    Returns bits of entropy
    """
    if not password:
        return 0.0

    # Count character frequencies
    counter = Counter(password)
    length = len(password)

    # Calculate Shannon entropy
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    # Multiply by length to get total bits
    total_entropy = entropy * length

    return round(total_entropy, 2)

def CalculateCharacterPoolEntropy(password: str) -> float:
    """
    Calculate entropy based on character pool size
    Formula: log2(pool_size^length) = length * log2(pool_size)
    """
    pool_size = GetCharacterPoolSize(password)
    length = len(password)

    if pool_size == 0 or length == 0:
        return 0.0

    entropy = length * math.log2(pool_size)
    return round(entropy, 2)

def GetCharacterPoolSize(password: str) -> int:
    """Determine character pool size based on character types used"""
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_symbols = any(not c.isalnum() for c in password)

    pool_size = 0
    if has_lowercase: pool_size += 26
    if has_uppercase: pool_size += 26
    if has_digits: pool_size += 10
    if has_symbols: pool_size += 32  # Common symbols

    return pool_size

def GetEntropyCategory(entropy: float) -> str:
    """Categorize entropy strength"""
    if entropy >= 80: return "Excellent"
    if entropy >= 60: return "Strong"
    if entropy >= 40: return "Moderate"
    if entropy >= 28: return "Weak"
    return "Very Weak"
