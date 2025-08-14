#!/usr/bin/env python3

import re

def test_iteration_splitting():
    print("Testing iteration splitting logic...")
    
    # Simulate the data format created by add_iteration
    sample_data = """
ITERATION_01
Some log line 1
Some log line 2
Button up event detected

ITERATION_02
Some log line 3
Some log line 4
Button down event detected

ITERATION_03
Some log line 5
Some log line 6
Power button event detected
"""
    
    print("Sample data:")
    print(sample_data)
    print("\n" + "="*50 + "\n")
    
    # Test the regex splitting logic from LogProcessor
    iterations = re.split(r'ITERATION_(\d+)', sample_data)[1:]
    
    print(f"Raw split result: {len(iterations)} parts")
    for i, part in enumerate(iterations):
        print(f"Part {i}: {repr(part[:50])}...")
    
    print("\n" + "="*50 + "\n")
    
    if not iterations:
        print("No iterations found, using fallback")
        iterations = ["01", sample_data]
    
    # Pair iteration numbers with content
    iteration_pairs = []
    for i in range(0, len(iterations), 2):
        if i+1 < len(iterations):
            iteration_num = iterations[i]
            iteration_content = iterations[i+1]
            iteration_pairs.append((iteration_num, iteration_content))
    
    print(f"Found {len(iteration_pairs)} iteration pairs:")
    for num, content in iteration_pairs:
        print(f"  Iteration {num}: {len(content.strip().split())} words")
        print(f"    First line: {content.strip().split()[0] if content.strip() else 'Empty'}")
    
    return len(iteration_pairs)

if __name__ == "__main__":
    result = test_iteration_splitting()
    print(f"\nTest completed: {result} iterations processed")