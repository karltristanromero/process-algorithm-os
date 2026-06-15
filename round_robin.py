"""
Round Robin Scheduler implementation.
Inherits from SchedulerBase and implements RR-specific logic.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from scheduler_base import SchedulerBase
from temporary_utils.theme import WINDOW_SIZES


class RoundRobin(SchedulerBase):
    """Round Robin Scheduler."""

    def __init__(self, title, width, height):
        """Initialize the Round Robin scheduler."""
        super().__init__(title, width, height)
        self.time_quantum = 2  # Default time quantum
        self.process_table = None  # Will be set in add process window
        self.add_process_window = None  # Reference to the add process window

    def setup_add_process_window(self):
        """Set up the Add Process popup window for Round Robin."""
        self.add_process_window = tk.Toplevel(self.root)
        self.add_process_window.title("Add Process")
        self.add_process_window.geometry(f"{WINDOW_SIZES['add_process'][0]}x{WINDOW_SIZES['add_process'][1]}")
        self.add_process_window.resizable(False, False)
        self.add_process_window.configure(bg='#2b2b2b')
        self.add_process_window.transient(self.root)  # Make it modal
        self.add_process_window.grab_set()

        # Main frame
        main_frame = tk.Frame(self.add_process_window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Add New Process",
            font=('Helvetica', 16, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        title_label.pack(pady=(0, 20))

        # Input fields frame
        input_frame = tk.Frame(main_frame, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Arrival Time
        tk.Label(
            input_frame,
            text="Arrival Time:",
            font=('Helvetica', 12),
            bg='#2b2b2b',
            fg='white'
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.arrival_entry = tk.Entry(
            input_frame,
            font=('Helvetica', 12),
            width=20
        )
        self.arrival_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        # Burst Time
        tk.Label(
            input_frame,
            text="Burst Time:",
            font=('Helvetica', 12),
            bg='#2b2b2b',
            fg='white'
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.burst_entry = tk.Entry(
            input_frame,
            font=('Helvetica', 12),
            width=20
        )
        self.burst_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        # Time Quantum (Global setting for RR)
        tk.Label(
            input_frame,
            text="Time Quantum:",
            font=('Helvetica', 12),
            bg='#2b2b2b',
            fg='white'
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantum_entry = tk.Entry(
            input_frame,
            font=('Helvetica', 12),
            width=20
        )
        self.quantum_entry.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        self.quantum_entry.insert(0, str(self.time_quantum))  # Set default value

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Add Process Button
        add_btn = tk.Button(
            btn_frame,
            text="Add Process",
            font=('Helvetica', 12, 'bold'),
            bg='#4caf50',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.add_process
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Cancel Button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=('Helvetica', 12),
            bg='#f44336',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.add_process_window.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # Process table frame
        table_frame = tk.Frame(main_frame, bg='#2b2b2b')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Table label
        tk.Label(
            table_frame,
            text="Process List:",
            font=('Helvetica', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        ).pack(anchor=tk.W, pady=(0, 5))

        # Create Treeview for process table
        self.process_table = ttk.Treeview(
            table_frame,
            columns=('PID', 'Arrival Time', 'Burst Time'),
            show='headings',
            height=10
        )

        # Define headings
        self.process_table.heading('PID', text='Process ID')
        self.process_table.heading('Arrival Time', text='Arrival Time')
        self.process_table.heading('Burst Time', text='Burst Time')

        # Define column widths
        self.process_table.column('PID', width=100)
        self.process_table.column('Arrival Time', width=150)
        self.process_table.column('Burst Time', width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.process_table.yview)
        self.process_table.configure(yscrollcommand=scrollbar.set)

        # Pack table and scrollbar
        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Table buttons frame
        table_btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        table_btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Edit Button
        edit_btn = tk.Button(
            table_btn_frame,
            text="Edit Selected",
            font=('Helvetica', 10),
            bg='#ff9800',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.edit_process
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Delete Button
        delete_btn = tk.Button(
            table_btn_frame,
            text="Delete Selected",
            font=('Helvetica', 10),
            bg='#f44336',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.delete_process
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Clear All Button
        clear_btn = tk.Button(
            table_btn_frame,
            text="Clear All",
            font=('Helvetica', 10),
            bg='#9e9e9e',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.clear_all_processes
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

    def add_process(self):
        """Add a new process from the input fields."""
        try:
            arrival_time = int(self.arrival_entry.get())
            burst_time = int(self.burst_entry.get())
            time_quantum = int(self.quantum_entry.get())

            if arrival_time < 0 or burst_time <= 0:
                raise ValueError("Arrival time must be >= 0 and burst time must be > 0")
            if time_quantum <= 0:
                raise ValueError("Time quantum must be > 0")

            # Update the time quantum (applies to all processes in RR)
            self.time_quantum = time_quantum

            # Generate PID
            pid = f"P{len(self.processes) + 1}"

            # Add to processes list
            process = {
                'pid': pid,
                'arrival_time': arrival_time,
                'burst_time': burst_time,
                'remaining_time': burst_time,  # For RR scheduling
                'completion_time': 0,
                'start_time': -1,
                'color': self.generate_process_color(len(self.processes))
            }

            self.processes.append(process)

            # Add to table
            self.process_table.insert('', tk.END, values=(pid, arrival_time, burst_time))

            # Clear input fields
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            # Note: We don't clear the quantum entry as it's a global setting

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def edit_process(self):
        """Edit the selected process."""
        selected = self.process_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a process to edit")
            return

        item = self.process_table.item(selected[0])
        pid, arrival_time, burst_time = item['values']

        # Find the process in our list
        process_index = None
        for i, p in enumerate(self.processes):
            if p['pid'] == pid:
                process_index = i
                break

        if process_index is None:
            messagebox.showerror("Error", "Process not found")
            return

        # Get new values
        new_arrival = simpledialog.askinteger(
            "Edit Process",
            f"Enter new arrival time for {pid}:",
            initialvalue=arrival_time,
            minvalue=0
        )
        if new_arrival is None:
            return

        new_burst = simpledialog.askinteger(
            "Edit Process",
            f"Enter new burst time for {pid}:",
            initialvalue=burst_time,
            minvalue=1
        )
        if new_burst is None:
            return

        # Update process
        self.processes[process_index]['arrival_time'] = new_arrival
        self.processes[process_index]['burst_time'] = new_burst
        self.processes[process_index]['remaining_time'] = new_burst

        # Update table
        self.process_table.item(selected[0], values=(pid, new_arrival, new_burst))

    def delete_process(self):
        """Delete the selected process."""
        selected = self.process_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a process to delete")
            return

        item = self.process_table.item(selected[0])
        pid = item['values'][0]

        # Remove from processes list
        self.processes = [p for p in self.processes if p['pid'] != pid]

        # Remove from table
        self.process_table.delete(selected[0])

        # Update remaining process PIDs to maintain sequence
        for i, process in enumerate(self.processes):
            process['pid'] = f"P{i+1}"

        # Refresh table
        self.refresh_process_table()

    def clear_all_processes(self):
        """Clear all processes."""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all processes?"):
            self.processes.clear()
            self.time_quantum = 2  # Reset to default
            if self.add_process_window and self.add_process_window.winfo_exists():
                self.quantum_entry.delete(0, tk.END)
                self.quantum_entry.insert(0, str(self.time_quantum))
            self.process_table.delete(*self.process_table.get_children())

    def refresh_process_table(self):
        """Refresh the process table display."""
        # Clear existing items
        for item in self.process_table.get_children():
            self.process_table.delete(item)

        # Re-add all processes
        for process in self.processes:
            self.process_table.insert('', tk.END, values=(
                process['pid'],
                process['arrival_time'],
                process['burst_time']
            ))

    def generate_process_color(self, index):
        """Generate a distinct color for each process."""
        # Simple color generation - in practice, you might want a better algorithm
        colors = [
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#ffe66d',
            '#f7971e', '#ff9ff3', '#54a0ff', '#5f27cd',
            '#00d2d3', '#ff9f43', '#ee5a24', '#0984e3'
        ]
        return colors[index % len(colors)]

    def open_add_process_window(self):
        """Open the Add Process window."""
        if self.add_process_window is None or not self.add_process_window.winfo_exists():
            self.setup_add_process_window()
        else:
            self.add_process_window.lift()
            # Update the quantum entry to show current value
            self.quantum_entry.delete(0, tk.END)
            self.quantum_entry.insert(0, str(self.time_quantum))

    def start_simulation(self):
        """Start the Round Robin simulation."""
        if not self.processes:
            messagebox.showwarning("No Processes", "Please add at least one process before starting")
            return

        # Close add process window if open
        if self.add_process_window and self.add_process_window.winfo_exists():
            self.add_process_window.destroy()

        # Run the RR algorithm
        self.run_round_robin()

    def reset_simulation(self):
        """Reset the simulation."""
        self.processes.clear()
        self.time_quantum = 2  # Reset to default
        if self.process_table:
            self.process_table.delete(*self.process_table.get_children())
        self.clear_canvas()
        self.reset_metrics()

        # Close add process window if open
        if self.add_process_window and self.add_process_window.winfo_exists():
            self.add_process_window.destroy()
            # Reset quantum entry
            self.setup_add_process_window()  # This will recreate with default quantum

    def run_round_robin(self):
        """Execute the Round Robin algorithm and visualize results."""
        # Make a copy of processes to work with
        processes = [p.copy() for p in self.processes]

        # Sort by arrival time
        processes.sort(key=lambda p: p['arrival_time'])

        # Initialize variables
        time = 0
        completed = 0
        n = len(processes)

        # For visualization, we'll store execution segments
        execution_segments = []  # List of (process_index, start_time, end_time)
        # We also need to track when each process first starts
        first_start_times = [-1] * n

        # Create a queue for RR
        from collections import deque
        ready_queue = deque()
        # Track which processes have been added to the queue
        in_queue = [False] * n
        # Track arrival index
        arrival_idx = 0

        # Continue until all processes are completed
        while completed < n or ready_queue:
            # Add all processes that have arrived by current time to the queue
            while arrival_idx < n and processes[arrival_idx]['arrival_time'] <= time:
                if not in_queue[arrival_idx]:
                    ready_queue.append(arrival_idx)
                    in_queue[arrival_idx] = True
                arrival_idx += 1

            if ready_queue:
                # Get the next process from the queue
                idx = ready_queue.popleft()
                in_queue[idx] = False  # It's no longer in the queue (will be re-added if not finished)

                # If this is the first time this process is starting
                if processes[idx]['start_time'] == -1:
                    processes[idx]['start_time'] = time
                    first_start_times[idx] = time

                # Execute for up to time_quantum or until completion
                exec_time = min(self.time_quantum, processes[idx]['remaining_time'])

                # Record execution segment
                execution_segments.append((idx, time, time + exec_time))

                # Update time and remaining time
                time += exec_time
                processes[idx]['remaining_time'] -= exec_time

                # Add any processes that arrived during this execution to the queue
                while arrival_idx < n and processes[arrival_idx]['arrival_time'] <= time:
                    if not in_queue[arrival_idx]:
                        ready_queue.append(arrival_idx)
                        in_queue[arrival_idx] = True
                    arrival_idx += 1

                # If process is not completed, add it back to the queue
                if processes[idx]['remaining_time'] > 0:
                    ready_queue.append(idx)
                    in_queue[idx] = True
                else:
                    # Process is completed
                    processes[idx]['completion_time'] = time
                    completed += 1
            else:
                # No process in queue, jump to next arrival time
                if arrival_idx < n:
                    time = processes[arrival_idx]['arrival_time']
                else:
                    break  # No more processes

        # Calculate metrics
        self.calculate_and_display_metrics(processes, first_start_times, execution_segments)

    def calculate_and_display_metrics(self, processes, start_times, execution_segments):
        """Calculate and display metrics, then visualize the results."""
        n = len(processes)
        total_tat = 0
        total_wt = 0
        total_execution_time = sum(p['burst_time'] for p in processes)

        # Calculate TAT and WT for each process
        for i in range(n):
            tat = processes[i]['completion_time'] - processes[i]['arrival_time']
            wt = tat - processes[i]['burst_time']
            total_tat += tat
            total_wt += wt

        avg_tat = total_tat / n
        avg_wt = total_wt / n

        # CPU Utilization = (Total execution time / Total time) * 100
        total_time = execution_segments[-1][2] if execution_segments else 0
        if total_time == 0:
            total_time = 1
        cpu_util = (total_execution_time / total_time * 100)

        # Throughput = Total processes / Total time
        throughput = n / total_time if total_time > 0 else 0

        # Update metrics display
        self.update_metrics(avg_tat, avg_wt, cpu_util, throughput)

        # Visualize the results on canvas
        self.visualize_execution(execution_segments, processes)

    def visualize_execution(self, execution_segments, processes):
        """Visualize the execution on the canvas."""
        self.clear_canvas()

        if not execution_segments:
            return

        # Canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # If canvas not yet sized, use reasonable defaults
        if canvas_width <= 1:
            canvas_width = 1800
        if canvas_height <= 1:
            canvas_height = 800

        # Calculate scaling
        total_time = execution_segments[-1][2] if execution_segments else 1
        if total_time == 0:
            total_time = 1

        time_scale = (canvas_width - 200) / total_time  # Leave margins
        process_height = 60
        y_start = 100

        # Draw timeline
        self.canvas.create_line(100, y_start + process_height * len(processes) + 50,
                              canvas_width - 100, y_start + process_height * len(processes) + 50,
                              fill='white', width=2)

        # Draw time markers
        for i in range(0, int(total_time) + 1, max(1, int(total_time) // 10)):
            x = 100 + i * time_scale
            self.canvas.create_line(x, y_start + process_height * len(processes) + 45,
                                  x, y_start + process_height * len(processes) + 55,
                                  fill='white', width=1)
            self.canvas.create_text(x, y_start + process_height * len(processes) + 70,
                                  text=str(i), fill='white', font=('Helvetica', 8))

        # Draw process execution bars
        for proc_index, start_time, end_time in execution_segments:
            process = processes[proc_index]
            y = y_start + (proc_index % len(processes)) * process_height

            # Calculate bar dimensions
            bar_start_x = 100 + start_time * time_scale
            bar_width = (end_time - start_time) * time_scale
            bar_height = process_height - 10

            # Draw the process bar
            self.canvas.create_rectangle(
                bar_start_x, y + 5,
                bar_start_x + bar_width, y + 5 + bar_height,
                fill=process['color'],
                outline='white',
                width=1
            )

            # Draw process ID in center
            mid_x = bar_start_x + bar_width / 2
            mid_y = y + 5 + bar_height / 2
            self.canvas.create_text(
                mid_x, mid_y,
                text=process['pid'],
                fill='white',
                font=('Helvetica', 10, 'bold')
            )

            # Draw start and end times below the bar
            self.canvas.create_text(
                bar_start_x, y + 5 + bar_height + 15,
                text=str(start_time),
                fill='white',
                font=('Helvetica', 8),
                anchor=tk.N
            )
            self.canvas.create_text(
                bar_start_x + bar_width, y + 5 + bar_height + 15,
                text=str(end_time),
                fill='white',
                font=('Helvetica', 8),
                anchor=tk.N
            )

        # Draw process names on the left
        for i, process in enumerate(processes):
            y = y_start + i * process_height
            self.canvas.create_text(
                80, y + 5 + process_height / 2,
                text=process['pid'],
                fill='white',
                font=('Helvetica', 10, 'bold'),
                anchor=tk.E
            )


if __name__ == "__main__":
    # For testing
    app = RoundRobin("Round Robin Test", 1920, 1080)
    app.setup_main_window()
    # Add some test processes
    app.processes = [
        {'pid': 'P1', 'arrival_time': 0, 'burst_time': 5, 'remaining_time': 5, 'color': '#ff6b6b'},
        {'pid': 'P2', 'arrival_time': 1, 'burst_time': 3, 'remaining_time': 3, 'color': '#4ecdc4'},
        {'pid': 'P3', 'arrival_time': 2, 'burst_time': 8, 'remaining_time': 8, 'color': '#45b7d1'}
    ]
    for p in app.processes:
        app.process_table.insert('', tk.END, values=(p['pid'], p['arrival_time'], p['burst_time']))
    app.run()