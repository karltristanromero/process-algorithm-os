'''
Least Frequently Used (LFU) Page Replacement Algorithm.
'''

from base import PageReplacementAlgorithm, SimStep

class LFU(PageReplacementAlgorithm):
    '''
    Evicts the page with the lowest access frequency count.
    Ties are broken by recency (least recently used among tied pages).
    '''

    @property
    def name(self):
        return 'Least Frequently Used (LFU)'
    
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        self.steps = []
        self.fault_count = 0
        self.hit_count = 0

        frames = {}         # page -> frequency count
        lru_queue = []      # recency tracker for tie-breaking (oldest at front)