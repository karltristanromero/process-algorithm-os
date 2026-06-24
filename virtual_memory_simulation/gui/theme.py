'''
Shared theme constant: colors, fonts, and sizing.
All GUI files import from here to stay consistent.
'''

# ── Window ─────────────────────────────────────────────────────────────────────
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 810

# ── Colors ─────────────────────────────────────────────────────────────────────
COLOR_TITLE       = "#2D2466"   # dark purple — titles and headings
COLOR_BTN_BG      = "#F5E6C8"   # beige — button background
COLOR_BTN_BORDER  = "#C8A96E"   # warm tan — button border
COLOR_BTN_TEXT    = "#2D2466"   # dark purple — button label
COLOR_BTN_HOVER   = "#EDD9A3"   # slightly darker beige on hover
COLOR_PANEL_BG    = "#FFFFFF"   # white panel background
COLOR_FAULT       = "#C0392B"   # red — page fault marker
COLOR_HIT         = "#27AE60"   # green — page hit marker
COLOR_TABLE_HEADER= "#2D2466"   # dark purple — table column headers
COLOR_TABLE_ALT   = "#F9F3E8"   # very light beige — alternating row
COLOR_STATS_BG    = "#F0EAF8"   # light lavender — stats bar background
COLOR_BEST        = "#F0F9E8"   # light green — highlight best in comparison

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_TITLE_LARGE  = None
FONT_TITLE_SMALL  = None
FONT_BTN          = None
FONT_BODY         = None
FONT_BODY_BOLD    = None
FONT_TABLE        = None
FONT_TABLE_HEADER = None

def load_fonts():
    """Load custom fonts. Call once after the Tk root is created."""
    global FONT_TITLE_LARGE, FONT_TITLE_SMALL
    global FONT_BTN, FONT_BODY, FONT_BODY_BOLD
    global FONT_TABLE, FONT_TABLE_HEADER
 
    import os
    from tkinter import font as tkfont
 
    base = os.path.dirname(os.path.abspath(__file__))

    # Register Press Start 2P if available
    ps2p_path = os.path.join(base, "NTBrickSans.ttf")
    if os.path.exists(ps2p_path):
        try:
            from ctypes import windll
            windll.gdi32.AddFontResourceExW(ps2p_path, 0x10, 0)
            pixel_font = "NT BRick Sans"
        except Exception:
            pixel_font = "Courier"
    else:
        pixel_font = "Courier"