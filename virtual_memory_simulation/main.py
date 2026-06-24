'''
Entry point — launches the Virtual Memory GUI.
 
Run this file to start the program:
    python main.py
 
Project structure:
vm_simulator/
├── main.py                     ← updated: launches GUI
├── base.py                     ← unchanged
├── display.py                  ← unchanged (terminal version)
├── simulator.py                ← unchanged (terminal version)
├── algorithms/
│   ├── __init__.py
│   ├── fifo.py
│   ├── optimal.py
│   ├── lru.py
│   ├── lru_approximation.py
│   ├── lfu.py
│   └── mfu.py
└── gui/
    ├── __init__.py
    ├── theme.py                                                ← colors, fonts, sizing constants
    ├── widgets.py                                              ← RoundedButton, FrameTraceTable, StatsBar
    ├── algorithm_select.py                                     ← "Pick an Algorithm" screen
    ├── simulation_screen.py                                    ← single algo + Compare All screens
    ├── ALGO_MENU_BG.png                                        ← your Canva background (place here)
    ├── SIMULATION_BG.png                                       ← your Canva background (place here)
    ├── NTBrickSans.ttf                                         ← download from iFonts
    └── TT-Chocolates-Trial-Regular-iF67447a8ce204c.ttf         ← download from DaFonts
'''

import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import gui.theme as theme
from gui.algorithm_select import AlgorithmSelectScreen
from gui.simulation_screen import SimulationScreen, CompareAllScreen


class App(tk.Tk):
    '''
    Root application window.
    Manages screen switching between:
        - AlgorithmSelectScreen
        - SimulationScreen  (per algorithm)
        - CompareAllScreen
    '''

    def __init__(self):
        super().__init__()
        self.title("Virtual Memory Page Replacement Simulator")
        self.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Load custom fonts after root is created
        theme.load_fonts()

        self._current_screen = None
        self.show_algorithm_select()