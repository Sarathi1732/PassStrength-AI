import os

class PatternDetector:
    """Detects various patterns in passwords."""

    def __init__(self):
        self.common_passwords = [
            "password", "123456", "12345678", "qwerty", "abc123", "monkey", 
            "master", "dragon", "111111", "baseball", "iloveyou", "trustno1", 
            "sunshine", "princess", "football", "shadow", "superman", "michael", 
            "welcome", "admin", "letmein", "login", "starwars", "hello", 
            "charlie", "donald", "password1", "qwerty123"
        ]
        self.keyboard_rows = [
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm",
            "1234567890"
        ]
        self.leetspeak_map = {
            '@': 'a', '0': 'o', '1': 'i', '3': 'e', '$': 's', '5': 's', '7': 't', '4': 'a', '!': 'i'
        }

    def detect_all(self, password: str) -> dict:
        password_lower = password.lower()
        return {
            "sequential": self.detect_sequential(password_lower),
            "repeated": self.detect_repeated(password_lower),
            "keyboard_walks": self.detect_keyboard_walks(password_lower),
            "dictionary_words": self.detect_dictionary_words(password_lower),
            "leetspeak": self.detect_leetspeak(password_lower)
        }

    def detect_sequential(self, password: str) -> list:
        seqs = []
        for i in range(len(password) - 2):
            if ord(password[i]) + 1 == ord(password[i+1]) and ord(password[i+1]) + 1 == ord(password[i+2]):
                seqs.append(password[i:i+3])
            if ord(password[i]) - 1 == ord(password[i+1]) and ord(password[i+1]) - 1 == ord(password[i+2]):
                seqs.append(password[i:i+3])
        return list(set(seqs))

    def detect_repeated(self, password: str) -> list:
        reps = []
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                reps.append(password[i:i+3])
        return list(set(reps))

    def detect_keyboard_walks(self, password: str) -> list:
        walks = []
        for row in self.keyboard_rows:
            for i in range(len(row) - 2):
                walk = row[i:i+3]
                if walk in password:
                    walks.append(walk)
                if walk[::-1] in password:
                    walks.append(walk[::-1])
        return list(set(walks))

    def detect_dictionary_words(self, password: str) -> list:
        words = []
        for word in self.common_passwords:
            if word in password:
                words.append(word)
        return list(set(words))

    def detect_leetspeak(self, password: str) -> list:
        decoded = ""
        for char in password:
            decoded += self.leetspeak_map.get(char, char)
        return self.detect_dictionary_words(decoded)
