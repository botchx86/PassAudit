# PassAudit

> A comprehensive enterprise-ready password security analyzer with web interface, API, and advanced pattern detection.

PassAudit delivers transparent password analysis with specific explanations for security weaknesses. It identifies vulnerabilities including common patterns, breach exposure, leetspeak variations, and structural weaknesses with detailed remediation guidance.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-60%2B%20passed-brightgreen.svg)](tests/)

## Features

### Core Analysis
- **Quantitative strength scoring** (0-100 scale) based on length, entropy, and character diversity
- **Advanced pattern detection**: sequences, keyboard walks, repeated characters, dates, common words, **leetspeak**, and **context-specific patterns**
- **Breach database checking** via Have I Been Pwned's 600M+ compromised passwords database
- **Password policy validation** with customizable rules and preset policies
- **Detailed recommendations** with specific, actionable guidance

### Interfaces
- **CLI Tool**: Full-featured command-line interface
- **Interactive Mode**: Menu-driven interface with session tracking
- **Web Interface**: Professional Flask-based web application
- **RESTful API**: JSON API for programmatic access
- **Python Library**: Use as a module in your own applications

### Enterprise Features
- **Parallel batch processing** for analyzing thousands of passwords efficiently
- **Multiple export formats**: CSV, HTML, and **professional PDF reports**
- **Password policy enforcement** with preset and custom policies
- **HIBP caching** for improved performance
- **Docker deployment** with docker-compose support
- **Comprehensive logging** with rotating file handlers

## Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/botchx86/PassAudit.git
cd PassAudit

# Install dependencies
pip install -r requirements.txt

# Download password database (recommended)
python scripts/download_passwords.py
```

### Docker Installation

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t passaudit .
docker run -p 5000:5000 passaudit
```

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

## Quick Start

### Command Line

```bash
# Analyze a single password
python Main.py -p "MyPassword123"

# Generate secure passwords
python Main.py -g -c 5 -l 20

# Check against breach database
python Main.py -p "password" -b

# Validate against policy
python Main.py -p "MyPass123" --policy POLICY_STRONG

# Batch analysis with PDF export
python Main.py -f passwords.txt --export-pdf report.pdf
```

### Interactive Mode

```bash
python Main.py --interactive
```

Provides a menu-driven interface with options for analysis, generation, HIBP checking, configuration management, and session history.

### Web Interface

```bash
python run_web.py
```

Then open your browser to: **http://localhost:5000**

Features:
- Real-time password strength checker
- Batch file upload and analysis
- Password generator with custom options
- Detailed analysis visualizations
- Export results to CSV/HTML/PDF

### Python API

```python
from api import PassAuditAPI

# Initialize API
api = PassAuditAPI()

# Analyze a password
result = api.analyze_password("MyPassword123", check_hibp=True)
print(f"Strength: {result['strength_score']}/100")
print(f"Category: {result['strength_category']}")

# Batch analysis
passwords = ["password1", "password2", "password3"]
results = api.analyze_batch(passwords)

# Generate passwords
passwords = api.generate_batch(count=5, length=16)
```

See [examples/](examples/) directory for complete usage examples.

## Usage

### Command Line Interface

#### Single Password Analysis
```bash
python Main.py -p "YourPassword"
python Main.py -p "MyP@ss123" -b  # With HIBP check
python Main.py -p "Test123" --policy POLICY_STRONG  # With policy validation
```

#### Batch Analysis
```bash
# Analyze passwords from file (one per line)
python Main.py -f passwords.txt

# With HIBP checking
python Main.py -f passwords.txt -b

# With policy validation
python Main.py -f passwords.txt --policy POLICY_ENTERPRISE
```

#### Password Generation
```bash
# Generate 5 passwords of 20 characters
python Main.py -g -c 5 -l 20

# Generate without special characters
python Main.py -g --no-symbols

# Generate and analyze
python Main.py -g -c 10 -l 16
```

#### Export Reports
```bash
# Export to different formats
python Main.py -f passwords.txt --export-csv results.csv
python Main.py -f passwords.txt --export-html report.html
python Main.py -f passwords.txt --export-pdf report.pdf

# Multiple exports
python Main.py -f passwords.txt --export-csv data.csv --export-pdf report.pdf
```

### Command Line Options

