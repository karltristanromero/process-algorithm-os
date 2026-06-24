import tkinter as tk
from typing import Optional, Dict

class SchedulerBase:
    def __init__(self, title: str, width: int, height: int):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.state('zoomed')
        self.root.configure(bg="#2b2b2b")
        self.processes = []
        self.canvas: Optional[tk.Canvas] = None
        self.metrics_labels: Dict[str, tk.Label] = {}

    def setup_main_window(self):
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        control_frame = tk.Frame(main_frame, bg="#2b2b2b")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        btn_config = {'font': ("Helvetica", 12, "bold"), 'fg': "white"}
        tk.Button(control_frame, text="Start", bg="#4caf50", command=self.start_simulation, **btn_config).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Add Process", bg="#ff9800", command=self.open_add_process_window, **btn_config).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset", bg="#f44336", command=self.reset_simulation, **btn_config).pack(side=tk.LEFT, padx=5)

        metrics_frame = tk.Frame(main_frame, bg="#1e1e1e", bd=2, relief=tk.RAISED)
        metrics_frame.pack(fill=tk.X, pady=(0, 20))
        for i, label in enumerate(["Average TAT", "Average WT", "CPU Utilization", "Throughput"]):
            key = label.lower().replace(" ", "_")
            tk.Label(metrics_frame, text=f"{label}:", bg="#1e1e1e", fg="#cccccc").grid(row=0, column=i*2, padx=10)
            self.metrics_labels[key] = tk.Label(metrics_frame, text="--", bg="#1e1e1e", fg="white")
            self.metrics_labels[key].grid(row=0, column=i*2+1, padx=(0, 20))

        self.canvas = tk.Canvas(main_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def update_metrics(self, avg_tat: float, avg_wt: float, cpu_util: float, throughput: float):
        """Updates the metrics panel labels."""
        if "average_tat" in self.metrics_labels:
            self.metrics_labels["average_tat"].config(text=f"{avg_tat:.2f}")
            self.metrics_labels["average_wt"].config(text=f"{avg_wt:.2f}")
            self.metrics_labels["cpu_utilization"].config(text=f"{cpu_util:.2f}%")
            self.metrics_labels["throughput"].config(text=f"{throughput:.2f}")

    def reset_metrics(self):
        for label in self.metrics_labels.values():
            label.config(text="--")

    def generate_process_color(self, i: int) -> str:
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffe66d', '#f7971e', '#ff9ff3', '#54a0ff']
        return colors[i % len(colors)]

    def animate_execution_loop(self, segments, processes, step=0):
        if not self.canvas: return
        self.root.update()
        if step == 0: self.canvas.delete("all")
        if step < len(segments):
            idx, s, e = segments[step]
            width = (e - s) * 20
            self.canvas.create_rectangle(50 + s*20, 100, 50 + e*20, 160, fill=processes[idx]['color'])
            self.canvas.create_text(50 + s*20 + width/2, 130, text=processes[idx]['pid'], fill='white')
            self.root.after(400, lambda: self.animate_execution_loop(segments, processes, step + 1))

    def clear_canvas(self):
        if self.canvas: self.canvas.delete("all")

    def start_simulation(self): pass
    def reset_simulation(self): pass
    def open_add_process_window(self): pass
    def run(self): self.root.mainloop()