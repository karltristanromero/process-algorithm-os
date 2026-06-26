"""
First-Come, First-Served (FCFS) Scheduler implementation.
Refactored for safe window management and correct metric ordering.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Optional

from scheduler_base import SchedulerBase
from temporary_utils.theme import FONTS, WINDOW_SIZES, BG_FCFS
from temporary_utils.layout_config import SIMULATION_PANE

class FCFS(SchedulerBase):
    def __init__(self, title: str, width: int, height: int):
        super().__init__(title, width, height)
        self.background_path = BG_FCFS
        self.arrival_entry: Optional[tk.Entry] = None
        self.burst_entry: Optional[tk.Entry] = None

    def setup_add_process_window(self):
        self.add_process_window = tk.Toplevel(self.root)
        self.add_process_window.title("Add Process")
        self.add_process_window.geometry(f"{WINDOW_SIZES['add_process'][0]}x{WINDOW_SIZES['add_process'][1]}")
        self.add_process_window.grab_set()

        frame = tk.Frame(self.add_process_window, bg='#2b2b2b')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Arrival Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').pack()
        self.arrival_entry = tk.Entry(frame, font=FONTS['default'])
        self.arrival_entry.pack(pady=(0, 10))

        tk.Label(frame, text="Burst Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').pack()
        self.burst_entry = tk.Entry(frame, font=FONTS['default'])
        self.burst_entry.pack(pady=(0, 20))

        tk.Button(frame, text="Add Process", command=self.add_process, bg='#ffe6ad').pack()

    def add_process(self):
        assert self.arrival_entry is not None
        assert self.burst_entry is not None
        
        try:
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            
            process = {
                'pid': f"P{len(self.processes) + 1}",
                'arrival_time': arrival,
                'burst_time': burst,
                'color': self.generate_process_color(len(self.processes))
            }
            self.processes.append(process)
            
            # Close window BEFORE showing messagebox to prevent focus/closing bugs
            if self.add_process_window:
                self.add_process_window.destroy()
                self.add_process_window = None
                
            messagebox.showinfo("Success", f"{process['pid']} added successfully.")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid inputs. Please enter integers.")

    def start_simulation(self):
        if not self.processes:
            messagebox.showwarning("Empty", "No tasks.")
            return
        self.run_fcfs()

    def run_fcfs(self):
        processes = sorted(self.processes, key=lambda p: p['arrival_time'])
        current_time = 0
        segments = []
        
        for p in processes:
            if current_time < p['arrival_time']:
                current_time = p['arrival_time']
            start = current_time
            current_time += p['burst_time']
            p['completion_time'] = current_time
            segments.append((self.processes.index(p), start, current_time))
            
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
            self.root.after(500, lambda: self.animate_execution_loop(segments, processes, None, step+1))
        else:
            self.finalize_metrics(processes, segments)

    def finalize_metrics(self, processes, segments):
        n = len(processes)
        total_time = segments[-1][2]
        
        avg_tat = sum(p['completion_time'] - p['arrival_time'] for p in processes) / n
        avg_wt = sum((p['completion_time'] - p['arrival_time']) - p['burst_time'] for p in processes) / n
        cpu_util = (sum(p['burst_time'] for p in processes) / total_time) * 100
        throughput = n / total_time
        
        # Order: WT, TAT, Throughput, CPU
        self.update_metrics(avg_wt, avg_tat, throughput, cpu_util)

    def reset_simulation(self):
        self.processes.clear()
        self.clear_canvas()
        self.reset_metrics()
        if self.add_process_window:
            self.add_process_window.destroy()
            self.add_process_window = None

    def open_add_process_window(self): self.setup_add_process_window()