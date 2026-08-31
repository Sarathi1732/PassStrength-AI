class FeedbackEngine:
    """Generates actionable feedback based on password analysis."""
    
    def generate_feedback(self, analysis: dict, patterns: dict) -> list[dict]:
        feedback = []
        
        if analysis['length'] < 8:
            feedback.append({"type": "warning", "message": "Password is too short. Use at least 8 characters.", "priority": "high"})
        elif analysis['length'] >= 12:
            feedback.append({"type": "info", "message": "Good password length.", "priority": "low"})
            
        if analysis['uppercase_count'] == 0:
            feedback.append({"type": "warning", "message": "Add uppercase letters to improve strength.", "priority": "medium"})
        if analysis['lowercase_count'] == 0:
            feedback.append({"type": "warning", "message": "Add lowercase letters to improve strength.", "priority": "medium"})
        if analysis['digit_count'] == 0:
            feedback.append({"type": "warning", "message": "Add numbers to improve strength.", "priority": "medium"})
        if analysis['special_count'] == 0:
            feedback.append({"type": "warning", "message": "Add special characters to improve strength.", "priority": "medium"})
            
        if analysis['shannon_entropy'] < 3.0:
            feedback.append({"type": "warning", "message": "Password has low entropy, making it easier to guess.", "priority": "medium"})
            
        if patterns.get('dictionary_words'):
            feedback.append({"type": "warning", "message": "Common dictionary words detected.", "priority": "high"})
        if patterns.get('keyboard_walks'):
            feedback.append({"type": "warning", "message": "Keyboard patterns (like 'qwerty') detected.", "priority": "high"})
        if patterns.get('sequential'):
            feedback.append({"type": "warning", "message": "Sequential characters (like 'abc' or '123') detected.", "priority": "high"})
        if patterns.get('repeated'):
            feedback.append({"type": "warning", "message": "Repeated characters detected.", "priority": "medium"})
        if patterns.get('leetspeak'):
            feedback.append({"type": "warning", "message": "Leetspeak substitutions of common words detected.", "priority": "high"})
            
        if not any(f['priority'] == 'high' for f in feedback) and analysis['complexity_score'] > 70:
            feedback.append({"type": "info", "message": "Excellent password! Very hard to crack.", "priority": "low"})
            
        return feedback
