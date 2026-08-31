"""
Tests for PatternDetector service.
Tests sequential, repeated, keyboard walk, dictionary, and leetspeak detection.
"""

import pytest


def test_sequential_detection(pattern_detector):
    """'abc' in password should be detected as sequential."""
    result = pattern_detector.detect_all("abc123def")
    assert len(result["sequential"]) > 0


def test_reverse_sequential_detection(pattern_detector):
    """Reverse sequence like '321' should also be detected."""
    result = pattern_detector.detect_all("x321y")
    assert len(result["sequential"]) > 0


def test_repeated_detection(pattern_detector):
    """'aaa' should be detected as repeated characters."""
    result = pattern_detector.detect_all("aaa111")
    assert len(result["repeated"]) > 0


def test_keyboard_walk_detection(pattern_detector):
    """'qwerty' should be detected as a keyboard walk."""
    result = pattern_detector.detect_all("qwerty")
    assert len(result["keyboard_walks"]) > 0


def test_dictionary_word_detection(pattern_detector):
    """'password' embedded in string should be detected."""
    result = pattern_detector.detect_all("my_password_123")
    assert len(result["dictionary_words"]) > 0


def test_leetspeak_detection(pattern_detector):
    """'P@ssw0rd' should detect leetspeak substitution of 'password'."""
    result = pattern_detector.detect_all("P@ssw0rd")
    assert len(result["leetspeak"]) > 0


def test_no_patterns(pattern_detector):
    """A random-looking password should have no detected patterns."""
    result = pattern_detector.detect_all("xK9#mP2$")
    assert len(result["sequential"]) == 0
    assert len(result["repeated"]) == 0
    assert len(result["keyboard_walks"]) == 0
    assert len(result["dictionary_words"]) == 0
