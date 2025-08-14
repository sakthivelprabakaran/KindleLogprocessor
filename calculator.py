"""
calculator.py - Module for processing log data and calculating durations
This module processes log data to extract start and stop points and calculate durations
"""
import re
from event_parser import get_parser

def get_mode_description(mode):
    """Get a user-friendly description of the calculation mode"""
    descriptions = {
        "default": "Default (Button Up)",
        "swipe": "Swipe Cases (Button Down)",
        "suspend": "Suspend Scenarios (Power Button)"
    }
    return descriptions.get(mode, "Unknown Mode")

def process_iteration(lines, iteration_num, mode="default", parser=None):
    """
    Process a single iteration of log data using the specified mode
    
    Args:
        lines: List of log lines to process
        iteration_num: The iteration number
        mode: One of "default", "swipe", or "suspend"
        parser: Optional parser instance (if None, one will be created based on mode)
        
    Returns:
        A dictionary with processed data or None if processing failed
    """
    if parser is None:
        parser = get_parser(mode)
    
    start_time = None
    end_times_by_marker = {}
    heights_by_marker = {}
    current_marker = None
    
    for line in lines:
        if not line.strip():
            continue
        
        # Check for start time based on the parser's implementation
        if not start_time:
            possible_start = parser.extract_start_timestamp(line)
            if possible_start:
                start_time = possible_start
        
        marker = parser.extract_marker(line)
        if marker:
            current_marker = marker
        
        if "Sending update" in line and current_marker:
            height_waveform = parser.extract_height_and_waveform(line)
            if height_waveform:
                height = height_waveform['height']
                waveform = height_waveform['waveform']
                
                heights_by_marker[current_marker] = {
                    'height': height,
                    'waveform': waveform if waveform and waveform != "auto" else "unknown",
                    'line': line.strip()
                }
        
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
    
    if not start_time or not heights_by_marker or not end_times_by_marker:
        return None
    
    # Filter out markers with "unknown" waveforms
    valid_heights = {
        marker: info for marker, info in heights_by_marker.items() 
        if info['waveform'].lower() != "unknown"
    }
    
    # If no valid waveforms found, use all heights as a fallback
    if not valid_heights:
        valid_heights = heights_by_marker
    
    # Find the marker with the maximum height among valid waveforms
    max_height = max(info['height'] for info in valid_heights.values())
    max_height_markers = [marker for marker, info in valid_heights.items() 
                         if info['height'] == max_height]
    
    max_height_markers.sort(key=lambda m: int(m) if m.isdigit() else 0)
    chosen_marker = max_height_markers[-1] if max_height_markers else list(valid_heights.keys())[0]
    
    max_height_info = valid_heights[chosen_marker]
    
    # Get the end time for the chosen marker
    if chosen_marker in end_times_by_marker:
        max_height_end_time = end_times_by_marker[chosen_marker]['time']
    else:
        # If no end time for the chosen marker, use the maximum end time
        if end_times_by_marker:
            max_height_end_time = max(end_times_by_marker.values(), key=lambda x: x['time'])['time']
        else:
            return None
    
    # Calculate duration
    duration = max_height_end_time - start_time
    if duration < 0:
        duration = abs(duration)
    
    return {
        'iteration': iteration_num,
        'start': start_time,
        'stop': max_height_end_time,
        'marker': chosen_marker,
        'duration': duration,
        'max_height': max_height_info['height'],
        'max_height_waveform': max_height_info['waveform'],
        'all_heights': [{'marker': m, 'height': h['height'], 'waveform': h['waveform']} 
                       for m, h in heights_by_marker.items()],
        'mode': mode  # Include the mode in the result
    }

def process_log_content(log_content, mode="default"):
    """
    Process all iterations in log content using the specified mode
    
    Args:
        log_content: The complete log content
        mode: One of "default", "swipe", or "suspend"
        
    Returns:
        List of processed results for each iteration
    """
    import re
    
    # Split content into iterations
    iterations = re.split(r'ITERATION_(\d+)', log_content)[1:]
    
    if not iterations:
        iterations = ["01", log_content]
    
    # Pair iteration numbers with content
    iteration_pairs = []
    for i in range(0, len(iterations), 2):
        if i+1 < len(iterations):
            iteration_num = iterations[i]
            iteration_content = iterations[i+1]
            iteration_pairs.append((iteration_num, iteration_content))
    
    results = []
    parser = get_parser(mode)
    
    for iteration_num, iteration_content in iteration_pairs:
        lines = iteration_content.split('\n')
        result = process_iteration(lines, iteration_num, mode, parser)
        if result:
            results.append(result)
    
    return results

def debug_log_scan(log_content, mode="suspend"):
    """Scan log content for relevant events based on mode for debugging purposes"""
    import re
    
    debug_info = {
        "default": {"pattern": r"button 1 up", "description": "Button Up events"},
        "swipe": {"pattern": r"button 1 down", "description": "Button Down events"},
        "suspend": {"pattern": r"power|pbpress", "description": "Power Button events"}
    }
    
    mode_info = debug_info.get(mode, debug_info["default"])
    pattern = mode_info["pattern"]
    description = mode_info["description"]
    
    print(f"Scanning log for {description} (pattern: {pattern})...")
    found = []
    
    lines = log_content.split('\n')
    for i, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            context_start = max(0, i-2)
            context_end = min(len(lines), i+3)
            context = '\n'.join(lines[context_start:context_end])
            found.append(f"Line {i+1}: {line.strip()}\nContext:\n{context}\n{'='*50}")
    
    print(f"Found {len(found)} potential {description}")
    if found:
        print("First 5 occurrences:")
        for i, f in enumerate(found[:5]):
            print(f"{i+1}. {f}")
    else:
        print("No matching lines found.")
    
    # Add debugging for waveforms
    print("\nScanning for waveform information...")
    waveform_patterns = [
        r'new waveform = (?:0x)?[\da-f]+ \(([\w_() ]+)\)', 
        r'waveform:(?:0x)?[\da-f]+ \(([\w_() ]+)\)',
        r'waveform=(?:0x)?[\da-f]+ \(([\w_() ]+)\)',
        r'Sending update\. waveform:(?:0x)?[\da-f]+ \(([\w_() ]+)\)'
    ]
    
    waveform_counts = {}
    for line in lines:
        for pattern in waveform_patterns:
            match = re.search(pattern, line)
            if match:
                waveform = match.group(1).strip()
                waveform_counts[waveform] = waveform_counts.get(waveform, 0) + 1
                break
    
    print(f"Found {sum(waveform_counts.values())} waveforms:")
    for waveform, count in sorted(waveform_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {waveform}: {count}")
    
    height_lines = []
    for i, line in enumerate(lines):
        if "height=" in line:
            height_match = re.search(r'height=(\d+)', line)
            if height_match:
                height = height_match.group(1)
                height_lines.append(f"Line {i+1}: height={height} - {line.strip()}")
    
    print(f"\nFound {len(height_lines)} height values. First 10:")
    for line in height_lines[:10]:
        print(f"  {line}")