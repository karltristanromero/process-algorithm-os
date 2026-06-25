import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "Backgrounds")

BACKGROUND_MAP = {
    "FCFS": os.path.join(ASSETS_DIR, "background_FCFS.png"),
    "PRIO_PREEMPT": os.path.join(ASSETS_DIR, "background_prio_pre.png"),
    "PRIO_NON_PREEMPT": os.path.join(ASSETS_DIR, "background_prio_non_pre.png")
}

UI_CONFIG = {
    'font_family': "Courier",
    'font_size': 12,
    'bg_color': "#FFFFFF",
    'text_color': "#000000",
    'button_bg': "#EEDC82"
}