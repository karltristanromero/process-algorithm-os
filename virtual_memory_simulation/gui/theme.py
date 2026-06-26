'''
Shared theme constant: colors, fonts, and sizing.
All GUI files import from here to stay consistent.
'''

# ── Window ─────────────────────────────────────────────────────────────────────
<<<<<<< HEAD
WINDOW_WIDTH  = 1280   # fallback only — overwritten at runtime by main.py
WINDOW_HEIGHT = 720    # fallback only — overwritten at runtime by main.py
=======
WINDOW_WIDTH = 1540
WINDOW_HEIGHT = 850
>>>>>>> 2ec6bbabd0781473477be6f8cd7227741393929e

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

    # Register NT Brick Sans if available
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

    # Register TT Chocolates if available
    nunito_path = os.path.join(base, "TT-Chocolates-Trial-Regular-iF67447a8ce204c.ttf")
    if os.path.exists(nunito_path):
        try:
            from ctypes import windll
            windll.gdi32.AddFontResourceExW(nunito_path, 0x10, 0)
            nunito_font = "TT Chocolates"
        except:
            nunito_font = "Helvetica"
    else:
        nunito_font = "Helvetica"

    FONT_TITLE_LARGE  = (pixel_font,  20, "bold")
    FONT_TITLE_SMALL  = (pixel_font,  10, "bold")
    FONT_BTN          = (nunito_font, 14, "bold")
    FONT_BODY         = (nunito_font, 13)
    FONT_BODY_BOLD    = (nunito_font, 13, "bold")
    FONT_TABLE        = (nunito_font, 11)
    FONT_TABLE_HEADER = (nunito_font, 11, "bold")

# ── Button sizing ──────────────────────────────────────────────────────────────
BTN_WIDTH        = 28
BTN_PADX         = 18
BTN_PADY         = 12
BTN_RELIEF       = "flat"
BTN_BORDER_WIDTH = 2
BTN_CURSOR       = "hand2"