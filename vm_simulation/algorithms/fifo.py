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

        for i, page in enumerate(reference_string, 1):
            if page in frames:
                self.hit_count += 1
                self.steps.append(SimStep(i, page, self.snapshot(frames), False))
            else:
                self.fault_count += 1
                evicted = None

                if len(frames) < self.num_frames:
                    frames.append(page)
                else:
                    evicted = queue.popleft()
                    frames[frames.index(evicted)] = page

                