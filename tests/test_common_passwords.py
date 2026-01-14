import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.common_passwords import IsCommonPassword, COMMON_PASSWORDS

def test_is_common_password():
    """Test common password detection"""
    # These should be in our database
    assert IsCommonPassword("password")
    assert IsCommonPassword("123456")
    assert IsCommonPassword("qwerty")
    assert IsCommonPassword("admin")

def test_is_common_password_case_insensitive():
    """Test that common password check is case-insensitive"""
    assert IsCommonPassword("PASSWORD")
    assert IsCommonPassword("Password")
    assert IsCommonPassword("PaSsWoRd")

def test_is_not_common_password():
    """Test that strong passwords are not marked as common"""
    assert not IsCommonPassword("C0rr3ct-H0rs3-B@tt3ry")
    assert not IsCommonPassword("xY9#mQ2$pL5!")
    assert not IsCommonPassword("VeryUniquePassword2024!")

def test_common_passwords_loaded():
    """Test that common passwords database is loaded"""
    assert len(COMMON_PASSWORDS) > 0  # Should have loaded passwords
    assert "password" in COMMON_PASSWORDS
    assert "123456" in COMMON_PASSWORDS
