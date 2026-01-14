import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.patterns import (
    DetectPatterns,
    DetectSequences,
    DetectKeyboardWalks,
    DetectRepeatedChars,
    DetectDatePatterns,
    DetectCommonWords,
    DetectLeetspeak,
    DetectContextPatterns
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
    assert len(patterns['leetspeak']) == 0
    assert len(patterns['context_patterns']) == 0

def test_detect_leetspeak():
    """Test leetspeak detection"""
    # Test p@ssw0rd -> password
    leetspeak = DetectLeetspeak("p@ssw0rd")
    assert "password" in leetspeak or "passwd" in leetspeak

    # Test passw0rd -> password
    leetspeak = DetectLeetspeak("passw0rd")
    assert "password" in leetspeak or "passwd" in leetspeak

    # Test adm1n -> admin
    leetspeak = DetectLeetspeak("adm1n")
    assert "admin" in leetspeak

    # Test l3tm31n -> letmein
    leetspeak = DetectLeetspeak("l3tm31n")
    assert "letmein" in leetspeak

    # Test clean password has no leetspeak
    assert len(DetectLeetspeak("strongPassword123!")) == 0

def test_detect_enhanced_keyboard_patterns():
    """Test enhanced keyboard walk detection with new patterns"""
    # Test diagonal patterns
    walks = DetectKeyboardWalks("1q2w3e4r")
    assert len(walks) > 0

    # Test vertical patterns
    walks = DetectKeyboardWalks("qazwsx")
    assert len(walks) > 0

    # Test numpad patterns
    walks = DetectKeyboardWalks("789456123")
    assert len(walks) > 0

    # Test extended diagonal
    walks = DetectKeyboardWalks("zaq12wsx")
    assert len(walks) > 0

    # Test clean password has no keyboard walks
    assert len(DetectKeyboardWalks("rX9mK2pL5")) == 0

def test_detect_context_patterns():
    """Test context-specific pattern detection"""
    # Test company names
    context = DetectContextPatterns("microsoft123")
    assert "microsoft" in context

    context = DetectContextPatterns("google2023")
    assert "google" in context

    # Test tech terms
    context = DetectContextPatterns("linux4ever")
    assert "linux" in context

    context = DetectContextPatterns("iphone15")
    assert "iphone" in context

    # Test sports teams
    context = DetectContextPatterns("yankees2023")
    assert "yankees" in context

    # Test pop culture
    context = DetectContextPatterns("starwars123")
    assert "starwars" in context

    # Test clean password has no context patterns
    assert len(DetectContextPatterns("rX9mK2pL5vN8")) == 0

def test_detect_enhanced_date_patterns():
    """Test enhanced date pattern detection"""
    # Test 8-digit dates
    dates = DetectDatePatterns("password20231225")
    assert len(dates) > 0

    # Test month names (short)
    dates = DetectDatePatterns("jan2023")
    assert len(dates) > 0

    dates = DetectDatePatterns("dec15")
    assert len(dates) > 0

    # Test month names (full)
    dates = DetectDatePatterns("january2023")
    assert len(dates) > 0

    dates = DetectDatePatterns("december")
    assert len(dates) > 0

    # Test clean password has no dates
    assert len(DetectDatePatterns("strongXyZ")) == 0

def test_comprehensive_new_patterns():
    """Test all new patterns together"""
    # Password with leetspeak
    patterns = DetectPatterns("p@ssw0rd123")
    assert len(patterns['leetspeak']) > 0

    # Password with context pattern
    patterns = DetectPatterns("microsoft2023")
    assert len(patterns['context_patterns']) > 0

    # Password with enhanced keyboard
    patterns = DetectPatterns("1q2w3e4r")
    assert len(patterns['keyboard_walks']) > 0

    # Password with enhanced dates
    patterns = DetectPatterns("january2023")
    assert len(patterns['dates']) > 0

    # Complex password with multiple new patterns
    patterns = DetectPatterns("p@ssw0rdjanuary2023")
    assert len(patterns['leetspeak']) > 0  # password
    assert len(patterns['dates']) > 0  # january, 2023

    # Password with context and dates
    patterns = DetectPatterns("googlejanuary2023")
    assert len(patterns['context_patterns']) > 0  # google
    assert len(patterns['dates']) > 0  # january, 2023
