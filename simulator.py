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