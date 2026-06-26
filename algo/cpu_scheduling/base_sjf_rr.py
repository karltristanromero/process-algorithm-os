import tkinter as tk
from utils.cpu_sched_theme import BG_CPU_SCHED, COLORS, FONTS
from utils.cpu_sched_config import METRICS_LAYOUT, SIMULATION_PANE, BUTTONS_LAYOUT


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
        # FIX: Pull dynamically from the current instance value
        self.bg_image = tk.PhotoImage(file=self.background_path)
        
        self.canvas = tk.Canvas(self.root, bg=COLORS['background'], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Layer 0: Draw background image
        bg_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)
        self.persistent_canvas_items.append(bg_id)
               
        # =====================================================================
        # 1. LIVE METRICS LAYER (Dynamic Results Only - Labels are baked into background.png)
        # =====================================================================
        # All string literals for names have been removed. We only loop through keys
        # to map the text modification IDs directly under your background artwork.
        metrics_keys = ["average_tat", "average_wt", "cpu_utilization", "throughput"]

        m_x = METRICS_LAYOUT['start_x']
        m_y = METRICS_LAYOUT['start_y']
        m_space = METRICS_LAYOUT['spacing_x']
        v_offset_y = METRICS_LAYOUT['value_offset_y']

        for i, key_name in enumerate(metrics_keys):
            current_x = m_x + (i * m_space)
            
            # Dynamic Value Text Layer (Positioned directly over your graphic slots)
            initial_val = "--%" if key_name == "cpu_utilization" else "--"
            value_id = self.canvas.create_text(
                current_x, m_y + v_offset_y, text=initial_val, font=FONTS['metric'],
                fill="#8c6f87", anchor=tk.W
            )
            
            # Register value ID to protection arrays and backend tracking dicts
            self.metrics_labels[key_name] = value_id
            self.persistent_canvas_items.append(value_id)

        # =====================================================================
        # 2. NATIVE CONTROL BUTTONS LAYER (Dynamic Floating Flow Layout)
        # =====================================================================
        btn_y = BUTTONS_LAYOUT['start_y']
        current_x = BUTTONS_LAYOUT['start_x']   # This tracker shifts dynamically across the loop
        btn_gap = BUTTONS_LAYOUT['button_gap']

        button_properties = {
            'font': FONTS['default'],
            'bg': '#ffe6ad',
            'fg': '#000000',
            'relief': tk.SOLID,
            'bd': 1,
            'padx': BUTTONS_LAYOUT['main_btn_padx'],  
            'pady': BUTTONS_LAYOUT['main_btn_pady'],  
            'activebackground': '#ebd29b',
            'activeforeground': '#000000'
        }
        
        self.menu_btn = tk.Button(self.root, text="Menu", command=self.return_to_menu, **button_properties)
        self.start_btn = tk.Button(self.root, text="Start", command=self.start_simulation, **button_properties)
        self.add_process_btn = tk.Button(self.root, text="Add Process", command=self.open_add_process_window, **button_properties)
        self.reset_btn = tk.Button(self.root, text="Reset", command=self.reset_simulation, **button_properties)

        # FIX: Loop calculates widget widths on-the-fly to ensure uniform small spacing
        for btn in [self.menu_btn, self.start_btn, self.add_process_btn, self.reset_btn]:
            # Draw the button at the current horizontal tracker location
            w_id = self.canvas.create_window(current_x, btn_y, window=btn, anchor=tk.W)
            self.persistent_canvas_items.append(w_id)
            
            # Read the exact requested pixel width of the button and shift the tracker
            current_x += btn.winfo_reqwidth() + btn_gap

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

    def return_to_menu(self):
        self.root.destroy()
        
        # 2. Perform a scoped runtime import to completely eliminate circular import crashes
        from menu_launcher import LauncherMenu
        menu = LauncherMenu()
        menu.setup_menu_window()
        menu.run()

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