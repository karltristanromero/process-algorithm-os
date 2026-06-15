'''
Optimal (Belady's) Page Replacement Algorithm.
'''

from base import PageReplacementAlgorithm, SimStep

class Optimal(PageReplacementAlgorithm):
    '''
    Evicts the page that will not be used for the longest time in the future.
    Requires knowing the full reference list in advance (theoretical base case).
    '''

    @property
    def name(self):
        return 'Optimal'
    
    def simulate(self, reference_string: list[int]) -> list[SimStep]:
        self.steps = []
        self.fault_count = 0 
        self.hit_count = 0

        frames = []

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
                    future = reference_string[i:]     # remaining references after current step
                    farthest_index = -1
                    victim = frames[0]

                    for f in frames:
                        if f not in future:
                            # page never used again – ideal candidate for eviction
                            victim = f
                            break
                        next_use = future.index(f)
                        if next_use > farthest_index:
                            farthest_index = next_use
                            victim = f

                    evicted = victim
                    frames[frames.index(victim)] = page
                
                self.steps.append(SimStep(i, page, self.snapshot(frames), True, evicted))

        return self.steps