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
    'spacing_x': 350,                
    'value_offset_y': 40             # FIX: Vertical gap pushing metrics directly UNDER names
}

# =====================================================================
# 2. SIMULATION CANVAS TRACK (Middle Section Group)
# =====================================================================
SIMULATION_PANE = {
    'y_start_coordinate': 900,       
    'process_block_height': 80,      
    'left_margin': 100,              
    'right_margin': 100,             
    'timestamp_offset_y': 20,        
}

# =====================================================================
# 3. NATIVE BUTTONS CONTROL LAYOUT (Main Page Only)
# =====================================================================
BUTTONS_LAYOUT = {
    'start_x': 30,                  
    'start_y': 1020,                 
    'spacing_x': 340,                
    
    # FIX: Exclusive main window sizing constants (Independent from child popup)
    'main_btn_padx': 40,             # Increased horizontal padding for larger layout
    'main_btn_pady': 22              # Increased vertical padding for larger layout
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