"""
Main Entry Point - Integrated OS Simulator Suite.
Manages the top-level 2x2 grid framework overlaying assets/main_menu.png.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Updated imports pointing to your new permanent utils folder
from utils.cpu_sched_theme import COLORS, FONTS
from utils.cpu_sched_config import MAIN_MENU_LAYOUT


class IntegratedSuiteMenu:
    """Top-level controller routing execution pathways to separate sub-menu dashboards."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Operating System Simulator Suite")
        
        # Fullscreen tracking across the entire suite
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.destroy())

        self.canvas = None
        self.bg_image = None

    def setup_suite_window(self):
        """Build canvas viewport and map the 2x2 selector grid matrix."""
        self.bg_image = tk.PhotoImage(file="assets/main_menu.png")
        
        self.canvas = tk.Canvas(self.root, bg=COLORS['background'], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Layer 0: Draw structural background
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        button_properties = {
            'font': FONTS['heading'],      
            'bg': '#ffe6ad',
            'fg': '#000000',
            'relief': tk.SOLID,
            'bd': 1,
            'padx': MAIN_MENU_LAYOUT['btn_padx'],
            'pady': MAIN_MENU_LAYOUT['btn_pady'],
            'activebackground': '#ebd29b',
            'activeforeground': '#000000',
            'width': 28                    
        }

        # Centered 2x2 grid configuration layout matrix
        suite_items = [
            ("CPU Scheduling", 0, MAIN_MENU_LAYOUT['col0_x'], self.open_cpu_scheduling),
            ("Memory Management", 0, MAIN_MENU_LAYOUT['col1_x'], self.open_memory_management),
            
            ("Virtual Memory", 1, MAIN_MENU_LAYOUT['col0_x'], self.open_virtual_memory),
            ("Disk Scheduling", 1, MAIN_MENU_LAYOUT['col1_x'], self.open_disk_scheduling)
        ]

        for label, row_idx, col_x, callback in suite_items:
            target_y = MAIN_MENU_LAYOUT['start_y'] + (row_idx * MAIN_MENU_LAYOUT['row_gap_y'])
            btn = tk.Button(self.root, text=label, command=callback, **button_properties)
            self.canvas.create_window(col_x, target_y, window=btn, anchor=tk.CENTER)

        # Master application closure route button
        self.exit_btn = tk.Button(
            self.root, text="Exit", command=self.root.destroy, **button_properties
        )
        self.canvas.create_window(
            MAIN_MENU_LAYOUT['exit_btn_x'], 
            MAIN_MENU_LAYOUT['exit_btn_y'], 
            window=self.exit_btn, 
            anchor=tk.SE
        )

    # =====================================================================
    # MULTI-PROGRAM ROUTING LINKS (Updated to look inside your algo/ folder)
    # =====================================================================
    def open_cpu_scheduling(self):
        """Dismantle suite layer and initialize the CPU Scheduling dashboard launcher."""
        self.root.destroy()
        
        # Dynamically inject the subfolder paths to the Python lookup registry 
        # so files inside the algo folder can find each other seamlessly
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'algo', 'cpu_scheduling')))
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
        
        from algo.cpu_scheduling.menu_launcher import LauncherMenu
        menu = LauncherMenu()
        menu.setup_menu_window()
        menu.run()

    def open_memory_management(self):
        """Dismantle suite layer and initialize the CPU Scheduling dashboard launcher."""
        self.root.destroy()
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'algo', 'memory_management')))
        
        # Import their exact class name
        from algo.memory_management.memory_management_main import MemoryManagementApp
        
        # 1. Provide the root window container their constructor demands
        mem_root = tk.Tk()
        
        # 2. Instantiate using their exact variable signatures
        app = MemoryManagementApp(mem_root)
        
        # 3. Dynamic Back Route Injection (Fixes their empty 'pass' logic without touching their file)
        def runtime_back_navigation():
            mem_root.destroy()
            from main import IntegratedSuiteMenu
            suite = IntegratedSuiteMenu()
            suite.setup_suite_window()
            suite.run()
            
        app.go_back_to_main_menu = runtime_back_navigation
        
        # 4. Turn control over to their application loop execution layer
        mem_root.mainloop()

    def open_virtual_memory(self):
        self.root.destroy()
        
        target_path = os.path.join(self.root_dir, 'algo', 'virtual_memory_simulation')
        sys.path.append(target_path)
        os.chdir(target_path)
        
        from algo.virtual_memory_simulation.main import App as VMApp
        app = VMApp()
        
        def return_to_suite():
            app.destroy()
            os.chdir(self.root_dir) # Safely restore root environment layout
            from main import IntegratedSuiteMenu
            suite = IntegratedSuiteMenu()
            suite.setup_suite_window()
            suite.run()

        original_show_select = app.show_algorithm_select
        
        def patched_show_algorithm_select():
            original_show_select()
            back_btn = tk.Button(
                app._current_screen, text="⬅ BACK TO SUITE", 
                font=('Courier', 12, 'bold'), bg='#ffe6ad', fg='#000000',
                relief=tk.SOLID, bd=1, padx=15, pady=8,
                activebackground='#ebd29b', command=return_to_suite
            )
            back_btn.place(x=30, y=30)

        app.show_algorithm_select = patched_show_algorithm_select
        patched_show_algorithm_select()
        app.mainloop()

    def open_disk_scheduling(self):
        """Placeholder for Disk Scheduling execution module wrapper."""
        messagebox.showinfo("Suite Route", "Disk Scheduling sub-suite module is currently unlinked.")

    def run(self):
        self.root.mainloop()

    def open_disk_scheduling(self):
        """Dismantle suite layer and initialize the CPU Scheduling dashboard launcher."""
        self.root.destroy()
        
        target_path = os.path.join(self.root_dir, 'algo', 'disk_scheduling')
        sys.path.insert(0, target_path)
        os.chdir(target_path)  # Shift execution context for assets
        
        from algo.disk_scheduling.main_gui import DiskSchedulerGUI
        
        disk_root = tk.Tk()
        app = DiskSchedulerGUI(disk_root)
        
        # Intercept their Quit button action to make it act as a "Back to Suite" transition
        def runtime_back_navigation():
            disk_root.destroy()
            os.chdir(self.root_dir)  # Reset back to global root directory
            from main import IntegratedSuiteMenu
            suite = IntegratedSuiteMenu()
            suite.setup_suite_window()
            suite.run()
            
        # Re-map the window closure and button trigger dynamically
        disk_root.protocol("WM_DELETE_WINDOW", runtime_back_navigation)
        # Note: If they named their button variable specifically, we can intercept its command here
        
        disk_root.mainloop()


if __name__ == "__main__":
    suite = IntegratedSuiteMenu()
    suite.setup_suite_window()
    suite.run()