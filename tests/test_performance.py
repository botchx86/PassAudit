"""
Performance tests for PassAudit
Tests throughput and timing of key operations
"""

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.patterns import DetectPatterns
from analyzer.strength import CalculateStrength
from analyzer.generator import GeneratePassword


def test_pattern_detection_performance():
    """Test pattern detection is fast enough"""
    password = "password123qwerty"
    start = time.time()

    # Run 100 iterations
    for _ in range(100):
        patterns = DetectPatterns(password)

    duration = time.time() - start
    avg_time = (duration / 100) * 1000  # Convert to ms

    # Should be < 10ms per password on average
    assert avg_time < 10, f"Pattern detection too slow: {avg_time:.2f}ms"


def test_strength_calculation_performance():
    """Test strength calculation is fast enough"""
    password = "ComplexP@ssw0rd123!"
    patterns = DetectPatterns(password)

    start = time.time()

    # Run 100 iterations
    for _ in range(100):
        score = CalculateStrength(password, patterns)

    duration = time.time() - start
    avg_time = (duration / 100) * 1000

    # Should be < 5ms per password
    assert avg_time < 5, f"Strength calculation too slow: {avg_time:.2f}ms"


def test_password_generation_performance():
    """Test password generation is fast enough"""
    start = time.time()

    # Generate 100 passwords
    for _ in range(100):
        password = GeneratePassword(length=16)

    duration = time.time() - start
    avg_time = (duration / 100) * 1000

    # Should be < 1ms per password
    assert avg_time < 1, f"Password generation too slow: {avg_time:.2f}ms"


def test_batch_throughput():
    """Test overall throughput meets target"""
    passwords = [GeneratePassword(length=12) for _ in range(20)]

    start = time.time()

    for password in passwords:
        patterns = DetectPatterns(password)
        score = CalculateStrength(password, patterns)

    duration = time.time() - start
    throughput = len(passwords) / duration

    # Should process at least 100 passwords per second
    assert throughput >= 100, f"Throughput too low: {throughput:.1f} passwords/sec"
