"""
Reusable custom widgets used across all screens.
  - RoundedButton    : beige styled button matching the Canva design
  - FrameTraceTable  : renders the page frame trace as a scrollable grid
  - StatsBar         : shows faults, hits, and hit rate summary
"""

import tkinter as tk
from tkinter import ttk
import gui.theme as theme


class RoundedButton(tk.Button):
    '''Styled button matching the beige/dark-purple Canva design.'''