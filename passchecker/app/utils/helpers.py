def format_time(seconds: float) -> str:
    """Format seconds into a human-readable string."""
    if seconds < 1:
        return "less than a second"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 3153600000: # 100 years
        return f"{int(seconds / 31536000)} years"
    elif seconds < 315360000000: # 10,000 years
        return f"{int(seconds / 3153600000)} centuries"
    else:
        return "thousands of centuries"

def sanitize_password(password: str) -> str:
    """Sanitize the password by stripping whitespace and limiting length."""
    return password.strip()[:1000]
