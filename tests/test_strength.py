import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.strength import (
    CalculateStrength,
    CalculateLengthScore,
    CalculateCharacterDiversity,
    GetStrengthCategory
)

def test_calculate_length_score():
    """Test length scoring"""
    assert CalculateLengthScore("abc") < 10  # Very short
    assert 10 <= CalculateLengthScore("password") < 20  # 8 chars
    assert 20 <= CalculateLengthScore("passwordlonger") < 30  # 14 chars
    assert CalculateLengthScore("verylongpasswordhere123456") >= 25  # Very long

def test_calculate_character_diversity():
    """Test character diversity scoring"""
    assert CalculateCharacterDiversity("abc") == 5  # lowercase only
    assert CalculateCharacterDiversity("abc123") == 10  # lowercase + digits
    assert CalculateCharacterDiversity("Abc123") == 18  # lower + upper + digits
    assert CalculateCharacterDiversity("Abc123!") == 25  # all types

def test_calculate_strength_weak():
    """Test strength calculation for weak passwords"""
    score = CalculateStrength("password")
    assert score < 40  # Should be weak

def test_calculate_strength_medium():
    """Test strength calculation for medium passwords"""
    score = CalculateStrength("Password123")
    assert 30 < score < 70  # Should be medium

def test_calculate_strength_strong():
    """Test strength calculation for strong passwords"""
    score = CalculateStrength("C0rr3ct-H0rs3-B@tt3ry-St@pl3")
    assert score >= 70  # Should be strong

def test_get_strength_category():
    """Test strength categorization"""
    assert GetStrengthCategory(90) == "Very Strong"
    assert GetStrengthCategory(70) == "Strong"
    assert GetStrengthCategory(50) == "Medium"
    assert GetStrengthCategory(30) == "Weak"
    assert GetStrengthCategory(10) == "Very Weak"

def test_calculate_strength_empty():
    """Test strength calculation with empty password"""
    score = CalculateStrength("")
    assert score == 0