```
Analysis:
  -p, --password          Analyze a single password
  -f, --file              Analyze passwords from a file
  -g, --generate          Generate secure passwords
  -i, --interactive       Start interactive CLI mode

Generation:
  -c, --count             Number of passwords to generate (default: 1, max: 100)
  -l, --length            Password length (default: 16)
  --no-uppercase          Exclude uppercase letters
  --no-lowercase          Exclude lowercase letters
  --no-digits             Exclude numbers
  --no-symbols            Exclude symbols

Security:
  -b, --check-hibp        Check Have I Been Pwned database
  --policy PRESET         Validate against policy (POLICY_BASIC, POLICY_MEDIUM, POLICY_STRONG, POLICY_ENTERPRISE)
  --policy-file FILE      Use custom policy JSON file

Output:
  -j, --json              Output in JSON format
  --export-csv FILE       Export to CSV
  --export-html FILE      Export to HTML
  --export-pdf FILE       Export to PDF

Configuration:
  --config-show           Show current configuration
  --config-init           Initialize default configuration
  --config-reset          Reset to defaults
  --config-set SECTION KEY VALUE  Set configuration value
```

## Analysis Output

PassAudit provides comprehensive analysis results:

```
============================================================
PASSWORD ANALYSIS RESULTS
============================================================

Password: Te******4!
Length: 9 characters

Strength Score: 29.9/100 (Weak)
Shannon Entropy: 28.53 bits
Character Pool Entropy: 42.18 bits

Detected Patterns:
  - Sequences: 123, 234
  - Keyboard Walks: 1234
  - Common Words: test
  - Leetspeak: test

Recommendations:
  1. Consider using at least 12 characters for improved security
  2. Avoid predictable sequences like: 123, 234
  3. Avoid keyboard patterns like: 1234
  4. Avoid common words like: test

Policy Validation (POLICY_STRONG):
  [FAIL] Password does not meet policy requirements

  Policy Violations:
    1. Password must be at least 12 characters long
    2. Password must have at least 50 bits of entropy
    3. Password contains forbidden patterns

============================================================
```

## Password Policies

PassAudit includes preset password policies and supports custom policies:

### Preset Policies

**POLICY_BASIC** (Good for general use)
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 digit

**POLICY_MEDIUM** (Recommended for most applications)
- Minimum 10 characters
- At least 1 uppercase, 1 lowercase, 1 digit, 1 symbol
- Must not be a common password
- Minimum strength score of 40

**POLICY_STRONG** (Recommended for sensitive accounts)
- Minimum 12 characters
- Mixed character types
- Must not be common password
- Minimum 50 bits entropy
- Minimum strength score of 60
- No sequences or keyboard walks

**POLICY_ENTERPRISE** (Maximum security)
- Minimum 14 characters
- At least 2 of each character type
- Minimum 60 bits entropy
- Minimum strength score of 70
- No patterns allowed
- Must not be in HIBP database

### Custom Policies

```python
from analyzer.policy import PasswordPolicy

# Create custom policy
policy = PasswordPolicy("Custom Company Policy")
policy.add_min_length(12)
policy.require_uppercase(2)
policy.require_digits(2)
policy.require_symbols(1)
policy.forbid_common_passwords()
policy.add_blacklist_words(['company', 'admin', 'password'])

# Validate password
is_valid, errors = policy.validate("MyPassword123", analysis_result)
```

## Pattern Detection

PassAudit identifies multiple categories of vulnerable patterns:

- **Sequential patterns**: Numeric (123, 789), alphabetic (abc, xyz)
- **Keyboard walks**: Layout patterns (qwerty, asdfgh, 1234, qazwsx)
- **Repeated characters**: Consecutive identical chars (aaa, 111)
- **Date patterns**: Years (1990, 2023), dates (12/31/2023)
- **Common words**: Dictionary words (password, admin, test)
- **Leetspeak**: Substitutions (p@ssw0rd, h4ck3r, l33t)
- **Context patterns**: Brands (google, amazon), tech terms, sports, pop culture
- **Common passwords**: Database of 10,000+ compromised passwords

## Web API

PassAudit provides a RESTful JSON API:

### Endpoints

**POST /api/v1/analyze**
```json
{
  "password": "MyPassword123",
  "check_hibp": false
}
```

**POST /api/v1/analyze/batch**
```json
{
  "passwords": ["password1", "password2"],
  "check_hibp": false
}
```

**POST /api/v1/generate**
```json
{
  "count": 5,
  "length": 16,
  "use_symbols": true
}
```

**GET /api/v1/stats**

See [API documentation](web/routes/api_routes.py) for complete details.

## Configuration

PassAudit stores configuration in `~/.passaudit/config.json`:

```bash
# Initialize configuration
python Main.py --config-init

# View current settings
python Main.py --config-show

# Set default password length
python Main.py --config-set generator default_length 20

# Enable HIBP checking by default
python Main.py --config-set security check_hibp true
```

### Configuration Sections

- **generator**: Default length, count, character preferences
- **output**: JSON mode, color output
- **security**: HIBP defaults, cache settings, timeouts
- **logging**: Log levels, file/console output
- **performance**: Batch processing threads

