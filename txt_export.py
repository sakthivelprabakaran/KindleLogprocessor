
"""
TXT Export Module for Kindle Log Analyzer
Exports iteration logs in original input format
"""
import os
import re
from datetime import datetime
from pathlib import Path


class TxtExporter:
    """TXT export functionality maintaining original log format"""
    
    def __init__(self):
        self.separator = "=" * 80
        self.iteration_separator = "-" * 40
    
    def export_txt_file(self, results, output_path, include_summary=True):
        """Export results to TXT file maintaining original format"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("KINDLE LOG ANALYZER - EXPORTED LOGS\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(self.separator + "\n\n")
                
                # Write summary if requested
                if include_summary and results:
                    f.write("SUMMARY\n")
                    f.write(self.iteration_separator + "\n")
                    f.write(f"Total Iterations: {len(results)}\n")
                    
                    durations = [r.get('duration', 0) for r in results if r.get('duration') is not None]
                    if durations:
                        f.write(f"Average Duration: {sum(durations) / len(durations):.2f}\n")
                        f.write(f"Min Duration: {min(durations)}\n")
                        f.write(f"Max Duration: {max(durations)}\n")
                    
                    f.write("\nIteration Details:\n")
                    for result in results:
                        f.write(f"  ITERATION_{result.get('iteration', 'N/A')}: "
                               f"Start={result.get('start', 'N/A')}, "
                               f"Stop={result.get('stop', 'N/A')}, "
                               f"Duration={result.get('duration', 'N/A')}\n")
                    
                    f.write("\n" + self.separator + "\n\n")
                
                # Write each iteration's original log content
                for idx, result in enumerate(results):
                    iteration_num = result.get('iteration', f'{idx+1:02d}')
                    f.write(f"ITERATION_{iteration_num}\n")
                    f.write(self.iteration_separator + "\n")
                    
                    # Write original log content exactly as it was
                    original_log = result.get('original_log', '')
                    if original_log:
                        # Ensure we maintain exact formatting
                        f.write(original_log)
                        if not original_log.endswith('\n'):
                            f.write('\n')
                    else:
                        f.write("No original log content available for this iteration.\n")
                    
                    # Add separator between iterations
                    if idx < len(results) - 1:
                        f.write("\n" + self.separator + "\n\n")
                
                f.write("\n" + self.separator + "\n")
                f.write("END OF LOG EXPORT\n")
            
            return True, f"TXT file exported successfully to {output_path}"
            
        except Exception as e:
            return False, f"Error exporting TXT file: {str(e)}"
    
    def export_raw_logs_only(self, results, output_path):
        """Export only the raw log content without any additional formatting"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for idx, result in enumerate(results):
                    iteration_num = result.get('iteration', f'{idx+1:02d}')
                    
                    # Write iteration header exactly as it would appear in original logs
                    f.write(f"ITERATION_{iteration_num}\n")
                    
                    # Write original log content exactly as it was
                    original_log = result.get('original_log', '')
                    if original_log:
                        f.write(original_log)
                        if not original_log.endswith('\n'):
                            f.write('\n')
                    
                    # Add blank line between iterations (if not last)
                    if idx < len(results) - 1:
                        f.write('\n')
            
            return True, f"Raw logs exported successfully to {output_path}"
            
        except Exception as e:
            return False, f"Error exporting raw logs: {str(e)}"
    
    def create_comparison_file(self, original_content, results, output_path):
        """Create a comparison file showing original vs processed content"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("KINDLE LOG ANALYZER - ORIGINAL vs PROCESSED COMPARISON\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(self.separator + "\n\n")
                
                f.write("ORIGINAL CONTENT:\n")
                f.write(self.iteration_separator + "\n")
                f.write(original_content)
                f.write("\n\n" + self.separator + "\n\n")
                
                f.write("PROCESSED ITERATIONS:\n")
                f.write(self.iteration_separator + "\n")
                
                for idx, result in enumerate(results):
                    iteration_num = result.get('iteration', f'{idx+1:02d}')
                    f.write(f"\nITERATION_{iteration_num} - PROCESSED RESULTS:\n")
                    f.write(f"  Start: {result.get('start', 'N/A')}\n")
                    f.write(f"  Stop: {result.get('stop', 'N/A')}\n")
                    f.write(f"  Duration: {result.get('duration', 'N/A')}\n")
                    f.write(f"  Max Height: {result.get('max_height', 'N/A')}\n")
                    f.write(f"  Waveform: {result.get('max_height_waveform', 'N/A')}\n")
                    
                    f.write(f"\nORIGINAL LOG FOR ITERATION_{iteration_num}:\n")
                    original_log = result.get('original_log', '')
                    if original_log:
                        f.write(original_log)
                        if not original_log.endswith('\n'):
                            f.write('\n')
                    else:
                        f.write("No original log content available.\n")
                    
                    if idx < len(results) - 1:
                        f.write("\n" + self.iteration_separator + "\n")
                
                f.write("\n" + self.separator + "\n")
                f.write("END OF COMPARISON\n")
            
            return True, f"Comparison file created successfully at {output_path}"
            
        except Exception as e:
            return False, f"Error creating comparison file: {str(e)}"


def test_txt_export():
    """Test function for TXT export"""
    # Sample test data
    test_results = [
        {
            'iteration': '01',
            'start': 650205,
            'stop': 651234,
            'duration': 1029,
            'marker': '123',
            'max_height': 1200,
            'max_height_waveform': 'DU',
            'original_log': '''1751099650.205215 def:pbpress:time=650.205:Power button pressed
1751099651.234567 Some log line with marker [123] and height=1200
1751099651.234567 update end marker=123 end time=1751099651234567'''
        },
        {
            'iteration': '02',
            'start': 652345,
            'stop': 653456,
            'duration': 1111,
            'marker': '124',
            'max_height': 800,
            'max_height_waveform': 'GC16',
            'original_log': '''1751099652.345678 def:pbpress:time=652.345:Power button pressed
1751099653.456789 Another log line with different data
1751099653.456789 update end marker=124 end time=1751099653456789'''
        }
    ]
    
    exporter = TxtExporter()
    
    # Test regular export
    success1, message1 = exporter.export_txt_file(test_results, "/home/ubuntu/test_export.txt")
    print(f"TXT Export Test: {message1}")
    
    # Test raw logs only export
    success2, message2 = exporter.export_raw_logs_only(test_results, "/home/ubuntu/test_raw.txt")
    print(f"Raw Export Test: {message2}")
    
    return success1 and success2


if __name__ == "__main__":
    test_txt_export()
