"""
Base scheduler class containing shared Tkinter setup and common UI elements
for the CPU scheduling simulator.
"""

import tkinter as tk
from temporary_utils.theme import COLORS, FONTS


class SchedulerBase:
    """Base class for scheduler windows with shared Tkinter configuration."""

    def __init__(self, title, width, height):
        self.root = tk.Tk()
        self.root.title(title)
        
        # Maximize the window automatically based on your system's resolution
        try:
            self.root.attributes('-zoomed', True)  # Native Linux/Fedora maximization
        except Exception:
            try:
                self.root.state('zoomed')  # Windows/macOS Fallback
            except Exception:
                # Hard fallback to physical resolution dimensions
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                self.root.geometry(f"{screen_w}x{screen_h}")

        self.root.configure(bg=COLORS['background'])

        # Common variables
        self.processes = []  # List to store process dictionaries
        self.canvas = None   
        self.metrics_labels = {}  
        self.animation_running = False  # Track animation execution state

    def setup_main_window(self):
        """Set up the main dashboard window layout."""
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Control Layout
        control_frame = tk.Frame(main_frame, bg=COLORS['background'])
        control_frame.pack(fill=tk.X, pady=(0, 20))

        # Menu Button (Placeholder - Inactive)
        self.menu_btn = tk.Button(
            control_frame, text="Menu", font=FONTS['default'],
            bg=COLORS['accent'], fg=COLORS['text_primary'],
            relief=tk.FLAT, padx=20, pady=10
        )
        self.menu_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Start Button
        self.start_btn = tk.Button(
            control_frame, text="Start", font=FONTS['default'],
            bg=COLORS['success'], fg=COLORS['text_primary'],
            relief=tk.FLAT, padx=20, pady=10,
            command=self.start_simulation  
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        # Add Process Button
        self.add_process_btn = tk.Button(
            control_frame, text="Add Process", font=FONTS['default'],
            bg=COLORS['warning'], fg=COLORS['text_primary'],
            relief=tk.FLAT, padx=20, pady=10,
            command=self.open_add_process_window  
        )
        self.add_process_btn.pack(side=tk.LEFT, padx=10)

        # Reset Button
        self.reset_btn = tk.Button(
            control_frame, text="Reset", font=FONTS['default'],
            bg=COLORS['error'], fg=COLORS['text_primary'],
            relief=tk.FLAT, padx=20, pady=10,
            command=self.reset_simulation  
        )
        self.reset_btn.pack(side=tk.LEFT, padx=10)

        # Live Metrics Block
        metrics_frame = tk.Frame(main_frame, bg=COLORS['canvas'], relief=tk.RAISED, bd=2)
        metrics_frame.pack(fill=tk.X, pady=(0, 20))

        metrics_inner = tk.Frame(metrics_frame, bg=COLORS['canvas'])
        metrics_inner.pack(fill=tk.X, padx=20, pady=10)

        metrics_config = [
            ("Average TAT:", "--"),
            ("Average WT:", "--"),
            ("CPU Utilization:", "--%"),
            ("Throughput:", "--")
        ]

        for i, (label_text, initial_value) in enumerate(metrics_config):
            label = tk.Label(
                metrics_inner, text=label_text, font=FONTS['metric'],
                bg=COLORS['canvas'], fg=COLORS['text_secondary']
            )
            label.grid(row=0, column=i*2, sticky=tk.W, padx=(0, 5))

            value_label = tk.Label(
                metrics_inner, text=initial_value, font=FONTS['metric'],
                bg=COLORS['canvas'], fg=COLORS['text_primary']
            )
            value_label.grid(row=0, column=i*2+1, sticky=tk.W, padx=(0, 20))
            self.metrics_labels[label_text.replace(":", "").replace(" ", "_").lower()] = value_label

        # Simulation Canvas Workspace
        canvas_frame = tk.Frame(main_frame, bg=COLORS['canvas'], relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS['canvas'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_add_process_window(self):
        pass

    def update_metrics(self, avg_tat=None, avg_wt=None, cpu_util=None, throughput=None):
        """Update the live metrics display configuration."""
        if avg_tat is not None:
            self.metrics_labels['average_tat'].config(text=f"{avg_tat:.2f}")
        if avg_wt is not None:
            self.metrics_labels['average_wt'].config(text=f"{avg_wt:.2f}")
        if cpu_util is not None:
            self.metrics_labels['cpu_utilization'].config(text=f"{cpu_util:.1f}%")
        if throughput is not None:
            self.metrics_labels['throughput'].config(text=f"{throughput:.2f}")

    def reset_metrics(self):
        for label in self.metrics_labels.values():
            label.config(text="--")

    def clear_canvas(self):
        if self.canvas:
            self.canvas.delete("all")

    def start_simulation(self):
        raise NotImplementedError

    def reset_simulation(self):
        raise NotImplementedError

    def open_add_process_window(self):
        raise NotImplementedError

    def run(self):
        self.root.mainloop()