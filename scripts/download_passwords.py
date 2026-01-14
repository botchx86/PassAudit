#!/usr/bin/env python3
"""
Script to download and prepare the SecLists 10k-most-common passwords database
"""

import urllib.request
import os
import sys

# URLs for common password lists
SECLISTS_10K_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt"

def download_password_list(url, output_path):
    """Download password list from URL"""
    print(f"Downloading password list from {url}...")

    try:
        # Download the file
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Common Passwords Database (SecLists 10k)\n")
            f.write("# Source: https://github.com/danielmiessler/SecLists\n")
            f.write("#\n")
            f.write(content)

        # Count passwords
        password_count = len([line for line in content.splitlines() if line.strip() and not line.startswith('#')])

        print(f"✓ Successfully downloaded {password_count:,} passwords to {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error downloading password list: {e}")
        return False

def main():
    """Main function"""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    output_file = os.path.join(data_dir, "common_passwords.txt")

    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Check if file already exists
    if os.path.exists(output_file):
        response = input(f"File {output_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Download the list
    success = download_password_list(SECLISTS_10K_URL, output_file)

    if success:
        print("\nPassword database updated successfully!")
        print(f"Location: {output_file}")
        print("\nYou can now use the expanded database with PassAudit.")
    else:
        print("\nFailed to update password database.")
        print("You can manually download from:")
        print(SECLISTS_10K_URL)
        sys.exit(1)

if __name__ == "__main__":
    main()
