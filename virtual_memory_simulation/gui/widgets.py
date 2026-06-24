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

    def __init__(self, parent, text, command=None, width=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=theme.FONT_BTN,
            bg=theme.COLOR_BTN_BG,
            fg=theme.COLOR_BTN_TEXT,
            activebackground=theme.COLOR_BTN_HOVER,
            activeforeground=theme.COLOR_BTN_TEXT,
            relief=theme.BTN_RELIEF,
            bd=theme.BTN_BORDER_WIDTH,
            highlightbackground=theme.COLOR_BTN_BORDER,
            highlightthickness=2,
            cursor=theme.BTN_CURSOR,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
            width=width if width else theme.BTN_WIDTH,
            **kwargs
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)