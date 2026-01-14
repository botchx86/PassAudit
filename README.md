# PassAudit

> A comprehensive password security analyser that provides detailed vulnerability assessments and actionable recommendations.

PassAudit delivers transparent password analysis with specific explanations for security weaknesses. Rather than providing generic strength ratings, it identifies exact vulnerabilities including common patterns, breach exposure, and structural weaknesses with detailed remediation guidance.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)]
[![Tests](https://img.shields.io/badge/tests-40%20passed-brightgreen.svg)](tests/)

## Features

PassAudit provides comprehensive password security analysis including:

- **Quantitative strength scoring** (0-100 scale) based on length, entropy, and character diversity
- **Pattern detection** identifying sequences, keyboard walks, repeated characters, dates, and common words
- **Breach database checking** via Have I Been Pwned's database of over 600 million compromised passwords
- **Detailed recommendations** with specific, actionable guidance for improving password security
- **Cryptographically secure password generation** using Python's secrets module
- **Multiple output formats** including terminal display, JSON, CSV, and HTML reports

## Installation

```bash
# Clone the repository
git clone https://github.com/botchx86/PassAudit.git
cd PassAudit

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Analyse a single password
python Main.py -p "MyPassword123"

# Generate a secure password
python Main.py -g

# Check password against breach databases
python Main.py -p "password" -b
```

## Usage

### Command Line Interface

**Single Password Analysis**
```bash
python Main.py -p "YourPassword"
```

**Batch Analysis**
```bash
# Analyse passwords from a file (one per line)
python Main.py -f passwords.txt
```

**Password Generation**
```bash
# Generate 5 passwords of 20 characters each
python Main.py -g -c 5 -l 20

# Generate without special characters
python Main.py -g --no-symbols
```

**Breach Checking**
```bash
# Check against Have I Been Pwned database
python Main.py -p "test123" -b
```

**Report Export**
```bash
# Export to HTML or CSV format
python Main.py -f passwords.txt --export-html report.html
python Main.py -f passwords.txt --export-csv results.csv
```

### Command Line Options

```
-p, --password      Analyse a single password
-f, --file          Analyse passwords from a file
-g, --generate      Generate secure passwords
-c, --count         Number of passwords to generate (default: 1)
-l, --length        Password length (default: 16)
-j, --json          Output results in JSON format
-b, --check-hibp    Check Have I Been Pwned database
--export-csv        Export results to CSV file
--export-html       Export results to HTML file
--config-show       Show current configuration
--config-init       Initialise default configuration file
--config-reset      Reset configuration to defaults
--config-set        Set configuration value
```

## Analysis Output

PassAudit provides detailed analysis results including strength scores, entropy measurements, detected patterns, and specific recommendations:

```
============================================================
PASSWORD ANALYSIS RESULTS
============================================================

Password: Te******4!
Length: 9 characters

Strength Score: 29.9/100 (Weak)
Shannon Entropy: 28.53 bits

Detected Patterns:
  - Sequences: 123, 234
  - Keyboard Walks: 1234
  - Common Words: test

Recommendations:
  1. Consider using at least 12 characters
  2. Avoid predictable sequences like: 123, 234
  3. Avoid keyboard patterns like: 1234
  4. Avoid common words like: test

============================================================
```

## Scoring Methodology

PassAudit uses a multi-factor scoring algorithm that evaluates passwords on a 0-100 scale:

### Score Components

- **Length (30 points)** - Longer passwords provide more entropy and resistance to brute force attacks
- **Character diversity (25 points)** - Mixing uppercase, lowercase, numbers, and symbols increases complexity
- **Entropy (25 points)** - Shannon entropy measures actual randomness and unpredictability
- **Pattern penalties (-20 points)** - Deductions for sequences, keyboard walks, dates, repeated characters, and common words

### Strength Categories

- **80-100: Very Strong** - Excellent security for sensitive accounts
- **60-79: Strong** - Good security for most applications
- **40-59: Medium** - Acceptable for low-security applications, improvement recommended
- **20-39: Weak** - Vulnerable to various attack methods, should be changed
- **0-19: Very Weak** - Highly vulnerable, immediate replacement required

## Pattern Detection

PassAudit identifies multiple categories of vulnerable patterns:

- **Sequential patterns** - Numeric sequences (123, 789), alphabetic sequences (abc, xyz)
- **Keyboard walks** - Patterns following keyboard layout (qwerty, asdfgh, 1234567890)
- **Repeated characters** - Multiple consecutive identical characters (aaa, 111)
- **Date patterns** - Years (1990, 2023) and date formats (12/31/2023)
- **Common words** - Dictionary words and common password components (password, admin, test)
- **Common passwords** - Passwords appearing in breach databases (~200 by default, expandable to 10,000+)

## Have I Been Pwned Integration

PassAudit integrates with the Have I Been Pwned (HIBP) API to check passwords against a database of over 600 million compromised passwords from known data breaches.

### Privacy Implementation

The integration uses k-anonymity to protect password privacy:

1. Password is hashed using SHA-1
2. Only the first 5 characters of the hash are sent to the HIBP API
3. The full password or complete hash never leaves your system
4. This implementation is specifically designed by HIBP for secure third-party tools

### Example Usage

```bash
python Main.py -p "password" -b
# Output: HIBP ALERT: This password has been exposed in 52,256,179 data breaches!
```

Note that the above password has been compromised in over 52 million breaches and should never be used.

## Configuration

PassAudit stores user preferences in `~/.passaudit/config.json`, allowing you to set default values for password generation, output formatting, and security options.

### Configuration Commands

```bash
# Initialise configuration file with defaults
python Main.py --config-init

# Set default password length to 20 characters
python Main.py --config-set generator default_length 20

# View current configuration
python Main.py --config-show
```

### Configuration Options

- **Generator settings**: Default length, count, character type preferences
- **Output settings**: JSON mode, colour output preferences
- **Security settings**: Default HIBP checking behaviour

## Expanding the Password Database

PassAudit ships with approximately 200 of the most common passwords. For enhanced coverage, you can download and install the SecLists 10,000 most common passwords:

```bash
python scripts/download_passwords.py
```

This script downloads the SecLists database and replaces the default common password list, providing significantly improved detection of weak passwords.

## Development and Testing

PassAudit includes a comprehensive test suite with 40 unit tests covering all core functionality.

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run tests with coverage report
pytest tests/ --cov=analyzer --cov=utils --cov-report=html
```

All tests pass successfully, with good coverage of core modules including strength calculation, pattern detection, entropy analysis, password generation, and feedback generation.

## Project Structure

```
PassAudit/
├── Main.py                     # CLI entry point and argument parsing
├── analyzer/                   # Core analysis engine
│   ├── strength.py            # Multi-factor strength scoring algorithm
│   ├── patterns.py            # Pattern detection (sequences, keyboard, dates)
│   ├── entropy.py             # Shannon and character pool entropy calculations
│   ├── generator.py           # Cryptographically secure password generation
│   ├── hibp.py                # Have I Been Pwned API integration
│   ├── common_passwords.py    # Common password database checking
│   └── feedback.py            # Recommendation generation
├── utils/                      # Output and configuration utilities
│   ├── output_formatter.py    # Terminal and JSON output formatting
│   ├── export.py              # CSV and HTML report generation
│   └── config.py              # Configuration file management
├── data/                       # Password databases
│   └── common_passwords.txt   # Common password list (~200 default)
├── tests/                      # Unit test suite (40 tests)
├── scripts/                    # Utility scripts
│   └── download_passwords.py  # Database expansion tool
└── .github/workflows/          # CI/CD configuration
    └── tests.yml              # Automated testing pipeline
```

## Design Philosophy

PassAudit addresses common shortcomings in password security tools:

1. **Transparency** - Provides specific explanations rather than opaque ratings
2. **Actionability** - Delivers concrete recommendations for improvement
3. **Comprehensiveness** - Checks against real breach databases, not just theoretical strength
4. **Privacy** - All analysis runs locally; HIBP integration uses k-anonymity
5. **Flexibility** - Supports both interactive CLI usage and automated batch processing
6. **Professional output** - Generates audit-ready reports in multiple formats

This tool is designed for security professionals conducting password audits, system administrators evaluating user password policies, and developers implementing password validation in applications.

## Use Cases

- **Security audits** - Batch analysis of organisational passwords with detailed reporting
- **Password policy enforcement** - Integration into user account systems for validation
- **Security training** - Demonstrating password vulnerabilities with specific examples
- **Incident response** - Checking whether credentials may be compromised
- **Automation** - JSON output mode for integration with security pipelines

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch
3. Implement changes with appropriate tests
4. Ensure all tests pass (`pytest tests/`)
5. Submit a pull request with a clear description of changes

Please include unit tests for new functionality and ensure code follows existing style conventions.

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the LICENSE file for complete terms.

Under GPL-3.0, you are free to use, modify, and distribute this software. If you distribute modified versions, they must also be licensed under GPL-3.0, ensuring the software remains open source.

## Credits

- **Author**: [@botchx86](https://github.com/botchx86)
- **Have I Been Pwned API**: [haveibeenpwned.com](https://haveibeenpwned.com/) by Troy Hunt
- **Common password lists**: [SecLists](https://github.com/danielmiessler/SecLists) by Daniel Miessler
- **Terminal colours**: [colorama](https://github.com/tartley/colorama)

## Frequently Asked Questions

**Does this tool send passwords to external services?**

No. All password analysis is performed locally on your system. The optional Have I Been Pwned integration only sends the first 5 characters of a SHA-1 hash using k-anonymity, never the actual password or complete hash.

**Is this suitable for professional security audits?**

Yes. PassAudit is designed for professional use and provides audit-ready output in multiple formats including HTML and CSV reports suitable for documentation purposes.

**How accurate is the scoring system?**

The scoring methodology is based on NIST password guidelines and industry-standard security practices. While no automated tool is perfect, PassAudit provides reliable detection of common password vulnerabilities and weaknesses.

**Can this be integrated into automated systems?**

Yes. PassAudit supports JSON output mode (`-j` flag) and can be integrated into security pipelines, password validation systems, and automated testing frameworks.

**What is the performance impact for large datasets?**

PassAudit is optimised for batch processing. The common password database uses hash-based lookups for O(1) performance. HIBP checks require network requests and should be used judiciously for large datasets.

---

PassAudit is a security tool designed to improve password hygiene through transparent analysis and specific recommendations.
