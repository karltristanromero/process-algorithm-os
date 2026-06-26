# main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from typing import List
import sys
import os
from pathlib import Path

# Force current directory visibility
current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import your renamed configuration file as 'config'
import ui_config as config
import core_algorithms as algorithms

class DiskSchedulerGUI:
    """GUI application for disk scheduling simulation"""
    
    def __init__(self, root):
        self.ui_images = {}
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.configure(bg=config.COLORS["bg_main"])
        
        self.algorithms = {
            "FCFS": algorithms.FCFS,
            "SSTF": algorithms.SSTF,
            "SCAN": algorithms.SCAN,
            "C-SCAN": algorithms.CSCAN,
            "LOOK": algorithms.LOOK,
            "C-LOOK": algorithms.CLOOK
        }
        
        self.configure_styles()
        self.create_widgets()

    def configure_styles(self):
        """Configure TTK styles pulling values from config module"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=config.COLORS["bg_frame"])
        style.configure('TLabel', background=config.COLORS["bg_frame"], foreground=config.COLORS["fg_text"], font=config.FONTS["label"])
        style.configure('TButton', font=config.FONTS["label"])
        style.configure('Title.TLabel', background=config.COLORS["bg_frame"], foreground=config.COLORS["fg_text"], font=config.FONTS["title"])
        style.configure('Retro.TLabelframe', background=config.COLORS["bg_retro_box"], bordercolor=config.COLORS["border_retro"], relief='solid')
        style.configure('Retro.TLabelframe.Label', background=config.COLORS["bg_retro_box"], foreground=config.COLORS["fg_text"], font=config.FONTS["retro_title"])
        style.configure('Retro.TCheckbutton', background=config.COLORS["bg_retro_box"], foreground=config.COLORS["fg_text"], font=config.FONTS["label"])
        style.configure('Retro.TRadiobutton', background=config.COLORS["bg_retro_box"], foreground=config.COLORS["fg_text"], font=config.FONTS["label"])

    def load_ui_image(self, filename: str) -> tk.PhotoImage:
        """Load and cache an image safely from resolved assets path"""
        if filename not in self.ui_images:
            self.ui_images[filename] = tk.PhotoImage(file=str(config.ASSETS_DIR / filename))
        return self.ui_images[filename]

    def create_image_button(self, parent, filename: str, command, bg_color):
        """Create a clickable image button wrapper"""
        image = self.load_ui_image(filename)
        button = tk.Button(
            parent, image=image, command=command, bd=0, relief="flat",
            highlightthickness=0, cursor="hand2", bg=bg_color, activebackground=bg_color
        )
        button.image = image
        return button

    def toggle_section(self, section_frame, grid_kwargs):
        """Show or hide a GUI section dynamically using layout configs"""
        if section_frame.winfo_ismapped():
            section_frame.grid_forget()
        else:
            section_frame.grid(**grid_kwargs)
   
    def create_widgets(self):
        """Build layouts dynamically binding configuration limits"""
        self.background_image = self.load_ui_image("bg3.png")
        self.root.geometry(f"{self.background_image.width()}x{self.background_image.height()}")
        
        background_label = tk.Label(self.root, image=self.background_image, bd=0)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.lower()

        # Grid configuration mapped directly on layout restrictions
        self.root.columnconfigure(0, weight=0, minsize=config.LEFT_PANEL_MIN_SIZE)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=0)

        # Input Parameters Section
        self.input_section = ttk.LabelFrame(self.root, text="Input Parameters", style='Retro.TLabelframe', padding=12)
        
        ttk.Label(self.input_section, text="DISK REQUESTS (COMMA-SEPARATED)").pack(anchor=tk.W, padx=(5, 0), pady=(0, 4))
        self.requests_entry = tk.Entry(self.input_section, width=38, font=config.FONTS["entry"], bd=0, relief='flat', bg=config.COLORS["bg_entry"], fg=config.COLORS["fg_dark"], insertbackground=config.COLORS["fg_dark"])
        self.requests_entry.pack(fill=tk.X, padx=(5, 0), pady=(0, 12), ipady=6)
        self.requests_entry.insert(0, config.DEFAULT_REQUESTS)

        ttk.Label(self.input_section, text="INITIAL HEAD POSITION").pack(anchor=tk.W, padx=(5, 0), pady=(0, 4))
        self.head_entry = tk.Entry(self.input_section, width=38, font=config.FONTS["entry"], bd=0, relief='flat', bg=config.COLORS["bg_entry"], fg=config.COLORS["fg_dark"], insertbackground=config.COLORS["fg_dark"])
        self.head_entry.pack(fill=tk.X, padx=(5, 0), pady=(0, 12), ipady=6)
        self.head_entry.insert(0, config.DEFAULT_HEAD)

        ttk.Label(self.input_section, text="DISK SIZE (CYLINDERS)").pack(anchor=tk.W, padx=(5, 0), pady=(0, 4))
        self.disk_size_entry = tk.Entry(self.input_section, width=38, font=config.FONTS["entry"], bd=0, relief='flat', bg=config.COLORS["bg_entry"], fg=config.COLORS["fg_dark"], insertbackground=config.COLORS["fg_dark"])
        self.disk_size_entry.pack(fill=tk.X, padx=(5, 0), pady=(0, 2), ipady=6)
        self.disk_size_entry.insert(0, config.DEFAULT_DISK_SIZE)

        # Algorithm Selection Section
        self.algorithm_section = ttk.LabelFrame(self.root, text="Select Algorithm", style='Retro.TLabelframe', padding=12)
        self.algorithm_var = tk.StringVar(value="FCFS")
        for algo in self.algorithms.keys():
            ttk.Radiobutton(self.algorithm_section, text=algo, variable=self.algorithm_var, value=algo, style='Retro.TRadiobutton').pack(anchor=tk.W, padx=(10, 0), pady=4)

        # Results Section
        results_frame = ttk.LabelFrame(self.root, text="Results", style='Retro.TLabelframe', padding=8)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=(10, 15))
        
        ttk.Label(results_frame, text="TOTAL SEEK TIME:").pack(anchor=tk.W)
        self.seek_time_label = ttk.Label(results_frame, text="N/A", foreground=config.COLORS["fg_result"])
        self.seek_time_label.pack(anchor=tk.W, pady=(0, 8))
        
        ttk.Label(results_frame, text="SEQUENCE:").pack(anchor=tk.W)
        self.sequence_text = tk.Text(results_frame, height=4, width=34, font=config.FONTS["text_box"], bd=0, relief='flat', bg=config.COLORS["bg_entry"], fg=config.COLORS["fg_result"])
        self.sequence_text.pack(fill=tk.X, expand=False, pady=(0, 8))

        ttk.Label(results_frame, text="COMPUTATION:").pack(anchor=tk.W, pady=(6, 0))
        self.computation_text = tk.Text(results_frame, height=6, width=34, font=config.FONTS["text_box"], bd=0, relief='flat', bg=config.COLORS["bg_entry"], fg=config.COLORS["fg_result"])
        self.computation_text.pack(fill=tk.X, expand=False)
        
        # Right Side Output Elements
        self.title_label = ttk.Label(self.root, text="Disk Head Movement Visualization", font=config.FONTS["title"], background=config.COLORS["bg_frame"], foreground=config.COLORS["fg_text"])
        self.title_label.grid(row=0, column=1, sticky="w", padx=(10, 20), pady=(15, 5))

        self.canvas_frame = tk.Frame(self.root, bg=config.COLORS["bg_retro_box"], bd=1, relief="solid")
        self.canvas_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(10, 20), pady=(5, 15))

        # Bottom Action Bar
        button_bar = tk.Frame(self.root, bg=config.COLORS["btn_action_bg"], height=config.BOTTOM_BAR_HEIGHT)
        button_bar.grid(row=3, column=0, columnspan=2, sticky="ew")
        button_bar.pack_propagate(False)

        # Dynamic assignments referencing configuration bundles
        input_button = self.create_image_button(button_bar, "Input_Parameter_button.png", lambda: self.toggle_section(self.input_section, config.INPUT_GRID_KWARGS), config.COLORS["btn_green_bg"])
        input_button.pack(side=tk.LEFT, padx=(40, 20), pady=8)

        algorithm_button = self.create_image_button(button_bar, "Pick_Algorithm_button.png", lambda: self.toggle_section(self.algorithm_section, config.ALGO_GRID_KWARGS), config.COLORS["btn_green_bg"])
        algorithm_button.pack(side=tk.LEFT, padx=(0, 20), pady=8)

        run_button = self.create_image_button(button_bar, "Run_Sim_button.png", self.run_simulation, config.COLORS["btn_green_bg"])
        run_button.pack(side=tk.LEFT, padx=(0, 20), pady=8)

        reset_button = self.create_image_button(button_bar, "Reset_button.png", self.reset_simulation, config.COLORS["btn_green_bg"])
        reset_button.pack(side=tk.LEFT, padx=(0, 20), pady=8)

        # Quit button with functional scaling configuration applied via custom logic
        image = self.load_ui_image("quit_button.png").subsample(2, 2)
        quit_button = tk.Button(button_bar, image=image, command=self.root.destroy, bd=0, relief="flat", highlightthickness=0, cursor="hand2", bg=config.COLORS["btn_action_bg"], activebackground=config.COLORS["btn_action_bg"])
        quit_button.image = image
        quit_button.pack(side=tk.RIGHT, padx=(0, 20), pady=8)
   
    def run_simulation(self):
        """Runs scheduling parsing from updated UI targets"""
        try:
            requests_str = self.requests_entry.get().strip()
            requests = [int(x.strip()) for x in requests_str.split(',')]
            head_pos = int(self.head_entry.get().strip())
            disk_size = int(self.disk_size_entry.get().strip())
           
            if not requests:
                messagebox.showerror("Error", "Please enter disk requests")
                return
           
            if head_pos < 0 or head_pos >= disk_size:
                messagebox.showerror("Error", f"Head position must be between 0 and {disk_size-1}")
                return
           
            if any(r < 0 or r >= disk_size for r in requests):
                messagebox.showerror("Error", f"All requests must be between 0 and {disk_size-1}")
                return
           
            algorithm_class = self.algorithms[self.algorithm_var.get()]
            scheduler = algorithm_class(requests, head_pos, disk_size)
            sequence, total_seek_time = scheduler.schedule()
           
            self.seek_time_label.config(text=str(total_seek_time))
           
            sequence_text = " → ".join(map(str, sequence))
            self.sequence_text.config(state=tk.NORMAL)
            self.sequence_text.delete(1.0, tk.END)
            self.sequence_text.insert(1.0, sequence_text)
            self.sequence_text.config(state=tk.DISABLED)

            computation_lines = ["Computing for the total head movement:"]
            running_total = 0
            for previous, current in zip(sequence, sequence[1:]):
                movement = abs(current - previous)
                running_total += movement
                computation_lines.append(f"from {previous} to {current} = {max(previous, current)} - {min(previous, current)} = {movement}")
            computation_lines.append(f"Total head movement = {running_total} tracks")

            self.computation_text.config(state=tk.NORMAL)
            self.computation_text.delete(1.0, tk.END)
            self.computation_text.insert(1.0, "\n".join(computation_lines))
            self.computation_text.config(state=tk.DISABLED)
           
            self.draw_visualization(sequence, disk_size, head_pos)
           
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_simulation(self):
        """Flush and drop layout state safely"""
        self.algorithm_var.set("FCFS")
        self.requests_entry.delete(0, tk.END)
        self.requests_entry.insert(0, config.DEFAULT_REQUESTS)
        self.head_entry.delete(0, tk.END)
        self.head_entry.insert(0, config.DEFAULT_HEAD)
        self.disk_size_entry.delete(0, tk.END)
        self.disk_size_entry.insert(0, config.DEFAULT_DISK_SIZE)

        self.seek_time_label.config(text="N/A")
        self.sequence_text.config(state=tk.NORMAL)
        self.sequence_text.delete(1.0, tk.END)
        self.sequence_text.config(state=tk.DISABLED)

        self.computation_text.config(state=tk.NORMAL)
        self.computation_text.delete(1.0, tk.END)
        self.computation_text.config(state=tk.DISABLED)

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
   
    def draw_visualization(self, sequence: List[int], disk_size: int, head_pos: int):
        """Draw visualization relying explicitly on PLOT_CONFIG rules"""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
       
        fig = Figure(figsize=(12, 8), dpi=100, facecolor=config.PLOT_CONFIG["face_color"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(config.PLOT_CONFIG["face_color"])
       
        axis_y = 1.0
        path_start_y, path_step = 0.55, 0.75
        y_positions = [path_start_y - (i * path_step) for i in range(len(sequence))]

        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.tick_params(axis='x', top=True, labeltop=True, bottom=False, labelbottom=False)
        ax.plot([0, disk_size], [axis_y, axis_y], 'k-', linewidth=3, zorder=1)
       
        for pos in sorted(set(sequence)):
            ax.plot([pos, pos], [axis_y - 0.08, axis_y + 0.08], 'k-', linewidth=2)
            ax.text(pos, axis_y + 0.16, str(pos), ha='center', va='bottom', fontsize=9, fontweight='bold')
       
        for i in range(len(sequence) - 1):
            x1, y1 = sequence[i], y_positions[i]
            x2, y2 = sequence[i + 1], y_positions[i + 1]
            is_wrap_jump = self.algorithm_var.get() == "C-SCAN" and x2 < x1
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', lw=2, color=config.PLOT_CONFIG["line_color"], alpha=0.7,
                                        linestyle='--' if is_wrap_jump else '-'))
       
        for i, (pos, y) in enumerate(zip(sequence, y_positions)):
            if i == 0:
                ax.scatter(pos, y, s=300, c=config.PLOT_CONFIG["start_node_color"], marker='o', zorder=5, edgecolors=config.PLOT_CONFIG["start_node_edge"], linewidth=2)
            elif i == len(sequence) - 1:
                ax.scatter(pos, y, s=300, c=config.PLOT_CONFIG["end_node_color"], marker='o', zorder=5, edgecolors=config.PLOT_CONFIG["end_node_edge"], linewidth=2)
            else:
                ax.scatter(pos, y, s=200, c=config.PLOT_CONFIG["req_node_color"], marker='o', zorder=5, edgecolors=config.PLOT_CONFIG["req_node_edge"], linewidth=1.5)
           
            ax.text(pos, y - 0.18, str(i), ha='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
       
        ax.set_xlim(-5, disk_size + 5)
        ax.set_ylim(min(y_positions) - 0.7, axis_y + 0.45)
        ax.set_xlabel("Disk Cylinder Number", fontsize=12, fontweight='bold')
        ax.set_title(f"Disk Scheduling: {self.algorithm_var.get()}\n{', '.join(map(str, sequence[1:]))}", fontsize=14, fontweight='bold')
       
        ax.set_yticks([])
        for spine in ['left', 'right', 'top', 'bottom']:
            ax.spines[spine].set_visible(False)
       
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=config.PLOT_CONFIG["start_node_color"], markersize=12, markeredgecolor=config.PLOT_CONFIG["start_node_edge"], markeredgewidth=2, label='Start Position'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=config.PLOT_CONFIG["req_node_color"], markersize=10, markeredgecolor=config.PLOT_CONFIG["req_node_edge"], markeredgewidth=1.5, label='Disk Request'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=config.PLOT_CONFIG["end_node_color"], markersize=12, markeredgecolor=config.PLOT_CONFIG["end_node_edge"], markeredgewidth=2, label='End Position'),
            Line2D([0], [0], color=config.PLOT_CONFIG["line_color"], lw=2, label='Head Movement Path')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.0, 1.20), fontsize=9, frameon=False)
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        fig.tight_layout(rect=[0, 0, 1, 0.93])
       
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulerGUI(root)
    root.mainloop()