import math
from collections import Counter

class PasswordAnalyzer:
    """Analyzes a password and returns various metrics."""
    
    def analyze(self, password: str) -> dict:
        """
        Analyzes the password and returns metrics like length, entropy, and complexity score.
        """
        length = len(password)
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        special_count = length - uppercase_count - lowercase_count - digit_count
        
        unique_char_ratio = len(set(password)) / length if length > 0 else 0
        
        char_types = sum([
            1 if uppercase_count > 0 else 0,
            1 if lowercase_count > 0 else 0,
            1 if digit_count > 0 else 0,
            1 if special_count > 0 else 0
        ])
        
        char_freq = dict(Counter(password))
        
        shannon_entropy = 0.0
        for count in char_freq.values():
            p = count / length
            shannon_entropy -= p * math.log2(p)
            
        charset_size = 0
        if lowercase_count > 0: charset_size += 26
        if uppercase_count > 0: charset_size += 26
        if digit_count > 0: charset_size += 10
        if special_count > 0: charset_size += 32
        
        search_space_entropy = length * math.log2(charset_size) if charset_size > 0 else 0
        
        complexity_score = min(100, max(0, int(search_space_entropy * 0.8 + char_types * 5)))
        
        return {
            "length": length,
            "uppercase_count": uppercase_count,
            "lowercase_count": lowercase_count,
            "digit_count": digit_count,
            "special_count": special_count,
            "unique_char_ratio": unique_char_ratio,
            "character_diversity": char_types,
            "character_frequency": char_freq,
            "shannon_entropy": shannon_entropy,
            "search_space_entropy": search_space_entropy,
            "complexity_score": complexity_score
        }
