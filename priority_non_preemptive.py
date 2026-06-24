import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from scheduler_base import SchedulerBase
from temporary_utils.theme import COLORS, FONTS
from temporary_utils.layout_config import ADD_PROCESS_LAYOUT

class PriorityNonPreemptive(SchedulerBase):
    """Non-Preemptive Priority Scheduler implementation."""

    def __init__(self, title: str, width: int, height: int):
        super().__init__(title, width, height)
        self.process_table: Optional[ttk.Treeview] = None
        self.arrival_entry: Optional[tk.Entry] = None
        self.burst_entry: Optional[tk.Entry] = None
        self.priority_entry: Optional[tk.Entry] = None

    # --- Required Overrides ---
    def open_add_process_window(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Processes")
        win.state('zoomed')
        win.configure(bg=COLORS['background'])
        
        frame = tk.Frame(win, bg=COLORS['background'])
        frame.pack(pady=ADD_PROCESS_LAYOUT.get('frame_padding', 20))
        
        tk.Label(frame, text="Arrival Time:", font=FONTS['default'], bg=COLORS['background'], fg='white').grid(row=0, column=0)
        self.arrival_entry = tk.Entry(frame, font=FONTS['default'])
        self.arrival_entry.grid(row=0, column=1)

        tk.Label(frame, text="Burst Time:", font=FONTS['default'], bg=COLORS['background'], fg='white').grid(row=1, column=0)
        self.burst_entry = tk.Entry(frame, font=FONTS['default'])
        self.burst_entry.grid(row=1, column=1)
        
        tk.Label(frame, text="Priority:", font=FONTS['default'], bg=COLORS['background'], fg='white').grid(row=2, column=0)
        self.priority_entry = tk.Entry(frame, font=FONTS['default'])
        self.priority_entry.grid(row=2, column=1)

        tk.Button(frame, text="Add Process", command=self.add_process).grid(row=3, columnspan=2, pady=10)

        self.process_table = ttk.Treeview(win, columns=('PID', 'Arrival', 'Burst', 'Priority'), show='headings')
        for col in ('PID', 'Arrival', 'Burst', 'Priority'): self.process_table.heading(col, text=col)
        self.process_table.pack(fill=tk.BOTH, expand=True)
        self.refresh_process_table()

    def start_simulation(self):
        if not self.processes:
            messagebox.showwarning("Empty", "No processes to run.")
            return
        self.run_priority_non_preemptive()

    def reset_simulation(self):
        self.processes = []
        self.clear_canvas()
        self.reset_metrics()
        self.refresh_process_table()

    # --- Logic ---
    def add_process(self):
        if not (self.arrival_entry and self.burst_entry and self.priority_entry): return
        try:
            p = {
                "pid": f"P{len(self.processes) + 1}",
                "arrival_time": int(self.arrival_entry.get()),
                "burst_time": int(self.burst_entry.get()),
                "priority": int(self.priority_entry.get()),
                "color": self.generate_process_color(len(self.processes))
            }
            self.processes.append(p)
            self.refresh_process_table()
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid inputs")

    def refresh_process_table(self):
        if self.process_table:
            for i in self.process_table.get_children(): self.process_table.delete(i)
            for p in self.processes:
                self.process_table.insert('', tk.END, values=(p['pid'], p['arrival_time'], p['burst_time'], p['priority']))

    def run_priority_non_preemptive(self):
        processes = [p.copy() for p in self.processes]
        n, time, completed = len(processes), 0, 0
        is_comp = [False] * n
        segments = []
        total_tat, total_wt = 0, 0
        
        while completed < n:
            available = [i for i in range(n) if processes[i]['arrival_time'] <= time and not is_comp[i]]
            
            if available:
                idx = min(available, key=lambda i: (processes[i]['priority'], processes[i]['arrival_time']))
                start_time = time
                time += processes[idx]['burst_time']
                
                # Metrics Calculation
                tat = time - processes[idx]['arrival_time']
                wt = tat - processes[idx]['burst_time']
                total_tat += tat
                total_wt += wt
                
                segments.append((idx, start_time, time))
                is_comp[idx] = True
                completed += 1
            else:
                time += 1
        
        self.update_metrics(
            avg_tat=total_tat/n,
            avg_wt=total_wt/n,
            cpu_util=(sum(p['burst_time'] for p in processes) / time) * 100,
            throughput=n/time
        )
        self.animate_execution_loop(segments, processes)