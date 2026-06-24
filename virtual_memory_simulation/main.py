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

