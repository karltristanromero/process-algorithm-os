"""
Algorithm Select Screen — shows 6 algorithm buttons + Compare All.
Background: ALGO_MENU_BG.png
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
import gui.theme as theme
from gui.widgets import RoundedButton


class AlgorithmSelectScreen(tk.Frame):
    '''
    Screen where the user picks which page replacement algorithm to run.
    Layout: 2-column grid of 6 algorithm buttons + centered Compare All button.
    '''

    ALGORITHMS = [
        ("First In, First Out (FIFO)",      "FIFO"),
        ("LRU Approximation",               "LRU_APPROX"),
        ("Optimal",                         "OPTIMAL"),
        ("Least Frequently Used (LFU)",     "LFU"),
        ("Least Recently Used (LRU)",       "LRU"),
        ("Most Frequently Used (MFU)",      "MFU"),
    ]

    def __init__(self, parent, on_select):
        '''
        parent      : the parent Tk/Frame container
        on_select   : callback(algo_key: str) called when user picks an algorithm
                      algo_key is one of: FIFO, OPTIMAL, LRU, LRU_APPROX, LFU, MFU, COMPARE_ALL 
        '''

        super().__init__(parent)
        self.on_select = on_select
        self._bg_image = None       # keep reference to prevent GC
        self._build()

    def _build(self):
        # ── Background image ──────────────────────────────────────
        bg_path = os.path.join(os.path.dirname(__file__), "ALGO_MENU_BG.png")
        if os.path.exists(bg_path):
            img = Image.open(bg_path).resize(
                (theme.WINDOW_WIDTH, theme.WINDOW_HEIGHT), Image.LANCZOS)
            self._bg_image = ImageTk.PhotoImage(img)
            bg_label = tk.Label(self, image=self._bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)