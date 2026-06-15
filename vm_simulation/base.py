'''
Contains the SimStep data class and the abstract base class
for all page replacement algorithms.
'''

from abc import ABC, abstractmethod

class SimStep:
    'Stores the state of frames at a single reference step.'