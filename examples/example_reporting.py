"""
Example: Generating Reports
Demonstrates various reporting capabilities including CSV, HTML, and PDF exports
"""

import sys
import os
import tempfile
from typing import List, Dict, Any

# Add parent directory to path to import PassAudit modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import PassAuditAPI
from utils.export import ExportToCSV, ExportToHTML
from utils.export_pdf import ExportToPDF
from analyzer.generator import GeneratePasswords


def generate_sample_data(count: int = 20) -> List[Dict[str, Any]]:
    """Generate sample password analysis data"""
    api = PassAuditAPI()

    # Mix of strong and weak passwords
    passwords = [
        # Weak passwords
        "password", "123456", "qwerty", "admin", "letmein",
        # Medium passwords
        "MyPass2023", "Hello@123", "Welcome1!", "Summer2023", "Winter!23",
        # Generated strong passwords
        *GeneratePasswords(count=count-10, length=16)
    ]

    return api.analyze_batch(passwords)


def example_csv_export():
    """Example 1: Export to CSV"""
    print("\n" + "="*60)
    print("Example 1: CSV Export")
    print("="*60 + "\n")

    # Generate analysis data
    results = generate_sample_data(15)

    # Export to CSV
    output_file = "password_analysis.csv"
    success = ExportToCSV(results, output_file)

    if success:
        print(f"\nCSV file created: {output_file}")
        print(f"Contains {len(results)} password analyses")

        # Show preview
        print("\nPreview of CSV content:")
        with open(output_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:5]):  # Show first 5 lines
                print(f"  {line.rstrip()}")
            if len(lines) > 5:
                print(f"  ... ({len(lines)-5} more lines)")

        # Cleanup
        os.remove(output_file)
        print(f"\n(Cleaned up: {output_file})")


def example_html_export():
    """Example 2: Export to HTML"""
    print("\n" + "="*60)
    print("Example 2: HTML Export")
    print("="*60 + "\n")

    # Generate analysis data
    results = generate_sample_data(15)

    # Export to HTML
    output_file = "password_report.html"
    success = ExportToHTML(results, output_file)

    if success:
        print(f"\nHTML report created: {output_file}")
        print(f"Contains {len(results)} password analyses")

        # Show file size
        file_size = os.path.getsize(output_file)
        print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

        print("\nHTML report features:")
        print("  - Responsive design")
        print("  - Color-coded strength indicators")
        print("  - Summary statistics")
        print("  - Pattern detection details")
        print("  - Professional styling")

        print(f"\nOpen in browser: file://{os.path.abspath(output_file)}")

        # Cleanup
        os.remove(output_file)
        print(f"\n(Cleaned up: {output_file})")


def example_pdf_export():
    """Example 3: Export to PDF"""
    print("\n" + "="*60)
    print("Example 3: PDF Export")
    print("="*60 + "\n")

    # Generate analysis data
    results = generate_sample_data(15)

    # Export to PDF
    output_file = "password_report.pdf"
    success = ExportToPDF(results, output_file)

    if success:
        print(f"\nPDF report created: {output_file}")
        print(f"Contains {len(results)} password analyses")

        # Show file size
        file_size = os.path.getsize(output_file)
        print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

        print("\nPDF report features:")
        print("  - Professional multi-page layout")
        print("  - Executive summary with statistics")
        print("  - Detailed analysis table")
        print("  - Color-coded strength indicators")
        print("  - Masked passwords for security")

        # Cleanup
        os.remove(output_file)
        print(f"\n(Cleaned up: {output_file})")


