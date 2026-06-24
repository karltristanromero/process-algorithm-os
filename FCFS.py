import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from scheduler_base import SchedulerBase
from temporary_utils.theme import COLORS

class FCFS(SchedulerBase):
    def __init__(self, title: str, width: int, height: int):
        super().__init__(title, width, height)
        self.process_table: Optional[ttk.Treeview] = None
        self.arrival_entry: Optional[tk.Entry] = None
        self.burst_entry: Optional[tk.Entry] = None

    # --- Mandatory Overrides ---
    def open_add_process_window(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Processes")
        win.state('zoomed')
        win.configure(bg=COLORS['background'])
        
        tk.Label(win, text="Arrival Time:", bg=COLORS['background'], fg='white').pack()
        self.arrival_entry = tk.Entry(win)
        self.arrival_entry.pack()

        tk.Label(win, text="Burst Time:", bg=COLORS['background'], fg='white').pack()
        self.burst_entry = tk.Entry(win)
        self.burst_entry.pack()

        tk.Button(win, text="Add Process", command=self.add_process).pack()

        self.process_table = ttk.Treeview(win, columns=('PID', 'Arrival', 'Burst'), show='headings')
        for col in ('PID', 'Arrival', 'Burst'): self.process_table.heading(col, text=col)
        self.process_table.pack(fill=tk.BOTH, expand=True)
        self.refresh_process_table()

    def start_simulation(self):
        if not self.processes:
            messagebox.showwarning("Empty", "No processes to run.")
            return
        self.run_fcfs()

    def reset_simulation(self):
        self.processes = []
        self.clear_canvas()
        self.reset_metrics()
        self.refresh_process_table()

    # --- FCFS Logic ---
    def add_process(self):
        if not (self.arrival_entry and self.burst_entry): return
        try:
            p = {
                "pid": f"P{len(self.processes) + 1}", 
                "arrival_time": int(self.arrival_entry.get()), 
                "burst_time": int(self.burst_entry.get()),
                "color": self.generate_process_color(len(self.processes))
            }
            self.processes.append(p)
            self.refresh_process_table()
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid inputs")

    def refresh_process_table(self):
        if self.process_table:
            for item in self.process_table.get_children(): self.process_table.delete(item)
            for p in self.processes:
                self.process_table.insert('', tk.END, values=(p['pid'], p['arrival_time'], p['burst_time']))

    def run_fcfs(self):
        # Sort by arrival
        processes = sorted(self.processes, key=lambda x: x['arrival_time'])
        n = len(processes)
        time = 0
        total_tat, total_wt = 0, 0
        segments = []
        
        for i, p in enumerate(processes):
            if time < p['arrival_time']: time = p['arrival_time']
            start = time
            time += p['burst_time']
            completion_time = time
            
            tat = completion_time - p['arrival_time']
            wt = tat - p['burst_time']
            total_tat += tat
            total_wt += wt
            
            segments.append((i, start, completion_time))
            
        # Metric Calculations
        avg_tat = total_tat / n
        avg_wt = total_wt / n
        cpu_util = (sum(p['burst_time'] for p in processes) / time) * 100
        throughput = n / time
        
        self.update_metrics(avg_tat=avg_tat, avg_wt=avg_wt, cpu_util=cpu_util, throughput=throughput)
        self.animate_execution_loop(segments, processes)