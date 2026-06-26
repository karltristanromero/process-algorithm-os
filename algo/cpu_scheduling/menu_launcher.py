import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from tkinter import messagebox
from utils.cpu_sched_theme import BG_CPU_SCHED, COLORS, FONTS
from utils.cpu_sched_config import MENU_LAYOUT

class LauncherMenu:
    """Main menu system routing calls to individual execution simulator modules."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CPU Scheduler Simulator - Main Menu")
        
        # True, borderless immersive full screen tracking matching core panels
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.destroy())

        self.canvas = None
        self.bg_image = None

    def setup_menu_window(self):
        """Build the master canvas workspace and plot the 3x2 center layout grid."""
        self.bg_image = tk.PhotoImage(file=BG_CPU_SCHED)
        
        # Instantiate master canvas mapping layer
        self.canvas = tk.Canvas(self.root, bg=COLORS['background'], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Plot Layer 0: Full window background graphic matching dashboard specs
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Unified styling matching native `#ffe6ad` layout requirements
        button_properties = {
            'font': FONTS['heading'],      # Large bold typography wrapper
            'bg': '#ffe6ad',
            'fg': '#000000',
            'relief': tk.SOLID,
            'bd': 1,
            'padx': MENU_LAYOUT['menu_btn_padx'],
            'pady': MENU_LAYOUT['menu_btn_pady'],
            'activebackground': '#ebd29b',
            'activeforeground': '#000000',
            'width': 28                    # Enforces uniform button width bounds
        }

        # Definition layout list mapping display strings to destination callback methods
        menu_items = [
            # Row 0
            ("First Come First Served", 0, MENU_LAYOUT['col0_x'], self.launch_fcfs),
            ("SJF Non-Preemptive", 0, MENU_LAYOUT['col1_x'], self.launch_sjf_np),
            
            # Row 1
            ("SJF Preemptive", 1, MENU_LAYOUT['col0_x'], self.launch_sjf_p),
            ("Round Robin", 1, MENU_LAYOUT['col1_x'], self.launch_round_robin),
            
            # Row 2
            ("Priority Non-Preemptive", 2, MENU_LAYOUT['col0_x'], self.launch_priority_np),
            ("Priority Preemptive", 2, MENU_LAYOUT['col1_x'], self.launch_priority_p)
        ]

        # Process the configuration arrays and blit items to the canvas layer
        for label, row_idx, col_x, callback in menu_items:
            # Map vertical spacing coordinates down the window structure
            target_y = MENU_LAYOUT['start_y'] + (row_idx * MENU_LAYOUT['row_gap_y'])
            
            btn = tk.Button(self.root, text=label, command=callback, **button_properties)
            
            # Embed window instance onto canvas tracking workspace
            self.canvas.create_window(col_x, target_y, window=btn, anchor=tk.CENTER)

        # FIX: Changed command from self.root.destroy to self.return_to_suite
        self.back_btn = tk.Button(
            self.root, text="Back", command=self.return_to_suite, **button_properties
        )
        
        # Pull layout coordinates dynamically from the configuration dictionary
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
        self.root.destroy()
        from FCFS import FCFS
        app = FCFS(
            title="First Come First Serve Scheduler",
            width=1920,
            height=1080
        )

        app.setup_main_window()
        app.run()

    def launch_priority_np(self):
        self.root.destroy()
        from priority_non_preemptive import PriorityNonPreemptive
        app = PriorityNonPreemptive(
            title="Priority Non-Preemptive Scheduler",
            width=1920,
            height=1080
        )

        app.setup_main_window()
        app.run()

    def launch_priority_p(self):
        self.root.destroy()
        from priority_preemptive import PriorityPreemptive
        app = PriorityPreemptive(
            title="Priority Preemptive Scheduler",
            width=1920,
            height=1080
        )

        app.setup_main_window()
        app.run()

    # =====================================================================
    # BACK NAVIGATION ROUTE TO ROOT LAYER
    # =====================================================================
    def return_to_suite(self):
        """Dismantle CPU menu and safely revert context to the main entry point."""
        self.root.destroy()
        
        # Explicitly shift working directory back to root so main.py finds its assets
        os.chdir(project_root)
        
        # Load and run your master integrated main framework
        from main import IntegratedSuiteMenu
        suite = IntegratedSuiteMenu()
        suite.setup_suite_window()
        suite.run()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    menu = LauncherMenu()
    menu.setup_menu_window()
    menu.run()