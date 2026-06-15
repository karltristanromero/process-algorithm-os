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
        lru_order = []      # recency tracker for tie-breaking (oldest at front)

        for i, page in enumerate(reference_string, 1):
            if page in frames:
                # hit – increment frequency and update recency
                frames[page] += 1
                lru_order.remove(page)
                lru_order.append(page)
                self.hit_count += 1
                self.steps.append(SimStep(i, page, self._snapshot(list(frames)), False))
            else:
                self.fault_count += 1
                evicted = None

                if len(frames) < self.num_frames:
                    frames[pages] = 1
                    lru_order.append(page)
                else:
                    # evict the page with the lowest frequency
                    # among ties, pick the least recently used
                    min_freq = min(frames.values())
                    victim = next(p for p in lru_order if frames[p] == min_freq)

                    evicted = victim
                    del frames[victim]
                    lru_order.remove(victim)
                    frames[page] = 1
                    lru_order.append(page)

                self.steps.append(SimStep(i, page, self._snapshot(list(frames)), True, evicted))

        return self.steps