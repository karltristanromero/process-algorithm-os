# Centralized UI color codes, font choices, and asset mapping variables

# Asset paths - using relative paths for easy refactoring
BACKGROUND = "temporary_assets/background.png"  # Default fallback asset
BG_ROUND_ROBIN = "temporary_assets/background_rr.png"
BG_SJF_PREEMPTIVE = "temporary_assets/background_sjf_p.png"
BG_SJF_NON_PREEMPTIVE = "temporary_assets/background_sjf_np.png"
BG_PRIORITY_PREEMPTIVE = "temporary_assets/bg_prio_preemp.png"
BG_PRIORITY_NON_PREEMPTIVE = "temporary_assets/bg_prio_non.png"
BG_FCFS = "temporary_assets/Bg_FCFS.png"
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
    'metrics_text': '#2e1b5b',
    'process_base': '#3f51b5'  # Base color for processes (will be varied)
}

# Font specifications
# Font specifications - Retro pixel/monospaced aesthetic
FONTS = {
    'default': ('Courier', 11, 'bold'),
    'heading': ('Courier', 16, 'bold'),
    'small': ('Courier', 9, 'bold'),
    'metric': ('Courier', 20, 'bold')
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