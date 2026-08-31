"""
Tests for CrackTimeEstimator service.
Tests crack time estimation and human-readable formatting.
"""

import pytest
from app.utils.helpers import format_time


def test_short_password_crack_time(crack_estimator):
    """Short password should produce small crack times."""
    result = crack_estimator.estimate("abc")
    # At 10 billion guesses/sec, a 3-char lowercase password (26^3 = 17576) is instant
    assert result["10B_guesses_per_sec"] == "less than a second"


def test_long_password_crack_time(crack_estimator):
    """Long complex password should take a very long time."""
    result = crack_estimator.estimate("aB1!xY2@Lkj9#mP$")
    # This should take centuries or more at any speed
    massive = result["10B_guesses_per_sec"]
    assert any(word in massive.lower() for word in ["year", "centur", "thousands"])


def test_crack_time_returns_all_speeds(crack_estimator):
    """All 4 speed tiers should be present in the result."""
    result = crack_estimator.estimate("TestPassword1!")
    assert "1K_guesses_per_sec" in result
    assert "1M_guesses_per_sec" in result
    assert "100M_guesses_per_sec" in result
    assert "10B_guesses_per_sec" in result


def test_format_time_instant():
    """Sub-second values should format as 'less than a second'."""
    assert format_time(0.5) == "less than a second"


def test_format_time_minutes():
    """120 seconds should format as minutes."""
    assert "minute" in format_time(120).lower()
