'''
Entry point for the Virtual Memory Page Replacement Simulator.
 
Run this file to start the program:
    python main.py
 
Project structure:
virtual_memory_simulation/
├── main.py                     ← you are here
├── base.py                     ← SimStep + PageReplacementAlgorithm (abstract base)
├── display.py                  ← Display class (frame trace, stats, comparison)
├── simulator.py                ← VMSimulator controller (input + flow)
└── algorithms/
    ├── __init__.py             ← package exports
    ├── first_in_first_out.py
    ├── optimal.py
    ├── least_recent_used.py
    ├── least_recent_used_approximation.py
    ├── least_frequently_used.py
    ├── most_frequently_used.py
'''