'''
VMSimulator — the main controller.
Handles user input, selects algorithms, and coordinates display output.
'''

import random
from display import Display
from algorithms import FIFO, Optimal, LRU, LRUApproximation, LFU, MFU