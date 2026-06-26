"""
Centralized structural layout configuration for absolute positioning 
on the master canvas window layer.
"""

# =====================================================================
# 1. LIVE METRICS AREA COORDINATES (Top Section Group)
# =====================================================================
METRICS_LAYOUT = {
    'start_x': 380,                  
    'start_y': 720,                   
    'spacing_x': 340,                
    'value_offset_y': 40             # FIX: Vertical gap pushing metrics directly UNDER names
}

# =====================================================================
# 2. SIMULATION CANVAS TRACK (Middle Section Group)
# =====================================================================
SIMULATION_PANE = {
    'y_start_coordinate': 350,       
    'process_block_height': 80,      
    'left_margin': 120,              
    'right_margin': 100,             
    'timestamp_offset_y': 20,        
}

# =====================================================================
# 3. NATIVE BUTTONS CONTROL LAYOUT (Main Page Only)
# =====================================================================
BUTTONS_LAYOUT = {
    'start_x': 30,                  # Horizontal starting point for the button row
    'start_y': 1025,                 # Absolute vertical coordinate at the bottom
    
    'button_gap': 15,               # FIX: The exact small space (in pixels) between buttons
    
    # MANUAL SIZE ADJUSTMENTS: Increase these to make buttons larger
    'main_btn_padx': 60,             
    'main_btn_pady': 22,          
}

# =====================================================================
# 4. ADD PROCESS WINDOW LAYOUT (1280x720 Popup Scoped)
# =====================================================================
ADD_PROCESS_LAYOUT = {
    'frame_padding': 20,
    'entry_field_width': 20,         
    'table_row_height': 12,          
    'col_pid_width': 100,
    'col_arrival_width': 150,
    'col_burst_width': 150
}

MENU_LAYOUT = {
    'col0_x': 610, # Absolute X coordinate for the left column
    'col1_x': 1335, # Absolute X coordinate for the right column
    'start_y': 443, # Absolute Y coordinate for the top row
    'row_gap_y': 140, # Vertical pixel distance between successive rows

    'menu_btn_padx': 48, # Horizontal interior element text clearance
    'menu_btn_pady': 15, # Vertical interior element text clearance

    'back_btn_x': 1290,              
    'back_btn_y': 897    
}