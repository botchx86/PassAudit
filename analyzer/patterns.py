import re

def DetectPatterns(password):
    """
    Returns dict of detected patterns
    {
        'sequences': [list of detected sequences],
        'keyboard_walks': [list of keyboard patterns],
        'repeated_chars': [list of repeated segments],
        'dates': [list of date patterns],
        'common_words': [list of dictionary words]
    }
    """
    patterns = {
        'sequences': DetectSequences(password),
        'keyboard_walks': DetectKeyboardWalks(password),
        'repeated_chars': DetectRepeatedChars(password),
        'dates': DetectDatePatterns(password),
        'common_words': DetectCommonWords(password)
    }

    return patterns

def DetectSequences(password):
    """
    Detect sequential patterns: 123, abc, 987, zyx
    """
    sequences_found = []
    password_lower = password.lower()

    # Check numeric sequences (123, 987)
    for i in range(len(password) - 2):
        if password[i:i+3].isdigit():
            nums = [int(c) for c in password[i:i+3]]
            if len(nums) == 3:
                diff1 = nums[1] - nums[0]
                diff2 = nums[2] - nums[1]
                if diff1 == diff2 and abs(diff1) == 1:
                    sequences_found.append(password[i:i+3])

    # Check alphabetic sequences (abc, xyz, cba)
    for i in range(len(password_lower) - 2):
        if password_lower[i:i+3].isalpha():
            ords = [ord(c) for c in password_lower[i:i+3]]
            if len(ords) == 3:
                diff1 = ords[1] - ords[0]
                diff2 = ords[2] - ords[1]
                if diff1 == diff2 and abs(diff1) == 1:
                    sequences_found.append(password[i:i+3])

    return sequences_found

def DetectKeyboardWalks(password):
    """
    Detect keyboard patterns: qwerty, asdfgh, 1qaz, etc.
    """
    keyboard_layouts = [
        'qwertyuiop',
        'asdfghjkl',
        'zxcvbnm',
        '1234567890',
        '1qaz2wsx3edc',
        'qazwsx',
        'qweasd',
        'zaqxswcde'
    ]

    walks_found = []
    password_lower = password.lower()

    for layout in keyboard_layouts:
        # Check forward and backward
        for direction in [layout, layout[::-1]]:
            for i in range(len(direction) - 3):
                pattern = direction[i:i+4]
                if pattern in password_lower:
                    # Find the actual case-sensitive match
                    start_idx = password_lower.find(pattern)
                    walks_found.append(password[start_idx:start_idx+4])

    return list(set(walks_found))  # Remove duplicates

def DetectRepeatedChars(password):
    """
    Detect repeated characters: aaa, 111, !!!!
    """
    repeated = re.findall(r'(.)\1{2,}', password)
    # Return the actual repeated segments
    results = []
    for match in repeated:
        # Find all occurrences of this repeated character (3+ times)
        pattern = re.escape(match) + r'{3,}'
        matches = re.findall(pattern, password)
        results.extend(matches)
    return list(set(results))  # Remove duplicates

def DetectDatePatterns(password):
    """
    Detect date patterns: 1990, 2023, 19/01, 01-01-2000
    """
    date_patterns = [
        r'19\d{2}',           # 1900-1999
        r'20[0-2]\d',         # 2000-2029
        r'\d{2}[/-]\d{2}[/-]\d{2,4}',  # DD/MM/YY or DD-MM-YYYY
        r'\d{4}[/-]\d{2}[/-]\d{2}'     # YYYY/MM/DD
    ]

    dates_found = []
    for pattern in date_patterns:
        matches = re.findall(pattern, password)
        dates_found.extend(matches)

    return dates_found

def DetectCommonWords(password):
    """
    Detect common dictionary words (embedded list of common words)
    """
    common_words = [
        'password', 'passwd', 'admin', 'user', 'login', 'welcome',
        'master', 'letmein', 'monkey', 'dragon', 'shadow', 'sunshine',
        'princess', 'qwerty', 'abc123', 'password1', 'iloveyou',
        'football', 'baseball', 'basketball', 'soccer', 'batman',
        'superman', 'hello', 'test', 'demo', 'sample', 'temp',
        'secret', 'passw0rd', 'p@ssword', 'trustno1', 'starwars',
        'freedom', 'whatever', 'mustang', 'jordan', 'harley',
        'ranger', 'buster', 'hunter', 'killer', 'summer', 'winter',
        'spring', 'autumn', 'internet', 'computer', 'gaming'
    ]

    found_words = []
    password_lower = password.lower()

    for word in common_words:
        if word in password_lower:
            found_words.append(word)

    return found_words
