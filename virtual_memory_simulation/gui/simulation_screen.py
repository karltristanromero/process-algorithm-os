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

        # ── White panel ───────────────────────────────────────────
        panel = tk.Frame(self, bg=theme.COLOR_PANEL_BG)
        panel.place(relx=0.5, rely=0.56, anchor="center", relwidth=0.78, relheight=0.76)

        # ── Split: left input | right results ─────────────────────
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=3)
        panel.rowconfigure(0, weight=1)

        # Divider line between left and right
        tk.Frame(panel, bg=theme.COLOR_BTN_BORDER, width=2).grid(
            row=0, column=0, sticky="nse", padx=(0, 0)
        )

        self._build_input_panel(panel)
        self._build_results_panel(panel)

    # ── Left: Input Panel ──────────────────────────────────────────────────────
    def _build_input_panel(self, parent):
        left = tk.Frame(parent, bg=theme.COLOR_PANEL_BG, padx=20, pady=20)
        left.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            left,
            text="Reference String",
            font=theme.COLOR_PANEL_BG,
            fg=theme.COLOR_TITLE
        ).pack(anchor="w", pady=(8, 4))

        tk.Label(
            left,
            text="Enter numbers separated by spaces or commas:",
            font=theme.FONT_BODY,
            bg=theme.COLOR_PANEL_BG,
            fg=theme.COLOR_TITLE
        ).pack(anchor="w")

        self._ref_entry = tk.Entry(
            left, font=theme.FONT_BODY,
            bg="#FAFAFA", fg=theme.COLOR_TITLE,
            relief="solid", bd=1, width=24
        )
        self._ref_entry.pack(anchor="w", pady=(4, 8), ipady=5)

        RoundedButton(left, text="Randomize", width=18, command=self._randomize).pack(anchor="w", pady=(0, 16))

        tk.Frame(left, bg=theme.COLOR_BTN_BORDER, height=1).pack(fill=tk.X, pady=8)

        tk.Label(left, text=f"Number of Frames: {NUM_FRAMES} (fixed)",
                 font=theme.FONT_BODY,
                 bg=theme.COLOR_PANEL_BG,
                 fg=theme.COLOR_TITLE).pack(anchor="w", pady=(0, 16))
        
        tk.Frame(left, bg=theme.COLOR_BTN_BORDER, height=1).pack(fill=tk.X, pady=8)

        RoundedButton(
            left,
            text="Simulate",
            width=18,
            command=self._simulate
        ).pack(anchor="w", pady=(8, 6))

        RoundedButton(
            left,
            text="Reset",
            width=18,
            command=self._reset
        ).pack(anchor="w", pady=6)

        RoundedButton(
            left,
            text="Back",
            width=18,
            command=self.on_back
        ).pack(anchor="w", pady=6)

    # ── Right: Results Panel ───────────────────────────────────────────────────
    def _build_results_panel(self, parent):
        right = tk.Frame(parent, bg=theme.COLOR_PANEL_BG, padx=16, pady=20)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        tk.Label(
            right,
            text="Frame Trace",
            bg=theme.COLOR_PANEL_BG,
            fg=theme.COLOR_TITLE
        ).grid(row=0, column=0, sticky="w", pady=(8, 6))

        tk.Label(
            right,
            text="Legend:  F = Page Fault  |  H = Page Hit  |  · = Empty frame",
            font=theme.FONT_TABLE,
            bg=theme.COLOR_PANEL_BG,
            fg="#888888"
        ).grid(row=0, column=0, sticky="e", pady=(8, 6))

        self._trace_table = FrameTraceTable(right)
        self._trace_table.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        self._stats_bar = StatsBar(right)
        self._stats_bar.grid(row=2, column=0, sticky="ew")

    # ── Actions ────────────────────────────────────────────────────────────────
    def _parse_input(self):
        raw = self._ref_entry.get().strip()
        if not raw:
            messagebox.showwarning("Empty input!", "Please enter a reference string. ")
            return None
        try:
            pages = [int(x) for x in raw.replace("," or " ").split() if x]
            if len(pages) < 2:
                messagebox.showwarning("Too short!", "Please enter at least 2 page numbers.")
                return None
            return pages
        except ValueError:
            messagebox.showerror("Invalid input!", "Please enter integers only.")
            return None
        
    def _randomize(self):
        pages = [random.randint(0, 9) for _ in range(15)]
        self._ref_entry.delete(0, tk.END)
        self._ref_entry.insert(0, " ".join(map(str, pages)))

    def _simulate(self):
        ref = self._parse_input()
        if ref is None:
            return
        algo = self._algo_class(NUM_FRAMES)
        steps = algo.simulate(ref)
        self._trace_table.render(steps, NUM_FRAMES)
        self._stats_bar.update_stats(algo.fault_count, algo.hit_count, algo.hit_rate)

    def reset(self):
        self._ref_entry.delete(0, tk.END)
        self._trace_table.render([], NUM_FRAMES)
        self._stats_bar.reset()

    
