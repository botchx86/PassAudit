import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.entropy import (
    CalculateEntropy,
    CalculateCharacterPoolEntropy,
    GetCharacterPoolSize,
    GetEntropyCategory
)

def test_calculate_entropy_empty():
    """Test entropy calculation with empty password"""
    assert CalculateEntropy("") == 0.0

def test_calculate_entropy_simple():
    """Test entropy calculation with simple password"""
    # "aaa" has very low entropy (all same character)
    entropy = CalculateEntropy("aaa")
    assert entropy == 0.0  # Same character = 0 entropy

def test_calculate_entropy_complex():
    """Test entropy calculation with complex password"""
    # Random-looking password should have high entropy
    entropy = CalculateEntropy("aB3$xY9!")
    assert entropy > 20  # Should have reasonable entropy

def test_character_pool_size():
    """Test character pool size calculation"""
    assert GetCharacterPoolSize("abc") == 26  # lowercase only
    assert GetCharacterPoolSize("ABC") == 26  # uppercase only
    assert GetCharacterPoolSize("123") == 10  # digits only
    assert GetCharacterPoolSize("!@#") == 32  # symbols only
    assert GetCharacterPoolSize("aB") == 52  # lowercase + uppercase
    assert GetCharacterPoolSize("a1") == 36  # lowercase + digits
    assert GetCharacterPoolSize("a1!") == 68  # lowercase + digits + symbols
    assert GetCharacterPoolSize("aB1!") == 94  # all types

def test_character_pool_entropy():
    """Test character pool entropy calculation"""
    assert CalculateCharacterPoolEntropy("") == 0.0
    entropy = CalculateCharacterPoolEntropy("abcdefgh")
    assert entropy > 0

def test_entropy_category():
    """Test entropy categorization"""
    assert GetEntropyCategory(90) == "Excellent"
    assert GetEntropyCategory(70) == "Strong"
    assert GetEntropyCategory(50) == "Moderate"
    assert GetEntropyCategory(35) == "Weak"
    assert GetEntropyCategory(20) == "Very Weak"
