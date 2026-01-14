import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from analyzer.generator import GeneratePassword, GeneratePasswords

def test_generate_password_default():
    """Test default password generation"""
    password = GeneratePassword()
    assert len(password) == 16
    # Should contain at least one of each type
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(not c.isalnum() for c in password)

def test_generate_password_custom_length():
    """Test password generation with custom length"""
    password = GeneratePassword(length=24)
    assert len(password) == 24

def test_generate_password_no_symbols():
    """Test password generation without symbols"""
    password = GeneratePassword(length=16, use_symbols=False)
    assert len(password) == 16
    assert not any(not c.isalnum() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)

def test_generate_password_no_uppercase():
    """Test password generation without uppercase"""
    password = GeneratePassword(length=16, use_uppercase=False)
    assert len(password) == 16
    assert not any(c.isupper() for c in password)

def test_generate_password_only_lowercase():
    """Test password generation with only lowercase"""
    password = GeneratePassword(
        length=12,
        use_uppercase=False,
        use_digits=False,
        use_symbols=False
    )
    assert len(password) == 12
    assert all(c.islower() for c in password)

def test_generate_password_too_short():
    """Test that very short passwords raise an error"""
    with pytest.raises(ValueError):
        GeneratePassword(length=3)

def test_generate_password_no_char_types():
    """Test that disabling all character types raises an error"""
    with pytest.raises(ValueError):
        GeneratePassword(
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_symbols=False
        )

def test_generate_passwords_multiple():
    """Test generating multiple passwords"""
    passwords = GeneratePasswords(count=5, length=16)
    assert len(passwords) == 5
    # Check that they're all unique
    assert len(set(passwords)) == 5
    # Check that they all have correct length
    assert all(len(p) == 16 for p in passwords)

def test_generate_passwords_invalid_count():
    """Test that invalid counts raise errors"""
    with pytest.raises(ValueError):
        GeneratePasswords(count=0)

    with pytest.raises(ValueError):
        GeneratePasswords(count=101)

def test_password_uniqueness():
    """Test that generated passwords are unique"""
    passwords = [GeneratePassword() for _ in range(100)]
    # All 100 should be unique
    assert len(set(passwords)) == 100
