import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
from typing import List, Tuple


class DiskSchedulingAlgorithm(ABC):
    """Abstract base class for disk scheduling algorithms"""
    
    def __init__(self, requests: List[int], head_position: int, disk_size: int):
        self.requests = requests  # Keep original order for FCFS
        self.head_position = head_position
        self.disk_size = disk_size
        self.sequence = []
        self.total_seek_time = 0
    
    @abstractmethod
    def schedule(self) -> Tuple[List[int], int]:
        """Execute the scheduling algorithm and return sequence and total seek time"""
        pass
    
    def calculate_seek_time(self, from_pos: int, to_pos: int) -> int:
        """Calculate seek time between two positions"""
        return abs(to_pos - from_pos)


class FCFS(DiskSchedulingAlgorithm):
    """First Come First Served - processes requests in the order they arrive"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        for request in self.requests:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        return self.sequence, self.total_seek_time


class SSTF(DiskSchedulingAlgorithm):
    """Shortest Seek Time First - always serves the closest request"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        remaining = list(self.requests)  # Work with unsorted requests
        
        while remaining:
            closest = min(remaining, key=lambda x: abs(x - current_head))
            seek_time = self.calculate_seek_time(current_head, closest)
            self.total_seek_time += seek_time
            self.sequence.append(closest)
            remaining.remove(closest)
            current_head = closest
        
        return self.sequence, self.total_seek_time


class SCAN(DiskSchedulingAlgorithm):
    """SCAN - moves toward track 0 first, then reverses upward"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        # Separate requests into left and right of current head
        left = sorted([x for x in self.requests if x < current_head], reverse=True)
        right = sorted([x for x in self.requests if x >= current_head])
        
        # Move toward track 0 first
        for request in left:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request

        # Continue to track 0 before reversing
        if current_head != 0:
            seek_time = self.calculate_seek_time(current_head, 0)
            self.total_seek_time += seek_time
            self.sequence.append(0)
            current_head = 0
        
        # Reverse direction and service the higher-numbered requests
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        return self.sequence, self.total_seek_time


class CSCAN(DiskSchedulingAlgorithm):
    """Circular SCAN - moves in one direction and wraps around"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        # Separate requests into left and right of current head
        left = [x for x in self.requests if x < current_head]
        right = [x for x in self.requests if x >= current_head]
        
        left.sort()
        right.sort()
        
        # Move right to end
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        # Move to disk end, then wrap to beginning
        if left:
            seek_time = self.calculate_seek_time(current_head, self.disk_size - 1)
            self.total_seek_time += seek_time
            current_head = self.disk_size - 1
            
            seek_time = self.calculate_seek_time(current_head, 0)
            self.total_seek_time += seek_time
            current_head = 0
            
            # Service left requests
            for request in left:
                seek_time = self.calculate_seek_time(current_head, request)
                self.total_seek_time += seek_time
                self.sequence.append(request)
                current_head = request
        
        return self.sequence, self.total_seek_time


class LOOK(DiskSchedulingAlgorithm):
    """LOOK - like SCAN but doesn't go to end, reverses when no requests ahead"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        # Separate requests into left and right of current head
        left = [x for x in self.requests if x < current_head]
        right = [x for x in self.requests if x >= current_head]
        
        left.sort(reverse=True)
        right.sort()
        
        # Move right
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        # Move left
        for request in left:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        return self.sequence, self.total_seek_time


class CLOOK(DiskSchedulingAlgorithm):
    """Circular LOOK - like C-SCAN but doesn't go to end"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        # Separate requests into left and right of current head
        left = [x for x in self.requests if x < current_head]
        right = [x for x in self.requests if x >= current_head]
        
        left.sort()
        right.sort()
        
        # Move right
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        # Wrap and service left requests
        if left:
            # Jump to leftmost request
            seek_time = self.calculate_seek_time(current_head, left[0])
            self.total_seek_time += seek_time
            current_head = left[0]
            self.sequence.append(current_head)
            
            # Service remaining left requests
            for request in left[1:]:
                seek_time = self.calculate_seek_time(current_head, request)
                self.total_seek_time += seek_time
                self.sequence.append(request)
                current_head = request
        
        return self.sequence, self.total_seek_time


