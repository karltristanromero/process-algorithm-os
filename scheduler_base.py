"""
Base scheduler class utilizing a unified Master Canvas system with persistent
widget tracking to prevent layout items from disappearing during canvas wipes.
"""

import tkinter as tk
from temporary_utils.theme import BACKGROUND, COLORS, FONTS
from temporary_utils.layout_config import METRICS_LAYOUT, SIMULATION_PANE, BUTTONS_LAYOUT


class SchedulerBase:
    """Base class for scheduler interfaces utilizing absolute master canvas layering."""

    def __init__(self, title, width, height):
        self.root = tk.Tk()
        self.root.title(title)
        
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.destroy())

        self.processes = []  
        self.canvas = None   
        self.metrics_labels = {}  
        self.persistent_canvas_items = []  # Protection registry list for UI items

    def setup_main_window(self):
        """Set up the master canvas view, eliminating blocking dark-gray frames entirely."""
        self.bg_image = tk.PhotoImage(file=BACKGROUND)
        
        self.canvas = tk.Canvas(self.root, bg=COLORS['background'], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Layer 0: Draw background image (ID: 1)
        bg_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)
        self.persistent_canvas_items.append(bg_id)
        
        # =====================================================================
        # 1. LIVE METRICS LAYER (Uses color token: COLORS['metrics_text'])
        # =====================================================================
        metrics_config = [
            ("AVG TAT:", "average_tat"),
            ("AVG WT:", "average_wt"),
            ("CPU Utilization:", "cpu_utilization"),
            ("Throughput:", "throughput")
        ]

        m_x = METRICS_LAYOUT['start_x']
        m_y = METRICS_LAYOUT['start_y']
        m_space = METRICS_LAYOUT['spacing_x']
        v_offset = METRICS_LAYOUT['value_offset_x']

        for i, (label_text, key_name) in enumerate(metrics_config):
            current_x = m_x + (i * m_space)
            
            lbl_id = self.canvas.create_text(
                current_x, m_y, text=label_text, font=FONTS['metric'],
                fill=COLORS['metrics_text'], anchor=tk.W
            )
            
            initial_val = "--%" if key_name == "cpu_utilization" else "--"
            value_id = self.canvas.create_text(
                current_x + v_offset, m_y, text=initial_val, font=FONTS['metric'],
                fill=COLORS['metrics_text'], anchor=tk.W
            )
            
            self.metrics_labels[key_name] = value_id
            self.persistent_canvas_items.append(lbl_id)
            self.persistent_canvas_items.append(value_id)

        # =====================================================================
        # 2. NATIVE CONTROL BUTTONS LAYER (Absolute Coordinate Positioning)
        # =====================================================================
        # FIX: Switched from relative offsets to a direct absolute pixel coordinate
        btn_y = BUTTONS_LAYOUT['start_y']
        btn_x_start = BUTTONS_LAYOUT['start_x']
        btn_space = BUTTONS_LAYOUT['spacing_x']

        button_properties = {
            'font': FONTS['default'],
            'bg': '#ffe6ad',
            'fg': '#000000',
            'relief': tk.SOLID,
            'bd': 1,
            'padx': BUTTONS_LAYOUT['btn_padx'],  
            'pady': BUTTONS_LAYOUT['btn_pady'],  
            'activebackground': '#ebd29b',
            'activeforeground': '#000000'
        }

        self.menu_btn = tk.Button(self.root, text="Menu", **button_properties)
        self.start_btn = tk.Button(self.root, text="Start", command=self.start_simulation, **button_properties)
        self.add_process_btn = tk.Button(self.root, text="Add Process", command=self.open_add_process_window, **button_properties)
        self.reset_btn = tk.Button(self.root, text="Reset", command=self.reset_simulation, **button_properties)

        # Embed buttons and preserve their canvas window container element IDs
        for idx, btn in enumerate([self.menu_btn, self.start_btn, self.add_process_btn, self.reset_btn]):
            w_id = self.canvas.create_window(btn_x_start + (idx * btn_space), btn_y, window=btn, anchor=tk.W)
            self.persistent_canvas_items.append(w_id)

    def update_metrics(self, avg_tat=None, avg_wt=None, cpu_util=None, throughput=None):
        """Update canvas text elements using item configurations."""
        if avg_tat is not None: 
            self.canvas.itemconfig(self.metrics_labels['average_tat'], text=f"{avg_tat:.2f}")
        if avg_wt is not None: 
            self.canvas.itemconfig(self.metrics_labels['average_wt'], text=f"{avg_wt:.2f}")
        if cpu_util is not None: 
            self.canvas.itemconfig(self.metrics_labels['cpu_utilization'], text=f"{cpu_util:.1f}%")
        if throughput is not None: 
            self.canvas.itemconfig(self.metrics_labels['throughput'], text=f"{throughput:.2f}")

    def reset_metrics(self):
        """Reset canvas string displays back to default markers."""
        for key, text_id in self.metrics_labels.items():
            default_text = "--%" if key == "cpu_utilization" else "--"
            self.canvas.itemconfig(text_id, text=default_text)

    def clear_canvas(self):
        """FIX: Only deletes simulation blocks. Ignores persistent menu assets, labels, and buttons."""
        if self.canvas:
            for item in self.canvas.find_all():
                if item not in self.persistent_canvas_items:
                    self.canvas.delete(item)

    def start_simulation(self): raise NotImplementedError
    def reset_simulation(self): raise NotImplementedError
    def open_add_process_window(self): raise NotImplementedError

    def run(self):
        self.root.mainloop()