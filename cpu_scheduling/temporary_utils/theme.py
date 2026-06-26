# Centralized UI color codes, font choices, and asset mapping variables
from pathlib import Path

# 1. This gets the 'temporary_utils' folder
UTILS_DIR = Path(__file__).resolve().parent

# 2. This climbs up one level to the main project folder (the parent)
PROJECT_ROOT = UTILS_DIR.parent

# 3. Now point directly to the sibling 'temporary_assets' folder
BACKGROUND = (PROJECT_ROOT / "temporary_assets/background.png").as_posix()
BG_ROUND_ROBIN = (PROJECT_ROOT / "temporary_assets/background_rr.png").as_posix()
BG_SJF_PREEMPTIVE = (PROJECT_ROOT / "temporary_assets/background_sjf_p.png").as_posix()
BG_SJF_NON_PREEMPTIVE = (PROJECT_ROOT / "temporary_assets/background_sjf_np.png").as_posix()
BG_PRIORITY_PREEMPTIVE = (PROJECT_ROOT / "temporary_assets/bg_prio_preemp.png").as_posix()
BG_PRIORITY_NON_PREEMPTIVE = (PROJECT_ROOT / "temporary_assets/bg_prio_non.png").as_posix()
BG_FCFS = (PROJECT_ROOT / "temporary_assets/Bg_FCFS.png").as_posix()

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