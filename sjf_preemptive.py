"""
Preemptive Shortest Job First (SJF) Scheduler implementation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from scheduler_base import SchedulerBase
from temporary_utils.theme import WINDOW_SIZES


class SJFPreemptive(SchedulerBase):
    """Preemptive Shortest Job First Scheduler."""

    def __init__(self, title, width, height):
        super().__init__(title, width, height)
        self.process_table = None  
        self.add_process_window = None  

    def setup_add_process_window(self):
        """Set up the Add Process popup window using a unified retro typography theme."""
        self.add_process_window = tk.Toplevel(self.root)
        self.add_process_window.title("Add Process")
        self.add_process_window.geometry(f"{WINDOW_SIZES['add_process'][0]}x{WINDOW_SIZES['add_process'][1]}")
        self.add_process_window.resizable(False, False)
        self.add_process_window.configure(bg='#2b2b2b')
        self.add_process_window.transient(self.root)  
        self.add_process_window.grab_set()

        main_frame = tk.Frame(self.add_process_window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = tk.Label(main_frame, text="ADD NEW PROCESS", font=('Courier', 16, 'bold'), bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 20))

        input_frame = tk.Frame(main_frame, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Input Rows with updated pixelated font attributes
        tk.Label(input_frame, text="Arrival Time:", font=('Courier', 12, 'bold'), bg='#2b2b2b', fg='white').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.arrival_entry = tk.Entry(input_frame, font=('Courier', 12, 'bold'), width=20)
        self.arrival_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        tk.Label(input_frame, text="Burst Time:", font=('Courier', 12, 'bold'), bg='#2b2b2b', fg='white').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.burst_entry = tk.Entry(input_frame, font=('Courier', 12, 'bold'), width=20)
        self.burst_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)

        # Control panel buttons
        btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        add_btn = tk.Button(btn_frame, text="Add Process", font=('Courier', 12, 'bold'), bg='#4caf50', fg='white', relief=tk.FLAT, padx=20, pady=10, command=self.add_process)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        confirm_btn = tk.Button(btn_frame, text="Confirm", font=('Courier', 12, 'bold'), bg='#007acc', fg='white', relief=tk.FLAT, padx=20, pady=10, command=self.add_process_window.destroy)
        confirm_btn.pack(side=tk.LEFT, padx=10)

        # Tabular registry list layout segment
        table_frame = tk.Frame(main_frame, bg='#2b2b2b')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        tk.Label(table_frame, text="Process Registry List:", font=('Courier', 12, 'bold'), bg='#2b2b2b', fg='white').pack(anchor=tk.W, pady=(0, 5))

        # Inject styling elements into the default Treeview frame font mapping pipeline
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Courier', 10, 'bold'))
        style.configure("Treeview", font=('Courier', 10, 'bold'))

        self.process_table = ttk.Treeview(table_frame, columns=('PID', 'Arrival Time', 'Burst Time'), show='headings', height=10)
        self.process_table.heading('PID', text='Process ID')
        self.process_table.heading('Arrival Time', text='Arrival Time')
        self.process_table.heading('Burst Time', text='Burst Time')
        self.process_table.column('PID', width=100)
        self.process_table.column('Arrival Time', width=150)
        self.process_table.column('Burst Time', width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.process_table.yview)
        self.process_table.configure(yscrollcommand=scrollbar.set)
        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Table processing items action tray
        table_btn_frame = tk.Frame(main_frame, bg='#2b2b2b')
        table_btn_frame.pack(fill=tk.X, pady=(10, 0))

        edit_btn = tk.Button(table_btn_frame, text="Edit Selected", font=('Courier', 10, 'bold'), bg='#ff9800', fg='white', relief=tk.FLAT, padx=15, pady=5, command=self.edit_process)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        delete_btn = tk.Button(table_btn_frame, text="Delete Selected", font=('Courier', 10, 'bold'), bg='#f44336', fg='white', relief=tk.FLAT, padx=15, pady=5, command=self.delete_process)
        delete_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_process_table()

    def add_process(self):
        if len(self.processes) >= 10:
            messagebox.showwarning("Capped Capacity", "Simulation maximum boundary condition reached (10 Processes).")
            return
        try:
            arrival_time = int(self.arrival_entry.get())
            burst_time = int(self.burst_entry.get())

            if arrival_time < 0 or burst_time <= 0: raise ValueError

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
            messagebox.showerror("Invalid Input", "Provide standard integers for parameters.")

    def edit_process(self):
        """Open a single unified dialog frame to edit all process specs under a retro layout."""
        selected = self.process_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please choose a target process entry.")
            return

        item = self.process_table.item(selected[0])
        pid, arrival_time, burst_time = item['values']
        p_index = next(i for i, p in enumerate(self.processes) if p['pid'] == pid)

        edit_win = tk.Toplevel(self.add_process_window)
        edit_win.title(f"Modify: {pid}")
        edit_win.geometry("380x180")
        edit_win.configure(bg='#2b2b2b')
        edit_win.grab_set()

        tk.Label(edit_win, text="Arrival Time:", font=('Courier', 11, 'bold'), bg='#2b2b2b', fg='white').grid(row=0, column=0, padx=15, pady=15, sticky=tk.W)
        arr_entry = tk.Entry(edit_win, font=('Courier', 11, 'bold'))
        arr_entry.insert(0, str(arrival_time))
        arr_entry.grid(row=0, column=1)

        tk.Label(edit_win, text="Burst Time:", font=('Courier', 11, 'bold'), bg='#2b2b2b', fg='white').grid(row=1, column=0, padx=15, pady=15, sticky=tk.W)
        burst_entry = tk.Entry(edit_win, font=('Courier', 11, 'bold'))
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

        save_btn = tk.Button(edit_win, text="Save Parameters", font=('Courier', 11, 'bold'), bg='#4caf50', fg='white', relief=tk.FLAT, padx=10, pady=5, command=save_changes)
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
        self.run_preemptive_sjf()

    def run_preemptive_sjf(self):
        processes = [p.copy() for p in self.processes]
        time, completed, n = 0, 0, len(processes)
        is_completed = [False] * n
        completion_times = [0] * n
        start_times = [-1] * n
        execution_segments = []

        while completed != n:
            idx = -1
            min_remaining = float('inf')

            for i in range(n):
                if processes[i]['arrival_time'] <= time and not is_completed[i]:
                    if processes[i]['remaining_time'] < min_remaining:
                        min_remaining = processes[i]['remaining_time']
                        idx = i
                    elif processes[i]['remaining_time'] == min_remaining and idx != -1:
                        if processes[i]['arrival_time'] < processes[idx]['arrival_time']:
                            idx = i

            if idx != -1:
                if start_times[idx] == -1:
                    start_times[idx] = time
                processes[idx]['remaining_time'] -= 1
                time += 1

                if execution_segments and execution_segments[-1][0] == idx:
                    execution_segments[-1] = (idx, execution_segments[-1][1], time)
                else:
                    execution_segments.append((idx, time - 1, time))

                if processes[idx]['remaining_time'] == 0:
                    completion_times[idx] = time
                    is_completed[idx] = True
                    completed += 1
            else:
                time += 1

        self.animate_execution_loop(execution_segments, processes, start_times, completion_times)

    def animate_execution_loop(self, segments, processes, *args, step=0):
        """Animate process blocks along a single horizontal track using explicit step tracking."""
        self.root.update()
        canvas_width = max(self.canvas.winfo_width(), 1000)
        total_time = segments[-1][2] if segments else 1
        time_scale = (canvas_width - 200) / total_time
        process_height, y_start = 60, 100

        if step == 0:
            self.clear_canvas()

        if step < len(segments):
            proc_idx, s_time, e_time = segments[step]
            process = processes[proc_idx]
            y = y_start 
            
            bar_x = 100 + s_time * time_scale
            bar_w = (e_time - s_time) * time_scale

            # Seamless process block
            self.canvas.create_rectangle(bar_x, y + 5, bar_x + bar_w, y + 5 + process_height - 10, fill=process['color'], outline='white')
            
            # Internal ID text using your new pixelated font scheme
            self.canvas.create_text(bar_x + bar_w / 2, y + 5 + (process_height - 10) / 2, text=process['pid'], fill='white', font=('Courier', 12, 'bold'))
            
            # High-contrast, large pixelated timestamps
            self.canvas.create_text(bar_x, y + process_height + 15, text=str(s_time), fill='#ffcc00', font=('Courier', 14, 'bold'), anchor=tk.N)
            self.canvas.create_text(bar_x + bar_w, y + process_height + 15, text=str(e_time), fill='#ffcc00', font=('Courier', 14, 'bold'), anchor=tk.N)

            # FIX: Explicitly specify step as a keyword argument so it doesn't get swallowed by *args
            if len(args) == 2:  # SJF
                self.root.after(400, lambda: self.animate_execution_loop(segments, processes, args[0], args[1], step=step+1))
            else:  # Round Robin
                self.root.after(450, lambda: self.animate_execution_loop(segments, processes, args[0], step=step+1))
        else:
            if len(args) == 2:
                self.finalize_metrics_calculations(processes, args[1])
            else:
                self.finalize_metrics_calculations(processes, segments)

    def finalize_metrics_calculations(self, processes, completion_times):
        n = len(processes)
        total_tat = sum(completion_times[i] - processes[i]['arrival_time'] for i in range(n))
        total_wt = sum((completion_times[i] - processes[i]['arrival_time']) - processes[i]['burst_time'] for i in range(n))
        total_time = max(completion_times) if completion_times else 1
        
        avg_tat = total_tat / n
        avg_wt = total_wt / n
        cpu_util = (sum(p['burst_time'] for p in processes) / total_time) * 100
        throughput = n / total_time

        self.update_metrics(avg_tat, avg_wt, cpu_util, throughput)


if __name__ == "__main__":
    app = SJFPreemptive("Preemptive SJF Scheduler", 1920, 1080)
    app.setup_main_window()
    app.run()