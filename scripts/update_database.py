#!/usr/bin/env python3
"""
Script to check and update the common passwords database
Can be run manually or scheduled for automatic updates
"""

import os
import sys
import hashlib
import urllib.request
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# URL for the password database
DATABASE_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt"

def get_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def check_for_updates(current_file, url):
    """Check if database has updates available"""
    try:
        # Download current version from URL
        with urllib.request.urlopen(url, timeout=10) as response:
            remote_content = response.read()

        # Calculate hash of remote version
        remote_hash = hashlib.sha256(remote_content).hexdigest()

        # Calculate hash of local version
        local_hash = get_file_hash(current_file)

        if local_hash is None:
            return True, "Local file not found"

        if remote_hash != local_hash:
            return True, "New version available"
        else:
            return False, "Database is up to date"

    except Exception as e:
        return None, f"Error checking for updates: {e}"

def update_database(output_path, url):
    """Download and update the password database"""
    try:
        print(f"Downloading password database from {url}...")

        # Download the file
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8')

        # Write to file with metadata
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Common Passwords Database (SecLists 10k)\n")
            f.write("# Source: https://github.com/danielmiessler/SecLists\n")
            f.write(f"# Last Updated: {datetime.now().isoformat()}\n")
            f.write("#\n")
            f.write(content)

        # Count passwords
        password_count = len([line for line in content.splitlines() if line.strip() and not line.startswith('#')])

        print(f"[OK] Successfully updated database with {password_count:,} passwords")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to update database: {e}")
        return False

def should_auto_update(config_file, days=30):
    """Check if auto-update is needed based on config"""
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)

        last_updated = config.get('database', {}).get('last_updated')
        if not last_updated:
            return True

        last_date = datetime.fromisoformat(last_updated)
        return (datetime.now() - last_date) > timedelta(days=days)

    except Exception:
        return True  # Update if can't read config

def update_config_timestamp(config_file):
    """Update the last_updated timestamp in config"""
    try:
        import json

        # Load existing config or create default
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}

        # Update database section
        if 'database' not in config:
            config['database'] = {}

        config['database']['last_updated'] = datetime.now().isoformat()
        config['database']['password_count'] = 10000

        # Save config
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    except Exception as e:
        print(f"Warning: Could not update config timestamp: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Update common passwords database")
    parser.add_argument("--check", action="store_true", help="Only check for updates without downloading")
    parser.add_argument("--force", action="store_true", help="Force update even if database is current")
    parser.add_argument("--auto", action="store_true", help="Run in auto-update mode (checks if update needed)")
    args = parser.parse_args()

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    output_file = os.path.join(data_dir, "common_passwords.txt")
    config_file = os.path.join(Path.home(), ".passaudit", "config.json")

    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Check-only mode
    if args.check:
        print("Checking for database updates...")
        has_update, message = check_for_updates(output_file, DATABASE_URL)
        if has_update is None:
            print(f"[ERROR] {message}")
            sys.exit(1)
        elif has_update:
            print(f"[UPDATE AVAILABLE] {message}")
            sys.exit(0)
        else:
            print(f"[OK] {message}")
            sys.exit(0)

    # Auto-update mode (check config first)
    if args.auto:
        if not should_auto_update(config_file):
            print("Auto-update: Database updated recently, skipping.")
            sys.exit(0)
        print("Auto-update: Database update needed.")

    # Force mode or auto mode - proceed with update
    if args.force or args.auto:
        success = update_database(output_file, DATABASE_URL)
        if success:
            update_config_timestamp(config_file)
            print(f"\nDatabase location: {output_file}")
            sys.exit(0)
        else:
            sys.exit(1)

    # Interactive mode (default)
    print("Checking for updates...")
    has_update, message = check_for_updates(output_file, DATABASE_URL)

    if has_update is None:
        print(f"[ERROR] {message}")
        sys.exit(1)
    elif has_update:
        print(f"[UPDATE AVAILABLE] {message}")
        response = input("Update database now? (Y/n): ")
        if response.lower() in ['', 'y', 'yes']:
            success = update_database(output_file, DATABASE_URL)
            if success:
                update_config_timestamp(config_file)
                print(f"\nDatabase location: {output_file}")
        else:
            print("Update cancelled.")
    else:
        print(f"[OK] {message}")

if __name__ == "__main__":
    main()
