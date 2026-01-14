import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from analyzer.strength import CalculateStrength, GetStrengthCategory
from analyzer.entropy import CalculateEntropy, CalculateCharacterPoolEntropy
from analyzer.patterns import DetectPatterns
from analyzer.common_passwords import IsCommonPassword
from analyzer.feedback import GenerateFeedback
from analyzer.generator import GeneratePasswords
from analyzer.hibp import CheckHIBP
from analyzer.policy import get_policy, PasswordPolicy
from utils.output_formatter import DisplayResults
from utils.export import ExportToCSV, ExportToHTML
from utils.export_pdf import ExportToPDF
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

    group.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive CLI mode"
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

    # Policy validation options
    parser.add_argument(
        "--policy",
        type=str,
        metavar="PRESET",
        choices=['POLICY_BASIC', 'POLICY_MEDIUM', 'POLICY_STRONG', 'POLICY_ENTERPRISE'],
        help="Validate passwords against a policy preset (POLICY_BASIC, POLICY_MEDIUM, POLICY_STRONG, POLICY_ENTERPRISE)"
        )

    parser.add_argument(
        "--policy-file",
        type=str,
        metavar="FILE",
        help="Path to custom policy JSON file"
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

    parser.add_argument(
        "--export-pdf",
        type=str,
        metavar="FILE",
        help="Export results to PDF file"
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

def AnalyzePassword(password, check_hibp=False, hibp_timeout=5, policy=None):
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
        hibp_pwned, hibp_count = CheckHIBP(password, timeout=hibp_timeout)
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

    # Validate against policy if provided
    if policy:
        is_valid, errors = policy.validate(password, result)
        result['policy_valid'] = is_valid
        result['policy_errors'] = errors
        result['policy_name'] = policy.name

    return result

def AnalyzePasswords(passwords, check_hibp=False, hibp_timeout=5, max_workers=4, policy=None):
    """
    Analyze multiple passwords and return results
    Uses parallel processing for improved performance on large batches

    Args:
        passwords: List of passwords to analyze
        check_hibp: Whether to check HIBP database
        hibp_timeout: Timeout for HIBP requests
        max_workers: Maximum number of parallel workers (default: 4)
        policy: Optional PasswordPolicy for validation
    """
    # For small batches or single passwords, use sequential processing
    if len(passwords) <= 5:
        results = []
        for password in passwords:
            result = AnalyzePassword(password, check_hibp=check_hibp, hibp_timeout=hibp_timeout, policy=policy)
            results.append(result)
        return results

    # For larger batches, use parallel processing
    results = [None] * len(passwords)  # Pre-allocate to maintain order

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(AnalyzePassword, password, check_hibp, hibp_timeout, policy): idx
            for idx, password in enumerate(passwords)
        }

        # Collect results as they complete
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                # Log error but continue with other passwords
                print(f"Error analyzing password {idx + 1}: {e}")
                # Create error result
                results[idx] = {
                    'password': passwords[idx],
                    'error': str(e),
                    'strength_score': 0,
                    'strength_category': 'Error'
                }

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

    # Handle interactive mode
    if args.interactive:
        from cli.interactive import InteractiveCLI
        cli = InteractiveCLI()
        cli.run()
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

    # Load password policy if specified
    policy = None
    if args.policy:
        policy = get_policy(args.policy)
        if policy and not args.json:
            print(f"Using policy: {policy.name}")
            print(f"Policy requirements:")
            for req in policy.get_requirements():
                print(f"  - {req}")
            print()
    elif args.policy_file:
        # TODO: Implement custom policy file loading
        print("Custom policy files not yet implemented")

    # Perform analysis
    check_hibp = args.check_hibp or config['security'].get('check_hibp', False)
    hibp_timeout = config['security'].get('hibp_timeout', 5)
    max_workers = config.get('performance', {}).get('batch_processing_threads', 4)
    results = AnalyzePasswords(passwords, check_hibp=check_hibp, hibp_timeout=hibp_timeout, max_workers=max_workers, policy=policy)

    # Format and display results
    DisplayResults(results, json_output=args.json)

    # Handle exports
    if args.export_csv:
        ExportToCSV(results, args.export_csv)

    if args.export_html:
        ExportToHTML(results, args.export_html)

    if args.export_pdf:
        ExportToPDF(results, args.export_pdf)
    
if __name__ == "__main__":
    Main()