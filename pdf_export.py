
"""
PDF Export Module for Kindle Log Analyzer
Generates comprehensive PDF reports with highlighted start/stop points
"""
import re
import os
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import yellow, black, white, blue, red, green
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


class PdfExporter:
    """PDF export functionality with highlighting and comprehensive reporting"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=blue,
            alignment=TA_CENTER
        )
        
        # Iteration header style
        self.iteration_style = ParagraphStyle(
            'IterationHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=red,
            borderWidth=1,
            borderColor=red,
            borderPadding=5
        )
        
        # Log line style
        self.log_style = ParagraphStyle(
            'LogLine',
            parent=self.styles['Code'],
            fontSize=8,
            fontName='Courier',
            leftIndent=10,
            spaceAfter=2
        )
        
        # Highlighted log style
        self.highlight_style = ParagraphStyle(
            'HighlightedLog',
            parent=self.log_style,
            backColor=yellow,
            borderColor=red,
            borderWidth=0.5
        )
        
        # Summary style
        self.summary_style = ParagraphStyle(
            'Summary',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=8,
            textColor=blue
        )
    
    def extract_start_digits(self, timestamp_str, mode):
        """Extract 5-6 digit numbers from timestamps based on mode"""
        if mode == "suspend":
            # For suspend mode: def:pbpress:time=650.205:Power button pressed
            # Extract 650.205 -> 650205
            match = re.search(r'def:pbpress:time=(\d+\.\d+):Power button pressed', timestamp_str)
            if match:
                ts = match.group(1)
                parts = ts.split('.')
                if len(parts) == 2:
                    before_dot = parts[0][-3:]  # Last 3 digits before dot
                    after_dot = parts[1][:3]    # First 3 digits after dot
                    return before_dot + after_dot
        
        elif mode in ["default", "swipe"]:
            # For default/swipe: extract from patterns like "button 1 up 123.456"
            patterns = [
                r'button 1 up (\d+\.\d+)',
                r'Sending button 1 down (\d+\.\d+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, timestamp_str)
                if match:
                    ts = match.group(1)
                    parts = ts.split('.')
                    if len(parts) == 2:
                        last_3_first = parts[0][-3:]
                        first_3_second = parts[1][:3]
                        return last_3_first + first_3_second
        
        # Fallback: extract any 5-6 digit sequence
        digits_match = re.search(r'\b(\d{5,6})\b', timestamp_str)
        if digits_match:
            return digits_match.group(1)
            
        return None
    
    def highlight_log_line(self, line, start_points=None, stop_points=None, mode="default"):
        """Apply highlighting to log lines for start/stop points"""
        if not start_points:
            start_points = []
        if not stop_points:
            stop_points = []
            
        highlighted_line = line
        
        # Highlight start points (5-6 digit sequences from timestamps)
        start_digits = self.extract_start_digits(line, mode)
        if start_digits:
            # Highlight the extracted digits
            highlighted_line = highlighted_line.replace(
                start_digits, 
                f'<font backColor="yellow" color="red"><b>{start_digits}</b></font>'
            )
        
        # Highlight stop points (lines containing end markers and end times)
        if "update end marker=" in line and "end time=" in line:
            # This is a stop point line, highlight the end time
            end_time_match = re.search(r'end time=(\d+)', line)
            if end_time_match:
                end_time = end_time_match.group(1)
                last_6 = end_time[-6:]
                highlighted_line = highlighted_line.replace(
                    end_time,
                    f'<font backColor="lightblue" color="darkblue"><b>{end_time}</b></font>'
                )
        
        return highlighted_line
    
    def generate_pdf_report(self, results, output_path, mode="default"):
        """Generate comprehensive PDF report with highlighting"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            story = []
            
            # Add title
            title = f"Kindle Log Analysis Report - {mode.title()} Mode"
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 20))
            
            # Add generation timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"Generated on: {timestamp}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Generate table of contents with durations and averages
            story.extend(self.create_table_of_contents(results))
            story.append(PageBreak())
            
            # Process each iteration
            for idx, result in enumerate(results):
                story.extend(self.process_iteration_for_pdf(result, mode))
                if idx < len(results) - 1:  # Add page break between iterations
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            return True, f"PDF report generated successfully at {output_path}"
            
        except Exception as e:
            return False, f"Error generating PDF: {str(e)}"
    
    def create_table_of_contents(self, results):
        """Create table of contents with iteration summary"""
        story = []
        
        # Table of contents header
        story.append(Paragraph("Table of Contents", self.styles['Heading1']))
        story.append(Spacer(1, 15))
        
        # Summary statistics
        if results:
            total_iterations = len(results)
            durations = [r.get('duration', 0) for r in results if r.get('duration') is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Iterations', str(total_iterations)],
                ['Average Duration', f"{avg_duration:.2f}"],
                ['Min Duration', str(min_duration)],
                ['Max Duration', str(max_duration)]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), white),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Detailed iteration table
        if results:
            table_data = [['Iteration', 'Start', 'Stop', 'Duration', 'Max Height', 'Waveform']]
            
            for result in results:
                table_data.append([
                    f"ITERATION_{result.get('iteration', 'N/A')}",
                    str(result.get('start', 'N/A')),
                    str(result.get('stop', 'N/A')),
                    str(result.get('duration', 'N/A')),
                    str(result.get('max_height', 'N/A')),
                    result.get('max_height_waveform', 'N/A')
                ])
            
            iterations_table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            iterations_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), green),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), white),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, '#f0f0f0'])
            ]))
            
            story.append(iterations_table)
        
        return story
    
    def process_iteration_for_pdf(self, result, mode):
        """Process a single iteration for PDF output"""
        story = []
        
        # Iteration header
        iteration_num = result.get('iteration', 'Unknown')
        story.append(Paragraph(f"ITERATION_{iteration_num}", self.iteration_style))
        story.append(Spacer(1, 10))
        
        # Process original log content with highlighting
        original_log = result.get('original_log', '')
        if original_log:
            story.append(Paragraph("Original Log Content:", self.styles['Heading3']))
            story.append(Spacer(1, 5))
            
            # Split log into lines and process each
            log_lines = original_log.split('\n')
            for line in log_lines:
                if line.strip():
                    highlighted_line = self.highlight_log_line(line.strip(), mode=mode)
                    # Escape HTML characters for ReportLab
                    safe_line = highlighted_line.replace('<', '&lt;').replace('>', '&gt;')
                    # But keep our highlighting tags
                    safe_line = re.sub(r'&lt;(/?font[^&]*?)&gt;', r'<\1>', safe_line)
                    safe_line = re.sub(r'&lt;(/?b)&gt;', r'<\1>', safe_line)
                    
                    story.append(Paragraph(safe_line, self.log_style))
            
            story.append(Spacer(1, 15))
        
        # Add calculation details
        story.extend(self.create_calculation_details(result))
        
        return story
    
    def create_calculation_details(self, result):
        """Create calculation details section for an iteration"""
        story = []
        
        story.append(Paragraph("Calculation Details:", self.styles['Heading3']))
        story.append(Spacer(1, 5))
        
        # Key metrics
        details = [
            f"<b>Start Time:</b> {result.get('start', 'N/A')}",
            f"<b>Stop Time:</b> {result.get('stop', 'N/A')}",
            f"<b>Duration:</b> {result.get('duration', 'N/A')}",
            f"<b>Selected Marker:</b> {result.get('marker', 'N/A')}",
            f"<b>Max Height:</b> {result.get('max_height', 'N/A')}",
            f"<b>Max Height Waveform:</b> {result.get('max_height_waveform', 'N/A')}"
        ]
        
        for detail in details:
            story.append(Paragraph(detail, self.summary_style))
        
        # All heights information
        all_heights = result.get('all_heights', [])
        if all_heights:
            story.append(Spacer(1, 10))
            story.append(Paragraph("All Heights Found:", self.styles['Heading4']))
            
            height_data = [['Marker', 'Height', 'Waveform']]
            for height_info in all_heights:
                height_data.append([
                    height_info.get('marker', 'N/A'),
                    str(height_info.get('height', 'N/A')),
                    height_info.get('waveform', 'N/A')
                ])
            
            if len(height_data) > 1:  # More than just header
                height_table = Table(height_data, colWidths=[1*inch, 1*inch, 2*inch])
                height_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), blue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('GRID', (0, 0), (-1, -1), 1, black)
                ]))
                
                story.append(height_table)
        
        story.append(Spacer(1, 15))
        return story


def test_pdf_export():
    """Test function for PDF export"""
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
            'all_heights': [
                {'marker': '123', 'height': 1200, 'waveform': 'DU'},
                {'marker': '124', 'height': 800, 'waveform': 'unknown'}
            ],
            'original_log': '''1751099650.205215 def:pbpress:time=650.205:Power button pressed
1751099651.234567 update end marker=123 end time=1751099651234567'''
        }
    ]
    
    exporter = PdfExporter()
    success, message = exporter.generate_pdf_report(
        test_results, 
        "/home/ubuntu/test_report.pdf", 
        "suspend"
    )
    
    print(f"PDF Export Test: {message}")
    return success


if __name__ == "__main__":
    test_pdf_export()
