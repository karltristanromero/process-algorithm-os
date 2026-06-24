"""
Simulation Screen — handles both single algorithm and Compare All views.
 
Single algorithm layout:
  Left      : reference string input, randomize, simulate, reset, back buttons
  Right     : frame trace table + stats bar
 
Compare All layout:
  Top       : reference string input + buttons strip
  Middle    : ttk.Notebook with one tab per algorithm (frame trace + stats each)
  Bottom    : comparison summary table + back button
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import os
from PIL import Image, ImageTk

import gui.theme as theme
from gui.widgets import RoundedButton, FrameTraceTable, StatsBar

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from algorithms import FIFO, Optimal, LRU, LRUApproximation, LFU, MFU


# ── Algorithm registry ─────────────────────────────────────────────────────────
ALGO_MAP = {
    "FIFO":         ("First In, First Out (FIFO)",      FIFO),
    "OPTIMAL":      ("Optimal",                         Optimal),
    "LRU":          ("Least Recently Used (LRU)",       LRU),
    "LRU_APPROX":   ("LRU Approximation",               LRUApproximation),
    "LFU":          ("Least Frequently Used (LFU)",     LFU),
    "MFU":          ("Most Frequenly Used (MFU)",       MFU),
}

NUM_FRAMES = 4


# ─────────────────────────────────────────────
#  Single Algorithm Simulation Screen
# ─────────────────────────────────────────────
class SimulationScreen(tk.Frame):
    '''
    Simulation screen for a single page replacement algorithm.
    Split layout: input panel (left) | results panel (right).
    '''

    def __init__(self, parent, algo_key: str, on_back):
        super().__init__(parent)
        self.algo_key = algo_key
        self.on_back = on_back
        self._bg_image = None
        self._algo_name, self._algo_class = ALGO_MAP[algo_key]
        self._build()

    def _build(self):
        # ── Background ────────────────────────────────────────────
        bg_path = os.path.join(os.path.dirname(__file__), "SIMULATION_BG.png")
        if os.path.exists(bg_path):
            img = Image.open(bg_path).resize(
                (theme.WINDOW_WIDTH, theme.WINDOW_HEIGHT), Image.LANCZOS)
            self._bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self._bg_image).place(
                x=0, y=0, relwidth=1, relheight=1)
            
        # ── Algorithm title (above panel, over BG) ────────────────
        tk.Label(
            self,
            text=self._algo_name.upper(),
            font=theme.FONT_TITLE_LARGE,
            bg="#F5C842",
            fg=theme.COLOR_TITLE
        ).place(relx=0.5, rely=0.09, anchor="center")