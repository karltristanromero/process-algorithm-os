# gui_config.py
"""
Dedicated layout configuration file for the Memory Management Simulator.
Manually adjust component coordinates, dimensions, and styling properties here.
"""

from memory_management_main import Theme

# =========================================================
# 1. STATISTICS DASHBOARD CARDS (Right side trackers)
# =========================================================
STATS_LAYOUT = {
    "right_edge_offset": 120,  # Pixels away from the right screen boundary
    "total_space_y": 160,
    "external_frag_y": 365,
    "internal_frag_y": 570,
    "font": ("Courier", 32, "bold")
}

# =========================================================
# 2. INTERACTIVE ENTRY TEXT FIELDS & MANUAL CONTROLS
# =========================================================
INPUTS_LAYOUT = {
    "right_edge_offset": 40,
    "pid_y_offset": -250,        # Relative to screen height bottom edge
    "size_y_offset": -195,       # Relative to screen height bottom edge
    "alloc_btn_y_offset": -145,  # Relative to screen height bottom edge
    "dealloc_btn_y_offset": -105, # Relative to screen height bottom edge
    "entry_width": 8,
    "button_width": 60,
    "button_height": 35,
    "font_entry": ("Arial", 11, "bold"),
    "font_button": ("Arial", 9, "bold")
}

# =========================================================
# 3. BOTTOM MENU NAVIGATION BAR
# =========================================================
BOTTOM_MENU_LAYOUT = {
    "y_offset_from_bottom": 20,  # Added to the bottom edge boundary calculation
    "menu_label_x": 98,
    "mode_label_x": 150,
    "combo_mode_x": 210,
    "algo_label_x": 320,
    "combo_algo_x": 370,
    "btn_start_x": 600,
    "btn_reset_x": 710,
    "btn_compaction_offset_right": -20, # Distance from right edge
    "status_label_y_offset": 70,        # Distance added below the bottom edge row
    "row_height": 50,
    "combo_mode_width": 100,
    "combo_algo_width": 210,
    "action_btn_width": 90,
    "compaction_btn_width": 210
}

# =========================================================
# 4. EVENT LOG STREAM INTERFACE
# =========================================================
EVENT_LOG_LAYOUT = {
    "right_edge_offset": -240,
    "y_offset_from_bottom": -180,
    "text_widget_width": 35,
    "text_widget_height": 10,
    "font": ("Courier", 8)
}

# =========================================================
# 5. CORE SIMULATION PANE (RAM Core Stack Columns)
# =========================================================
SIMULATION_PANE_LAYOUT = {
    "queue_title_x": 640,
    "queue_title_y": 100,
    "queue_list_start_y": 150,
    "queue_list_spacing_y": 35,
    
    "ram_column_start_y": 100,
    "ram_column_x1": 320,        # Left coordinate border edge of RAM stack
    "ram_column_x2": 560,        # Right coordinate border edge of RAM stack
    "ram_vertical_scale": 10.0,  # Multiplier converting memory K units to pixel heights
    
    "font_title": ("Courier", 22, "bold"),
    "font_waiting_proc": ("Courier", 16, "bold"),
    "font_address_label": ("Courier", 14, "bold"),
    "font_allocated_block": ("Arial", 13, "bold"),
    "font_frag_block": ("Arial", 11, "bold")
}