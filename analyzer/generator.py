import secrets
import string

def GeneratePassword(length=16, use_uppercase=True, use_lowercase=True,
                     use_digits=True, use_symbols=True):
    """
    Generate a cryptographically secure random password

    Args:
        length: Password length (default 16)
        use_uppercase: Include uppercase letters (default True)
        use_lowercase: Include lowercase letters (default True)
        use_digits: Include numbers (default True)
        use_symbols: Include symbols (default True)

    Returns:
        Generated password string
    """
    if length < 4:
        raise ValueError("Password length must be at least 4 characters")

    # Build character pool
    char_pool = ""
    required_chars = []

    if use_lowercase:
        char_pool += string.ascii_lowercase
        required_chars.append(secrets.choice(string.ascii_lowercase))

    if use_uppercase:
        char_pool += string.ascii_uppercase
        required_chars.append(secrets.choice(string.ascii_uppercase))

    if use_digits:
        char_pool += string.digits
        required_chars.append(secrets.choice(string.digits))

    if use_symbols:
        char_pool += string.punctuation
        required_chars.append(secrets.choice(string.punctuation))

    if not char_pool:
        raise ValueError("At least one character type must be enabled")

    # Generate remaining characters
    remaining_length = length - len(required_chars)
    if remaining_length < 0:
        # If length is too short for all required chars, just use the pool
        password_chars = [secrets.choice(char_pool) for _ in range(length)]
    else:
        # Ensure at least one of each required type, then fill the rest randomly
        password_chars = required_chars + [secrets.choice(char_pool) for _ in range(remaining_length)]

    # Shuffle to avoid predictable patterns
    password_list = list(password_chars)
    secrets.SystemRandom().shuffle(password_list)

    return ''.join(password_list)

def GeneratePasswords(count=1, length=16, use_uppercase=True, use_lowercase=True,
                      use_digits=True, use_symbols=True):
    """
    Generate multiple passwords

    Args:
        count: Number of passwords to generate
        length: Password length
        use_uppercase: Include uppercase letters
        use_lowercase: Include lowercase letters
        use_digits: Include numbers
        use_symbols: Include symbols

    Returns:
        List of generated passwords
    """
    if count < 1:
        raise ValueError("Count must be at least 1")

    if count > 100:
        raise ValueError("Cannot generate more than 100 passwords at once")

    passwords = []
    for _ in range(count):
        password = GeneratePassword(length, use_uppercase, use_lowercase,
                                   use_digits, use_symbols)
        passwords.append(password)

    return passwords
