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
# Create class MemoryManagementApp
    # Initialize __init__ with root window configuration (Strict 1920x1080 geometry)
    # Instantiate FixedMemoryManager and VariableMemoryManager backends
    # Create empty list trackers for MFT and MVT waiting queues
    # Invoke build_gui_layout() to set up panels
    # Trigger initial canvas repaint updates

    # Method build_gui_layout():
        # 1. Create a ttk.Notebook tab framework spanning the window viewport
        # 2. Build MFT and MVT tab containers
        # 3. For each tab, create a Header bar showing the unallocated free space all the time
        # 4. Partition both tabs into Control Frames (Left) and Canvas Displays (Right)
        # 5. Populate left columns with Form Entry grids (PID, Size, Algorithm selectors)
        # 6. Add dynamic action trigger buttons (EXECUTE ALLOCATE, DEALLOCATE, RANDOM, COMPACTION)
        # 7. Add scrolled text widgets to serve as scrolling system logs

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