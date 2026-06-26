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
                    frames[page] = 1
                    lru_order.append(page)
                else:
                    max_freq = max(frames.values())
                    victim = next(p for p in lru_order if frames[p] == max_freq)

                    evicted = victim
                    del frames[victim]
                    lru_order.remove(victim)
                    frames[page] = 1
                    lru_order.append(page)

                self.steps.append(SimStep(i, page, self._snapshot(list(frames)), True, evicted))

        return self.steps