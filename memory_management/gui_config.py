# gui_config.py
"""
Dedicated layout configuration file for the Memory Management Simulator.
Manually adjust component coordinates, dimensions, and styling properties here.
"""

# =========================================================
# GLOBAL SCREEN & CANVAS REGIONS
# =========================================================
WINDOW_SETUP = {
    "base_width": 1920,
    "base_height": 1080,
    "bottom_control_panel_height": 120,  # Offset subtracting workspace area from window height
}

# =========================================================
# 1. STATISTICS DASHBOARD CARDS (Right side trackers)
# =========================================================
STATS_LAYOUT = {
    "right_edge_offset": 300,  # Center X position for the text readouts
    "total_space_y": 200,
    "external_frag_y": 380,
    "internal_frag_y": 560,
    "font": ("Courier", 32, "bold")
}

# =========================================================
# 2. INTERACTIVE ENTRY TEXT FIELDS & MANUAL CONTROLS
# =========================================================
INPUTS_LAYOUT = {
    "right_edge_offset": 450,        # Base X anchor position for input entries
    "button_x_offset": 130,          # Added to push buttons to the right of inputs
    
    # ROW 1: Process ID Entry + ALLOCATE Button (Y matching)
    "pid_y_offset": -240,            # 960 - 240 = 720px
    "alloc_btn_y_offset": -245,      # -5px shift to align top edge nicely
    
    # ROW 2: Process Size Entry + DEALLOCATE Button (Y matching)
    "size_y_offset": -180,           # 960 - 180 = 780px
    "dealloc_btn_y_offset": -185,    # -5px shift to align top edge nicely
    
    "entry_width": 8,
    "button_width": 110,             # Widened to fit text fully
    "button_height": 35,
    "font_entry": ("Arial", 14, "bold"),
    "font_button": ("Arial", 10, "bold")
}

# =========================================================
# 3. BOTTOM MENU NAVIGATION BAR
# =========================================================
BOTTOM_MENU_LAYOUT = {
    "y_offset_from_bottom": 960,     # Explicit target bottom menu row Y anchor
    "menu_label_x": 100,
    "mode_label_x": 260,
    "combo_mode_x": 330,
    "algo_label_x": 480,
    "combo_algo_x": 540,
    "btn_start_x": 790,
    "btn_reset_x": 920,
    "btn_compaction_x": 1050,
    
    "row_height": 45,
    "combo_mode_width": 120,
    "combo_algo_width": 220,
    "action_btn_width": 110,
    "compaction_btn_width": 140
}

# =========================================================
# 4. EVENT LOG STREAM INTERFACE
# =========================================================
EVENT_LOG_LAYOUT = {
    "text_x": 100,
    "text_y": 765,
    "label_x": 100,
    "label_y": 730,
    "text_width": 72,
    "text_height": 8,
    "font": ("Courier", 10, "bold")
}

# =========================================================
# 5. CORE SIMULATION PANE (RAM Core Stack Columns)
# =========================================================
SIMULATION_PANE_LAYOUT = {
    "queue_title_x": 500,
    "queue_title_y": 100,
    "queue_list_start_y": 150,
    "queue_list_spacing_y": 30,
    
    "ram_column_start_y": 100,
    "ram_column_x1": 150,         # Left border coordinate of RAM block
    "ram_column_x2": 400,         # Right border coordinate of RAM block
    "ram_vertical_scale": 8.5,    # Balanced vertical multiplier for 1080p viewport
    
    "font_title": ("Courier", 22, "bold"),
    "font_address_label": ("Courier", 14, "bold"),
    "font_allocated_block": ("Arial", 13, "bold"),
    "font_frag_block": ("Arial", 11, "bold")
}