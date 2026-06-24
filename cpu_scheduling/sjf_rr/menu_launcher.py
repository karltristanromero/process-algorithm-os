"""
Central launcher system window managing the dashboard main menu panel.
Maintains full operational links to separate scheduler modules.
"""

import tkinter as tk
from tkinter import messagebox

# Configurable assets and positioning dimensions
from temporary_utils.theme import BACKGROUND, COLORS, FONTS
from temporary_utils.layout_config import MENU_LAYOUT


class LauncherMenu:
    """Main menu system routing calls to individual execution simulator modules."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CPU Scheduler Simulator - Main Menu")
        
        # Borderless fullscreen setup
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.destroy())

        self.canvas = None
        self.bg_image = None

    def setup_menu_window(self):
        """Build the master canvas workspace and plot the 3x2 center layout grid."""
        self.bg_image = tk.PhotoImage(file=BACKGROUND)
        
        self.canvas = tk.Canvas(self.root, bg=COLORS['background'], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Layer 0: Full window background graphic
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Unified styling constraints
        button_properties = {
            'font': FONTS['heading'],      
            'bg': '#ffe6ad',
            'fg': '#000000',
            'relief': tk.SOLID,
            'bd': 1,
            'padx': MENU_LAYOUT['menu_btn_padx'],
            'pady': MENU_LAYOUT['menu_btn_pady'],
            'activebackground': '#ebd29b',
            'activeforeground': '#000000',
            'width': 28                    
        }

        # Definition matrix mapping text labels, row indices, target columns, and function targets
        menu_items = [
            ("First Come First Served", 0, MENU_LAYOUT['col0_x'], self.launch_fcfs),
            ("SJF Non-Preemptive", 0, MENU_LAYOUT['col1_x'], self.launch_sjf_np),
            
            ("SJF Preemptive", 1, MENU_LAYOUT['col0_x'], self.launch_sjf_p),
            ("Round Robin", 1, MENU_LAYOUT['col1_x'], self.launch_round_robin),
            
            ("Priority Non-Preemptive", 2, MENU_LAYOUT['col0_x'], self.launch_priority_np),
            ("Priority Preemptive", 2, MENU_LAYOUT['col1_x'], self.launch_priority_p)
        ]

        for label, row_idx, col_x, callback in menu_items:
            target_y = MENU_LAYOUT['start_y'] + (row_idx * MENU_LAYOUT['row_gap_y'])
            btn = tk.Button(self.root, text=label, command=callback, **button_properties)
            self.canvas.create_window(col_x, target_y, window=btn, anchor=tk.CENTER)

        # Back Button utilizing unified layout specs
        self.back_btn = tk.Button(
            self.root, text="Back", command=self.root.destroy, **button_properties
        )
        self.canvas.create_window(
            MENU_LAYOUT['back_btn_x'], 
            MENU_LAYOUT['back_btn_y'], 
            window=self.back_btn, 
            anchor=tk.SE
        )

    # =====================================================================
    # LIVE ACTIVE ROUTING INTERRUPTS
    # =====================================================================
    def launch_sjf_np(self):
        """Clean handoff route to the SJF Non-Preemptive scheduler module."""
        self.root.destroy()  # Close menu loop
        from sjf_non_preemptive import SJFNonPreemptive
        app = SJFNonPreemptive("SJF Non-Preemptive Scheduler", 1920, 1080)
        app.setup_main_window()
        app.run()

    def launch_sjf_p(self):
        """Clean handoff route to the SJF Preemptive scheduler module."""
        self.root.destroy()  # Close menu loop
        from sjf_preemptive import SJFPreemptive
        app = SJFPreemptive("SJF Preemptive Scheduler", 1920, 1080)
        app.setup_main_window()
        app.run()

    def launch_round_robin(self):
        """Clean handoff route to the Round Robin scheduler module."""
        self.root.destroy()  # Close menu loop
        from round_robin import RoundRobin
        app = RoundRobin("Round Robin Scheduler", 1920, 1080)
        app.setup_main_window()
        app.run()

    # =====================================================================
    # PLACEHOLDER INTERRUPTS (For the other files in your skeleton branch)
    # =====================================================================
    def launch_fcfs(self):
        messagebox.showinfo("Placeholder Link", "FCFS module file has not been implemented yet.")

    def launch_priority_np(self):
        messagebox.showinfo("Placeholder Link", "Priority Non-Preemptive module file has not been implemented yet.")

    def launch_priority_p(self):
        messagebox.showinfo("Placeholder Link", "Priority Preemptive module file has not been implemented yet.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    menu = LauncherMenu()
    menu.setup_menu_window()
    menu.run()