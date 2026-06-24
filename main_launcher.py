
"""
main_launcher.py

Launcher for:
1. FCFS
2. Priority Preemptive
3. Priority Non-Preemptive
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import schedulers
from FCFS import FCFS
from priority_preemptive import PriorityPreemptive
from priority_non_preemptive import PriorityNonPreemptive


def fcfs_play():
    """Launch FCFS Scheduler"""
    print("Starting FCFS Scheduler...")

    app = FCFS(
        title="First Come First Serve Scheduler",
        width=1920,
        height=1080
    )

    app.setup_main_window()
    app.run()


def priority_preemptive_play():
    """Launch Priority Preemptive Scheduler"""
    print("Starting Priority Preemptive Scheduler...")

    app = PriorityPreemptive(
        title="Priority Preemptive Scheduler",
        width=1920,
        height=1080
    )

    app.setup_main_window()
    app.run()


def priority_non_preemptive_play():
    """Launch Priority Non-Preemptive Scheduler"""
    print("Starting Priority Non-Preemptive Scheduler...")

    app = PriorityNonPreemptive(
        title="Priority Non-Preemptive Scheduler",
        width=1920,
        height=1080
    )

    app.setup_main_window()
    app.run()


def show_menu():
    """Display scheduler menu"""

    while True:

        print("\n====================================")
        print("     CPU SCHEDULING SIMULATOR")
        print("====================================")
        print("1. FCFS")
        print("2. Priority Preemptive")
        print("3. Priority Non-Preemptive")
        print("4. Exit")
        print("====================================")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            fcfs_play()
            break

        elif choice == "2":
            priority_preemptive_play()
            break

        elif choice == "3":
            priority_non_preemptive_play()
            break

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("\nInvalid choice. Please try again.\n")


if __name__ == "__main__":
    show_menu()