## Performance

PassAudit is optimized for high-performance batch processing:

- **Parallel processing**: ThreadPoolExecutor for concurrent analysis
- **HIBP caching**: SQLite cache with 30-day expiration (90%+ hit rate)
- **Compiled patterns**: Pre-compiled regex for 20-30% speed improvement
- **Throughput**: 100+ passwords/second for batch analysis

### Benchmarks

| Operation | Performance |
|-----------|------------|
| Single password analysis | < 10ms |
| Batch (100 passwords) | ~1 second |
| Pattern detection | < 10ms per password |
| HIBP check (cached) | < 20ms |
| Password generation | < 1ms |

## Deployment

### Docker

```bash
# Using Docker Compose
docker-compose up -d

# Access web interface
open http://localhost:5000
```

### Production

```bash
# With Gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 'web.app:create_app()'

# With Waitress (Windows)
waitress-serve --host=0.0.0.0 --port=5000 web.app:create_app
```

See [DEPLOY.md](DEPLOY.md) for Kubernetes, systemd, and Nginx configurations.

## Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=analyzer --cov=utils --cov-report=html

# Specific test module
pytest tests/test_policy.py -v
```

### Project Structure

```
PassAudit/
├── Main.py                     # CLI entry point
├── run_web.py                  # Web server launcher
├── analyzer/                   # Core analysis engine
│   ├── strength.py            # Strength scoring
│   ├── patterns.py            # Pattern detection (enhanced)
│   ├── entropy.py             # Entropy calculations
│   ├── policy.py              # Policy validation (new)
│   ├── generator.py           # Password generation
│   ├── hibp.py                # HIBP integration
│   ├── common_passwords.py    # Common password checking
│   └── feedback.py            # Recommendations
├── api/                        # Python API (new)
│   ├── __init__.py
│   └── core.py
├── cli/                        # Interactive CLI (new)
│   └── interactive.py
├── web/                        # Web interface (new)
│   ├── app.py                 # Flask application
│   ├── routes/                # Route handlers
│   ├── static/                # CSS, JS assets
│   └── templates/             # HTML templates
├── utils/                      # Utilities
│   ├── output_formatter.py    # Terminal output
│   ├── export.py              # CSV/HTML export
│   ├── export_pdf.py          # PDF reports (new)
│   ├── cache.py               # HIBP caching (new)
│   ├── logging_config.py      # Logging setup (new)
│   └── config.py              # Configuration
├── data/                       # Databases
│   ├── common_passwords.txt   # 10,000 passwords
│   ├── common_words.txt       # Common words (new)
│   └── context_patterns.txt   # Context patterns (new)
├── examples/                   # Usage examples (new)
├── tests/                      # Test suite (60+ tests)
└── Dockerfile                  # Docker deployment (new)
```

## Examples

The [examples/](examples/) directory contains complete examples:

- `example_basic_usage.py` - Core analysis functions
- `example_api_usage.py` - Python API integration
- `example_batch_processing.py` - Efficient batch analysis
- `example_custom_patterns.py` - Pattern detection deep dive
- `example_reporting.py` - Export and reporting

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines (PEP 8, type hints required)
- Testing requirements (85% coverage threshold)
- Pull request process
- Commit conventions

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details.

## Credits

- **Author**: [@botchx86](https://github.com/botchx86)
- **Have I Been Pwned API**: [haveibeenpwned.com](https://haveibeenpwned.com/) by Troy Hunt
- **Common password lists**: [SecLists](https://github.com/danielmiessler/SecLists) by Daniel Miessler
- **Dependencies**: Flask, ReportLab, colorama, pytest

## FAQ

**Does this send passwords to external services?**

No. All analysis is performed locally. The optional HIBP integration uses k-anonymity and only sends the first 5 characters of a SHA-1 hash.

**Is this suitable for professional security audits?**

Yes. PassAudit provides audit-ready output in multiple formats (CSV, HTML, PDF) and supports policy validation.

**Can this be integrated into applications?**

Yes. Use it as a Python library, call the CLI from scripts, or use the RESTful API.

**What about performance with large datasets?**

PassAudit uses parallel processing and achieves 100+ passwords/second. HIBP caching provides 90%+ hit rates.

**How accurate is the scoring?**

Based on NIST guidelines and industry standards. Combines multiple factors including length, entropy, character diversity, and pattern detection.

## Support

- **Issues**: [GitHub Issues](https://github.com/botchx86/PassAudit/issues)
- **Documentation**: This README, [CONTRIBUTING.md](CONTRIBUTING.md), [DEPLOY.md](DEPLOY.md)
- **Examples**: [examples/](examples/) directory

---

**PassAudit** - Enterprise-ready password security analysis
