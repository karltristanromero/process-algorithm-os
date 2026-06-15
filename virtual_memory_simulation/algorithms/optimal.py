'''
Optimal (Belady's) Page Replacement Algorithm.
'''

from base import PageReplacementAlgorithm, SimStep

class Optimal(PageReplacementAlgorithm):
    '''
    Evicts the page that will not be used for the longest time in the future.
    Requires knowing the full reference list in advance (theoretical base case).
    '''

    