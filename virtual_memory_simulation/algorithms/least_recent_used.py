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