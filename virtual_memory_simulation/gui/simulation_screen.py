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

import os
import random
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

import gui.theme as theme
from gui.widgets import FrameTraceTable, RoundedButton, StatsBar

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from algorithms import FIFO, LFU, MFU, LRU, LRUApproximation, Optimal

# ── Algorithm registry ─────────────────────────────────────────────────────────
ALGO_MAP = {
    "FIFO": ("First In, First Out (FIFO)", FIFO),
    "OPTIMAL": ("Optimal", Optimal),
    "LRU": ("Least Recently Used (LRU)", LRU),
    "LRU_APPROX": ("LRU Approximation", LRUApproximation),
    "LFU": ("Least Frequently Used (LFU)", LFU),
    "MFU": ("Most Frequenly Used (MFU)", MFU),
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

        # Image memory references to guard against Garbage Collection
        self.original_bg = None
        self._bg_image_tk = None

        self._algo_name, self._algo_class = ALGO_MAP[algo_key]

        # Load raw asset once
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SIMULATION_BG.png")
        if os.path.exists(bg_path):
            self.original_bg = Image.open(bg_path)

        self._build()

        # Bind configuration updates to recalculate background boundaries
        if self.original_bg:
            self.bind("<Configure>", self._resize_background)

    def _build(self):
        # ── Background ────────────────────────────────────────────
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Algorithm title (above panel, over BG) ────────────────
        tk.Label(
            self,
            text=self._algo_name.upper(),
            font=theme.FONT_TITLE_LARGE,
            bg="#FFFFFF",
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

        self._build_results_panel(panel)
        self._build_input_panel(panel)

    def _resize_background(self, event):
        '''Fires when user resizes or zooms the Simulation Window.'''
        new_width = event.width
        new_height = event.height

        if new_width > 10 and new_height > 10:
            resized_img = self.original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self._bg_image_tk = ImageTk.PhotoImage(resized_img)
            self.bg_label.config(image=self._bg_image_tk)

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
            pages = [int(x) for x in raw.replace(",", " ").split() if x]
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

    def _reset(self):
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

        self.original_bg = None
        self._bg_image_tk = None

        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SIMULATION_BG.png")
        if os.path.exists(bg_path):
            self.original_bg = Image.open(bg_path)

        self._build()

        if self.original_bg:
            self.bind("<Configure>", self._resize_background)

    def _build(self):
        # ── Background ────────────────────────────────────────────
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Title ─────────────────────────────────────────────────
        tk.Label(
            self,
            text="Compare All",
            font=theme.FONT_TITLE_LARGE,
            bg="#FFFFFF",
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

    def _resize_background(self, event):
        '''Fires when user resizes or zooms the Comparison Window.'''
        new_width = event.width
        new_height = event.height

        if new_width > 10 and new_height > 10:
            resized_img = self.original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self._bg_image_tk = ImageTk.PhotoImage(resized_img)
            self.bg_label.config(image=self._bg_image_tk)

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
        ).pack(side=tk.LEFT, padx=12)

        RoundedButton(strip, text="Simulate", width=10,
                          command=self._simulate).pack(side=tk.LEFT, padx=4)
        RoundedButton(strip, text="Reset", width=8,
                          command=self._reset).pack(side=tk.LEFT, padx=4)
            
    # ── Tabbed notebook ────────────────────────────────────────────────────────
    def _build_notebook(self, parent):
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
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1) 
            tab.rowconfigure(1, weight=0)
            self._notebook.add(tab, text=name)

            table_container = tk.Frame(tab, bg=theme.COLOR_PANEL_BG)
            table_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
            table_container.columnconfigure(0, weight=1)
            table_container.rowconfigure(0, weight=1)

            canvas = tk.Canvas(table_container, bg=theme.COLOR_PANEL_BG, bd=0, highlightthickness=0)
            scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")

            scrollable_table_frame = tk.Frame(canvas, bg=theme.COLOR_PANEL_BG)
            scrollable_table_frame.columnconfigure(0, weight=1)
            
            canvas_window = canvas.create_window((0, 0), window=scrollable_table_frame, anchor="nw")

            def _configure_scroll_region(event, c=canvas):
                c.configure(scrollregion=c.bbox("all"))

            def _configure_canvas_window(event, c=canvas, cw=canvas_window):
                c.itemconfig(cw, width=event.width)

            scrollable_table_frame.bind("<Configure>", _configure_scroll_region)
            canvas.bind("<Configure>", _configure_canvas_window)

            def _on_mousewheel(event, c=canvas):
                delta = event.delta if event.delta else (-120 if event.num == 5 else 120)
                c.yview_scroll(int(-1 * (delta / 120)), "units")

            canvas.bind_all("<MouseWheel>", lambda e, c=canvas: _on_mousewheel(e, c))
            canvas.bind_all("<Button-4>", lambda e, c=canvas: _on_mousewheel(e, c))
            canvas.bind_all("<Button-5>", lambda e, c=canvas: _on_mousewheel(e, c))

            trace = FrameTraceTable(scrollable_table_frame)
            trace.grid(row=0, column=0, sticky="nsew")

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

        RoundedButton(
            summary_outer, text="Back", width=10,
            command=self.on_back
        ).grid(row=2, column=0, sticky="e", pady=6)

        self._draw_summary_placeholder()

    def _draw_summary_placeholder(self):
        for w in self._summary_frame.winfo_children():
            w.destroy()

        headers = ["Algorithm", "Faults", "Hits", "Hit Rate"]
        for col, h in enumerate(headers):
            tk.Label(
                self._summary_frame, text=h,
                font=theme.FONT_TABLE_HEADER,
                bg=theme.COLOR_TABLE_HEADER,
                fg="#FFFFFF",
                relief="solid", bd=1,
                padx=8, pady=4, width=20 if col == 0 else 8
            ).grid(row=0, column=col, sticky="ew", padx=1)

        tk.Label(
            self._summary_frame,
            text="Run a simulation to see results here.",
            font=theme.FONT_BODY,
            bg=theme.COLOR_PANEL_BG,
            fg="#AAAAAA"
        ).grid(row=1, column=0, columnspan=4, pady=8, padx=4, sticky="w")

    def _draw_summary_results(self, results):
        '''Results: list of (name, faults, hits, rate) sorted by faults asc.'''
        for w in self._summary_frame.winfo_children():
            w.destroy()

        headers = ["Algorithm", "Faults", "Hit", "Hit Rate"]
        widths = [24, 8, 8, 10]
        for col, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(
                self._summary_frame, text=h,
                font=theme.FONT_TABLE_HEADER,
                bg=theme.COLOR_TABLE_HEADER,
                fg="#FFFFFF", relief="solid", bd=1,
                padx=8, pady=4, width=w,
            ).grid(row=0, column=col, sticky="ew", padx=1)

        best_faults = results[0][1]
        for r, (name, faults, hits, rate) in enumerate(results, 1):
            bg = theme.COLOR_BEST if faults == best_faults else (
                theme.COLOR_TABLE_ALT if r % 2 == 0 else theme.COLOR_PANEL_BG
            )
            vals = [name, faults, hits, f"{rate:.1f}%"]
            for col, (val, w) in enumerate(zip(vals, widths)):
                tk.Label(
                    self._summary_frame, text=str(val),
                    font=theme.FONT_TABLE,
                    bg=bg, fg=theme.COLOR_TITLE,
                    relief="solid", bd=1,
                    padx=8, pady=3, width=w
                ).grid(row=r, column=col, sticky="ew", padx=1)
    
    # ── Actions ────────────────────────────────────────────────────────────────
    def _parse_input(self):
        raw = self._ref_entry.get().strip()
        if not raw:
            messagebox.showwarning("Empty input!", "Please enter a reference string.")
            return None
        try:
            pages = [int(x) for x in raw.replace(",", " ").split() if x]
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
        
        results = []
        for key, (name, AlgoClass) in ALGO_MAP.items():
            algo = AlgoClass(NUM_FRAMES)
            steps = algo.simulate(ref)
            self._tab_traces[key].render(steps, NUM_FRAMES)
            self._tab_stats[key].update_stats(
                algo.fault_count, algo.hit_count, algo.hit_rate
            )
            results.append((name, algo.fault_count, algo.hit_count, algo.hit_rate))

        results.sort(key=lambda x: x[1])
        self._draw_summary_results(results)

    def _reset(self):
        self._ref_entry.delete(0, tk.END)
        for key in ALGO_MAP:
            self._tab_traces[key].render([], NUM_FRAMES)
            self._tab_stats[key].reset()
        self._draw_summary_placeholder()