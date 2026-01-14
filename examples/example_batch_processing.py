"""
Example: Batch Password Processing
Demonstrates efficient processing of large password lists using parallel processing
"""

import sys
import os
import time
from typing import List, Dict, Any

# Add parent directory to path to import PassAudit modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import PassAuditAPI
from analyzer.generator import GeneratePasswords


def example_sequential_processing():
    """Example 1: Sequential processing (small batches)"""
    print("\n" + "="*60)
    print("Example 1: Sequential Processing")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Generate test passwords
    passwords = GeneratePasswords(count=10, length=12)

    print(f"Processing {len(passwords)} passwords sequentially...")
    start_time = time.time()

    results = []
    for password in passwords:
        result = api.analyze_password(password)
        results.append(result)

    duration = time.time() - start_time
    throughput = len(passwords) / duration

    print(f"Completed in {duration:.2f} seconds")
    print(f"Throughput: {throughput:.1f} passwords/second")
    print(f"Average time per password: {(duration/len(passwords)*1000):.2f}ms")


def example_batch_processing():
    """Example 2: Batch processing (optimized)"""
    print("\n" + "="*60)
    print("Example 2: Batch Processing")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Generate larger test set
    passwords = GeneratePasswords(count=50, length=12)

    print(f"Processing {len(passwords)} passwords in batch...")
    start_time = time.time()

    # Use batch processing API (uses parallel processing internally)
    results = api.analyze_batch(passwords)

    duration = time.time() - start_time
    throughput = len(passwords) / duration

    print(f"Completed in {duration:.2f} seconds")
    print(f"Throughput: {throughput:.1f} passwords/second")
    print(f"Average time per password: {(duration/len(passwords)*1000):.2f}ms")


def example_file_processing():
    """Example 3: Processing passwords from a file"""
    print("\n" + "="*60)
    print("Example 3: File Processing")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Create a test file
    test_file = "test_passwords.txt"
    test_passwords = GeneratePasswords(count=20, length=14)

    # Write to file
    with open(test_file, 'w') as f:
        for pwd in test_passwords:
            f.write(pwd + '\n')

    print(f"Created test file: {test_file}")

    # Read and process
    print("Reading and processing passwords from file...")
    start_time = time.time()

    with open(test_file, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]

    results = api.analyze_batch(passwords)
    duration = time.time() - start_time

    print(f"Processed {len(results)} passwords in {duration:.2f} seconds")

    # Calculate statistics
    avg_strength = sum(r['strength_score'] for r in results) / len(results)
    common_count = sum(1 for r in results if r['is_common'])

    print(f"\nStatistics:")
    print(f"  Average Strength: {avg_strength:.1f}/100")
    print(f"  Common Passwords: {common_count}")
    print(f"  Unique Patterns: {len(set(tuple(sorted(r['patterns'].keys())) for r in results))}")

    # Cleanup
    os.remove(test_file)
    print(f"\nCleaned up test file: {test_file}")


def example_progress_tracking():
    """Example 4: Progress tracking for large batches"""
    print("\n" + "="*60)
    print("Example 4: Progress Tracking")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Generate large test set
    total = 100
    passwords = GeneratePasswords(count=total, length=12)

    print(f"Processing {total} passwords with progress tracking...")
    print("Progress: ", end='', flush=True)

    results = []
    batch_size = 10

    # Process in batches to show progress
    for i in range(0, total, batch_size):
        batch = passwords[i:i+batch_size]
        batch_results = api.analyze_batch(batch)
        results.extend(batch_results)

        # Show progress
        progress = (i + len(batch)) / total * 100
        print(f"{progress:.0f}%", end=' ', flush=True)

    print("\nProcessing complete!")

    # Analyze results
    strength_categories = {}
    for result in results:
        category = result['strength_category']
        strength_categories[category] = strength_categories.get(category, 0) + 1

    print("\nStrength Distribution:")
    for category, count in sorted(strength_categories.items()):
        percentage = (count / total) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {category:15} | {bar:25} {count:3d} ({percentage:.1f}%)")


def example_filtering_and_reporting():
    """Example 5: Filtering weak passwords and generating report"""
    print("\n" + "="*60)
    print("Example 5: Filtering and Reporting")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Mix of strong and weak passwords
    test_passwords = [
        "password123",
        "xK9#mQ2$pL7!vN5@",
        "admin",
        "MyS3cur3P@ss!2023",
        "qwerty",
        "zXcVbNm!@#$%^&*()_+",
        "123456",
        "P@ssw0rd"
    ]

    print(f"Analyzing {len(test_passwords)} passwords...")
    results = api.analyze_batch(test_passwords)

    # Filter weak passwords (score < 60)
    weak_passwords = [
        (test_passwords[i], r)
        for i, r in enumerate(results)
        if r['strength_score'] < 60
    ]

    # Filter strong passwords (score >= 60)
    strong_passwords = [
        (test_passwords[i], r)
        for i, r in enumerate(results)
        if r['strength_score'] >= 60
    ]

    print(f"\n{'='*60}")
    print(f"WEAK PASSWORDS ({len(weak_passwords)}):")
    print(f"{'='*60}")
    for pwd, result in weak_passwords:
        masked = pwd[:2] + '*' * (len(pwd) - 4) + pwd[-2:] if len(pwd) > 4 else '*' * len(pwd)
        print(f"\n{masked}")
        print(f"  Score: {result['strength_score']:.1f}/100")
        print(f"  Issues: ", end='')
        if result['is_common']:
            print("Common password ", end='')
        if result['patterns'].get('sequences'):
            print("Contains sequences ", end='')
        if result['patterns'].get('dates'):
            print("Contains dates ", end='')
        print()

    print(f"\n{'='*60}")
    print(f"STRONG PASSWORDS ({len(strong_passwords)}):")
    print(f"{'='*60}")
    for pwd, result in strong_passwords:
        masked = '*' * len(pwd)
        print(f"{masked:20} | Score: {result['strength_score']:.1f}/100 | [OK] Good")


def example_performance_comparison():
    """Example 6: Compare sequential vs batch performance"""
    print("\n" + "="*60)
    print("Example 6: Performance Comparison")
    print("="*60 + "\n")

    api = PassAuditAPI()

    # Generate test set
    test_size = 30
    passwords = GeneratePasswords(count=test_size, length=12)

    # Sequential processing
    print(f"Testing sequential processing ({test_size} passwords)...")
    start = time.time()
    seq_results = []
    for pwd in passwords:
        seq_results.append(api.analyze_password(pwd))
    seq_time = time.time() - start

    # Batch processing
    print(f"Testing batch processing ({test_size} passwords)...")
    start = time.time()
    batch_results = api.analyze_batch(passwords)
    batch_time = time.time() - start

    # Results
    print(f"\nResults:")
    print(f"  Sequential: {seq_time:.3f}s ({test_size/seq_time:.1f} passwords/sec)")
    print(f"  Batch:      {batch_time:.3f}s ({test_size/batch_time:.1f} passwords/sec)")
    print(f"  Speedup:    {seq_time/batch_time:.2f}x faster")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*15 + "PassAudit Batch Processing Examples")
    print("="*70)

    example_sequential_processing()
    example_batch_processing()
    example_file_processing()
    example_progress_tracking()
    example_filtering_and_reporting()
    example_performance_comparison()

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