class DiskSchedulerGUI:
    """GUI application for disk scheduling simulation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Algorithms Simulator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        self.algorithms = {
            "FCFS": FCFS,
            "SSTF": SSTF,
            "SCAN": SCAN,
            "C-SCAN": CSCAN,
            "LOOK": LOOK,
            "C-LOOK": CLOOK
        }
        
        self.create_widgets()
        self.configure_styles()
    
    def configure_styles(self):
        """Configure TTK styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Input
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        ttk.Label(left_frame, text="Input Parameters", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 15))
        
        # Disk requests input
        ttk.Label(left_frame, text="Disk Requests (comma-separated):").pack(anchor=tk.W)
        self.requests_entry = ttk.Entry(left_frame, width=30)
        self.requests_entry.pack(fill=tk.X, pady=(0, 10))
        self.requests_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")
        
        # Initial head position
        ttk.Label(left_frame, text="Initial Head Position:").pack(anchor=tk.W)
        self.head_entry = ttk.Entry(left_frame, width=30)
        self.head_entry.pack(fill=tk.X, pady=(0, 10))
        self.head_entry.insert(0, "53")
        
        # Disk size
        ttk.Label(left_frame, text="Disk Size (cylinders):").pack(anchor=tk.W)
        self.disk_size_entry = ttk.Entry(left_frame, width=30)
        self.disk_size_entry.pack(fill=tk.X, pady=(0, 15))
        self.disk_size_entry.insert(0, "200")
        
        # Algorithm selection
        ttk.Label(left_frame, text="Select Algorithm:", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 10))
        
        self.algorithm_var = tk.StringVar(value="FCFS")
        for algo in self.algorithms.keys():
            ttk.Radiobutton(left_frame, text=algo, variable=self.algorithm_var, 
                           value=algo).pack(anchor=tk.W, pady=5)
        
        # Run button
        ttk.Button(left_frame, text="Run Simulation", 
                  command=self.run_simulation).pack(fill=tk.X, pady=(20, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(left_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(results_frame, text="Total Seek Time:").pack(anchor=tk.W)
        self.seek_time_label = ttk.Label(results_frame, text="N/A", foreground="blue")
        self.seek_time_label.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(results_frame, text="Sequence:").pack(anchor=tk.W)
        self.sequence_text = tk.Text(results_frame, height=6, width=28, font=('Courier', 9))
        self.sequence_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Visualization
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Disk Head Movement Visualization", 
                 style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        self.canvas_frame = ttk.Frame(right_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    def run_simulation(self):
        """Execute the selected algorithm and display results"""
        try:
            # Parse inputs
            requests_str = self.requests_entry.get().strip()
            requests = [int(x.strip()) for x in requests_str.split(',')]
            head_pos = int(self.head_entry.get().strip())
            disk_size = int(self.disk_size_entry.get().strip())
            
            # Validate inputs
            if not requests:
                messagebox.showerror("Error", "Please enter disk requests")
                return
            
            if head_pos < 0 or head_pos >= disk_size:
                messagebox.showerror("Error", f"Head position must be between 0 and {disk_size-1}")
                return
            
            if any(r < 0 or r >= disk_size for r in requests):
                messagebox.showerror("Error", f"All requests must be between 0 and {disk_size-1}")
                return
            
            # Run selected algorithm
            algorithm_class = self.algorithms[self.algorithm_var.get()]
            scheduler = algorithm_class(requests, head_pos, disk_size)
            sequence, total_seek_time = scheduler.schedule()
            
            # Update results
            self.seek_time_label.config(text=str(total_seek_time))
            
            sequence_text = " → ".join(map(str, sequence))
            self.sequence_text.config(state=tk.NORMAL)
            self.sequence_text.delete(1.0, tk.END)
            self.sequence_text.insert(1.0, sequence_text)
            self.sequence_text.config(state=tk.DISABLED)
            
            # Draw visualization
            self.draw_visualization(sequence, disk_size, head_pos)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def draw_visualization(self, sequence: List[int], disk_size: int, head_pos: int):
        """Draw the disk head movement visualization"""
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Create figure with a top cylinder scale and a downward head path
        fig = Figure(figsize=(12, 8), dpi=100)
        
        ax = fig.add_subplot(111)
        
        axis_y = 1.0
        path_start_y = 0.55
        path_step = 0.75
        y_positions = [path_start_y - (i * path_step) for i in range(len(sequence))]

        # Put the cylinder scale at the top so the movement path stays visually separate
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.tick_params(axis='x', top=True, labeltop=True, bottom=False, labelbottom=False)
        ax.plot([0, disk_size], [axis_y, axis_y], 'k-', linewidth=3, zorder=1)
        
        # Mark key cylinder positions on the disk
        unique_positions = sorted(set(sequence))
        for pos in unique_positions:
            ax.plot([pos, pos], [axis_y - 0.08, axis_y + 0.08], 'k-', linewidth=2)
            ax.text(pos, axis_y + 0.16, str(pos), ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Draw connecting lines between accesses
        for i in range(len(sequence) - 1):
            x1, y1 = sequence[i], y_positions[i]
            x2, y2 = sequence[i + 1], y_positions[i + 1]
            
            # Draw line with arrow
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=2, color='navy', alpha=0.7))
        
        # Mark all access points with dots
        for i, (pos, y) in enumerate(zip(sequence, y_positions)):
            # Color code: green for start, red for requests, orange for end
            if i == 0:
                ax.scatter(pos, y, s=300, c='green', marker='o', zorder=5, edgecolors='darkgreen', linewidth=2)
            elif i == len(sequence) - 1:
                ax.scatter(pos, y, s=300, c='orange', marker='o', zorder=5, edgecolors='darkorange', linewidth=2)
            else:
                ax.scatter(pos, y, s=200, c='red', marker='o', zorder=5, edgecolors='darkred', linewidth=1.5)
            
            # Add step number
            ax.text(pos, y - 0.18, str(i), ha='center', fontsize=8, fontweight='bold', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Configure axes
        ax.set_xlim(-5, disk_size + 5)
        ax.set_ylim(min(y_positions) - 0.7, axis_y + 0.45)
        ax.set_xlabel("Disk Cylinder Number", fontsize=12, fontweight='bold')
        ax.set_title(f"Disk Scheduling: {self.algorithm_var.get()}\n{', '.join(map(str, sequence[1:]))}", 
                    fontsize=14, fontweight='bold')
        
        # Remove y-axis
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=12, 
                   markeredgecolor='darkgreen', markeredgewidth=2, label='Start Position'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, 
                   markeredgecolor='darkred', markeredgewidth=1.5, label='Disk Request'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=12, 
                   markeredgecolor='darkorange', markeredgewidth=2, label='End Position'),
            Line2D([0], [0], color='navy', lw=2, label='Head Movement Path')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        # Add grid for reference
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulerGUI(root)
    root.mainloop()
