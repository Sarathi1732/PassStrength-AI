import math
import re
from collections import Counter
from typing import List

class FeatureExtractor:
    """Extracts numerical features from passwords for ML models."""

    def __init__(self):
        # A small sample of common dictionary words to avoid external dependencies
        self.common_words = {
            "password", "123456", "12345678", "qwerty", "abc123", "monkey", 
            "1234567", "letmein", "trustno1", "dragon", "baseball", "iloveyou", 
            "master", "sunshine", "ashley", "bailey", "shadow", "123123", 
            "654321", "superman", "qazwsx", "michael", "football", "password1", 
            "welcome", "jesus", "ninja", "mustang", "password123", "admin"
        }
        self.leetspeak_map = {'@': 'a', '0': 'o', '1': 'i', '3': 'e', '$': 's', '5': 's', '7': 't'}
        self.keyboard_walks = ["qwerty", "asdf", "zxcv", "qazwsx"]

    def get_feature_names(self) -> List[str]:
        """Returns the list of feature names."""
        return [
            "length",
            "uppercase_count",
            "lowercase_count",
            "digit_count",
            "special_char_count",
            "unique_char_ratio",
            "char_diversity",
            "shannon_entropy",
            "has_sequential",
            "has_repeated",
            "has_keyboard_walk",
            "has_dictionary_word",
            "has_leetspeak",
            "search_space_log",
            "complexity_score"
        ]

    def extract_features(self, password: str) -> List[float]:
        """Extracts 15 numerical features from the given password."""
        if not password:
            return [0.0] * 15

        length = len(password)
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        special_char_count = length - (uppercase_count + lowercase_count + digit_count)

        unique_chars = len(set(password))
        unique_char_ratio = unique_chars / length if length > 0 else 0.0

        char_diversity = sum([
            1 if uppercase_count > 0 else 0,
            1 if lowercase_count > 0 else 0,
            1 if digit_count > 0 else 0,
            1 if special_char_count > 0 else 0
        ])

        # Shannon Entropy
        freqs = Counter(password)
        shannon_entropy = -sum((count / length) * math.log2(count / length) for count in freqs.values())

        # Patterns
        lower_pass = password.lower()
        
        # Sequential: 3+ consecutive ascending/descending (e.g., abc, 123)
        has_sequential = 0
        for i in range(length - 2):
            if abs(ord(lower_pass[i+1]) - ord(lower_pass[i])) == 1 and \
               ord(lower_pass[i+2]) - ord(lower_pass[i+1]) == ord(lower_pass[i+1]) - ord(lower_pass[i]):
                has_sequential = 1
                break

        # Repeated: 3+ same consecutive chars (e.g., aaa)
        has_repeated = 1 if re.search(r'(.)\1{2,}', lower_pass) else 0

        # Keyboard walk
        has_keyboard_walk = 0
        for walk in self.keyboard_walks:
            if walk in lower_pass or walk[::-1] in lower_pass:
                has_keyboard_walk = 1
                break

        # Dictionary word
        has_dictionary_word = 1 if any(word in lower_pass for word in self.common_words) else 0

        # Leetspeak
        normalized_pass = "".join(self.leetspeak_map.get(c, c) for c in lower_pass)
        has_leetspeak = 1 if normalized_pass != lower_pass and any(word in normalized_pass for word in self.common_words) else 0

        # Search space log
        charset_size = 0
        if uppercase_count > 0: charset_size += 26
        if lowercase_count > 0: charset_size += 26
        if digit_count > 0: charset_size += 10
        if special_char_count > 0: charset_size += 32
        
        search_space_log = 0.0
        if charset_size > 0 and length > 0:
            search_space_log = min(50.0, length * math.log10(charset_size))

        # Complexity Score (0-100 composite)
        complexity_score = min(100.0, (
            length * 4 +
            (uppercase_count * 2 if uppercase_count > 0 else 0) +
            (lowercase_count * 2 if lowercase_count > 0 else 0) +
            (digit_count * 4 if digit_count > 0 else 0) +
            (special_char_count * 6 if special_char_count > 0 else 0) +
            (char_diversity * 5) -
            (has_sequential * 10) -
            (has_repeated * 10) -
            (has_keyboard_walk * 10) -
            (has_dictionary_word * 15)
        ))
        if complexity_score < 0:
            complexity_score = 0.0

        return [
            float(length),
            float(uppercase_count),
            float(lowercase_count),
            float(digit_count),
            float(special_char_count),
            float(unique_char_ratio),
            float(char_diversity),
            float(shannon_entropy),
            float(has_sequential),
            float(has_repeated),
            float(has_keyboard_walk),
            float(has_dictionary_word),
            float(has_leetspeak),
            float(search_space_log),
            float(complexity_score)
        ]
