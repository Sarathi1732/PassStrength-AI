import secrets
import string

class PasswordGenerator:
    """Generates secure passwords."""
    
    def generate(self, length=16, uppercase=True, lowercase=True, digits=True, symbols=True, exclude_ambiguous=False) -> str:
        if not any([uppercase, lowercase, digits, symbols]):
            raise ValueError("At least one character set must be selected.")
            
        ambiguous = "0Ol1I" if exclude_ambiguous else ""
        
        char_sets = []
        if uppercase: char_sets.append(string.ascii_uppercase)
        if lowercase: char_sets.append(string.ascii_lowercase)
        if digits: char_sets.append(string.digits)
        if symbols: char_sets.append(string.punctuation)
        
        if exclude_ambiguous:
            char_sets = [[c for c in s if c not in ambiguous] for s in char_sets]
            
        all_chars = [c for s in char_sets for c in s]
        
        if not all_chars:
             raise ValueError("No valid characters available for generation.")
             
        password = []
        # Ensure at least one character from each selected set
        for s in char_sets:
            if s:
                password.append(secrets.choice(s))
                
        # Fill the rest
        while len(password) < length:
            password.append(secrets.choice(all_chars))
            
        secrets.SystemRandom().shuffle(password)
        return "".join(password)
