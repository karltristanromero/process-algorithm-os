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
        
    def _get_manual_input(self) -> list[int]:
        while True:
            raw = input("\n Enter page numbers (space or comma separated):\n > ").strip()

            try:
                pages = [int(x) for x in raw.replace(",", " ").split() if x]
                if len(pages) < 2:
                    print("  ⚠  Please enter at least 2 page numbers.")
                    continue
                return pages
            except ValueError:
                print("  ⚠  Invalid input — please enter integers only.")

    def _generate_random(self) -> list[int]:
        while True:
            try:
                length = int(input("\n How many page references? (e.g. 15): ").strip())
                page_max = int(input("  Highest page number? (e.g. 9 gives pages 0-9): ").strip())

                if length < 2 or page_max < 1:
                    print("  ⚠  Length must be ≥ 2 and page max ≥ 1.")
                    continue
                ref = [random.randint(0, page_max) for _ in range(length)]
                print("\n Generated: {' '.join(map(str, ref))}")
                return ref
            except ValueError:
                print("  ⚠  Please enter valid integers.")

    def choose_algorithm(self) -> str:
        print("\n Select a page replacement algorithm:")
        for key, (name, _) in self.ALGORITHMS.items():
            print(f"    [{key}] {name}")
        print("    [7] Compare All")

        while True:
            choice = input("\n  Your choice: ").strip()
            if choice in self.ALGORITHMS or choice == "7":
                return choice
            print("  ⚠  Please enter a number between 1 and 7.")