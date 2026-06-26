"""
Algorithm Select Screen — shows 6 algorithm buttons + Compare All.
Background: ALGO_MENU_BG.png
"""

import os
import tkinter as tk
import gui.theme as theme
from gui.widgets import RoundedButton
from PIL import Image, ImageTk


class AlgorithmSelectScreen(tk.Frame):
    """Screen where the user picks which page replacement algorithm to run.

    Layout: 2-column grid of 6 algorithm buttons + centered Compare All button.
    """

    ALGORITHMS = [
        ("First In, First Out (FIFO)", "FIFO"),
        ("LRU Approximation", "LRU_APPROX"),
        ("Optimal", "OPTIMAL"),
        ("Least Frequently Used (LFU)", "LFU"),
        ("Least Recently Used (LRU)", "LRU"),
        ("Most Frequently Used (MFU)", "MFU"),
    ]

    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select = on_select

        # Keep a reference to the raw PIL Image object for clean, un-degraded scaling
        self.original_img = None
        self._bg_image_tk = None  # Keeps the ImageTk reference safe from garbage collection

        # Load the image asset once during initialization
        bg_path = os.path.join(os.path.dirname(__file__), "ALGO_MENU_BG.png")
        if os.path.exists(bg_path):
            self.original_img = Image.open(bg_path)

        self._build()

        # Bind the frame's structural change event to the resizing function
        if self.original_img:
            self.bind("<Configure>", self._resize_background)

    def _build(self):
        # ── Background image ──────────────────────────────────────
        # Initialize the label. We leave the image blank; _resize_background will fill it in.
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # ── White panel overlay ───────────────────────────────────
        panel = tk.Frame(self, bg=theme.COLOR_PANEL_BG, bd=0)
        panel.place(
            relx=0.5,  # horizontally centered (50% of window width)
            rely=0.52,  # slightly below center (52% of window height)
            anchor="center",  # the center of the panel sits at that point
            relwidth=0.74,  # panel is 74% of the window width
            relheight=0.72,  # panel is 72% of the window height
        )

        # ── Title ─────────────────────────────────────────────────
        tk.Label(
            panel,
            text="PICK AN ALGORITHM",
            font=theme.FONT_TITLE_LARGE,
            bg=theme.COLOR_PANEL_BG,
            fg=theme.COLOR_TITLE,
        ).pack(pady=(28, 24))

        # ── 2-column button grid ──────────────────────────────────
        grid_frame = tk.Frame(panel, bg=theme.COLOR_PANEL_BG)
        grid_frame.pack(pady=(0, 16))

        for idx, (label, key) in enumerate(self.ALGORITHMS):
            row = idx // 2
            col = idx % 2
            btn = RoundedButton(
                grid_frame,
                text=label,
                width=26,
                command=lambda k=key: self.on_select(k),
            )
            btn.grid(row=row, column=col, padx=16, pady=10, sticky="ew")

        # ── Compare All button (centered below grid) ──────────────
        RoundedButton(
            panel,
            text="Compare All Algorithms",
            width=40,
            command=lambda: self.on_select("COMPARE_ALL"),
        ).pack(pady=(4, 20))

    def _resize_background(self, event):
        """Fires whenever the frame is resized (including window zoom).

        Dynamically scales the background asset to perfectly fit the new window
        bounds.
        """
        # Read the current layout dimensions directly from the event data
        new_width = event.width
        new_height = event.height

        # Protect against tiny dimensions when window minimized or initializing
        if new_width > 10 and new_height > 10:
            # Resize from the original untouched asset using high-quality Resampling
            resized_img = self.original_img.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            # Convert and apply to the background label
            self._bg_image_tk = ImageTk.PhotoImage(resized_img)
            self.bg_label.config(image=self._bg_image_tk)