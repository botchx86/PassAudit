import re
import os
from typing import List, Dict, Set

# Compiled regex patterns for performance
REPEATED_CHARS_PATTERN = re.compile(r'(.)\1{2,}')
DATE_PATTERNS = [
    re.compile(r'19\d{2}'),           # 1900-1999
    re.compile(r'20[0-2]\d'),         # 2000-2029
    re.compile(r'\d{2}[/-]\d{2}[/-]\d{2,4}'),  # DD/MM/YY or DD-MM-YYYY
    re.compile(r'\d{4}[/-]\d{2}[/-]\d{2}'),    # YYYY/MM/DD
    re.compile(r'\d{8}'),             # YYYYMMDD or MMDDYYYY or DDMMYYYY (8 digits)
    re.compile(r'(0[1-9]|[12][0-9]|3[01])'),  # Day 01-31
    re.compile(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', re.IGNORECASE),  # Month names (short)
    re.compile(r'(january|february|march|april|may|june|july|august|september|october|november|december)', re.IGNORECASE)  # Month names (full)
]

def LoadCommonWords() -> Set[str]:
    """Load common words from external file"""
    common_words = set()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.dirname(current_dir)
    file_path = os.path.join(data_dir, "data", "common_words.txt")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    common_words.add(line.lower())
    except FileNotFoundError:
        pass  # Return empty set if file not found

    return common_words

# Load common words at module level for performance
COMMON_WORDS = LoadCommonWords()

def DetectPatterns(password: str) -> Dict[str, List[str]]:
    """
    Returns dict of detected patterns
    {
        'sequences': [list of detected sequences],
        'keyboard_walks': [list of keyboard patterns],
        'repeated_chars': [list of repeated segments],
        'dates': [list of date patterns],
        'common_words': [list of dictionary words],
        'leetspeak': [list of leetspeak words detected],
        'context_patterns': [list of context-specific patterns]
    }
    """
    patterns = {
        'sequences': DetectSequences(password),
        'keyboard_walks': DetectKeyboardWalks(password),
        'repeated_chars': DetectRepeatedChars(password),
        'dates': DetectDatePatterns(password),
        'common_words': DetectCommonWords(password),
        'leetspeak': DetectLeetspeak(password),
        'context_patterns': DetectContextPatterns(password)
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
    Enhanced with additional diagonal and vertical patterns
    """
    keyboard_layouts = [
        # Standard rows
        'qwertyuiop',
        'asdfghjkl',
        'zxcvbnm',
        '1234567890',
        # Diagonal patterns
        '1qaz2wsx3edc',
        '1q2w3e4r',
        'zaq12wsx',
        'xsw23edc',
        'zaqxswcdevfr',
        # Vertical patterns
        'qazwsx',
        'qweasd',
        'qweasdzxc',
        'zaqxswcde',
        # Additional patterns
        'plmoknijb',
        'zaq12wsx23edc',
        # Numpad patterns
        '789456123',
        '741852963',
        '987654321'
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
    repeated = REPEATED_CHARS_PATTERN.findall(password)
    # Return the actual repeated segments
    results = []
    for match in repeated:
        # Find all occurrences of this repeated character (3+ times)
        pattern = re.compile(re.escape(match) + r'{3,}')
        matches = pattern.findall(password)
        results.extend(matches)
    return list(set(results))  # Remove duplicates

def DetectDatePatterns(password):
    """
    Detect date patterns: 1990, 2023, 19/01, 01-01-2000
    """
    dates_found = []
    for pattern in DATE_PATTERNS:
        matches = pattern.findall(password)
        dates_found.extend(matches)

    return dates_found

def DetectCommonWords(password):
    """
    Detect common dictionary words from external file
    """
    found_words = []
    password_lower = password.lower()

    for word in COMMON_WORDS:
        if word in password_lower:
            found_words.append(word)

    return found_words

def DetectLeetspeak(password):
    """
    Detect leetspeak substitutions (e.g., p@ssw0rd, passw0rd)
    Common substitutions: a→@/4, e→3, i→1/!, o→0, s→5/$, t→7
    """
    # Mapping of leetspeak characters to their normal equivalents
    leet_map = {
        '@': 'a', '4': 'a',
        '3': 'e',
        '1': 'i', '!': 'i',
        '0': 'o',
        '5': 's', '$': 's',
        '7': 't',
        '+': 't',
        '8': 'b',
        '9': 'g'
    }

    # Convert password by replacing leetspeak characters
    normalized = []
    for char in password.lower():
        if char in leet_map:
            normalized.append(leet_map[char])
        else:
            normalized.append(char)

    normalized_password = ''.join(normalized)

    # Check if the normalized version contains common words
    found_leetspeak = []
    for word in COMMON_WORDS:
        if word in normalized_password and word not in password.lower():
            # The word exists in normalized form but not in original
            # This means leetspeak was used
            found_leetspeak.append(word)

    return found_leetspeak

def LoadContextPatterns():
    """Load context-specific patterns from external file"""
    context_patterns = set()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.dirname(current_dir)
    file_path = os.path.join(data_dir, "data", "context_patterns.txt")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    context_patterns.add(line.lower())
    except FileNotFoundError:
        # Return default set if file not found
        context_patterns = {
            'microsoft', 'google', 'facebook', 'apple', 'amazon',
            'linux', 'windows', 'android', 'iphone', 'macos',
            'yankees', 'lakers', 'cowboys', 'patriots', 'redsox',
            'starwars', 'pokemon', 'marvel', 'superman', 'batman'
        }

    return context_patterns

# Load context patterns at module level for performance
CONTEXT_PATTERNS = LoadContextPatterns()

def DetectContextPatterns(password):
    """
    Detect context-specific patterns: companies, tech terms, sports, pop culture
    """
    found_patterns = []
    password_lower = password.lower()

    for word in CONTEXT_PATTERNS:
        if word in password_lower:
            found_patterns.append(word)

    return found_patterns
