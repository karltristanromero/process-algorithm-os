# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import random

# Import core structural classes for memory management
from utils.process_generator import process_pool, process_user_choice

from mft.fixed_partition import FixedMemoryManager
from mft.first_fit import first_fit_mft
from mft.best_fit import best_fit_mft
from mft.best_available_fit import best_available_fit_mft

from mvt.variable_partition import VariableMemoryManager
from mvt.first_fit import first_fit_mvt
from mvt.best_fit import best_fit_mvt
from mvt.worst_fit import worst_fit_mvt

# Part 2: Main Application Architecture and Layout Structure
class MemoryManagementApp:
    def __init__(self, window_root):
        self.window_root = window_root
        self.window_root.title("Memory Management Simulator - MFT & MVT")
        
        # Set window size
        self.window_root.geometry("1920x1080")
        
        # Initialize core memory engines
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        
        # Track waiting processes that cannot currently fit into active vlocks
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        # Build the layout grids
        self.build_gui_layout()
        
        # Initial draw of both workspace components to calculate starting free spaces
        self.update_mft_display_map()
        self.update_mvt_display_map()

    def build_gui_layout(self):
       # Crate a central notebook layout element spanning the whole viewport
        self.notebook = ttk.Notebook(self.window_root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.mft_tab = ttk.Frame(self.notebook)
        self.mvt_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.mft_tab, text="   MFT (Fixed Partitioning Mode)   ")
        self.notebook.add(self.mvt_tab, text="   MVT (Variable Partitioning Mode)   ")

        # 1. MFT INTERFACE GRID PANEL DESIGN
        # Real-time Stats Header bar for MFT (Shows free space all the time)
        # Split Bottom Layout into Control (Left) and Maps (Right)
        # Manual input entry panels for MFT
        # Automated random panels for MFT
        # Text Console Output log panel for MFT
        # Right Graphical Canvas Mapping for MFT
        
        # 2. MVT INTERFACE GRID PANEL DESIGN
        # Real-time Stats Header bar for MVT (Shows free space all the time)
        # Split Bottom Layout into Control (Left) and Maps (Right)
        # Manual input entry panels for MVT
        # Automated random panels for MVT + compaction trigger
        # Text Console Output log panel for MVT
        # Right Graphical Canvas Mapping for MVT
        
# Part 3: Operational Controllers and Memory Routing Rules
    # Method execute_mft_action(mode, action):
        # 1. Query process context properties from router based on mode
        # 2. Direct process size to selected fit strategy (First Fit, Best Fit, Best Available Fit)
        # 3. If allocation fails, drop the process into the MFT waiting queue
        # 4. If action is deallocate, free the partition block and retry waiting queue list
        # 5. Refresh MFT canvas

    # Method execute_mvt_action(mode, action):
        # 1. Query process context from router based on mode
        # 2. Route process payload to dynamic fit strategy (First Fit, Best Fit, Worst Fit)
        # 3. If allocation fails, drop the process into the MVT waiting queue
        # 4. If action is deallocate, invoke manager without compaction and reorder queue
        # 5. Refresh MVT canvas

    # Method trigger_mvt_compaction():
        # 1. Invoke memory compaction sequence on dynamic manager
        # 2. Cycle through MVT waiting queue to pack newly unified free holes
        # 3. Refresh MVT canvas

# Part 4: Physical Canvas Rendering Engines (Vertical Box Track)
    # Method update_mft_display_map():
        # 1. Clear MFT canvas tracking elements
        # 2. Render vertical text listings for the current Waiting Queue
        # 3. Iterate through partition arrays and stack rectangle blocks vertically (Y coordinates)
        # 4. Render process tags in occupied portions and red-hatched bars for internal fragmentation
        # 5. Update header labels to display total free space continuously

    # Method update_mvt_display_map():
        # 1. Clear MVT canvas tracking elements
        # 2. Render vertical text listings for the current Waiting Queue
        # 3. Iterate through dynamic block arrays and stack slots vertically using start_address parameters
        # 4. Render blue boxes for packed processes and green-hatched bars for empty holes
        # 5. Evaluate scattered spaces to calculate external fragmentation metrics
        # 6. Update header labels to display total free space continuously