def example_all_formats():
    """Example 4: Export to all formats"""
    print("\n" + "="*60)
    print("Example 4: Export to All Formats")
    print("="*60 + "\n")

    # Generate analysis data
    results = generate_sample_data(20)

    print(f"Generating reports for {len(results)} passwords...")

    # Export to all formats
    csv_file = "report.csv"
    html_file = "report.html"
    pdf_file = "report.pdf"

    csv_success = ExportToCSV(results, csv_file)
    html_success = ExportToHTML(results, html_file)
    pdf_success = ExportToPDF(results, pdf_file)

    print("\nExport Summary:")
    print(f"  CSV:  {'[OK] Success' if csv_success else '[FAIL] Failed'} ({os.path.getsize(csv_file)/1024:.1f} KB)")
    print(f"  HTML: {'[OK] Success' if html_success else '[FAIL] Failed'} ({os.path.getsize(html_file)/1024:.1f} KB)")
    print(f"  PDF:  {'[OK] Success' if pdf_success else '[FAIL] Failed'} ({os.path.getsize(pdf_file)/1024:.1f} KB)")

    # Cleanup
    for f in [csv_file, html_file, pdf_file]:
        if os.path.exists(f):
            os.remove(f)


def example_custom_reporting():
    """Example 5: Custom report generation"""
    print("\n" + "="*60)
    print("Example 5: Custom Reporting")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Analyze passwords
    passwords = [
        "password123", "qwerty", "admin", "letmein",
        "MySecureP@ss2023", "Tr0ub4dor&3", "xK9#mQ2$pL7!"
    ]
    results = api.analyze_batch(passwords)

    # Custom text report
    report_file = "custom_report.txt"
    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write(" "*20 + "CUSTOM PASSWORD AUDIT REPORT\n")
        f.write("="*70 + "\n\n")

        # Summary
        total = len(results)
        avg_score = sum(r['strength_score'] for r in results) / total
        weak_count = sum(1 for r in results if r['strength_score'] < 40)
        common_count = sum(1 for r in results if r['is_common'])

        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Passwords Analyzed: {total}\n")
        f.write(f"Average Strength Score:   {avg_score:.1f}/100\n")
        f.write(f"Weak Passwords:           {weak_count} ({weak_count/total*100:.1f}%)\n")
        f.write(f"Common Passwords:         {common_count} ({common_count/total*100:.1f}%)\n")
        f.write("\n")

        # Detailed results
        f.write("DETAILED ANALYSIS\n")
        f.write("-" * 70 + "\n\n")

        for idx, result in enumerate(results, 1):
            masked = '*' * len(passwords[idx-1])
            f.write(f"{idx}. Password: {masked} (length: {result['length']})\n")
            f.write(f"   Strength: {result['strength_score']:.1f}/100 ({result['strength_category']})\n")
            f.write(f"   Entropy:  {result['entropy']:.1f} bits\n")
            f.write(f"   Common:   {'YES [WARNING]' if result['is_common'] else 'NO [OK]'}\n")

            if result['patterns']:
                f.write(f"   Patterns: ")
                pattern_list = [ptype for ptype, items in result['patterns'].items() if items]
                f.write(", ".join(pattern_list) if pattern_list else "None")
                f.write("\n")

            if result['feedback']:
                f.write(f"   Feedback:\n")
                for feedback in result['feedback'][:2]:  # Show first 2
                    f.write(f"     - {feedback}\n")

            f.write("\n")

        f.write("="*70 + "\n")
        f.write("End of Report\n")

    print(f"Custom text report created: {report_file}")

    # Show preview
    print("\nReport preview:")
    with open(report_file, 'r') as f:
        lines = f.readlines()
        for line in lines[:20]:  # Show first 20 lines
            print(f"  {line.rstrip()}")
        if len(lines) > 20:
            print(f"  ... ({len(lines)-20} more lines)")

    # Cleanup
    os.remove(report_file)
    print(f"\n(Cleaned up: {report_file})")


