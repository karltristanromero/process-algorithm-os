# Centralized UI color codes, font choices, and window configurations

# Asset paths
BACKGROUND = "temporary_assets/background.png"

# Color scheme - High contrast for process visualization
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
    'process_base': '#3f51b5'
}

# Font specifications - Retro pixel/monospaced aesthetic
FONTS = {
    'default': ('Courier', 11, 'bold'),
    'heading': ('Courier', 16, 'bold'),
    'small': ('Courier', 9, 'bold'),
    'metric': ('Courier', 20, 'bold')
}

# Window dimensions - Added to resolve the missing Key error
WINDOW_SIZES = {
    'main': (1920, 1080),
    'add_process': (1280, 720)
}

# Process table configuration constants
PROCESS_TABLE_COLUMNS = ('PID', 'Arrival Time', 'Burst Time')