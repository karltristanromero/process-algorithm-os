"""
Centralized structural layout configuration for absolute positioning 
on the master canvas window layer.
"""

# =====================================================================
# 1. LIVE METRICS AREA COORDINATES (Top Section Group)
# =====================================================================
METRICS_LAYOUT = {
    'start_x': 300,                  
    'start_y': 700,                   
    'spacing_x': 370,                
    'value_offset_x': 160            
}

# =====================================================================
# 2. SIMULATION CANVAS TRACK (Middle Section Group)
# =====================================================================
SIMULATION_PANE = {
    'y_start_coordinate': 400,       
    'process_block_height': 80,      
    'left_margin': 100,              
    'right_margin': 100,             
    'timestamp_offset_y': 20,        
}

# =====================================================================
# 3. NATIVE BUTTONS CONTROL LAYOUT (Bottom Section Group)
# =====================================================================
BUTTONS_LAYOUT = {
    'start_x': 30,                  # Horizontal starting point for the button row
    'start_y': 1020,                 # FIX: Absolute vertical coordinate (places them cleanly at the bottom)
    'spacing_x': 340,                
    
    # MANUAL SIZE ADJUSTMENTS: Increase these to make buttons larger
    'btn_padx': 35,                  
    'btn_pady': 15                   
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