'''
LRU Approximation using the Second-Chance (Clock) Algorithm.
'''

from base import PageReplacementAlgorithm, SimStep

class LRUApproximation(PageReplacementAlgorithm):
    '''
    Approximates LRU using reference bits and a clock hand.

    Each page has a reference bit (0 or 1). When a page is accessed,
    its bit is set to 1. On replacement, the clock hand scans frames:
       - bit = 1 → give a second chance (reset to 0, advance hand)
       - bit = 0 → evict this page
    '''

    @property
    def name(self):
        return 'LRU Approximation (Second-Chance)'
    
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        self.steps = []
        self.fault_count = 0
        self.hit_count = 0

        frames = []        # list of [page, reference_bit]
        clock_hand = 0     # points to next eviction candidate

        