# Contributing to PassAudit

Thank you for your interest in contributing to PassAudit! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Conventions](#commit-conventions)
- [Project Structure](#project-structure)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professionalism in all interactions

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PassAudit.git
   cd PassAudit
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/botchx86/PassAudit.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install pytest pytest-cov mypy black flake8 bandit
   ```

4. Download password database:
   ```bash
   python scripts/download_passwords.py
   ```

### Running the Application

```bash
# Analyze a password
python Main.py -p "YourPassword123"

# Run with options
python Main.py -p "YourPassword123" -b --export-csv output.csv
```

## Code Style

### Python Style Guide

We follow **PEP 8** with the following specifications:

- **Line length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Prefer double quotes for strings
- **Imports**: Group in order (standard library, third-party, local)

### Type Hints

All functions **must include type hints**:

```python
from typing import List, Dict, Optional, Any

def analyze_password(password: str, check_hibp: bool = False) -> Dict[str, Any]:
    """
    Analyze password strength and patterns

    Args:
        password: Password to analyze
        check_hibp: Whether to check Have I Been Pwned database

    Returns:
        Dictionary containing analysis results
    """
    pass
```

### Docstrings

Use **Google-style docstrings** for all public functions and classes:

```python
def calculate_entropy(password: str) -> float:
    """Calculate Shannon entropy of password.

    Args:
        password: Password string to analyze

    Returns:
        Entropy value in bits

    Raises:
        ValueError: If password is empty
    """
    pass
```

### Code Formatting

Use **black** for automatic code formatting:

```bash
black analyzer/ utils/ Main.py
```

### Linting

Run **flake8** to check for style issues:

```bash
flake8 analyzer/ utils/ Main.py --max-line-length=100
```

### Type Checking

Run **mypy** to verify type hints:

```bash
mypy analyzer/ utils/ Main.py
```

## Testing Requirements

### Test Coverage

- Minimum **85% code coverage** required for all PRs
- All new features must include tests
- Bug fixes should include regression tests

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=analyzer --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_patterns.py

# Run specific test function
pytest tests/test_patterns.py::test_detect_leetspeak
```

### Writing Tests

Place tests in the `tests/` directory with naming convention `test_*.py`:

```python
import pytest
from analyzer.patterns import DetectPatterns

def test_detect_sequences():
    """Test sequence detection in passwords"""
    patterns = DetectPatterns("abc123xyz")
    assert len(patterns['sequences']) > 0
    assert 'abc' in patterns['sequences']
    assert '123' in patterns['sequences']

def test_detect_leetspeak_basic():
    """Test basic leetspeak detection"""
    patterns = DetectPatterns("p@ssw0rd")
    assert len(patterns['leetspeak']) > 0
    assert 'password' in patterns['leetspeak']
```

### Test Categories

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test interactions between modules
- **Performance tests**: Verify speed requirements (<10ms per password)

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   # Format code
   black analyzer/ utils/ Main.py

   # Run linter
   flake8 analyzer/ utils/ Main.py --max-line-length=100

   # Type check
   mypy analyzer/ utils/ Main.py

   # Run tests
   pytest --cov=analyzer --cov=utils

   # Security scan
   bandit -r analyzer/ utils/
   ```

3. **Ensure all tests pass** with adequate coverage

4. **Update documentation** if needed

### Creating a Pull Request

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following code style guidelines

3. **Commit your changes** using conventional commits (see below)

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Link to any related issues
   - Screenshots/examples if applicable

### PR Review Process

- At least one maintainer approval required
- All CI checks must pass
- Code coverage must not decrease
- Address all review feedback
- Squash commits if requested

## Commit Conventions

We follow **Conventional Commits** specification:

### Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without changing functionality
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process or auxiliary tool changes

### Examples

```bash
# Feature addition
git commit -m "feat(patterns): add leetspeak detection algorithm"

# Bug fix
git commit -m "fix(hibp): handle timeout errors gracefully"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Performance improvement
git commit -m "perf(patterns): compile regex patterns at module level"

# Breaking change
git commit -m "feat(api): redesign password analysis API

BREAKING CHANGE: AnalyzePassword now returns Dict instead of tuple"
```

### Commit Best Practices

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Keep subject line under 50 characters
- Separate subject from body with blank line
- Wrap body at 72 characters
- Explain *what* and *why*, not *how*

## Project Structure

```
PassAudit/
├── analyzer/              # Core analysis modules
│   ├── common_passwords.py
│   ├── entropy.py
│   ├── feedback.py
│   ├── generator.py
│   ├── hibp.py
│   ├── patterns.py        # Pattern detection (sequences, leetspeak, etc.)
│   └── strength.py        # Strength calculation
├── utils/                 # Utility modules
│   ├── cache.py           # HIBP result caching
│   ├── config.py          # Configuration management
│   ├── export.py          # CSV/HTML export
│   ├── export_pdf.py      # PDF report generation
│   ├── logging_config.py  # Logging configuration
│   └── output_formatter.py
├── api/                   # Python API for library usage
│   ├── __init__.py
│   └── core.py
├── data/                  # Data files
│   ├── common_passwords.txt
│   ├── common_words.txt
│   └── context_patterns.txt
├── scripts/               # Utility scripts
│   ├── download_passwords.py
│   └── update_database.py
├── tests/                 # Test suite
│   ├── test_patterns.py
│   ├── test_strength.py
│   ├── test_performance.py
│   └── ...
├── Main.py               # CLI entry point
├── setup.py              # Package configuration
├── requirements.txt      # Runtime dependencies
└── README.md             # Project documentation
```

## Development Workflow

### Adding a New Feature

1. Create issue describing the feature
2. Discuss approach with maintainers
3. Create feature branch
4. Implement feature with tests
5. Update documentation
6. Submit pull request

### Fixing a Bug

1. Create issue describing the bug (if not exists)
2. Write failing test that reproduces bug
3. Fix the bug
4. Verify test now passes
5. Submit pull request referencing issue

### Performance Improvements

1. Profile code to identify bottlenecks
2. Implement optimization
3. Add/update performance tests
4. Document performance gains
5. Submit pull request with benchmarks

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Tag maintainers for urgent matters
- Be patient - we review PRs as time allows

## License

By contributing to PassAudit, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to PassAudit! Your efforts help make password security more accessible to everyone.
