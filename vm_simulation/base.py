'''
Contains the SimStep data class and the abstract base class
for all page replacement algorithms.
'''

from abc import ABC, abstractmethod

class SimStep:
    'Stores the state of frames at a single reference step.'

    def __init__(self, step: int, page: int, frames: list, is_fault: bool, evicted=None):
        self.step = step            # step number (1-indexed)
        self.page = page            # page that was referenced
        self.frames = frames        # snapshot of frame contents (None = empty slot)
        self.is_fault = is_fault 
        self.evicted = evicted      # page that was evicted (None if no eviction)