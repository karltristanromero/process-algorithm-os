'''
Least Frequently Used (LFU) Page Replacement Algorithm.
'''

from base import PageReplacementAlgorithm, SimStep

class LFU(PageReplacementAlgorithm):
    '''
    Evicts the page with the lowest access frequency count.
    Ties are broken by recency (least recently used among tied pages).
    '''