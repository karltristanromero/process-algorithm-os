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

                