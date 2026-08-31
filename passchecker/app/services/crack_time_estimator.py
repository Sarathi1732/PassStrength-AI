from app.utils.helpers import format_time

class CrackTimeEstimator:
    """Estimates time required to crack a password."""
    
    def estimate(self, password: str) -> dict:
        length = len(password)
        charset_size = 0
        if any(c.islower() for c in password): charset_size += 26
        if any(c.isupper() for c in password): charset_size += 26
        if any(c.isdigit() for c in password): charset_size += 10
        if any(not c.isalnum() for c in password): charset_size += 32
        
        search_space = charset_size ** length if charset_size > 0 else 0
        
        speeds = {
            "1K_guesses_per_sec": 1_000,
            "1M_guesses_per_sec": 1_000_000,
            "100M_guesses_per_sec": 100_000_000,
            "10B_guesses_per_sec": 10_000_000_000
        }
        
        results = {}
        for name, speed in speeds.items():
            if speed > 0:
                seconds = search_space / speed
                results[name] = format_time(seconds)
            else:
                results[name] = "0 seconds"
                
        return results
