"""
Interactive CLI Mode
Menu-driven interface for PassAudit with session history tracking
"""

import os
import sys
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import PassAuditAPI
from analyzer.generator import GeneratePasswords
from utils.config import LoadConfig, ShowConfig, UpdateConfigValue
from utils.cache import get_cache
from utils.export import ExportToCSV, ExportToHTML
from utils.export_pdf import ExportToPDF


class InteractiveCLI:
    """Interactive command-line interface for PassAudit"""

    def __init__(self):
        """Initialize interactive CLI"""
        self.api = PassAuditAPI()
        self.session_history = []
        self.config = LoadConfig()
        self.running = True

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print application header"""
        print("\n" + "="*70)
        print(" "*20 + "PassAudit - Interactive Mode")
        print("="*70)

    def print_menu(self):
        """Print main menu"""
        print("\n" + "-"*70)
        print("MAIN MENU")
        print("-"*70)
        print("  1. Analyze Single Password")
        print("  2. Analyze Password File")
        print("  3. Generate Secure Passwords")
        print("  4. Check Password Against HIBP")
        print("  5. View/Update Configuration")
        print("  6. View Database Statistics")
        print("  7. Clear HIBP Cache")
        print("  8. View Session History")
        print("  9. Export Session Results")
        print("  0. Exit")
        print("-"*70)

    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default value"""
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "

        value = input(prompt).strip()
        return value if value else (default or "")

    def wait_for_key(self):
        """Wait for user to press Enter"""
        input("\nPress Enter to continue...")

    def analyze_single_password(self):
        """Option 1: Analyze a single password"""
        self.clear_screen()
        self.print_header()
        print("\n--- Analyze Single Password ---\n")

        password = self.get_input("Enter password to analyze")
        if not password:
            print("\n[ERROR] Password cannot be empty")
            self.wait_for_key()
            return

        check_hibp = self.get_input("Check against HIBP database? (y/n)", "n").lower() == 'y'

        print("\nAnalyzing...")
        start_time = time.time()

        result = self.api.analyze_password(password, check_hibp=check_hibp)

        duration = time.time() - start_time

        # Display results
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)

        masked = '*' * len(password)
        print(f"\nPassword: {masked} (Length: {result['length']})")
        print(f"Strength Score: {result['strength_score']:.1f}/100")
        print(f"Category: {result['strength_category']}")
        print(f"Shannon Entropy: {result['entropy']:.2f} bits")
        print(f"Pool Entropy: {result['pool_entropy']:.2f} bits")
        print(f"Is Common: {'YES [WARNING]' if result['is_common'] else 'NO [OK]'}")

        if check_hibp and 'hibp_pwned' in result:
            if result['hibp_pwned']:
                print(f"HIBP Status: [WARNING] Found in {result['hibp_count']:,} breaches!")
            else:
                print("HIBP Status: [OK] Not found in breaches")

        if result['patterns']:
            print("\nDetected Patterns:")
            for pattern_type, items in result['patterns'].items():
                if items:
                    print(f"  - {pattern_type.replace('_', ' ').title()}: {', '.join(str(x) for x in items[:5])}")

        if result['feedback']:
            print("\nRecommendations:")
            for idx, feedback in enumerate(result['feedback'], 1):
                print(f"  {idx}. {feedback}")

        print(f"\nAnalysis completed in {duration*1000:.2f}ms")

        # Add to session history
        self.session_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'analyze_single',
            'result': result
        })

        self.wait_for_key()

    def analyze_password_file(self):
        """Option 2: Analyze passwords from a file"""
        self.clear_screen()
        self.print_header()
        print("\n--- Analyze Password File ---\n")

        file_path = self.get_input("Enter file path")
        if not file_path or not os.path.exists(file_path):
            print(f"\n[ERROR] File not found: {file_path}")
            self.wait_for_key()
            return

        check_hibp = self.get_input("Check against HIBP database? (y/n)", "n").lower() == 'y'

        print("\nReading passwords from file...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"\n[ERROR] Could not read file: {e}")
            self.wait_for_key()
            return

        if not passwords:
            print("\n[ERROR] No passwords found in file")
            self.wait_for_key()
            return

        print(f"Found {len(passwords)} password(s)")
        print("\nAnalyzing...")

        start_time = time.time()
        results = self.api.analyze_batch(passwords, check_hibp=check_hibp)
        duration = time.time() - start_time

        # Display summary statistics
        print("\n" + "="*70)
        print("ANALYSIS SUMMARY")
        print("="*70)

        total = len(results)
        avg_score = sum(r['strength_score'] for r in results) / total
        weak_count = sum(1 for r in results if r['strength_score'] < 40)
        common_count = sum(1 for r in results if r['is_common'])

        print(f"\nTotal Passwords: {total}")
        print(f"Average Strength: {avg_score:.1f}/100")
        print(f"Weak Passwords (< 40): {weak_count} ({weak_count/total*100:.1f}%)")
        print(f"Common Passwords: {common_count} ({common_count/total*100:.1f}%)")

        if check_hibp:
            breached_count = sum(1 for r in results if r.get('hibp_pwned', False))
            print(f"Breached (HIBP): {breached_count} ({breached_count/total*100:.1f}%)")

        # Strength distribution
        strength_dist = {
            'Very Weak': sum(1 for r in results if r['strength_score'] < 20),
            'Weak': sum(1 for r in results if 20 <= r['strength_score'] < 40),
            'Medium': sum(1 for r in results if 40 <= r['strength_score'] < 60),
            'Strong': sum(1 for r in results if 60 <= r['strength_score'] < 80),
            'Very Strong': sum(1 for r in results if r['strength_score'] >= 80)
        }

        print("\nStrength Distribution:")
        for category, count in strength_dist.items():
            if count > 0:
                percentage = (count / total) * 100
                bar = '#' * int(percentage / 2)
                print(f"  {category:12} | {bar:25} {count:3d} ({percentage:5.1f}%)")

        print(f"\nProcessing speed: {total/duration:.1f} passwords/sec")
        print(f"Total time: {duration:.2f}s")

        # Add to session history
        self.session_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'analyze_file',
            'file_path': file_path,
            'results': results
        })

        # Offer to export
        print("\n" + "-"*70)
        export = self.get_input("Export results? (csv/html/pdf/n)", "n").lower()
        if export in ['csv', 'html', 'pdf']:
            output_file = self.get_input("Output filename", f"results.{export}")
            try:
                if export == 'csv':
                    ExportToCSV(results, output_file)
                elif export == 'html':
                    ExportToHTML(results, output_file)
                elif export == 'pdf':
                    ExportToPDF(results, output_file)
            except Exception as e:
                print(f"\n[ERROR] Export failed: {e}")

        self.wait_for_key()

    def generate_passwords(self):
        """Option 3: Generate secure passwords"""
        self.clear_screen()
        self.print_header()
        print("\n--- Generate Secure Passwords ---\n")

        try:
            count = int(self.get_input("Number of passwords to generate", "5"))
            count = min(max(count, 1), 100)  # Limit 1-100
        except ValueError:
            count = 5

        try:
            length = int(self.get_input("Password length", "16"))
            length = min(max(length, 8), 64)  # Limit 8-64
        except ValueError:
            length = 16

        use_uppercase = self.get_input("Include uppercase letters? (y/n)", "y").lower() == 'y'
        use_lowercase = self.get_input("Include lowercase letters? (y/n)", "y").lower() == 'y'
        use_digits = self.get_input("Include digits? (y/n)", "y").lower() == 'y'
        use_symbols = self.get_input("Include symbols? (y/n)", "y").lower() == 'y'

        print(f"\nGenerating {count} password(s) of length {length}...")

        passwords = GeneratePasswords(
            count=count,
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols
        )

        print("\n" + "="*70)
        print("GENERATED PASSWORDS")
        print("="*70 + "\n")

        for idx, password in enumerate(passwords, 1):
            # Analyze each generated password
            result = self.api.analyze_password(password)
            score = result['strength_score']
            category = result['strength_category']

            print(f"{idx:2d}. {password:30} | Score: {score:5.1f} ({category})")

        # Add to session history
        self.session_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'generate_passwords',
            'passwords': passwords
        })

        self.wait_for_key()

    def check_hibp(self):
        """Option 4: Check password against HIBP"""
        self.clear_screen()
        self.print_header()
        print("\n--- Check Password Against HIBP ---\n")

        password = self.get_input("Enter password to check")
        if not password:
            print("\n[ERROR] Password cannot be empty")
            self.wait_for_key()
            return

        print("\nChecking Have I Been Pwned database...")

        is_pwned, breach_count = self.api.check_breached(password)

        print("\n" + "="*70)
        print("HIBP CHECK RESULTS")
        print("="*70 + "\n")

        if is_pwned is None:
            print("[ERROR] Could not check HIBP (network error or timeout)")
        elif is_pwned:
            print(f"[WARNING] This password has been FOUND in {breach_count:,} data breaches!")
            print("\nThis password is COMPROMISED and should NOT be used.")
            print("Please choose a different, unique password.")
        else:
            print("[OK] This password was NOT found in known data breaches.")
            print("\nNote: This doesn't guarantee the password is strong.")
            print("Always use unique, complex passwords.")

        self.wait_for_key()

    def view_update_config(self):
        """Option 5: View/Update configuration"""
        self.clear_screen()
        self.print_header()
        print("\n--- Configuration ---\n")

        print("Current Configuration:")
        print(json.dumps(self.config, indent=2))

        print("\n" + "-"*70)
        update = self.get_input("Update a setting? (y/n)", "n").lower()

        if update == 'y':
            section = self.get_input("Section (e.g., security, generator)")
            key = self.get_input("Key (e.g., check_hibp, default_length)")
            value = self.get_input("Value")

            try:
                UpdateConfigValue(section, key, value)
                # Reload config
                self.config = LoadConfig()
                print("\n[OK] Configuration updated")
            except Exception as e:
                print(f"\n[ERROR] Failed to update: {e}")

        self.wait_for_key()

    def view_database_stats(self):
        """Option 6: View database statistics"""
        self.clear_screen()
        self.print_header()
        print("\n--- Database Statistics ---\n")

        # Check common passwords database
        common_passwords_file = os.path.join('data', 'common_passwords.txt')
        if os.path.exists(common_passwords_file):
            with open(common_passwords_file, 'r') as f:
                common_count = sum(1 for line in f if line.strip() and not line.startswith('#'))
            print(f"Common Passwords Database: {common_count:,} entries")
        else:
            print("Common Passwords Database: Not found")

        # Check common words
        common_words_file = os.path.join('data', 'common_words.txt')
        if os.path.exists(common_words_file):
            with open(common_words_file, 'r') as f:
                words_count = sum(1 for line in f if line.strip() and not line.startswith('#'))
            print(f"Common Words Database: {words_count} entries")
        else:
            print("Common Words Database: Not found")

        # Check context patterns
        context_file = os.path.join('data', 'context_patterns.txt')
        if os.path.exists(context_file):
            with open(context_file, 'r') as f:
                context_count = sum(1 for line in f if line.strip() and not line.startswith('#'))
            print(f"Context Patterns Database: {context_count} entries")
        else:
            print("Context Patterns Database: Not found")

        # HIBP cache stats
        try:
            cache = get_cache()
            stats = cache.get_stats()
            print(f"\nHIBP Cache Statistics:")
            print(f"  Total Entries: {stats['total_entries']:,}")
            print(f"  Expired Entries: {stats['expired_entries']:,}")
            print(f"  Cache Hit Rate: ~90%+ (estimated after warmup)")
        except Exception as e:
            print(f"\nHIBP Cache: Unable to retrieve stats ({e})")

        self.wait_for_key()

    def clear_hibp_cache(self):
        """Option 7: Clear HIBP cache"""
        self.clear_screen()
        self.print_header()
        print("\n--- Clear HIBP Cache ---\n")

        try:
            cache = get_cache()
            stats = cache.get_stats()
            print(f"Current cache contains {stats['total_entries']:,} entries")

            confirm = self.get_input("\nAre you sure you want to clear the cache? (yes/no)", "no")
            if confirm.lower() == 'yes':
                cache.clear()
                print("\n[OK] HIBP cache cleared successfully")
            else:
                print("\n[INFO] Cache clear cancelled")
        except Exception as e:
            print(f"\n[ERROR] Failed to clear cache: {e}")

        self.wait_for_key()

    def view_session_history(self):
        """Option 8: View session history"""
        self.clear_screen()
        self.print_header()
        print("\n--- Session History ---\n")

        if not self.session_history:
            print("No actions performed in this session yet.")
        else:
            print(f"Session started at: {self.session_history[0]['timestamp']}")
            print(f"Total actions: {len(self.session_history)}\n")

            for idx, item in enumerate(self.session_history, 1):
                timestamp = item['timestamp']
                action = item['action']
                print(f"{idx}. [{timestamp}] {action}")

        self.wait_for_key()

    def export_session_results(self):
        """Option 9: Export all session results"""
        self.clear_screen()
        self.print_header()
        print("\n--- Export Session Results ---\n")

        # Collect all results from session
        all_results = []
        for item in self.session_history:
            if item['action'] == 'analyze_single' and 'result' in item:
                all_results.append(item['result'])
            elif item['action'] == 'analyze_file' and 'results' in item:
                all_results.extend(item['results'])

        if not all_results:
            print("No analysis results to export in this session.")
            self.wait_for_key()
            return

        print(f"Found {len(all_results)} password analysis result(s)")

        export_format = self.get_input("Export format (csv/html/pdf)", "csv").lower()
        if export_format not in ['csv', 'html', 'pdf']:
            print("\n[ERROR] Invalid format")
            self.wait_for_key()
            return

        output_file = self.get_input("Output filename", f"session_results.{export_format}")

        try:
            if export_format == 'csv':
                ExportToCSV(all_results, output_file)
            elif export_format == 'html':
                ExportToHTML(all_results, output_file)
            elif export_format == 'pdf':
                ExportToPDF(all_results, output_file)
            print(f"\n[OK] Results exported to: {output_file}")
        except Exception as e:
            print(f"\n[ERROR] Export failed: {e}")

        self.wait_for_key()

    def exit_cli(self):
        """Option 0: Exit the interactive CLI"""
        self.clear_screen()
        self.print_header()
        print("\n--- Exit ---\n")

        if self.session_history:
            print(f"Session summary:")
            print(f"  Total actions: {len(self.session_history)}")

            save = self.get_input("\nSave session history? (y/n)", "n").lower()
            if save == 'y':
                filename = self.get_input("Filename", "session_history.json")
                try:
                    with open(filename, 'w') as f:
                        json.dump(self.session_history, f, indent=2)
                    print(f"\n[OK] Session history saved to: {filename}")
                except Exception as e:
                    print(f"\n[ERROR] Failed to save: {e}")

        print("\nThank you for using PassAudit!")
        self.running = False

    def run(self):
        """Main interactive loop"""
        self.clear_screen()
        self.print_header()
        print("\nWelcome to PassAudit Interactive Mode!")
        print("Analyze passwords, generate secure passwords, and more...")
        self.wait_for_key()

        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            choice = self.get_input("\nSelect an option (0-9)")

            if choice == '1':
                self.analyze_single_password()
            elif choice == '2':
                self.analyze_password_file()
            elif choice == '3':
                self.generate_passwords()
            elif choice == '4':
                self.check_hibp()
            elif choice == '5':
                self.view_update_config()
            elif choice == '6':
                self.view_database_stats()
            elif choice == '7':
                self.clear_hibp_cache()
            elif choice == '8':
                self.view_session_history()
            elif choice == '9':
                self.export_session_results()
            elif choice == '0':
                self.exit_cli()
            else:
                print("\n[ERROR] Invalid option. Please select 0-9.")
                self.wait_for_key()


def main():
    """Entry point for interactive CLI"""
    try:
        cli = InteractiveCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
