import tkinter as tk
from tkinter import messagebox

from scheduler_base import SchedulerBase
from temporary_utils.theme import BACKGROUND_MAP, UI_CONFIG


class PriorityPreemptive(SchedulerBase):

    def __init__(self, title, width, height):
        super().__init__(title, width, height)

        self.set_background(BACKGROUND_MAP["PRIO_PREEMPT"])
        self.setup_main_window()
        self.add_nav_buttons()

    # =================================================
    # Navigation Buttons
    # =================================================

    def add_nav_buttons(self):

        style = {
            "bg": UI_CONFIG["button_bg"],
            "fg": "black",
            "font": ("Georgia", 16, "bold"),
            "width": 8,
            "height": 1,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": UI_CONFIG["button_bg"],
            "activeforeground": "black",
            "highlightthickness": 0,
            "padx": 68,
            "pady": 15
        }

        tk.Button(
            self.root,
            text="MENU",
            command=self.root.destroy,
            **style
        ).place(relx=0.0967, rely=0.955, anchor="center")

        tk.Button(
            self.root,
            text="START",
            command=self.start_simulation,
            **style
        ).place(relx=0.271, rely=0.955, anchor="center")

        tk.Button(
            self.root,
            text="ADD",
            command=self.open_add_process_window,
            **style
        ).place(relx=0.45, rely=0.955, anchor="center")

        tk.Button(
            self.root,
            text="RESET",
            command=self.reset_simulation,
            **style
        ).place(relx=0.625, rely=0.955, anchor="center")

    # =================================================
    # Add Process Window
    # =================================================

    def open_add_process_window(self):

        win = tk.Toplevel(self.root)
        win.title("Add Process")
        win.geometry("300x230")

        tk.Label(win, text="Arrival Time").pack(pady=5)
        arr_ent = tk.Entry(win)
        arr_ent.pack()

        tk.Label(win, text="Burst Time").pack(pady=5)
        brst_ent = tk.Entry(win)
        brst_ent.pack()

        tk.Label(win, text="Priority").pack(pady=5)
        prio_ent = tk.Entry(win)
        prio_ent.pack()

        tk.Button(
            win,
            text="Add",
            command=lambda: self.add_process(
                win,
                arr_ent,
                brst_ent,
                prio_ent
            )
        ).pack(pady=15)

    # =================================================
    # Add Process
    # =================================================

    def add_process(self, win, arr_ent, brst_ent, prio_ent):

        try:

            arrival = int(arr_ent.get())
            burst = int(brst_ent.get())
            priority = int(prio_ent.get())

            process = {
                "pid": f"P{len(self._processes)+1}",
                "arrival_time": arrival,
                "burst_time": burst,
                "remaining_time": burst,
                "priority": priority,
                "color": self.generate_process_color(
                    len(self._processes)
                )
            }

            super().add_process(process)

            messagebox.showinfo(
                "Success",
                f"{process['pid']} added successfully."
            )

            win.destroy()

        except ValueError:

            messagebox.showerror(
                "Error",
                "Please enter valid integers."
            )

    # =================================================
    # Priority Preemptive Algorithm
    # =================================================

    def start_simulation(self):

        if not self._processes:

            messagebox.showwarning(
                "Warning",
                "No processes to schedule!"
            )

            return

        time = 0
        completed = 0
        total = len(self._processes)

        segments = []
        current = None

        while completed < total:

            available = [
                p for p in self._processes
                if p["arrival_time"] <= time
                and p["remaining_time"] > 0
            ]

            if not available:
                time += 1
                continue

            next_process = min(
                available,
                key=lambda p: (
                    p["priority"],
                    p["arrival_time"]
                )
            )

            if current != next_process:

                segments.append(
                    (
                        self._processes.index(next_process),
                        time,
                        time
                    )
                )

                current = next_process

            next_process["remaining_time"] -= 1
            time += 1

            segments[-1] = (
                segments[-1][0],
                segments[-1][1],
                time
            )

            if next_process["remaining_time"] == 0:

                completed += 1

                completion = time
                tat = completion - next_process["arrival_time"]
                wt = tat - next_process["burst_time"]

                next_process["tat"] = tat
                next_process["wt"] = wt

                current = None

        avg_tat = sum(
            p["tat"] for p in self._processes
        ) / total

        avg_wt = sum(
            p["wt"] for p in self._processes
        ) / total

        cpu_util = (
            sum(
                p["burst_time"]
                for p in self._processes
            )
            / time
        ) * 100

        throughput = total / time

        self.update_metrics(
            avg_tat,
            avg_wt,
            cpu_util,
            throughput
        )

        self.animate_execution_loop(
            segments,
            self._processes
        )

    # =================================================
    # Reset
    # =================================================

    def reset_simulation(self):

        for process in self._processes:
            process["remaining_time"] = process["burst_time"]

            process.pop("tat", None)
            process.pop("wt", None)

        self.clear_canvas()
        self.reset_metrics()

    # =================================================
    # Mainloop
    # =================================================

    def run(self):

        self.root.mainloop()