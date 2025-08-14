
"""
Waveform Visualization Module for Kindle Log Analyzer
Creates dynamic grid layout for enhanced waveform display
"""
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime
import os


class WaveformVisualizer:
    """Enhanced waveform visualization with dynamic grid layout"""
    
    def __init__(self, figure_size=(16, 12), dpi=100):
        self.figure_size = figure_size
        self.dpi = dpi
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def calculate_grid_dimensions(self, n_iterations):
        """Calculate optimal grid dimensions for n iterations"""
        if n_iterations <= 0:
            return 1, 1
        elif n_iterations == 1:
            return 1, 1
        elif n_iterations <= 4:
            return 2, 2
        else:
            cols = math.ceil(math.sqrt(n_iterations))
            rows = math.ceil(n_iterations / cols)
            return rows, cols
    
    def create_waveform_grid(self, results, output_path=None, show_plot=False):
        """Create dynamic grid layout for waveform visualization"""
        try:
            if not results:
                return False, "No results to visualize"
            
            n_iterations = len(results)
            rows, cols = self.calculate_grid_dimensions(n_iterations)
            
            # Create figure with dynamic grid
            fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
            fig.suptitle('Kindle Log Analyzer - Waveform Analysis Grid', 
                        fontsize=16, fontweight='bold', y=0.95)
            
            # Create grid spec for subplots
            gs = GridSpec(rows, cols, figure=fig, hspace=0.4, wspace=0.3)
            
            for idx, result in enumerate(results):
                row = idx // cols
                col = idx % cols
                
                # Create subplot
                ax = fig.add_subplot(gs[row, col])
                self.create_iteration_subplot(ax, result, idx)
            
            # Hide empty subplots
            total_subplots = rows * cols
            for idx in range(n_iterations, total_subplots):
                row = idx // cols
                col = idx % cols
                ax = fig.add_subplot(gs[row, col])
                ax.set_visible(False)
            
            # Add summary information
            self.add_summary_text(fig, results)
            
            plt.tight_layout()
            
            if output_path:
                plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return True, f"Waveform grid saved to {output_path}"
            
            if show_plot:
                plt.show()
                return True, "Waveform grid displayed"
            else:
                plt.close()
                return True, "Waveform grid created"
            
        except Exception as e:
            return False, f"Error creating waveform grid: {str(e)}"
    
    def create_iteration_subplot(self, ax, result, iteration_index):
        """Create subplot for a single iteration"""
        iteration_num = result.get('iteration', f'{iteration_index+1:02d}')
        
        # Get waveform data
        all_heights = result.get('all_heights', [])
        max_height = result.get('max_height', 0)
        max_waveform = result.get('max_height_waveform', 'unknown')
        duration = result.get('duration', 0)
        
        # Set title
        ax.set_title(f'ITERATION_{iteration_num}\nDuration: {duration}', 
                    fontweight='bold', fontsize=10)
        
        if not all_heights:
            ax.text(0.5, 0.5, 'No waveform data', ha='center', va='center',
                   transform=ax.transAxes, fontsize=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            return
        
        # Prepare data for plotting
        markers = [h.get('marker', f'M{i}') for i, h in enumerate(all_heights)]
        heights = [h.get('height', 0) for h in all_heights]
        waveforms = [h.get('waveform', 'unknown') for h in all_heights]
        
        # Create bar chart
        x_pos = np.arange(len(markers))
        color_map = [self.colors[i % len(self.colors)] for i in range(len(markers))]
        
        # Highlight the max height bar
        max_height_idx = None
        if max_height > 0:
            for i, h in enumerate(heights):
                if h == max_height:
                    max_height_idx = i
                    break
        
        bars = ax.bar(x_pos, heights, color=color_map, alpha=0.7, edgecolor='black', linewidth=1)
        
        # Highlight max height bar
        if max_height_idx is not None:
            bars[max_height_idx].set_color('red')
            bars[max_height_idx].set_alpha(1.0)
            bars[max_height_idx].set_linewidth(2)
        
        # Customize axes
        ax.set_xlabel('Markers', fontsize=9)
        ax.set_ylabel('Height', fontsize=9)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(markers, rotation=45, ha='right', fontsize=8)
        ax.tick_params(axis='y', labelsize=8)
        
        # Add value labels on bars
        for i, (bar, height, waveform) in enumerate(zip(bars, heights, waveforms)):
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(heights)*0.01,
                       f'{height}\n{waveform}', ha='center', va='bottom', fontsize=7,
                       fontweight='bold' if i == max_height_idx else 'normal')
        
        # Set y-axis limits with some padding
        if max(heights) > 0:
            ax.set_ylim(0, max(heights) * 1.15)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Add border around the subplot
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('gray')
    
    def add_summary_text(self, fig, results):
        """Add summary information to the figure"""
        if not results:
            return
        
        durations = [r.get('duration', 0) for r in results if r.get('duration') is not None]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            summary_text = (f"Summary: {len(results)} iterations | "
                          f"Avg: {avg_duration:.1f} | "
                          f"Min: {min_duration} | "
                          f"Max: {max_duration}")
            
            fig.text(0.5, 0.02, summary_text, ha='center', va='bottom',
                    fontsize=10, style='italic', color='darkblue')
    
    def create_copyable_data_view(self, results, output_path):
        """Create a text-based data view that's easy to copy"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("KINDLE LOG ANALYZER - COPYABLE WAVEFORM DATA\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for result in results:
                    iteration_num = result.get('iteration', 'N/A')
                    f.write(f"ITERATION_{iteration_num}:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Start: {result.get('start', 'N/A')}\n")
                    f.write(f"Stop: {result.get('stop', 'N/A')}\n")
                    f.write(f"Duration: {result.get('duration', 'N/A')}\n")
                    f.write(f"Max Height: {result.get('max_height', 'N/A')} ({result.get('max_height_waveform', 'N/A')})\n")
                    
                    all_heights = result.get('all_heights', [])
                    if all_heights:
                        f.write("\nAll Heights:\n")
                        for height_info in all_heights:
                            marker = height_info.get('marker', 'N/A')
                            height = height_info.get('height', 'N/A')
                            waveform = height_info.get('waveform', 'N/A')
                            f.write(f"  Marker {marker}: {height} ({waveform})\n")
                    
                    f.write("\n" + "=" * 60 + "\n\n")
            
            return True, f"Copyable data saved to {output_path}"
            
        except Exception as e:
            return False, f"Error creating copyable data: {str(e)}"


def test_waveform_visualization():
    """Test function for waveform visualization"""
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
                {'marker': '124', 'height': 800, 'waveform': 'GC16'},
                {'marker': '125', 'height': 600, 'waveform': 'unknown'}
            ]
        },
        {
            'iteration': '02',
            'start': 652345,
            'stop': 653456,
            'duration': 1111,
            'marker': '126',
            'max_height': 1000,
            'max_height_waveform': 'GC16',
            'all_heights': [
                {'marker': '126', 'height': 1000, 'waveform': 'GC16'},
                {'marker': '127', 'height': 750, 'waveform': 'DU'}
            ]
        },
        {
            'iteration': '03',
            'start': 654567,
            'stop': 655678,
            'duration': 1111,
            'marker': '128',
            'max_height': 1400,
            'max_height_waveform': 'GLR16',
            'all_heights': [
                {'marker': '128', 'height': 1400, 'waveform': 'GLR16'},
                {'marker': '129', 'height': 900, 'waveform': 'DU'},
                {'marker': '130', 'height': 700, 'waveform': 'GC16'}
            ]
        }
    ]
    
    visualizer = WaveformVisualizer()
    
    # Test grid creation
    success1, message1 = visualizer.create_waveform_grid(
        test_results, 
        "/home/ubuntu/test_waveform_grid.png"
    )
    print(f"Waveform Grid Test: {message1}")
    
    # Test copyable data
    success2, message2 = visualizer.create_copyable_data_view(
        test_results,
        "/home/ubuntu/test_copyable_data.txt"
    )
    print(f"Copyable Data Test: {message2}")
    
    return success1 and success2


if __name__ == "__main__":
    test_waveform_visualization()
