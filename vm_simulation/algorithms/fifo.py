'''
First In, First Out (FIFO) Page Replacement Algorithm.
'''

from collections import deque
from base import PageReplacementAlgorithm, SimStep

class FIFO(PageReplacementAlgorithm):
    '''
    Evicts the page that has been in memory the longest.
    Uses a queue to tract insertion order.
    '''

    @property
    def name(self):
        return 'FIFO'
    
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        self.steps = []
        self.fault_count = 0
        self.hit_count = 0

        frames = []         # current pages in memory
        queue = deque()     # tracks insertion order (oldest at front)