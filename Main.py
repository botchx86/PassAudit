import argparse
from analyzer.strength import CalculateStrength, GetStrengthCategory
from analyzer.entropy import CalculateEntropy, CalculateCharacterPoolEntropy
from analyzer.patterns import DetectPatterns
from analyzer.common_passwords import IsCommonPassword
from analyzer.feedback import GenerateFeedback
from analyzer.generator import GeneratePasswords
from analyzer.hibp import CheckHIBP
from utils.output_formatter import DisplayResults
from utils.export import ExportToCSV, ExportToHTML
from utils.config import LoadConfig, SaveConfig, ShowConfig, UpdateConfigValue, ResetConfig, InitializeConfig

def Parser():
    parser = argparse.ArgumentParser(
        prog="PassAudit",
        description="Password security analyzer and generator")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-f", "--file",
        help="Path to file containing passwords (one per line)"
        )

    group.add_argument(
        "-p", "--password",
        help="Single password to analyze"
        )

    group.add_argument(
        "-g", "--generate",
        action="store_true",
        help="Generate secure random passwords"
        )

    # Generator options
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=1,
        help="Number of passwords to generate (default: 1, max: 100)"
        )

    parser.add_argument(
        "-l", "--length",
        type=int,
        default=16,
        help="Length of generated passwords (default: 16)"
        )

    parser.add_argument(
        "--no-uppercase",
        action="store_true",
        help="Exclude uppercase letters from generated passwords"
        )

    parser.add_argument(
        "--no-lowercase",
        action="store_true",
        help="Exclude lowercase letters from generated passwords"
        )

    parser.add_argument(
        "--no-digits",
        action="store_true",
        help="Exclude numbers from generated passwords"
        )

    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Exclude symbols from generated passwords"
        )

    # Output options
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results in JSON format"
        )

    # Security checking options
    parser.add_argument(
        "-b", "--check-hibp",
        action="store_true",
        help="Check passwords against Have I Been Pwned breach database (requires internet)"
        )

    # Export options
    parser.add_argument(
        "--export-csv",
        type=str,
        metavar="FILE",
        help="Export results to CSV file"
        )

    parser.add_argument(
        "--export-html",
        type=str,
        metavar="FILE",
        help="Export results to HTML file"
        )

    # Config options
    parser.add_argument(
        "--config-show",
        action="store_true",
        help="Show current configuration"
        )

    parser.add_argument(
        "--config-init",
        action="store_true",
        help="Initialize default configuration file"
        )

    parser.add_argument(
        "--config-reset",
        action="store_true",
        help="Reset configuration to defaults"
        )

    parser.add_argument(
        "--config-set",
        nargs=3,
        metavar=("SECTION", "KEY", "VALUE"),
        help="Set a configuration value"
        )

    return parser.parse_args()

def LoadPasswordsFromFile(file_path):
    passwords = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            cleaned = line.strip()
            if cleaned:
                passwords.append(cleaned)

    return passwords

def GetPassword(args):
    if args.file:
        return LoadPasswordsFromFile(args.file)

    if args.password:
        return [args.password]

    if args.generate:
        return GeneratePasswords(
            count=args.count,
            length=args.length,
            use_uppercase=not args.no_uppercase,
            use_lowercase=not args.no_lowercase,
            use_digits=not args.no_digits,
            use_symbols=not args.no_symbols
        )

    raise ValueError("No valid input provided")

def AnalyzePassword(password, check_hibp=False):
    """
    Perform comprehensive analysis on a single password
    Returns analysis results as a dictionary
    """
    # Perform all analyses
    patterns = DetectPatterns(password)
    is_common = IsCommonPassword(password)

    # Check HIBP if requested
    hibp_pwned = False
    hibp_count = 0
    if check_hibp:
        hibp_pwned, hibp_count = CheckHIBP(password)
        # If hibp_pwned is None, the check failed (no internet, etc.)
        if hibp_pwned is None:
            hibp_pwned = False
            hibp_count = -1  # -1 indicates check couldn't be performed

    strength_score = CalculateStrength(password, patterns)
    strength_category = GetStrengthCategory(strength_score)
    entropy = CalculateEntropy(password)
    pool_entropy = CalculateCharacterPoolEntropy(password)
    feedback = GenerateFeedback(password, strength_score, patterns, is_common)

    result = {
        'password': password,
        'strength_score': strength_score,
        'strength_category': strength_category,
        'is_common': is_common,
        'entropy': entropy,
        'pool_entropy': pool_entropy,
        'length': len(password),
        'patterns': patterns,
        'feedback': feedback
    }

    # Add HIBP data if checked
    if check_hibp:
        result['hibp_pwned'] = hibp_pwned
        result['hibp_count'] = hibp_count

    return result

def AnalyzePasswords(passwords, check_hibp=False):
    """
    Analyze multiple passwords and return results
    """
    results = []
    for password in passwords:
        result = AnalyzePassword(password, check_hibp=check_hibp)
        results.append(result)

    return results

def Main():
    args = Parser()

    # Handle config commands (these exit early)
    if args.config_show:
        ShowConfig()
        return

    if args.config_init:
        InitializeConfig()
        return

    if args.config_reset:
        ResetConfig()
        return

    if args.config_set:
        section, key, value = args.config_set
        UpdateConfigValue(section, key, value)
        return

    # Check that one of the main options is provided
    if not (args.file or args.password or args.generate):
        print("Error: One of --file, --password, or --generate is required")
        print("Use --help for usage information")
        return

    # Load configuration
    config = LoadConfig()

    # Apply config defaults if not specified via CLI
    if args.generate:
        if args.length == 16:  # Default value, use config
            args.length = config['generator'].get('default_length', 16)
        if args.count == 1:  # Default value, use config
            args.count = config['generator'].get('default_count', 1)

    passwords = GetPassword(args)

    if not args.json:
        if args.generate:
            print(f"Generated {len(passwords)} password(s)\n")
        else:
            print(f"Loaded {len(passwords)} password(s) for analysis\n")

    # Perform analysis
    check_hibp = args.check_hibp or config['security'].get('check_hibp', False)
    results = AnalyzePasswords(passwords, check_hibp=check_hibp)

    # Format and display results
    DisplayResults(results, json_output=args.json)

    # Handle exports
    if args.export_csv:
        ExportToCSV(results, args.export_csv)

    if args.export_html:
        ExportToHTML(results, args.export_html)
    
if __name__ == "__main__":
    Main()