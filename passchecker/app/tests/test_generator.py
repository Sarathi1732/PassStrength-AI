"""
Tests for PasswordGenerator service.
Tests generation with various options and character sets.
"""

import pytest


def test_generate_default(generator):
    """Default generation produces 16-char password with all character types."""
    pwd = generator.generate()
    assert len(pwd) == 16
    assert any(c.islower() for c in pwd)
    assert any(c.isupper() for c in pwd)
    assert any(c.isdigit() for c in pwd)
    assert any(not c.isalnum() for c in pwd)


def test_generate_custom_length(generator):
    """Generator respects the length parameter."""
    pwd = generator.generate(length=24)
    assert len(pwd) == 24


def test_generate_excludes_ambiguous(generator):
    """Excludes ambiguous characters (0, O, l, 1, I) when flag is set."""
    pwd = generator.generate(length=100, exclude_ambiguous=True)
    ambiguous_chars = set("0Ol1I")
    assert not any(c in ambiguous_chars for c in pwd)


def test_generate_only_digits(generator):
    """Generates digits-only password when only digits=True."""
    pwd = generator.generate(length=10, uppercase=False, lowercase=False, digits=True, symbols=False)
    assert len(pwd) == 10
    assert pwd.isdigit()


def test_generate_at_least_one_char(generator):
    """Must raise ValueError if no character set is selected."""
    with pytest.raises(ValueError):
        generator.generate(uppercase=False, lowercase=False, digits=False, symbols=False)
