"""
Base scheduler class.
Manages canvas layering, dynamic background scaling, and persistent UI tracking.
"""

import tkinter as tk
from typing import Optional, List, Dict, Any
from PIL import Image, ImageTk
from utils.cpu_sched_theme import BG_CPU_SCHED, COLORS, FONTS
from utils.cpu_sched_config import METRICS_LAYOUT, BUTTONS_LAYOUT

class SchedulerBase:
    # Explicit type hints to satisfy Pylance
    root: tk.Tk
    canvas: Optional[tk.Canvas]
    add_process_window: Optional[tk.Toplevel]
    processes: List[Dict[str, Any]]
    metrics_labels: Dict[str, int]
    persistent_canvas_items: List[int]
    bg_image: Optional[ImageTk.PhotoImage]

    def __init__(self, title: str, width: int, height: int):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.destroy())

        self.processes = []
        self.canvas = None
        self.add_process_window = None
        self.metrics_labels = {}
        self.persistent_canvas_items = []
        self.background_path = BG_CPU_SCHED
        self.bg_image = None

    def generate_process_color(self, index: int) -> str:
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffe66d', '#f7971e', '#ff9ff3', '#54a0ff']
        return colors[index % len(colors)]
    
    def return_to_menu(self):
        """Safely tears down child widgets and hands execution focus back to the main menu launcher."""
        if self.add_process_window and self.add_process_window.winfo_exists():
            self.add_process_window.destroy()
            self.add_process_window = None
            
        self.root.destroy()
        
        # Perform a scoped local runtime import to eliminate circular dependency crashes
        from menu_launcher import LauncherMenu
        menu = LauncherMenu()
        menu.setup_menu_window()
        menu.run()

    def setup_main_window(self):
        """Initializes canvas, scales background, and layers UI elements."""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # 1. Initialize Canvas
        self.canvas = tk.Canvas(self.root, bg=COLORS['background'], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 2. Scale and Draw Background
        try:
            raw_img = Image.open(self.background_path)
            resized_img = raw_img.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_img)
            bg_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)
            self.persistent_canvas_items.append(bg_id)
            self.canvas.tag_lower(bg_id)  # Ensure background is the bottom layer
        except Exception as e:
            print(f"Background scaling error: {e}")
        
        # 3. Setup Metrics (Visual order: WT, TAT, Throughput, CPU)
        metrics_keys = ["average_wt", "average_tat", "throughput", "cpu_utilization"]
        m_x, m_y = METRICS_LAYOUT['start_x'], METRICS_LAYOUT['start_y']
        m_space = METRICS_LAYOUT['spacing_x']
        v_offset = METRICS_LAYOUT['value_offset_y']

        for i, key in enumerate(metrics_keys):
            val_id = self.canvas.create_text(
                m_x + (i * m_space), m_y + v_offset, text="--", 
                font=FONTS['metric'], fill="#8c6f87", anchor=tk.W
            )
            self.metrics_labels[key] = val_id
            self.persistent_canvas_items.append(val_id)

        # 4. Setup Buttons
        btn_props = {
            'font': FONTS['default'], 'bg': '#ffe6ad', 'fg': '#000000',
            'relief': tk.SOLID, 'bd': 1, 'padx': 60, 'pady': 22
        }
        
        buttons = [
            tk.Button(self.root, text="Menu", command=self.return_to_menu, **btn_props),
            tk.Button(self.root, text="Start", command=self.start_simulation, **btn_props),
            tk.Button(self.root, text="Add Process", command=self.open_add_process_window, **btn_props),
            tk.Button(self.root, text="Reset", command=self.reset_simulation, **btn_props)
        ]
        
        # Position buttons dynamically, ensuring visibility
        current_x = BUTTONS_LAYOUT['start_x']
        safe_btn_y = min(BUTTONS_LAYOUT['start_y'], screen_h - 100)
        
        for btn in buttons:
            w_id = self.canvas.create_window(current_x, safe_btn_y, window=btn, anchor=tk.W)
            self.persistent_canvas_items.append(w_id)
            current_x += 250 
            
        self.root.update_idletasks()

    def update_metrics(self, avg_wt: float, avg_tat: float, throughput: float, cpu_util: float):
        """Updates metrics with the visual order: WT, TAT, Throughput, CPU."""
        if not self.canvas: return
        self.canvas.itemconfig(self.metrics_labels['average_wt'], text=f"{avg_wt:.2f}")
        self.canvas.itemconfig(self.metrics_labels['average_tat'], text=f"{avg_tat:.2f}")
        self.canvas.itemconfig(self.metrics_labels['throughput'], text=f"{throughput:.2f}")
        self.canvas.itemconfig(self.metrics_labels['cpu_utilization'], text=f"{cpu_util:.1f}%")

    def reset_metrics(self):
        if self.canvas:
            for text_id in self.metrics_labels.values():
                self.canvas.itemconfig(text_id, text="--")

    def clear_canvas(self):
        if self.canvas:
            for item in self.canvas.find_all():
                if item not in self.persistent_canvas_items:
                    self.canvas.delete(item)

    def start_simulation(self): raise NotImplementedError
    def reset_simulation(self): raise NotImplementedError
    def open_add_process_window(self): raise NotImplementedError

    def run(self):
        self.root.mainloop()