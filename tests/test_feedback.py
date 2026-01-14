import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.feedback import GenerateFeedback, GetCharacterTypes, GetMissingCharacterTypes

def test_get_character_types():
    """Test character type counting"""
    assert GetCharacterTypes("abc") == 1  # lowercase only
    assert GetCharacterTypes("Abc") == 2  # lowercase + uppercase
    assert GetCharacterTypes("Abc1") == 3  # lowercase + uppercase + digits
    assert GetCharacterTypes("Abc1!") == 4  # all types

def test_get_missing_character_types():
    """Test missing character type detection"""
    missing = GetMissingCharacterTypes("abc")
    assert "uppercase letters" in missing
    assert "numbers" in missing
    assert "symbols" in missing

    missing = GetMissingCharacterTypes("Abc123!")
    assert len(missing) == 0  # Has all types

def test_generate_feedback_common_password():
    """Test feedback for common password"""
    patterns = {}
    feedback = GenerateFeedback("password", 20, patterns, is_common=True)
    assert len(feedback) > 0
    assert any("CRITICAL" in f for f in feedback)

def test_generate_feedback_short_password():
    """Test feedback for short password"""
    patterns = {}
    feedback = GenerateFeedback("abc", 10, patterns, is_common=False)
    assert len(feedback) > 0
    assert any("short" in f.lower() for f in feedback)

def test_generate_feedback_patterns():
    """Test feedback for passwords with patterns"""
    patterns = {
        'sequences': ['123'],
        'keyboard_walks': [],
        'repeated_chars': [],
        'dates': [],
        'common_words': []
    }
    feedback = GenerateFeedback("abc123", 30, patterns, is_common=False)
    assert any("sequence" in f.lower() for f in feedback)

def test_generate_feedback_strong_password():
    """Test feedback for strong password"""
    patterns = {
        'sequences': [],
        'keyboard_walks': [],
        'repeated_chars': [],
        'dates': [],
        'common_words': []
    }
    feedback = GenerateFeedback("C0rr3ct-H0rs3-B@tt3ry-St@pl3", 85, patterns, is_common=False)
    assert any("Excellent" in f for f in feedback)
