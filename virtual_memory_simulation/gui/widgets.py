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
        
        def cell(row, col, text, bg, fg=theme.COLOR_TITLE, bold=False):
            font = theme.FONT_TABLE_HEADER if bold else theme.FONT_TABLE
            tk.Label(
                self.inner, text=str(text), font=font,
                bg=bg, fg=fg, width=4, relief="solid", bd=1, anchor="center"
            ).grid(row=row, column=col, padx=1, pady=1, ipadx=4, ipady=4, sticky="nsew")

        # Step numbers
        cell(0, 0, "Step", theme.COLOR_TABLE_HEADER, "#FFFFFF", bold=True)
        for i, s in enumerate(steps, 1):
            cell(0, 1, s.step, theme.COLOR_TABLE_HEADER, "#FFFFFF", bold=True)

        # Reference string
        cell(0, 1, "Ref", theme.COLOR_BTN_BG, theme.COLOR_TITLE, bold=True)
        for i, s in enumerate(steps, 1):
            cell(1, i, s.page, theme.COLOR_BTN_BG, theme.COLOR_TITLE)

        # Frame rows
        for f in range(num_frames):
            cell(f+2, 0, f"F{f+1}", theme.COLOR_BTN_BG, theme.COLOR_TITLE, bold=True)
            for i, s in enumerate(steps, 1):
                val = s.frames[f]
                txt = str(val) if val is not None else "·"
                bg = theme.COLOR_TABLE_ALT if f % 2 == 0 else theme.COLOR_PANEL_BG
                cell(f+2, i, txt, bg)

        # Fault/Hit row
        sr = num_frames + 2
        cell(sr, 0, "F/H", theme.COLOR_PANEL_BG, theme.COLOR_TITLE, bold=True)
        for i, s in enumerate(steps, 1):
            if s.is_fault:
                cell(sr, i, "F", "#FDECEA", theme.COLOR_FAULT, bold=True)
            else:
                cell(sr, i, "H", "#EAF5EA", theme.COLOR_HIT, bold=True)


class StatsBar(tk.Frame):
    '''Horizontal summary strip showing faults, hits, and hit rate.'''