#!/usr/bin/env python3

import sys
import os
import re

def test_complete_processing():
    """Test the complete processing pipeline"""
    print("=== Testing Complete Processing Pipeline ===\n")
    
    # Sample log data that should work with the parsers
    sample_log_data = """
ITERATION_01
[12345.678] button 1 up 123456.789
[12345.679] EPDC][123] Some log line
[12345.680] Sending update. height=800 waveform:0x12345 (REAGL)
[12345.681] update end marker=123 end time=789456
[12345.682] Another log line

ITERATION_02
[12346.678] button 1 up 123457.890
[12346.679] EPDC][124] Some log line
[12346.680] Sending update. height=600 waveform:0x12346 (DU)
[12346.681] update end marker=124 end time=890567
[12346.682] Another log line
"""
    
    print("1. Testing iteration splitting...")
    iterations = re.split(r'ITERATION_(\d+)', sample_log_data)[1:]
    print(f"   Found {len(iterations)} parts after split")
    
    if not iterations:
        iterations = ["01", sample_log_data]
        print("   Using fallback mode")
    
    # Pair iteration numbers with content
    iteration_pairs = []
    for i in range(0, len(iterations), 2):
        if i+1 < len(iterations):
            iteration_num = iterations[i]
            iteration_content = iterations[i+1]
            iteration_pairs.append((iteration_num, iteration_content))
    
    print(f"   Created {len(iteration_pairs)} iteration pairs")
    
    print("\n2. Testing individual iteration processing...")
    
    # Test DefaultEventParser
    class TestDefaultEventParser:
        def extract_marker(self, line):
            match1 = re.search(r'EPDC\]\[(\d+)\]', line)
            if match1:
                return match1.group(1)
            match2 = re.search(r'mxc_epdc_fb: \[(\d+)\]', line)
            if match2:
                return match2.group(1)
            return None

        def extract_height_and_waveform(self, line):
            height_match = re.search(r'height=(\d+)', line)
            if not height_match:
                height_match = re.search(r'width=\d+, height=(\d+)', line)
            
            waveform_patterns = [
                r'new waveform = (?:0x)?[\da-f]+ \(([\w_() ]+)\)', 
                r'waveform:(?:0x)?[\da-f]+ \(([\w_() ]+)\)',
                r'waveform=(?:0x)?[\da-f]+ \(([\w_() ]+)\)',
                r'Sending update\. waveform:(?:0x)?[\da-f]+ \(([\w_() ]+)\)'
            ]
            
            waveform_name = None
            for pattern in waveform_patterns:
                match = re.search(pattern, line)
                if match:
                    waveform_name = match.group(1).strip()
                    break
            
            if height_match:
                height = int(height_match.group(1))
                return {
                    'height': height,
                    'waveform': waveform_name if waveform_name else "unknown"
                }
            return None

        def extract_end_timestamp(self, line):
            match = re.search(r'end time=(\d+)', line)
            if match:
                timestamp_str = match.group(1)
                last_6 = timestamp_str[-6:]
                return int(last_6)
            return None
        
        def extract_start_timestamp(self, line):
            match = re.search(r'button 1 up (\d+\.\d+)', line)
            if match:
                timestamp_str = match.group(1)
                parts = timestamp_str.split('.')
                if len(parts) == 2:
                    last_3_first = parts[0][-3:]
                    first_3_second = parts[1][:3]
                    result = int(last_3_first + first_3_second)
                    return result
            return None
    
    parser = TestDefaultEventParser()
    
    for iteration_num, iteration_content in iteration_pairs:
        print(f"\n   Processing Iteration {iteration_num}:")
        lines = iteration_content.split('\n')
        
        start_time = None
        start_line = None
        end_times_by_marker = {}
        heights_by_marker = {}
        current_marker = None
        
        for line in lines:
            if not line.strip():
                continue
            
            print(f"     Processing line: {line.strip()}")
            
            # Check for start time
            if not start_time:
                possible_start = parser.extract_start_timestamp(line)
                if possible_start:
                    start_time = possible_start
                    start_line = line.strip()
                    print(f"       Found start time: {start_time}")
            
            # Check for marker
            marker = parser.extract_marker(line)
            if marker:
                current_marker = marker
                print(f"       Found marker: {marker}")
            
            # Check for height/waveform
            if "Sending update" in line and current_marker:
                height_waveform = parser.extract_height_and_waveform(line)
                if height_waveform:
                    heights_by_marker[current_marker] = {
                        'height': height_waveform['height'],
                        'waveform': height_waveform['waveform'],
                        'line': line.strip()
                    }
                    print(f"       Found height/waveform: {height_waveform}")
            
            # Check for end time
            if "update end marker=" in line and "end time=" in line:
                end_marker_match = re.search(r'update end marker=(\d+)', line)
                if end_marker_match:
                    end_marker = end_marker_match.group(1)
                    end_time = parser.extract_end_timestamp(line)
                    if end_time:
                        end_times_by_marker[end_marker] = {
                            'time': end_time,
                            'line': line.strip()
                        }
                        print(f"       Found end time for marker {end_marker}: {end_time}")
        
        print(f"     Results for iteration {iteration_num}:")
        print(f"       Start time: {start_time}")
        print(f"       Heights by marker: {heights_by_marker}")
        print(f"       End times by marker: {end_times_by_marker}")
        
        # Check if we have all required data
        if start_time and heights_by_marker and end_times_by_marker:
            print(f"       ✓ Iteration {iteration_num} has all required data")
        else:
            print(f"       ✗ Iteration {iteration_num} is missing required data:")
            if not start_time:
                print(f"         - Missing start time")
            if not heights_by_marker:
                print(f"         - Missing heights")
            if not end_times_by_marker:
                print(f"         - Missing end times")

if __name__ == "__main__":
    test_complete_processing()