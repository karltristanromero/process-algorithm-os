"""
Main launcher for the CPU scheduling simulator.
Contains global execution entry points for different scheduling algorithms.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sjf_preemptive import SJFPreemptive
from sjf_non_preemptive import SJFNonPreemptive
from round_robin import RoundRobin


def sjf_pe_play():
    """Launch Preemptive SJF scheduler."""
    print("Starting Preemptive SJF Scheduler...")
    app = SJFPreemptive("Preemptive Shortest Job First", 1920, 1080)
    app.setup_main_window()
    app.run()


def sjf_non_pe_play():
    """Launch Non-Preemptive SJF scheduler."""
    print("Starting Non-Preemptive SJF Scheduler...")
    app = SJFNonPreemptive("Non-Preemptive Shortest Job First", 1920, 1080)
    app.setup_main_window()
    app.run()


def rr_play():
    """Launch Round Robin scheduler."""
    print("Starting Round Robin Scheduler...")
    app = RoundRobin("Round Robin Scheduler", 1920, 1080)
    app.setup_main_window()
    app.run()


if __name__ == "__main__":
    pass