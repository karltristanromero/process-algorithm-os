'''
VMSimulator — the main controller.
Handles user input, selects algorithms, and coordinates display output.
'''

import random
from display import Display
from algorithms import FIFO, Optimal, LRU, LRUApproximation, LFU, MFU

class VMSimulator:
    """
    Main controller for the Virtual Memory Page Replacement Simulator.
    Connects user input → algorithm selection → display output.
    """

    ALGORITHMS = {
        "1": ("FIFO",                          FIFO),
        "2": ("Optimal",                       Optimal),
        "3": ("LRU",                           LRU),
        "4": ("LRU Approximation",             LRUApproximation),
        "5": ("LFU",                           LFU),
        "6": ("MFU",                           MFU),
    }

    def __init__(self, num_frames: int = 4):
        self.num_frames = num_frames

    # ── Input helpers ──────────────────────────────────────────────────────────

    def get_reference_string(self) -> list[int]:
        print("\n   How would you like to provide the reference string?")
        print("     [1] Enter manually")
        print("     [2] Randomize")
        choice = input("\n Your choice: ").strip()

        if choice == "2":
            return self._generate_random()
        else:
            return self._get_manual_input()