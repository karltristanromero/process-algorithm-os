class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0, color="#FFFFFF"):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.color = color

        # optional metrics
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

    def run_one_unit(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1

    def is_done(self):
        return self.remaining_time == 0

    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = None
        self.completion_time = None