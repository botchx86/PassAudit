def GenerateFeedback(password, strength_score, patterns, is_common):
    """
    Generate specific, actionable feedback for password improvement
    Returns list of feedback messages ordered by priority
    """
    feedback = []

    # Critical issues first
    if is_common:
        feedback.append("CRITICAL: This password appears in common password lists and is easily guessable.")

    # Length issues
    if len(password) < 8:
        feedback.append("Your password is too short. Use at least 12 characters for better security.")
    elif len(password) < 12:
        feedback.append("Consider using at least 12 characters for improved security.")

    # Character diversity issues
    char_types = GetCharacterTypes(password)
    if char_types < 3:
        missing = GetMissingCharacterTypes(password)
        if missing:
            feedback.append(f"Add {', '.join(missing)} to increase password complexity.")

    # Pattern-specific feedback
    if patterns.get('sequences'):
        examples = ', '.join(patterns['sequences'][:3])
        feedback.append(f"Avoid predictable sequences like: {examples}")

    if patterns.get('keyboard_walks'):
        examples = ', '.join(patterns['keyboard_walks'][:3])
        feedback.append(f"Avoid keyboard patterns like: {examples}")

    if patterns.get('repeated_chars'):
        feedback.append("Avoid repeating the same character multiple times.")

    if patterns.get('dates'):
        feedback.append("Avoid using dates or years in your password.")

    if patterns.get('common_words'):
        examples = ', '.join(patterns['common_words'][:3])
        feedback.append(f"Avoid common words like: {examples}")

    # Positive reinforcement for strong passwords
    if strength_score >= 80 and not feedback:
        feedback.append("Excellent password! It's long, complex, and doesn't contain obvious patterns.")

    return feedback

def GetCharacterTypes(password):
    """Count number of character type categories used"""
    types = 0
    if any(c.islower() for c in password): types += 1
    if any(c.isupper() for c in password): types += 1
    if any(c.isdigit() for c in password): types += 1
    if any(not c.isalnum() for c in password): types += 1
    return types

def GetMissingCharacterTypes(password):
    """Return list of missing character types"""
    missing = []
    if not any(c.islower() for c in password): missing.append("lowercase letters")
    if not any(c.isupper() for c in password): missing.append("uppercase letters")
    if not any(c.isdigit() for c in password): missing.append("numbers")
    if not any(not c.isalnum() for c in password): missing.append("symbols")
    return missing
