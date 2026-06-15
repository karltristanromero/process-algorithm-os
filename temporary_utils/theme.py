# Centralized UI color codes, font choices, and asset mapping variables

# Asset paths - using relative paths for easy refactoring
BACKGROUND = "temporary_assets/background.png"
BUTTON_MAIN = "temporary_assets/button_main.png"
STATIC_TEXT = "temporary_assets/static_text.png"

# Color scheme - high contrast colors for process visualization
COLORS = {
    'background': '#2b2b2b',
    'canvas': '#1e1e1e',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'accent': '#007acc',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'process_base': '#3f51b5'  # Base color for processes (will be varied)
}

# Font specifications
FONTS = {
    'default': ('Helvetica', 10),
    'heading': ('Helvetica', 14, 'bold'),
    'small': ('Helvetica', 8),
    'metric': ('Helvetica', 12, 'bold')
}

# Window dimensions
WINDOW_SIZES = {
    'main': (1920, 1080),
    'add_process': (1280, 720)
}

# Process table configuration
PROCESS_TABLE_COLUMNS = ('PID', 'Arrival Time', 'Burst Time')
PROCESS_TABLE_HEADINGS = {
    'PID': 'Process ID',
    'Arrival Time': 'Arrival Time',
    'Burst Time': 'Burst Time'
}