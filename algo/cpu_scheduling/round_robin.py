"""
Round Robin (RR) Scheduler implementation inheriting from SchedulerBase.
Integrates configuration geometry layouts from layout_config.py and theme.py styles.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from base_sjf_rr import SchedulerBase
from utils.cpu_sched_theme import COLORS, FONTS, WINDOW_SIZES
from utils.cpu_sched_config import SIMULATION_PANE, ADD_PROCESS_LAYOUT
from utils.cpu_sched_theme import BG_ROUND_ROBIN

class RoundRobin(SchedulerBase):
    def __init__(self, title, width, height):
        super().__init__(title, width, height)
        # FIX: Point strictly to the Round Robin artwork asset
        self.background_path = BG_ROUND_ROBIN
        self.time_quantum = 2  
        self.process_table = None  
        self.add_process_window = None

    def setup_add_process_window(self):
        """Set up child modal popup matching the native button styling layout."""
        self.add_process_window = tk.Toplevel(self.root)
        self.add_process_window.title("Add Process")
        self.add_process_window.geometry(f"{WINDOW_SIZES['add_process'][0]}x{WINDOW_SIZES['add_process'][1]}")
        self.add_process_window.resizable(False, False)
        self.add_process_window.configure(bg='#2b2b2b')
        self.add_process_window.transient(self.root)  
        self.add_process_window.grab_set()

        main_frame = tk.Frame(self.add_process_window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=ADD_PROCESS_LAYOUT['frame_padding'], pady=ADD_PROCESS_LAYOUT['frame_padding'])

        title_label = tk.Label(main_frame, text="ADD NEW PROCESS", font=FONTS['heading'], bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 20))

        input_frame = tk.Frame(main_frame, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, pady=(0, 20))

        f_width = ADD_PROCESS_LAYOUT['entry_field_width']
        
        tk.Label(input_frame, text="Arrival Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.arrival_entry = tk.Entry(input_frame, font=FONTS['default'], width=f_width)
        self.arrival_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        tk.Label(input_frame, text="Burst Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.burst_entry = tk.Entry(input_frame, font=FONTS['default'], width=f_width)
        self.burst_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        tk.Label(input_frame, text="Time Quantum:", font=FONTS['default'], bg='#2b2b2b', fg='white').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantum_entry = tk.Entry(input_frame, font=FONTS['default'], width=f_width)
        self.quantum_entry.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        self.quantum_entry.insert(0, str(self.time_quantum))

        btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Reusable matching button configuration matrix
        child_btn_props = {
            'font': FONTS['default'],
            'bg': '#ffe6ad',
            'fg': '#000000',
            'relief': tk.SOLID,
            'bd': 1,
            'padx': 20,
            'pady': 8,
            'activebackground': '#ebd29b'
        }

        add_btn = tk.Button(btn_frame, text="Add Process", command=self.add_process, **child_btn_props)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        confirm_btn = tk.Button(btn_frame, text="Confirm", command=self.add_process_window.destroy, **child_btn_props)
        confirm_btn.pack(side=tk.LEFT, padx=10)

        table_frame = tk.Frame(main_frame, bg='#2b2b2b')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        tk.Label(table_frame, text="Process Registry List:", font=FONTS['default'], bg='#2b2b2b', fg='white').pack(anchor=tk.W, pady=(0, 5))

        style = ttk.Style()
        style.configure("Treeview.Heading", font=FONTS['small'])
        style.configure("Treeview", font=FONTS['small'])

        self.process_table = ttk.Treeview(table_frame, columns=('PID', 'Arrival Time', 'Burst Time'), show='headings', height=ADD_PROCESS_LAYOUT['table_row_height'])
        self.process_table.heading('PID', text='Process ID')
        self.process_table.heading('Arrival Time', text='Arrival Time')
        self.process_table.heading('Burst Time', text='Burst Time')
        
        self.process_table.column('PID', width=ADD_PROCESS_LAYOUT['col_pid_width'])
        self.process_table.column('Arrival Time', width=ADD_PROCESS_LAYOUT['col_arrival_width'])
        self.process_table.column('Burst Time', width=ADD_PROCESS_LAYOUT['col_burst_width'])

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.process_table.yview)
        self.process_table.configure(yscrollcommand=scrollbar.set)
        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        table_btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        table_btn_frame.pack(fill=tk.X, pady=(10, 0))

        edit_btn = tk.Button(table_btn_frame, text="Edit Selected", command=self.edit_process, **child_btn_props)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        delete_btn = tk.Button(table_btn_frame, text="Delete Selected", command=self.delete_process, **child_btn_props)
        delete_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_process_table()

    def add_process(self):
        """Validates entry parameters; saves quantum modifications if parameters are left blank."""
        arrival_raw = self.arrival_entry.get().strip()
        burst_raw = self.burst_entry.get().strip()
        quantum_raw = self.quantum_entry.get().strip()

        if not arrival_raw and not burst_raw:
            try:
                time_quantum = int(quantum_raw)
                if time_quantum <= 0: raise ValueError
                self.time_quantum = time_quantum  
                self.add_process_window.destroy()  
                return
            except ValueError:
                messagebox.showerror("Invalid Input", "Time quantum must be an integer greater than 0.")
                return

        try:
            arrival_time = int(arrival_raw)
            burst_time = int(burst_raw)
            time_quantum = int(quantum_raw)

            if arrival_time < 0 or burst_time <= 0 or time_quantum <= 0: raise ValueError
            self.time_quantum = time_quantum

            if len(self.processes) >= 10:
                messagebox.showwarning("Capped Capacity", "Simulation maximum bounds reached (10 Processes).")
                return

            pid = f"P{len(self.processes) + 1}"
            process = {
                'pid': pid, 'arrival_time': arrival_time, 'burst_time': burst_time,
                'remaining_time': burst_time, 'completion_time': 0, 'start_time': -1,
                'color': self.generate_process_color(len(self.processes))
            }
            self.processes.append(process)
            self.refresh_process_table()

            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Provide standard operational integers for parameters.")

    def edit_process(self):
        """Open single unified dialog window styled with thin-bordered yellow properties."""
        selected = self.process_table.selection()
        if not selected: return

        item = self.process_table.item(selected[0])
        pid, arrival_time, burst_time = item['values']
        p_index = next(i for i, p in enumerate(self.processes) if p['pid'] == pid)

        edit_win = tk.Toplevel(self.add_process_window)
        edit_win.title(f"Modify: {pid}")
        edit_win.geometry("380x180")
        edit_win.configure(bg='#2b2b2b')
        edit_win.grab_set()

        tk.Label(edit_win, text="Arrival Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').grid(row=0, column=0, padx=15, pady=15, sticky=tk.W)
        arr_entry = tk.Entry(edit_win, font=FONTS['default'])
        arr_entry.insert(0, str(arrival_time))
        arr_entry.grid(row=0, column=1)

        tk.Label(edit_win, text="Burst Time:", font=FONTS['default'], bg='#2b2b2b', fg='white').grid(row=1, column=0, padx=15, pady=15, sticky=tk.W)
        burst_entry = tk.Entry(edit_win, font=FONTS['default'])
        burst_entry.insert(0, str(burst_time))
        burst_entry.grid(row=1, column=1)

        def save_changes():
            try:
                new_arr = int(arr_entry.get())
                new_burst = int(burst_entry.get())
                if new_arr < 0 or new_burst <= 0: raise ValueError
                self.processes[p_index]['arrival_time'] = new_arr
                self.processes[p_index]['burst_time'] = new_burst
                if 'remaining_time' in self.processes[p_index]:
                    self.processes[p_index]['remaining_time'] = new_burst
                self.refresh_process_table()
                edit_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid metric specifications.")

        save_btn = tk.Button(
            edit_win, text="Save Parameters", font=FONTS['default'], 
            bg='#ffe6ad', fg='#000000', relief=tk.SOLID, bd=1, 
            padx=10, pady=5, command=save_changes
        )
        save_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def delete_process(self):
        selected = self.process_table.selection()
        if not selected: return
        item = self.process_table.item(selected[0])
        pid = item['values'][0]

        self.processes = [p for p in self.processes if p['pid'] != pid]
        for i, process in enumerate(self.processes):
            process['pid'] = f"P{i+1}"
        self.refresh_process_table()

    def refresh_process_table(self):
        if self.process_table:
            self.process_table.delete(*self.process_table.get_children())
            for process in self.processes:
                self.process_table.insert('', tk.END, values=(process['pid'], process['arrival_time'], process['burst_time']))

    def generate_process_color(self, index):
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffe66d', '#f7971e', '#ff9ff3', '#54a0ff']
        return colors[index % len(colors)]

    def open_add_process_window(self):
        if self.add_process_window is None or not self.add_process_window.winfo_exists():
            self.setup_add_process_window()
        else:
            self.add_process_window.lift()
        if self.quantum_entry and self.quantum_entry.winfo_exists():
            self.quantum_entry.delete(0, tk.END)
            self.quantum_entry.insert(0, str(self.time_quantum))

    def reset_simulation(self):
        self.processes.clear()
        self.clear_canvas()
        self.reset_metrics()
        if self.add_process_window and self.add_process_window.winfo_exists():
            self.add_process_window.destroy()

    def start_simulation(self):
        if not self.processes:
            messagebox.showwarning("Empty Context", "No execution tasks staged in memory registers.")
            return
        if self.add_process_window and self.add_process_window.winfo_exists():
            self.add_process_window.destroy()
        self.run_round_robin()

    def run_round_robin(self):
        processes = [p.copy() for p in self.processes]
        processes.sort(key=lambda p: p['arrival_time'])

        time, completed, n = 0, 0, len(processes)
        execution_segments = []
        first_start_times = [-1] * n

        from collections import deque
        ready_queue = deque()
        in_queue = [False] * n
        arrival_idx = 0

        while completed < n or ready_queue:
            while arrival_idx < n and processes[arrival_idx]['arrival_time'] <= time:
                if not in_queue[arrival_idx]:
                    ready_queue.append(arrival_idx)
                    in_queue[arrival_idx] = True
                arrival_idx += 1

            if ready_queue:
                idx = ready_queue.popleft()
                in_queue[idx] = False

                if first_start_times[idx] == -1:
                    first_start_times[idx] = time

                exec_time = min(self.time_quantum, processes[idx]['remaining_time'])
                execution_segments.append((idx, time, time + exec_time))
                time += exec_time
                processes[idx]['remaining_time'] -= exec_time

                while arrival_idx < n and processes[arrival_idx]['arrival_time'] <= time:
                    if not in_queue[arrival_idx]:
                        ready_queue.append(arrival_idx)
                        in_queue[arrival_idx] = True
                    arrival_idx += 1

                if processes[idx]['remaining_time'] > 0:
                    ready_queue.append(idx)
                    in_queue[idx] = True
                else:
                    processes[idx]['completion_time'] = time
                    completed += 1
            else:
                time = processes[arrival_idx]['arrival_time'] if arrival_idx < n else time + 1

        self.animate_execution_loop(execution_segments, processes, first_start_times)

    def animate_execution_loop(self, segments, processes, first_start_times, step=0):
        """Animate process blocks cleanly along a single horizontal row track using SIMULATION_PANE spatial parameters."""
        self.root.update()
        canvas_width = max(self.canvas.winfo_width(), 1000)
        total_time = segments[-1][2] if segments else 1
        
        # Read exact horizontal margins from cpu_sched_config variables
        l_margin = SIMULATION_PANE['left_margin']
        r_margin = SIMULATION_PANE['right_margin']
        time_scale = (canvas_width - (l_margin + r_margin)) / total_time
        
        p_height = SIMULATION_PANE['process_block_height']
        y_start = SIMULATION_PANE['y_start_coordinate']
        t_offset = SIMULATION_PANE['timestamp_offset_y']

        if step == 0:
            self.clear_canvas()

        if step < len(segments):
            proc_idx, s_time, e_time = segments[step]
            process = processes[proc_idx]
            y = y_start 
            
            bar_x = l_margin + s_time * time_scale
            bar_w = (e_time - s_time) * time_scale

            # Seamless process block rendering
            self.canvas.create_rectangle(bar_x, y + 5, bar_x + bar_w, y + 5 + p_height - 10, fill=process['color'], outline='white')
            self.canvas.create_text(bar_x + bar_w / 2, y + 5 + (p_height - 10) / 2, text=process['pid'], fill='white', font=FONTS['default'])
            
            # High-contrast pixelated timestamps printed explicitly at segment boundaries
            self.canvas.create_text(bar_x, y + p_height + t_offset, text=str(s_time), fill='#ffcc00', font=FONTS['metric'], anchor=tk.N)
            self.canvas.create_text(bar_x + bar_w, y + p_height + t_offset, text=str(e_time), fill='#ffcc00', font=FONTS['metric'], anchor=tk.N)

            # Explicitly pass step=step+1 keyword parameter to preserve variable execution scope
            self.root.after(450, lambda: self.animate_execution_loop(segments, processes, first_start_times, step=step+1))
        else:
            self.finalize_metrics_calculations(processes, segments)

    def finalize_metrics_calculations(self, processes, segments):
        n = len(processes)
        total_tat = sum(p['completion_time'] - p['arrival_time'] for p in processes)
        total_wt = sum((p['completion_time'] - p['arrival_time']) - p['burst_time'] for p in processes)
        total_time = segments[-1][2] if segments else 1
        
        avg_tat = total_tat / n
        avg_wt = total_wt / n
        cpu_util = (sum(p['burst_time'] for p in processes) / total_time) * 100
        throughput = n / total_time

        self.update_metrics(avg_tat, avg_wt, cpu_util, throughput)


if __name__ == "__main__":
    app = RoundRobin("Round Robin Scheduler", 1920, 1080)
    app.setup_main_window()
    app.run()