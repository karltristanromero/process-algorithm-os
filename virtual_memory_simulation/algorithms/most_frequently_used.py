'''
Most Frequently Used (MFU) Page Replacement Algorithm.
'''

from base import PageReplacementAlgorithm, SimStep

class MFU(PageReplacementAlgorithm):
    '''
    Evicts the page with the highest access frequency count.
    Rationale: the most-used page has likely already served its purpose,
    while a newly loaded page still needs time to be useful.
    Ties are broken by LRU order (least recently used among tied pages).
    '''

    @property
    def name(self):
        return 'MFU'
    
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        self.steps = []
        self.fault_count = 0
        self.hit_count = 0

        frames = {}         # page -> frequency count
        lru_order = []      # recency tracker for tie-breaking (oldest at front)