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

        # ── Detect screen size and scale to fit ───────────────
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Use 90% of screen to leave room for taskbar
        theme.WINDOW_WIDTH  = int(screen_w * 0.90)
        theme.WINDOW_HEIGHT = int(screen_h * 0.90)

        self.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
        self.resizable(True, True)   # allow resizing too
        self.state("zoomed")         # start maximized

        theme.load_fonts()
        self._current_screen = None
        self.show_algorithm_select()

    def _clear(self):
        if self._current_screen:
            self._current_screen.destroy()
            self._current_screen = None

    def show_algorithm_select(self):
        self._clear()
        screen = AlgorithmSelectScreen(self, on_select=self._on_algo_selected)
        screen.place(x=0, y=0, width=theme.WINDOW_WIDTH, height=theme.WINDOW_HEIGHT)
        self._current_screen = screen

    def _on_algo_selected(self, algo_key: str):
        self._clear()
        if algo_key == "COMPARE_ALL":
            screen = CompareAllScreen(self, on_back=self.show_algorithm_select)
        else:
            screen = SimulationScreen(
                self,
                algo_key=algo_key,
                on_back=self.show_algorithm_select
            )
        screen.place(x=0, y=0, width=theme.WINDOW_WIDTH, height=theme.WINDOW_HEIGHT)
        self._current_screen = screen

if __name__ == "__main__":
    app = App()
    app.mainloop()