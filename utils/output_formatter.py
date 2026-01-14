import json

# Try to import colorama for colored output
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Define dummy color codes if colorama is not available
    class Fore:
        RED = ''
        YELLOW = ''
        GREEN = ''
        CYAN = ''
        MAGENTA = ''
        WHITE = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''

def DisplayResults(results, json_output=False):
    """
    Display analysis results in readable format
    Supports both single and batch password analysis
    """
    if json_output:
        DisplayJSONResults(results)
    elif len(results) == 1:
        DisplaySingleResult(results[0])
    else:
        DisplayBatchResults(results)

def DisplaySingleResult(result):
    """Detailed output for single password analysis"""
    print("=" * 60)
    print(f"{Style.BRIGHT}PASSWORD ANALYSIS RESULTS{Style.RESET_ALL}")
    print("=" * 60)
    print()

    # Mask password for privacy
    masked = MaskPassword(result['password'])
    print(f"Password: {Fore.CYAN}{masked}{Style.RESET_ALL}")
    print(f"Length: {result['length']} characters")
    print()

    # Strength summary with color coding
    score = result['strength_score']
    category = result['strength_category']
    color = GetStrengthColor(score)
    print(f"Strength Score: {color}{score}/100 ({category}){Style.RESET_ALL}")
    print(f"Shannon Entropy: {result['entropy']} bits")
    print(f"Character Pool Entropy: {result['pool_entropy']} bits")
    print()

    # Common password warning
    if result['is_common']:
        print(f"{Fore.RED}{Style.BRIGHT}WARNING: This password is COMMONLY USED and appears in breach databases!{Style.RESET_ALL}")
        print()

    # HIBP breach warning
    if 'hibp_pwned' in result:
        if result['hibp_count'] == -1:
            print(f"{Fore.YELLOW}HIBP Check: Could not connect to Have I Been Pwned API{Style.RESET_ALL}")
            print()
        elif result['hibp_pwned']:
            print(f"{Fore.RED}{Style.BRIGHT}HIBP ALERT: This password has been exposed in {result['hibp_count']:,} data breaches!{Style.RESET_ALL}")
            print()
        else:
            print(f"{Fore.GREEN}HIBP Check: Password not found in known breaches{Style.RESET_ALL}")
            print()

    # Pattern detection
    patterns_detected = sum(len(v) for v in result['patterns'].values() if v)
    if patterns_detected > 0:
        print("Detected Patterns:")
        for pattern_type, items in result['patterns'].items():
            if items:
                formatted_type = pattern_type.replace('_', ' ').title()
                items_str = ', '.join(str(i) for i in items[:5])
                print(f"  - {formatted_type}: {items_str}")
        print()

    # Feedback
    if result['feedback']:
        print("Recommendations:")
        for i, feedback_item in enumerate(result['feedback'], 1):
            print(f"  {i}. {feedback_item}")
        print()

    print("=" * 60)

def DisplayBatchResults(results):
    """Summary table for multiple passwords"""
    print("=" * 80)
    print(f"{Style.BRIGHT}BATCH PASSWORD ANALYSIS RESULTS{Style.RESET_ALL}")
    print("=" * 80)
    print()

    # Table header
    print(f"{'#':<4} {'Password':<20} {'Length':<8} {'Score':<8} {'Category':<15} {'Common':<8}")
    print("-" * 80)

    # Table rows
    for i, result in enumerate(results, 1):
        masked = MaskPassword(result['password'])
        common_flag = "YES" if result['is_common'] else "NO"
        common_color = Fore.RED if result['is_common'] else Fore.WHITE

        # Color code the score
        score = result['strength_score']
        color = GetStrengthColor(score)

        print(f"{i:<4} {Fore.CYAN}{masked:<20}{Style.RESET_ALL} {result['length']:<8} "
              f"{color}{score:<8}{Style.RESET_ALL} {result['strength_category']:<15} {common_color}{common_flag:<8}{Style.RESET_ALL}")

    print("-" * 80)
    print()

    # Summary statistics
    avg_score = sum(r['strength_score'] for r in results) / len(results)
    common_count = sum(1 for r in results if r['is_common'])
    weak_count = sum(1 for r in results if r['strength_score'] < 40)

    print("Summary:")
    print(f"  Total passwords analyzed: {len(results)}")
    print(f"  Average strength score: {avg_score:.1f}/100")
    print(f"  Common passwords: {common_count}")
    print(f"  Weak passwords (score < 40): {weak_count}")
    print()

    print("=" * 80)

def MaskPassword(password):
    """Mask password for privacy, showing first 2 and last 2 chars"""
    if len(password) <= 6:
        if len(password) <= 2:
            return "*" * len(password)
        return password[:2] + "*" * (len(password) - 2)
    return password[:2] + "*" * (len(password) - 4) + password[-2:]

def DisplayJSONResults(results):
    """Output results in JSON format"""
    output = {
        "total_passwords": len(results),
        "passwords": []
    }

    for result in results:
        password_data = {
            "password": result['password'],
            "length": result['length'],
            "strength": {
                "score": result['strength_score'],
                "category": result['strength_category']
            },
            "entropy": {
                "shannon": result['entropy'],
                "character_pool": result['pool_entropy']
            },
            "is_common": result['is_common'],
            "patterns": {
                "sequences": result['patterns'].get('sequences', []),
                "keyboard_walks": result['patterns'].get('keyboard_walks', []),
                "repeated_chars": result['patterns'].get('repeated_chars', []),
                "dates": result['patterns'].get('dates', []),
                "common_words": result['patterns'].get('common_words', [])
            },
            "feedback": result['feedback']
        }

        # Add HIBP data if available
        if 'hibp_pwned' in result:
            password_data["hibp"] = {
                "pwned": result['hibp_pwned'],
                "breach_count": result['hibp_count']
            }

        output["passwords"].append(password_data)

    # Calculate summary statistics
    if len(results) > 1:
        avg_score = sum(r['strength_score'] for r in results) / len(results)
        common_count = sum(1 for r in results if r['is_common'])
        weak_count = sum(1 for r in results if r['strength_score'] < 40)

        output["summary"] = {
            "average_strength_score": round(avg_score, 2),
            "common_passwords_count": common_count,
            "weak_passwords_count": weak_count
        }

    print(json.dumps(output, indent=2))

def GetStrengthColor(score):
    """Return color code based on strength score"""
    if score >= 80:
        return Fore.GREEN + Style.BRIGHT
    elif score >= 60:
        return Fore.GREEN
    elif score >= 40:
        return Fore.YELLOW
    elif score >= 20:
        return Fore.YELLOW + Style.BRIGHT
    else:
        return Fore.RED + Style.BRIGHT
