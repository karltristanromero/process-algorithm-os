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