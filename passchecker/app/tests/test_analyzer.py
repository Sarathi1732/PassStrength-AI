"""
Tests for PasswordAnalyzer service.
Tests entropy calculation, feature extraction, and complexity scoring.
"""

import pytest
import math


def test_entropy_empty_password(analyzer):
    """Entropy should be 0 for an empty password."""
    result = analyzer.analyze("")
    assert result["shannon_entropy"] == 0
    assert result["length"] == 0


def test_entropy_single_char(analyzer):
    """Entropy should be 0 for a single repeated character."""
    result = analyzer.analyze("a")
    assert result["shannon_entropy"] == 0.0


def test_entropy_simple_password(analyzer):
    """Known entropy for 'aaaaaa' — all same chars means 0 entropy."""
    result = analyzer.analyze("aaaaaa")
    assert result["shannon_entropy"] == 0.0
    assert result["search_space_entropy"] > 0  # search space is based on charset


def test_entropy_complex_password(analyzer):
    """Complex password should have higher entropy than simple one."""
    simple = analyzer.analyze("aaaaaa")
    complex_pw = analyzer.analyze("aB1!xY2@")
    assert complex_pw["shannon_entropy"] > simple["shannon_entropy"]


def test_feature_extraction_counts(analyzer):
    """Verify correct uppercase, lowercase, digit, special counts."""
    result = analyzer.analyze("aBcD12!@")
    assert result["lowercase_count"] == 2  # a, c
    assert result["uppercase_count"] == 2  # B, D
    assert result["digit_count"] == 2      # 1, 2
    assert result["special_count"] == 2    # !, @


def test_complexity_score_range(analyzer):
    """Complexity score should be between 0 and 100."""
    result = analyzer.analyze("Password123!")
    assert 0 <= result["complexity_score"] <= 100


def test_unique_char_ratio(analyzer):
    """Verify unique character ratio calculation."""
    result = analyzer.analyze("aabbcc")
    assert result["unique_char_ratio"] == 0.5  # 3 unique / 6 total


def test_character_diversity(analyzer):
    """Password with all 4 char types should have diversity = 4."""
    result = analyzer.analyze("aA1!")
    assert result["character_diversity"] == 4
