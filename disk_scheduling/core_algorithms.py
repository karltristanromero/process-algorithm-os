# algorithms.py
from abc import ABC, abstractmethod
from typing import List, Tuple

class DiskSchedulingAlgorithm(ABC):
    """Abstract base class for disk scheduling algorithms"""
    
    def __init__(self, requests: List[int], head_position: int, disk_size: int):
        self.requests = requests
        self.head_position = head_position
        self.disk_size = disk_size
        self.sequence = []
        self.total_seek_time = 0
    
    @abstractmethod
    def schedule(self) -> Tuple[List[int], int]:
        pass
    
    def calculate_seek_time(self, from_pos: int, to_pos: int) -> int:
        return abs(to_pos - from_pos)


class FCFS(DiskSchedulingAlgorithm):
    """First Come First Served"""
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        for request in self.requests:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        return self.sequence, self.total_seek_time


class SSTF(DiskSchedulingAlgorithm):
    """Shortest Seek Time First"""
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        remaining = list(self.requests)
        
        while remaining:
            closest = min(remaining, key=lambda x: abs(x - current_head))
            seek_time = self.calculate_seek_time(current_head, closest)
            self.total_seek_time += seek_time
            self.sequence.append(closest)
            remaining.remove(closest)
            current_head = closest
        
        return self.sequence, self.total_seek_time


class SCAN(DiskSchedulingAlgorithm):
    """SCAN Elevator Algorithm (moves toward 0 first)"""
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        left = sorted([x for x in self.requests if x < current_head], reverse=True)
        right = sorted([x for x in self.requests if x >= current_head])
        
        for request in left:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request

        if current_head != 0:
            seek_time = self.calculate_seek_time(current_head, 0)
            self.total_seek_time += seek_time
            self.sequence.append(0)
            current_head = 0
        
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        return self.sequence, self.total_seek_time


class CSCAN(DiskSchedulingAlgorithm):
    """Circular SCAN"""
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        left = sorted([x for x in self.requests if x < current_head])
        right = sorted([x for x in self.requests if x >= current_head])

        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        if left:
            if current_head != self.disk_size - 1:
                seek_time = self.calculate_seek_time(current_head, self.disk_size - 1)
                self.total_seek_time += seek_time
                self.sequence.append(self.disk_size - 1)
                current_head = self.disk_size - 1

            seek_time = self.calculate_seek_time(current_head, 0)
            self.total_seek_time += seek_time
            self.sequence.append(0)
            current_head = 0
            
            for request in left:
                seek_time = self.calculate_seek_time(current_head, request)
                self.total_seek_time += seek_time
                self.sequence.append(request)
                current_head = request
        
        return self.sequence, self.total_seek_time


class LOOK(DiskSchedulingAlgorithm):
    """LOOK Algorithm"""
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        left = sorted([x for x in self.requests if x < current_head], reverse=True)
        right = sorted([x for x in self.requests if x >= current_head])
        
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        for request in left:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        return self.sequence, self.total_seek_time


class CLOOK(DiskSchedulingAlgorithm):
    """Circular LOOK"""
    def schedule(self) -> Tuple[List[int], int]:
        current_head = self.head_position
        self.sequence = [current_head]
        self.total_seek_time = 0
        
        left = sorted([x for x in self.requests if x < current_head])
        right = sorted([x for x in self.requests if x >= current_head])
        
        for request in right:
            seek_time = self.calculate_seek_time(current_head, request)
            self.total_seek_time += seek_time
            self.sequence.append(request)
            current_head = request
        
        if left:
            seek_time = self.calculate_seek_time(current_head, left[0])
            self.total_seek_time += seek_time
            current_head = left[0]
            self.sequence.append(current_head)
            
            for request in left[1:]:
                seek_time = self.calculate_seek_time(current_head, request)
                self.total_seek_time += seek_time
                self.sequence.append(request)
                current_head = request
        
        return self.sequence, self.total_seek_time