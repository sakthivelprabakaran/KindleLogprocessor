"""
event_parser.py - Module for parsing Kindle log events
This module contains classes for extracting timestamps and other data from log lines
"""
import re

class BaseEventParser:
    """Base class for parsing log events with common extraction methods"""
    
    def extract_marker(self, line):
        """Extract marker number from log line"""
        match1 = re.search(r'EPDC\]\[(\d+)\]', line)
        if match1:
            return match1.group(1)
        
        match2 = re.search(r'mxc_epdc_fb: \[(\d+)\]', line)
        if match2:
            return match2.group(1)
        
        return None

    def extract_height_and_waveform(self, line):
        """Extract height and waveform information from log line"""
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
        """Extract end timestamp from log line"""
        match = re.search(r'end time=(\d+)', line)
        if match:
            timestamp_str = match.group(1)
            last_6 = timestamp_str[-6:]
            return int(last_6)
        return None
    
    def extract_start_timestamp(self, line):
        """Base method for extracting start timestamp - to be implemented by subclasses"""
        return None

class DefaultEventParser(BaseEventParser):
    """Parser for default mode (Button Up)"""
    
    def extract_start_timestamp(self, line):
        """Extract start timestamp from "button 1 up" event"""
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

class SwipeEventParser(BaseEventParser):
    """Parser for swipe mode (Button Down)"""
    
    def extract_start_timestamp(self, line):
        """Extract start timestamp from "Sending button 1 down" event"""
        match = re.search(r'Sending button 1 down (\d+\.\d+)', line)
        if match:
            timestamp_str = match.group(1)
            parts = timestamp_str.split('.')
            if len(parts) == 2:
                last_3_first = parts[0][-3:]
                first_3_second = parts[1][:3]
                result = int(last_3_first + first_3_second)
                return result
        return None

class SuspendEventParser(BaseEventParser):
    """Enhanced parser for suspend mode (Power Button) with multiple patterns"""
    
    def extract_start_timestamp(self, line):
        """Extract start timestamp from power button press event with multiple pattern matching"""
        # Try multiple patterns for power button presses
        patterns = [
            # Standard pattern from specifications
            r'def:pbpress:time=(\d+):Power button pressed',
            
            # Alternative patterns that might appear in logs
            r'Power button pressed.*time[=:](\d+)',
            r'pbpress.*time[=:](\d+)',
            r'button.*power.*time[=:](\d+)',
            r'Power.*button.*time[=:](\d+)',
            r'Power.*pressed.*time[=:](\d+)',
            
            # General timestamp extraction if line contains power button reference
            r'(?:power|pb).*(\d{6,})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                timestamp_str = match.group(1)
                
                # Handle different timestamp formats
                if len(timestamp_str) > 6:
                    # If timestamp is longer, take last 6 digits
                    last_6 = timestamp_str[-6:]
                    return int(last_6)
                elif len(timestamp_str) == 6:
                    # If already 6 digits, use as is
                    return int(timestamp_str)
                else:
                    # Pad shorter timestamps
                    return int(timestamp_str.zfill(6))
        
        # Debug output for power button related lines to help identify format
        if 'power button' in line.lower() or 'pbpress' in line.lower():
            print(f"Debug - Found power button line but couldn't extract timestamp: {line.strip()}")
            
        return None

def get_parser(mode="default"):
    """Factory function to get the appropriate parser for the specified mode"""
    parsers = {
        "default": DefaultEventParser,
        "swipe": SwipeEventParser,
        "suspend": SuspendEventParser
    }
    return parsers.get(mode, DefaultEventParser)()

def debug_timestamp_extraction(log_content):
    """Debug function to show timestamp extraction from different parsers"""
    print("\n==== TIMESTAMP EXTRACTION DEBUGGING ====")
    
    default_parser = DefaultEventParser()
    swipe_parser = SwipeEventParser()
    suspend_parser = SuspendEventParser()
    
    # Process lines looking for timestamps
    lines = log_content.split('\n')
    for i, line in enumerate(lines):
        default_ts = default_parser.extract_start_timestamp(line)
        swipe_ts = swipe_parser.extract_start_timestamp(line)
        suspend_ts = suspend_parser.extract_start_timestamp(line)
        
        if default_ts or swipe_ts or suspend_ts:
            print(f"\nLine {i+1}: {line.strip()}")
            if default_ts:
                print(f"  Default parser extracted: {default_ts}")
            if swipe_ts:
                print(f"  Swipe parser extracted: {swipe_ts}")
            if suspend_ts:
                print(f"  Suspend parser extracted: {suspend_ts}")