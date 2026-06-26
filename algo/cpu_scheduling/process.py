"""
Encapsulated Process model.
Handles internal state management, metric calculation, and reset logic.
"""
from typing import Optional

class Process:
    def __init__(self, pid: str, arrival_time: int, burst_time: int, priority: int = 0, color: str = "#FFFFFF"):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.color = color

        # Metrics
        self.completion_time: Optional[int] = None
        self.waiting_time: int = 0
        self.turnaround_time: int = 0

    def run_one_unit(self):
        """Decrements remaining time by one unit."""
        if self.remaining_time > 0:
            self.remaining_time -= 1

    def is_done(self) -> bool:
        """Checks if process has finished execution."""
        return self.remaining_time == 0

    def finalize(self, completion_time: int):
        """Calculates TAT and WT based on the provided completion time."""
        self.completion_time = completion_time
        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time

    def reset(self):
        """Resets the process to its initial state."""
        self.remaining_time = self.burst_time
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

    def __repr__(self):
        return f"Process({self.pid}, Arr: {self.arrival_time}, Burst: {self.burst_time})"