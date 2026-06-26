"""
Priority Preemptive (PP) Scheduler implementation.
Refactored for safe window management and correct metric ordering.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Optional

from base_fcfs_prio import SchedulerBase
from temporary_utils.theme import FONTS, WINDOW_SIZES, BG_PRIORITY_PREEMPTIVE
from temporary_utils.layout_config import SIMULATION_PANE

class PriorityPreemptive(SchedulerBase):
    def __init__(self, title: str, width: int, height: int):
        super().__init__(title, width, height)
        self.background_path = BG_PRIORITY_PREEMPTIVE
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

        tk.Label(main_frame, text="Arrival Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').pack()
        self.arrival_entry = tk.Entry(main_frame, font=FONTS['default'])
        self.arrival_entry.pack(pady=(0, 10))

        tk.Label(main_frame, text="Burst Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').pack()
        self.burst_entry = tk.Entry(main_frame, font=FONTS['default'])
        self.burst_entry.pack(pady=(0, 10))

        tk.Label(main_frame, text="Priority (Low # = High):", font=FONTS['default'], bg='#2b2b2b', fg='white').pack()
        self.priority_entry = tk.Entry(main_frame, font=FONTS['default'])
        self.priority_entry.pack(pady=(0, 10))

        tk.Button(main_frame, text="Add Process", command=self.add_process, bg='#ffe6ad').pack(pady=10)

    def add_process(self):
        assert self.arrival_entry is not None
        assert self.burst_entry is not None
        assert self.priority_entry is not None
        
        try:
            p = {
                'pid': f"P{len(self.processes) + 1}",
                'arrival_time': int(self.arrival_entry.get()),
                'burst_time': int(self.burst_entry.get()),
                'priority': int(self.priority_entry.get()),
                'remaining_time': int(self.burst_entry.get()),
                'color': self.generate_process_color(len(self.processes))
            }
            self.processes.append(p)
            
            # Destroy window before showing message
            if self.add_process_window:
                self.add_process_window.destroy()
                self.add_process_window = None
                
            messagebox.showinfo("Success", f"{p['pid']} added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Enter valid integers.")

    def start_simulation(self):
        if not self.processes: return
        self.run_pp()

    def run_pp(self):
        processes = [p.copy() for p in self.processes]
        time, completed, n = 0, 0, len(processes)
        execution_log = []
        last_idx = -1

        while completed < n:
            available = [i for i, p in enumerate(processes) if p['arrival_time'] <= time and p['remaining_time'] > 0]
            if not available:
                time += 1
                continue
            
            idx = min(available, key=lambda i: processes[i]['priority'])
            
            if idx != last_idx:
                execution_log.append({'idx': idx, 'start': time})
                last_idx = idx
            
            processes[idx]['remaining_time'] -= 1
            time += 1
            
            if processes[idx]['remaining_time'] == 0:
                processes[idx]['completion_time'] = time
                completed += 1
                last_idx = -1

        segments = []
        for i in range(len(execution_log)):
            start = execution_log[i]['start']
            end = execution_log[i+1]['start'] if i + 1 < len(execution_log) else time
            segments.append((execution_log[i]['idx'], start, end))
            
        self.animate_execution_loop(segments, processes, None)

    def animate_execution_loop(self, segments, processes, first_start_times, step=0):
        canvas = self.canvas
        if canvas is None: return
        
        self.root.update()
        total_time = segments[-1][2]
        
        y_pos = SIMULATION_PANE['y_start_coordinate']
        p_height = SIMULATION_PANE['process_block_height']
        l_margin = SIMULATION_PANE['left_margin']
        r_margin = SIMULATION_PANE['right_margin']
        time_scale = (max(canvas.winfo_width(), 1000) - l_margin - r_margin) / total_time
        
        if step == 0: self.clear_canvas()

        if step < len(segments):
            proc_idx, s, e = segments[step]
            p = processes[proc_idx]
            x, w = l_margin + s * time_scale, (e - s) * time_scale
            canvas.create_rectangle(x, y_pos, x + w, y_pos + p_height, fill=p['color'], outline='white')
            canvas.create_text(x + w/2, y_pos + (p_height/2), text=p['pid'], fill='white', font=FONTS['default'])
            self.root.after(400, lambda: self.animate_execution_loop(segments, processes, None, step+1))
        else:
            self.finalize_metrics(processes, segments)

    def finalize_metrics(self, processes, segments):
        n = len(processes)
        total_time = segments[-1][2]
        
        avg_tat = sum(p['completion_time'] - p['arrival_time'] for p in processes) / n
        avg_wt = sum((p['completion_time'] - p['arrival_time']) - p['burst_time'] for p in processes) / n
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