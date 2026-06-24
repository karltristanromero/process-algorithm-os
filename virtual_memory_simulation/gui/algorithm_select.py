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