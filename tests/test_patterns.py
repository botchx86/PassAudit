import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.patterns import (
    DetectPatterns,
    DetectSequences,
    DetectKeyboardWalks,
    DetectRepeatedChars,
    DetectDatePatterns,
    DetectCommonWords
)

def test_detect_sequences():
    """Test sequence detection"""
    assert "123" in DetectSequences("abc123xyz")
    assert "abc" in DetectSequences("abc123xyz")
    assert len(DetectSequences("password")) == 0  # No sequences

def test_detect_keyboard_walks():
    """Test keyboard walk detection"""
    walks = DetectKeyboardWalks("qwerty123")
    assert len(walks) > 0  # Should detect qwerty
    assert len(DetectKeyboardWalks("randomXyZ")) == 0  # No keyboard walks

def test_detect_repeated_chars():
    """Test repeated character detection"""
    repeated = DetectRepeatedChars("aaa111bbb")
    assert len(repeated) > 0  # Should detect repeated chars
    assert len(DetectRepeatedChars("abc123")) == 0  # No repetitions

def test_detect_date_patterns():
    """Test date pattern detection"""
    dates = DetectDatePatterns("password1990")
    assert len(dates) > 0  # Should detect 1990
    dates = DetectDatePatterns("test2023end")
    assert len(dates) > 0  # Should detect 2023
    assert len(DetectDatePatterns("nodate")) == 0  # No dates

def test_detect_common_words():
    """Test common word detection"""
    words = DetectCommonWords("password123")
    assert "password" in words
    words = DetectCommonWords("admin")
    assert "admin" in words
    assert len(DetectCommonWords("xY9#mQ2")) == 0  # No common words

def test_detect_patterns_comprehensive():
    """Test comprehensive pattern detection"""
    patterns = DetectPatterns("password123qwerty")
    assert len(patterns['sequences']) > 0  # Should detect 123
    assert len(patterns['common_words']) > 0  # Should detect password and qwerty

def test_detect_patterns_clean_password():
    """Test pattern detection on clean password"""
    patterns = DetectPatterns("rX9$mK2#pL5")
    assert len(patterns['sequences']) == 0
    assert len(patterns['keyboard_walks']) == 0
    assert len(patterns['repeated_chars']) == 0
    assert len(patterns['dates']) == 0
    assert len(patterns['common_words']) == 0
