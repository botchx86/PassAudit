from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="passaudit",
    version="2.0.0",
    author="botchx86",
    description="Enterprise-ready password security analyzer with web interface, API, and advanced pattern detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/botchx86/PassAudit",
    project_urls={
        "Bug Tracker": "https://github.com/botchx86/PassAudit/issues",
        "Documentation": "https://github.com/botchx86/PassAudit#readme",
        "Source Code": "https://github.com/botchx86/PassAudit",
    },
    packages=find_packages(exclude=["tests*", "scripts*", "examples*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    keywords=[
        "password", "security", "analyzer", "audit", "strength",
        "entropy", "hibp", "breach", "policy", "validation",
        "flask", "web", "api", "cli", "tool"
    ],
    python_requires=">=3.9",
    install_requires=[
        "colorama>=0.4.6",
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "flask>=3.0.0",
        "werkzeug>=3.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "mypy>=1.7.0",
        ],
        "web": [
            "gunicorn>=21.0.0",
            "waitress>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "passaudit=Main:Main",
            "passaudit-web=run_web:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.txt"],
        "web": ["templates/*.html", "static/css/*.css", "static/js/*.js"],
    },
)
