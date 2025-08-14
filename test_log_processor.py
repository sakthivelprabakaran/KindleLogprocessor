#!/usr/bin/env python3

import sys
import os
import re

# Add current directory to path
sys.path.insert(0, '.')

# Test the LogProcessor functionality
def test_log_processor():
    print("Testing LogProcessor functionality...")
    
    # Import the actual LogProcessor from the main file
    try:
        # Read the main file and extract the LogProcessor class
        with open('final_kindle_analyzer.py', 'r') as f:
            content = f.read()
        
        # Check if LogProcessor class exists
        if 'class LogProcessor' in content:
            print("✓ LogProcessor class found in main file")
        else:
            print("✗ LogProcessor class NOT found in main file")
            return False
            
        # Test basic iteration splitting logic
        sample_log = """
Starting iteration 1
Some log line 1
Some log line 2
Starting iteration 2
Some log line 3
Some log line 4
"""
        
        lines = sample_log.strip().split('\n')
        print(f"Total lines in sample: {len(lines)}")
        
        # Test iteration detection
        iterations = []
        current_iteration = []
        
        for line in lines:
            if 'Starting iteration' in line:
                if current_iteration:
                    iterations.append(current_iteration)
                    current_iteration = []
            current_iteration.append(line)
        
        if current_iteration:
            iterations.append(current_iteration)
        
        print(f"Found {len(iterations)} iterations")
        for i, iteration in enumerate(iterations):
            print(f"  Iteration {i+1}: {len(iteration)} lines")
        
        return len(iterations) > 0
        
    except Exception as e:
        print(f"Error testing LogProcessor: {e}")
        return False

if __name__ == "__main__":
    success = test_log_processor()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")