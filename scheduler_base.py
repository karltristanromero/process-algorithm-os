import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

from temporary_utils.layout_config import (
    GANTT_CHART,
    METRIC_LOCATIONS
)
from temporary_utils.theme import UI_CONFIG


class SchedulerBase:

    def __init__(self, title: str, width: int, height: int):

        self.root = tk.Tk()
        self.root.title(title)
        self.root.overrideredirect(True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.root.geometry(f"{screen_w}x{screen_h}+0+0")

        # Encapsulated attributes
        self._processes = []
        self._metrics_labels = {}

        self._canvas = Canvas(
            self.root,
            bd=0,
            highlightthickness=0,
            bg="#F3EEFF"
        )

        self._bg_image = None
        self._bg_label = None

        self.root.bind("<ButtonPress-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._do_move)

    # =================================================
    # Window Dragging
    # =================================================

    def _start_move(self, event):
        self._x = event.x
        self._y = event.y

    def _do_move(self, event):
        x = self.root.winfo_x() + (event.x - self._x)
        y = self.root.winfo_y() + (event.y - self._y)
        self.root.geometry(f"+{x}+{y}")

    # =================================================
    # Background
    # =================================================

    def set_background(self, image_path):

        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        image = Image.open(image_path)
        image = image.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )

        self._bg_image = ImageTk.PhotoImage(image)

        if self._bg_label is not None:
            self._bg_label.destroy()

        self._bg_label = tk.Label(
            self.root,
            image=self._bg_image,
            bd=0
        )

        self._bg_label.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        self._bg_label.lower()

    # =================================================
    # Main Window
    # =================================================

    def setup_main_window(self):

        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        self._canvas.place(
            x=GANTT_CHART["relx"] * width,
            y=GANTT_CHART["rely"] * height,
            width=GANTT_CHART["relwidth"] * width,
            height=GANTT_CHART["relheight"] * height
        )

        for key, pos in METRIC_LOCATIONS.items():

            lbl = tk.Label(
                self.root,
                text="--",
                bg="#FFFFFF",
                fg=UI_CONFIG["text_color"],
                font=(
                    UI_CONFIG["font_family"],
                    UI_CONFIG["font_size"]
                )
            )

            lbl.place(
                x=pos["relx"] * width,
                y=pos["rely"] * height,
                anchor="center"
            )

            self._metrics_labels[key] = lbl

    # =================================================
    # Public Process Methods
    # =================================================

    def add_process(self, process):
        self._processes.append(process)

    def get_processes(self):
        return self._processes

    # =================================================
    # Shared Utility Methods
    # =================================================

    def generate_process_color(self, index):

        colors = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FFEAA7",
            "#DDA0DD",
            "#F4A261",
            "#A8DADC",
            "#74B9FF",
            "#55EFC4"
        ]

        return colors[index % len(colors)]

    def clear_canvas(self):
        self._canvas.delete("all")

    def reset_metrics(self):

        for lbl in self._metrics_labels.values():
            lbl.config(text="--")

    def update_metrics(
        self,
        avg_tat,
        avg_wt,
        cpu_util,
        throughput
    ):

        self._metrics_labels["avg_tat"].config(
            text=f"{avg_tat:.2f}"
        )

        self._metrics_labels["avg_wt"].config(
            text=f"{avg_wt:.2f}"
        )

        self._metrics_labels["cpu_util"].config(
            text=f"{cpu_util:.2f}%"
        )

        self._metrics_labels["throughput"].config(
            text=f"{throughput:.2f}"
        )

    # =================================================
    # Gantt Chart
    # =================================================

    def animate_execution_loop(
        self,
        segments,
        processes
    ):

        self.clear_canvas()

        if not segments:
            return

        self.root.update_idletasks()

        width = self._canvas.winfo_width()
        height = self._canvas.winfo_height()

        total_time = max(segment[2] for segment in segments)

        if total_time <= 0:
            total_time = 1

        top = 20
        bottom = height - 35

        for process_index, start, end in segments:

            x1 = (start / total_time) * width
            x2 = (end / total_time) * width

            self._canvas.create_rectangle(
                x1,
                top,
                x2,
                bottom,
                fill=processes[process_index]["color"],
                outline="black",
                width=2
            )

            self._canvas.create_text(
                (x1 + x2) / 2,
                (top + bottom) / 2,
                text=processes[process_index]["pid"],
                font=("Arial", 10, "bold")
            )

            self._canvas.create_text(
                x1,
                bottom + 15,
                text=str(start),
                anchor="n"
            )

        self._canvas.create_text(
            width,
            bottom + 15,
            text=str(total_time),
            anchor="ne"
        )

    # =================================================
    # Mainloop
    # =================================================

    def run(self):
        self.root.mainloop()