# ─────────────────────────────────────────────
#  Compare All Simulation Screen
# ─────────────────────────────────────────────
class CompareAllScreen(tk.Frame):
    '''
    Runs all 6 algorithms on the same reference string.
    Use ttk.Notebook for tabbed individual traces + summary table at bottom.
    '''

    def __init__(self, parent, on_back):
        super().__init__(parent)
        self.on_back = on_back
        self._bg_image = None
        self._build()

    def _build(self):
        # ── Background ────────────────────────────────────────────
        bg_path = os.path.join(os.path.dirname(__file__), "SIMULATION_BG.png")
        if os.path.exists(bg_path):
            img = Image.open(bg_path).resize(
                (theme.WINDOW_WIDTH, theme.WINDOW_HEIGHT), Image.LANZCOS)
            self._bg_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self._bg_image).place(x=0, y=0, relwidth=1, relheight=1)

        # ── Title ─────────────────────────────────────────────────
        tk.Label(
            self,
            text="Compare All",
            font=theme.FONT_TITLE_LARGE,
            bg="#F5C842",
            fg=theme.COLOR_TITLE
        ).place(relx=0.5, rely=0.09, anchor="center")

        # ── White panel ───────────────────────────────────────────
        panel = tk.Frame(self, bg=theme.COLOR_PANEL_BG)
        panel.place(relx=0.5, rely=0.56, anchor="center", relwidth=0.78, relheight=0.76)
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        self._build_input_strip(panel)
        self._build_notebook(panel)
        self._build_summary(panel)

        # ── Input strip (top bar) ──────────────────────────────────────────────────
        def _build_input_strip(self, parent):
            strip = tk.Frame(parent, bg=theme.COLOR_STATS_BG, pady=10, padx=16)
            strip.grid(row=0, column=0, sticky="ew")

            tk.Label(
                strip,
                text="Reference String:",
                bg=theme.COLOR_STATS_BG,
                fg=theme.COLOR_TITLE
            ).pack(side=tk.LEFT, padx=(0, 8))

            self._ref_entry = tk.Entry(
                strip,
                font=theme.FONT_BODY,
                bg="#FAFAFA",
                fg=theme.COLOR_TITLE,
                relief="solid",
                bd=1, width=30
            )
            self._ref_entry.pack(side=tk.LEFT, ipady=4, padx=(0, 10))

            RoundedButton(strip, text="Randomize", width=12,
                          command=self._randomize).pack(side=tk.LEFT, padx=4)
            
            tk.Label(
                strip,
                text=f"Frames: {NUM_FRAMES}",
                font=theme.FONT_BODY,
                bg=theme.COLOR_STATS_BG,
                fg=theme.COLOR_TITLE
            ).pack(tk.LEFT, padx=12)

            RoundedButton(strip, text="Simulate", width=10,
                          command=self._simulate).pack(side=tk.LEFT, padx=4)
            RoundedButton(strip, text="Reset", width=8,
                          command=self._reset).pack(tk.LEFT, padx=4)
            
    # ── Tabbed notebook ────────────────────────────────────────────────────────
    def _build_notebook(self, parent):
        # Style the notebook tabs to match theme
        style = ttk.Style()
        style.configure(
            "Custom.TNotebook",
            background=theme.COLOR_PANEL_BG
        )
        style.configure(
            "Custom.TNotebook.Tab",
            font=theme.FONT_BTN,
            background=theme.COLOR_BTN_BG,
            foreground=theme.COLOR_BTN_TEXT,
            padding=[12, 6]
        )
        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", theme.COLOR_BTN_HOVER)],
            foreground=[("selected", theme.COLOR_TITLE)]    
        )

        self._notebook = ttk.Notebook(parent, style="Custom.TNotebook")
        self._notebook.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)

        self._tab_traces = {}     # algo_key -> FrameTraceTable
        self._tab_stats = {}      # algo_key -> StatsBar

        for key, (name, _) in ALGO_MAP.items():
            tab = tk.Frame(self._notebook, bg=theme.COLOR_PANEL_BG)
            tab.rowconfigure(o, weight=1)
            tab.columnconfigure(0, weight=1)
            self._notebook.add(tab, text=name)

            trace = FrameTraceTable(tab)
            trace.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))

            stats = StatsBar(tab)
            stats.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))

            self._tab_traces[key] = trace
            self._tab_stats[key] = stats

    # ── Summary table ──────────────────────────────────────────────────────────
    def _build_summary(self, parent):
        summary_outer = tk.Frame(parent, bg=theme.COLOR_PANEL_BG)
        summary_outer.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 4))
        summary_outer.columnconfigure(0, weight=1)

        tk.Label(
            summary_outer,
            text="Summary",
            font=theme.FONT_TITLE_SMALL,
            bg=theme.COLOR_PANEL_BG,
            fg=theme.COLOR_TITLE
        ).grid(row=0, column=0, sticky="w", pady=(4, 2))

        self._summary_frame = tk.Frame(summary_outer, bg=theme.COLOR_PANEL_BG)
        self._summary_frame.grid(row=1, column=0, sticky="ew")

        # Back button
        RoundedButton(
            summary_outer, text="Back", width=10,
            command=self.on_back
        ).grid(row=2, column=0, sticky="e", pady=6)

        self._draw_summary_placeholder()