def example_summary_statistics():
    """Example 6: Generating summary statistics report"""
    print("\n" + "="*60)
    print("Example 6: Summary Statistics")
    print("="*60 + "\n")

    # Generate larger dataset
    results = generate_sample_data(50)

    print(f"Analyzing {len(results)} passwords...\n")

    # Calculate statistics
    total = len(results)
    avg_score = sum(r['strength_score'] for r in results) / total
    avg_entropy = sum(r['entropy'] for r in results) / total
    avg_length = sum(r['length'] for r in results) / total

    # Strength distribution
    strength_dist = {
        'Very Weak': sum(1 for r in results if r['strength_score'] < 20),
        'Weak': sum(1 for r in results if 20 <= r['strength_score'] < 40),
        'Medium': sum(1 for r in results if 40 <= r['strength_score'] < 60),
        'Strong': sum(1 for r in results if 60 <= r['strength_score'] < 80),
        'Very Strong': sum(1 for r in results if r['strength_score'] >= 80)
    }

    # Pattern statistics
    pattern_stats = {}
    for result in results:
        for ptype, items in result['patterns'].items():
            if items:
                pattern_stats[ptype] = pattern_stats.get(ptype, 0) + 1

    # Display report
    print("="*60)
    print("SUMMARY STATISTICS REPORT")
    print("="*60)
    print()

    print("Overall Metrics:")
    print(f"  Total Passwords:    {total}")
    print(f"  Average Score:      {avg_score:.1f}/100")
    print(f"  Average Entropy:    {avg_entropy:.1f} bits")
    print(f"  Average Length:     {avg_length:.1f} characters")
    print()

    print("Strength Distribution:")
    for category, count in strength_dist.items():
        percentage = (count / total) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {category:12} | {bar:25} {count:3d} ({percentage:5.1f}%)")
    print()

    print("Pattern Detection Frequency:")
    for pattern, count in sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {pattern:20} | {bar:20} {count:3d} ({percentage:5.1f}%)")
    print()

    print("Recommendations:")
    if strength_dist['Very Weak'] + strength_dist['Weak'] > total * 0.3:
        print("  [WARNING]  HIGH RISK: Over 30% of passwords are weak")
    elif strength_dist['Very Weak'] + strength_dist['Weak'] > total * 0.1:
        print("  [WARNING]  MODERATE RISK: 10-30% of passwords are weak")
    else:
        print("  [OK] LOW RISK: Less than 10% of passwords are weak")

    if sum(pattern_stats.values()) > total * 0.5:
        print("  [WARNING]  Many passwords contain predictable patterns")
    else:
        print("  [OK] Most passwords avoid common patterns")


def example_comparative_analysis():
    """Example 7: Compare password sets"""
    print("\n" + "="*60)
    print("Example 7: Comparative Analysis")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Two sets of passwords
    user_passwords = [
        "password123", "qwerty", "Welcome1!",
        "MyPass2023", "admin123"
    ]

    generated_passwords = GeneratePasswords(count=5, length=16)

    # Analyze both sets
    user_results = api.analyze_batch(user_passwords)
    generated_results = api.analyze_batch(generated_passwords)

    # Calculate metrics
    user_avg = sum(r['strength_score'] for r in user_results) / len(user_results)
    gen_avg = sum(r['strength_score'] for r in generated_results) / len(generated_results)

    user_patterns = sum(sum(len(v) for v in r['patterns'].values()) for r in user_results)
    gen_patterns = sum(sum(len(v) for v in r['patterns'].values()) for r in generated_results)

    # Display comparison
    print("COMPARATIVE ANALYSIS")
    print("="*60)
    print()
    print(f"{'Metric':<30} | {'User Passwords':<15} | {'Generated':<15}")
    print("-" * 60)
    print(f"{'Average Strength':<30} | {user_avg:>14.1f} | {gen_avg:>14.1f}")
    print(f"{'Total Patterns Detected':<30} | {user_patterns:>14} | {gen_patterns:>14}")
    print(f"{'Weak Passwords (<40)':<30} | {sum(1 for r in user_results if r['strength_score']<40):>14} | {sum(1 for r in generated_results if r['strength_score']<40):>14}")
    print(f"{'Strong Passwords (>=60)':<30} | {sum(1 for r in user_results if r['strength_score']>=60):>14} | {sum(1 for r in generated_results if r['strength_score']>=60):>14}")
    print()

    improvement = gen_avg - user_avg
    print(f"Generated passwords are {improvement:.1f} points stronger on average!")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*20 + "PassAudit Reporting Examples")
    print("="*70)

    example_csv_export()
    example_html_export()
    example_pdf_export()
    example_all_formats()
    example_custom_reporting()
    example_summary_statistics()
    example_comparative_analysis()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
