import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
from pathlib import Path
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
    """Circular SCAN - moves upward, goes to the end, wraps to 0, then continues upward"""
    
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        # Separate requests into left and right of current head
        left = sorted([x for x in self.requests if x < current_head])
        right = sorted([x for x in self.requests if x >= current_head])

        # Service higher-numbered requests first
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        # Move to the highest cylinder before wrapping
        if left:
            if current_head != self.disk_size - 1:
                seek_time = self.calculate_seek_time(current_head, self.disk_size - 1)
                self.total_seek_time += seek_time
                self.sequence.append(self.disk_size - 1)
                current_head = self.disk_size - 1

            seek_time = self.calculate_seek_time(current_head, 0)
            self.total_seek_time += seek_time
            self.sequence.append(0)
            current_head = 0
            
            # Continue upward from the low end
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
        self.base_dir = Path(__file__).resolve().parent
        self.assets_dir = self._resolve_assets_dir()
        self.ui_images = {}

        self.default_requests = "98, 183, 37, 122, 14, 124, 65, 67"
        self.default_head = "53"
        self.default_disk_size = "200"

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

    def _resolve_assets_dir(self) -> Path:
        """Find the directory that contains the GUI image assets"""
        for candidate in (self.base_dir / "buttons", self.base_dir / "utils"):
            if candidate.exists():
                return candidate
        return self.base_dir
    
    def configure_styles(self):
        """Configure TTK styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f5c9a1')
        style.configure('TLabel', background='#f5c9a1', foreground='#2b2235', font=('Courier New', 10, 'bold'))
        style.configure('TButton', font=('Courier New', 10, 'bold'))
        style.configure('Title.TLabel', background='#f5c9a1', foreground='#2b2235', font=('Courier New', 15, 'bold'))
        style.configure('Retro.TLabelframe', background='#f1ef8f', bordercolor='#5c4a78', relief='solid')
        style.configure('Retro.TLabelframe.Label', background='#f1ef8f', foreground='#2b2235', font=('Courier New', 12, 'bold'))
        style.configure('Retro.TCheckbutton', background='#f1ef8f', foreground='#2b2235', font=('Courier New', 10, 'bold'))
        style.configure('Retro.TRadiobutton', background='#f1ef8f', foreground='#2b2235', font=('Courier New', 10, 'bold'))

    def load_ui_image(self, filename: str) -> tk.PhotoImage:
        """Load and cache an image from the buttons folder"""
        if filename not in self.ui_images:
            self.ui_images[filename] = tk.PhotoImage(file=str(self.assets_dir / filename))
        return self.ui_images[filename]

    def create_image_button(self, parent, filename: str, command):
        """Create a clickable image button"""
        image = self.load_ui_image(filename)
        button = tk.Button(
            parent,
            image=image,
            command=command,
            bd=0,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            bg="#42c400",
            activebackground="#42c400",
        )
        button.image = image
        return button

    def create_scaled_image_button(self, parent, filename: str, command, scale: int = 2):
        """Create a smaller clickable image button"""
        image = self.load_ui_image(filename)
        if scale > 1:
            image = image.subsample(scale, scale)
        button = tk.Button(
            parent,
            image=image,
            command=command,
            bd=0,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            bg="#36c21f",
            activebackground="#36c21f",
        )
        button.image = image
        return button

    def toggle_section(self, section_frame, pack_kwargs):
        """Show or hide a GUI section without affecting the simulation logic"""
        if section_frame.winfo_ismapped():
            section_frame.pack_forget()
        else:
            section_frame.pack(**pack_kwargs)
    
    def create_widgets(self):
        """Create GUI widgets"""
        self.background_image = self.load_ui_image("bg2.png")
        self.root.geometry(f"{self.background_image.width()}x{self.background_image.height()}")
        self.root.configure(bg="#f5c9a1")

        background_label = tk.Label(self.root, image=self.background_image, bd=0)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = self.background_image
        background_label.lower()

        # Main container
        main_frame = tk.Frame(self.root, bg="#f5c9a1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 0))
        
        # Left panel - Input
        left_frame = tk.Frame(main_frame, width=360, bg="#f5c9a1")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(12, 22))
        left_frame.pack_propagate(False)
        
        self.input_section = ttk.LabelFrame(left_frame, text="Input Parameters", style='Retro.TLabelframe', padding=12)
        self.input_section.pack(fill=tk.X, pady=(0, 14))

        ttk.Label(self.input_section, text="DISK REQUESTS (COMMA-SEPARATED)").pack(anchor=tk.W, padx=(5, 0), pady=(0, 4))
        self.requests_entry = tk.Entry(self.input_section, width=38, font=('Courier New', 11, 'bold'), bd=0, relief='flat', bg='#a7a36c', fg='#151515', insertbackground='#151515')
        self.requests_entry.pack(fill=tk.X, padx=(5, 0), pady=(0, 12), ipady=6)
        self.requests_entry.insert(0, self.default_requests)

        ttk.Label(self.input_section, text="INITIAL HEAD POSITION").pack(anchor=tk.W, padx=(5, 0), pady=(0, 4))
        self.head_entry = tk.Entry(self.input_section, width=38, font=('Courier New', 11, 'bold'), bd=0, relief='flat', bg='#a7a36c', fg='#151515', insertbackground='#151515')
        self.head_entry.pack(fill=tk.X, padx=(5, 0), pady=(0, 12), ipady=6)
        self.head_entry.insert(0, self.default_head)

        ttk.Label(self.input_section, text="DISK SIZE (CYLINDERS)").pack(anchor=tk.W, padx=(5, 0), pady=(0, 4))
        self.disk_size_entry = tk.Entry(self.input_section, width=38, font=('Courier New', 11, 'bold'), bd=0, relief='flat', bg='#a7a36c', fg='#151515', insertbackground='#151515')
        self.disk_size_entry.pack(fill=tk.X, padx=(5, 0), pady=(0, 2), ipady=6)
        self.disk_size_entry.insert(0, self.default_disk_size)

        self.algorithm_section = ttk.LabelFrame(left_frame, text="Select Algorithm", style='Retro.TLabelframe', padding=12)
        self.algorithm_section.pack(fill=tk.X, pady=(0, 14))

        self.algorithm_var = tk.StringVar(value="FCFS")
        for algo in self.algorithms.keys():
            ttk.Radiobutton(self.algorithm_section, text=algo, variable=self.algorithm_var, value=algo, style='Retro.TRadiobutton').pack(anchor=tk.W, padx=(10, 0), pady=4)

        self.input_section.pack_forget()
        self.algorithm_section.pack_forget()

        # Action buttons controlled by the image assets
        button_bar = tk.Frame(self.root, bg="#36c21f", height=96)
        button_bar.pack(side=tk.BOTTOM, fill=tk.X)
        button_bar.pack_propagate(False)

        input_button = self.create_image_button(
            button_bar,
            "Input_Parameter_button.png",
            lambda: self.toggle_section(self.input_section, {"fill": tk.X, "pady": (0, 12)})
        )
        input_button.pack(side=tk.LEFT, padx=(40, 20), pady=8)

        algorithm_button = self.create_image_button(
            button_bar,
            "Pick_Algorithm_button.png",
            lambda: self.toggle_section(self.algorithm_section, {"fill": tk.X, "pady": (0, 12)})
        )
        algorithm_button.pack(side=tk.LEFT, padx=(0, 20), pady=8)

        run_button = self.create_image_button(button_bar, "Run_Sim_button.png", self.run_simulation)
        run_button.pack(side=tk.LEFT, padx=(0, 20), pady=8)

        reset_button = self.create_image_button(button_bar, "Reset_button.png", self.reset_simulation)
        reset_button.pack(side=tk.LEFT, padx=(0, 20), pady=8)

        quit_button = self.create_scaled_image_button(button_bar, "quit_button.png", self.root.destroy, scale=2)
        quit_button.pack(side=tk.RIGHT, padx=(0, 20), pady=8)
        
        # Results frame
        results_frame = ttk.LabelFrame(left_frame, text="Results", style='Retro.TLabelframe', padding=8)
        results_frame.pack(fill=tk.X, expand=False, pady=(18, 0), padx=(5, 0))
        
        ttk.Label(results_frame, text="TOTAL SEEK TIME:").pack(anchor=tk.W)
        self.seek_time_label = ttk.Label(results_frame, text="N/A", foreground="#111111")
        self.seek_time_label.pack(anchor=tk.W, pady=(0, 8))
        
        ttk.Label(results_frame, text="SEQUENCE:").pack(anchor=tk.W)
        self.sequence_text = tk.Text(results_frame, height=4, width=34, font=('Courier New', 9, 'bold'), bd=0, relief='flat', bg='#a7a36c', fg='#111111', insertbackground='#111111')
        self.sequence_text.pack(fill=tk.X, expand=False, pady=(0, 8))

        ttk.Label(results_frame, text="COMPUTATION:").pack(anchor=tk.W, pady=(6, 0))
        self.computation_text = tk.Text(results_frame, height=6, width=34, font=('Courier New', 9, 'bold'), bd=0, relief='flat', bg='#a7a36c', fg='#111111', insertbackground='#111111')
        self.computation_text.pack(fill=tk.X, expand=False)
        
        # Right panel - Visualization
        right_frame = ttk.Frame(main_frame, style='TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Disk Head Movement Visualization", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        self.canvas_frame = tk.Frame(right_frame, bg='#f1ef8f')
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

            computation_lines = ["Computing for the total head movement:"]
            running_total = 0
            for previous, current in zip(sequence, sequence[1:]):
                movement = abs(current - previous)
                running_total += movement
                computation_lines.append(f"from {previous} to {current} = {max(previous, current)} - {min(previous, current)} = {movement}")
            computation_lines.append(f"Total head movement = {running_total} tracks")

            self.computation_text.config(state=tk.NORMAL)
            self.computation_text.delete(1.0, tk.END)
            self.computation_text.insert(1.0, "\n".join(computation_lines))
            self.computation_text.config(state=tk.DISABLED)
            
            # Draw visualization
            self.draw_visualization(sequence, disk_size, head_pos)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_simulation(self):
        """Reset inputs, outputs, and plot to the initial state"""
        self.algorithm_var.set("FCFS")

        self.requests_entry.delete(0, tk.END)
        self.requests_entry.insert(0, self.default_requests)

        self.head_entry.delete(0, tk.END)
        self.head_entry.insert(0, self.default_head)

        self.disk_size_entry.delete(0, tk.END)
        self.disk_size_entry.insert(0, self.default_disk_size)

        self.seek_time_label.config(text="N/A")

        self.sequence_text.config(state=tk.NORMAL)
        self.sequence_text.delete(1.0, tk.END)
        self.sequence_text.config(state=tk.DISABLED)

        self.computation_text.config(state=tk.NORMAL)
        self.computation_text.delete(1.0, tk.END)
        self.computation_text.config(state=tk.DISABLED)

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
    
    def draw_visualization(self, sequence: List[int], disk_size: int, head_pos: int):
        """Draw the disk head movement visualization"""
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Create figure with a top cylinder scale and a downward head path
        fig = Figure(figsize=(12, 8), dpi=100, facecolor='#f1ef8f')
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f1ef8f')
        
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
            
            # Show C-SCAN wrap as a dashed jump so it does not look like C-LOOK
            is_wrap_jump = self.algorithm_var.get() == "C-SCAN" and x2 < x1
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=2, color='navy', alpha=0.7,
                                       linestyle='--' if is_wrap_jump else '-'))
        
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
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.0, 1.20), fontsize=9, frameon=False)
        
        # Add grid for reference
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        fig.tight_layout(rect=[0, 0, 1, 0.93])
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulerGUI(root)
    root.mainloop()
