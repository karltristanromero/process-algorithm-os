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

    @property
    def status(self):
        return 'FAULT' if self.is_fault else 'HIT'
    
class PageReplacementAlgorithm(ABC):
    '''Abstract base class for page replacement algorithms.'''

    def __init__(self, num_frames: int = 4):
        self.num_frames = num_frames
        self.steps = list[SimStep] = []
        self.fault_count = 0
        self.hit_count = 0

    @property
    def name(self) -> str:
        raise NotImplementedError
    
    @property
    def hit_rate(self) -> float:
        total = self.fault_count + self.hit_count
        return (self.hit_count / total * 100) if total > 0 else 0.0
    
    @abstractmethod
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        '''Run the algorithm on a reference string. Returns the list of SimStep.'''
        pass