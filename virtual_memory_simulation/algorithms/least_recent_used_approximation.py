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

        for i, page in enumerate(reference_string, 1):
            pages_in_mem = [f[0] for f in frames]

            if page in pages_in_mem:
                # hit – set the page's reference bit to 1
                index = pages_in_mem.index(page)
                frames[index][1] = 1
                self.hit_count += 1
                self.steps.append(SimStep(i, page, self.snapshot(pages_in_mem), False))
            else:
                self.fault_count += 1
                evicted = None

                if len(frames) < self.num_frames:
                    frames.append([page, 1])
                    clock_hand = len(frames) % self.num_frames
                else:
                    # spin clock until a page with bit = 0 is found
                    while frames[clock_hand][1] == 1:
                        frames[clock_hand][1] = 0  # second chance – clear bit
                        clock_hand = (clock_hand + 1) % self.num_frames

                    evicted = frames[clock_hand][0]
                    frames[clock_hand] = [page, 1]
                    clock_hand = (clock_hand + 1) % self.num_frames

                snapshot = self._snaphot([f[0] for f in frames])
                self.steps.append(SimStep(i, page, snapshot, True, evicted))
        
        return self.steps