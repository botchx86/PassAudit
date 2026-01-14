import os

def LoadCommonPasswords():
    """
    Load common passwords list into a set for O(1) lookup
    Uses data/common_passwords.txt
    """
    common_set = set()

    # Get the path relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    file_path = os.path.join(data_dir, "common_passwords.txt")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Skip comments and empty lines
                line = line.strip()
                if line and not line.startswith('#'):
                    # Store in lowercase for case-insensitive matching
                    common_set.add(line.lower())
    except FileNotFoundError:
        # If file doesn't exist, return empty set
        # This allows the tool to work without the common passwords database
        pass

    return common_set

# Cache at module level for performance
COMMON_PASSWORDS = LoadCommonPasswords()

def IsCommonPassword(password):
    """Check if password is in common passwords list (case-insensitive)"""
    return password.lower() in COMMON_PASSWORDS
