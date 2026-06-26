"""
Priority Non-Preemptive (PNP) Scheduler implementation.
Refactored for safe window management and consistent metric ordering.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Optional

from scheduler_base import SchedulerBase
from temporary_utils.theme import FONTS, WINDOW_SIZES, BG_PRIORITY_NON_PREEMPTIVE
from temporary_utils.layout_config import SIMULATION_PANE

class PriorityNonPreemptive(SchedulerBase):
    def __init__(self, title: str, width: int, height: int):
        super().__init__(title, width, height)
        self.background_path = BG_PRIORITY_NON_PREEMPTIVE
        self.arrival_entry: Optional[tk.Entry] = None
        self.burst_entry: Optional[tk.Entry] = None
        self.priority_entry: Optional[tk.Entry] = None

    def setup_add_process_window(self):
        self.add_process_window = tk.Toplevel(self.root)
        self.add_process_window.title("Add Process")
        self.add_process_window.geometry("300x320")
        self.add_process_window.grab_set()

        main_frame = tk.Frame(self.add_process_window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        fields = [("Arrival Time:", "arrival_entry"), 
                  ("Burst Time:", "burst_entry"), 
                  ("Priority (Low # = High):", "priority_entry")]
        
        for label, attr in fields:
            tk.Label(main_frame, text=label, font=FONTS['default'], bg='#2b2b2b', fg='white').pack()
            entry = tk.Entry(main_frame, font=FONTS['default'])
            entry.pack(pady=(0, 10))
            setattr(self, attr, entry)

        tk.Button(main_frame, text="Add Process", command=self.add_process, bg='#ffe6ad').pack(pady=10)

    def add_process(self):
        # Pylance type safety
        assert self.arrival_entry is not None
        assert self.burst_entry is not None
        assert self.priority_entry is not None

        try:
            p = {
                'pid': f"P{len(self.processes) + 1}",
                'arrival_time': int(self.arrival_entry.get()),
                'burst_time': int(self.burst_entry.get()),
                'priority': int(self.priority_entry.get()),
                'color': self.generate_process_color(len(self.processes))
            }
            self.processes.append(p)
            
            # Destroy window before messagebox to fix focus bug
            if self.add_process_window:
                self.add_process_window.destroy()
                self.add_process_window = None
                
            messagebox.showinfo("Success", f"{p['pid']} added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Enter valid integers.")

    def start_simulation(self):
        if not self.processes: return
        self.run_pnp()

    def run_pnp(self):
        processes = sorted(self.processes, key=lambda p: p['arrival_time'])
        time = 0
        completed_tasks = []
        ready_queue = []
        remaining = [p.copy() for p in processes]
        
        while len(completed_tasks) < len(processes):
            for p in remaining[:]:
                if p['arrival_time'] <= time:
                    ready_queue.append(p)
                    remaining.remove(p)
            
            if not ready_queue:
                if remaining:
                    time = min(p['arrival_time'] for p in remaining)
                    continue
                break
            
            curr = min(ready_queue, key=lambda x: x['priority'])
            ready_queue.remove(curr)
            
            start = time
            time += curr['burst_time']
            curr['completion_time'] = time
            curr['tat'] = curr['completion_time'] - curr['arrival_time']
            curr['wt'] = curr['tat'] - curr['burst_time']
            
            completed_tasks.append((curr, start, time))
            
        self.animate_execution_loop(completed_tasks)

    def animate_execution_loop(self, completed_tasks, step=0):
        canvas = self.canvas
        if canvas is None: return
        
        self.root.update()
        if step == 0: self.clear_canvas()

        if step < len(completed_tasks):
            p, s, e = completed_tasks[step]
            canvas_width = max(canvas.winfo_width(), 1000)
            
            y_pos = SIMULATION_PANE['y_start_coordinate']
            p_height = SIMULATION_PANE['process_block_height']
            l_margin = SIMULATION_PANE['left_margin']
            r_margin = SIMULATION_PANE['right_margin']
            time_scale = (canvas_width - l_margin - r_margin) / completed_tasks[-1][2]
            
            x, w = l_margin + s * time_scale, (e - s) * time_scale
            canvas.create_rectangle(x, y_pos, x + w, y_pos + p_height, fill=p['color'], outline='white')
            canvas.create_text(x + w/2, y_pos + (p_height/2), text=p['pid'], fill='white', font=FONTS['default'])
            
            self.root.after(600, lambda: self.animate_execution_loop(completed_tasks, step+1))
        else:
            self.finalize_metrics(completed_tasks)

    def finalize_metrics(self, completed_tasks):
        processes = [c[0] for c in completed_tasks]
        n = len(processes)
        total_time = completed_tasks[-1][2]
        
        avg_tat = sum(p['tat'] for p in processes) / n
        avg_wt = sum(p['wt'] for p in processes) / n
        cpu_util = (sum(p['burst_time'] for p in processes) / total_time) * 100
        throughput = n / total_time
        
        # New synchronized order: WT, TAT, Throughput, CPU
        self.update_metrics(avg_wt, avg_tat, throughput, cpu_util)

    def reset_simulation(self):
        self.processes.clear()
        self.clear_canvas()
        self.reset_metrics()
        if self.add_process_window:
            self.add_process_window.destroy()
            self.add_process_window = None

    def open_add_process_window(self): self.setup_add_process_window()