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

    def _on_enter(self, _):
        self.config(bg=theme.COLOR_BTN_HOVER)

    def _on_leave(self, _):
        self.config(bg=theme.COLOR_BTN_BG)


class FrameTraceTable(tk.Frame):
    '''
    Scrollable frame trace table.
    Columns = reference steps, rows = frames + status row
    '''

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=theme.COLOR_PANEL_BG, **kwargs)
        self._build_scroll_container()

    def _build_scroll_container(self):
        self.h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            self, bg=theme.COLOR_PANEL_BG,
            highlightthickness=0,
            xscrollcommand=self.h_scroll.set
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.h_scroll.config(command=self.canvas.xview)

        self.inner = tk.Frame(self.canvas, bg=theme.COLOR_PANEL_BG)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))

    def render(self, steps, num_frames: int):
        for widget in self.inner.winfo_children():
            widget.destroy()
        if not steps:
            return