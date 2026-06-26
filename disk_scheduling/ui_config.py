# config.py
from pathlib import Path

# --- Directory & Path Configuration ---
BASE_DIR = Path(__file__).resolve().parent
# Automatically checks for buttons or utils directory
ASSETS_DIR = BASE_DIR / "buttons" if (BASE_DIR / "buttons").exists() else (
    BASE_DIR / "utils" if (BASE_DIR / "utils").exists() else BASE_DIR
)

# --- Window Configurations ---
WINDOW_TITLE = "Disk Scheduling Algorithms Simulator"
DEFAULT_REQUESTS = "98, 183, 37, 122, 14, 124, 65, 67"
DEFAULT_HEAD = "53"
DEFAULT_DISK_SIZE = "200"

# --- Grid & Layout Configurations ---
LEFT_PANEL_MIN_SIZE = 380
BOTTOM_BAR_HEIGHT = 96

# Grid arguments for dynamic toggling
INPUT_GRID_KWARGS = {"row": 0, "column": 0, "sticky": "ew", "padx": (20, 10), "pady": (15, 5)}
ALGO_GRID_KWARGS = {"row": 1, "column": 0, "sticky": "ew", "padx": (20, 10), "pady": (5, 5)}

# --- Color Palette & Styling ---
COLORS = {
    "bg_main": "#f0f0f0",
    "bg_frame": "#f5c9a1",
    "bg_retro_box": "#f1ef8f",
    "bg_entry": "#a7a36c",
    "fg_text": "#2b2235",
    "fg_dark": "#151515",
    "fg_result": "#111111",
    "border_retro": "#5c4a78",
    "btn_green_bg": "#42c400",
    "btn_action_bg": "#36c21f",
}

FONTS = {
    "label": ('Courier New', 10, 'bold'),
    "title": ('Courier New', 15, 'bold'),
    "retro_title": ('Courier New', 12, 'bold'),
    "entry": ('Courier New', 11, 'bold'),
    "text_box": ('Courier New', 9, 'bold'),
}

# --- Matplotlib Plot Styles ---
PLOT_CONFIG = {
    "face_color": '#f1ef8f',
    "line_color": 'navy',
    "start_node_color": 'green',
    "start_node_edge": 'darkgreen',
    "end_node_color": 'orange',
    "end_node_edge": 'darkorange',
    "req_node_color": 'red',
    "req_node_edge": 'darkred',
}