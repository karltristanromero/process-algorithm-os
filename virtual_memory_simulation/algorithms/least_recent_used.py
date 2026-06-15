'''
Least Recently Used (LRU) Page Replacement Algorithm.
'''

from collections import OrderedDict
from base import PageReplacementAlgorithm, SimStep

class LRU(PageReplacementAlgorithm):
    '''
    Evicts the page that has not been used for the longest time.
    Uses an OrderedDict to efficiently track recency - least recently used
    page is always at the front, most recently used at the end.
    '''

    @property
    def name(self):
        return "LRU"
    
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        self.steps = []
        self.fault_count = 0
        self.hit_count = 0

        cache = OrderedDict()   # key = page, order = recency (end = most recent)

        for i, page in enumerate(reference_string, 1):
            if page in cache:
                # hit – move to most-recently-used end
                cache.move_to_end(page)
                self.hit_count += 1
                self.steps.append(SimStep(i, page, self.snapshot(list(cache)), False))
            else:
                self.fault_count += 1
                evicted = None

                