import hashlib
import urllib.request
import urllib.error

def CheckHIBP(password):
    """
    Check if password has been exposed in data breaches using Have I Been Pwned API
    Uses k-anonymity model - only sends first 5 characters of SHA-1 hash

    Returns:
        tuple: (is_pwned, breach_count)
        - is_pwned: Boolean indicating if password was found in breaches
        - breach_count: Number of times the password appears in breaches (0 if not found)
    """
    try:
        # Calculate SHA-1 hash of password
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

        # Split into prefix (first 5 chars) and suffix (rest)
        hash_prefix = sha1_hash[:5]
        hash_suffix = sha1_hash[5:]

        # Query HIBP API with the prefix
        url = f"https://api.pwnedpasswords.com/range/{hash_prefix}"

        # Add user agent to be polite to the API
        req = urllib.request.Request(url, headers={'User-Agent': 'PasswordRiskAnalyser'})

        with urllib.request.urlopen(req, timeout=5) as response:
            response_text = response.read().decode('utf-8')

        # Parse response - each line is: SUFFIX:COUNT
        for line in response_text.splitlines():
            line = line.strip()
            if ':' in line:
                response_suffix, count = line.split(':')
                if response_suffix == hash_suffix:
                    return (True, int(count))

        # Password not found in breaches
        return (False, 0)

    except urllib.error.URLError as e:
        # Network error - return None to indicate check couldn't be performed
        return (None, 0)
    except Exception as e:
        # Other error - return None to indicate check couldn't be performed
        return (None, 0)
