# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
import sys
from PIL import Image, ImageTk

# --- OS SCALE & DPI AWARENESS FIX ---
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older systems
        except Exception:
            pass
# ------------------------------------

from utils.process_generator import process_pool, process_user_choice
from mft.fixed_partition import FixedMemoryManager
from mft.first_fit import first_fit_mft
from mft.best_fit import best_fit_mft
from mft.best_available_fit import best_available_fit_mft

from mvt.variable_partition import VariableMemoryManager
from mvt.first_fit import first_fit_mvt
from mvt.best_fit import best_fit_mvt
from mvt.worst_fit import worst_fit_mvt

import gui_config as cfg

class Theme:
    BG_PRIMARY = "#F5E3B5"
    BG_SECONDARY = "#CBB279"
    PRIMARY = "#3D1E6D"
    SUCCESS = "#2E7D32"
    WARNING = "#FF9800"
    ERROR = "#E53935"
    ALLOCATED = "#007ACC"
    ALLOCATED_DARK = "#005A9C"
    FREE = "#E8F5E9"
    FREE_BORDER = "#81C784"
    FRAG = "#FF5252"
    FRAG_DARK = "#D32F2F"
    WAITING = "#C62828"
    NEUTRAL = "#757575"

class MemoryManagementApp:
    def __init__(self, window_root):
        self.window_root = window_root
        self.window_root.title("Memory Management Simulator")
        
        self.screen_width = cfg.WINDOW_SETUP["base_width"]
        self.screen_height = cfg.WINDOW_SETUP["base_height"]
        
        self.window_root.attributes("-fullscreen", True)
        self.window_root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        self.window_root.bind("<Escape>", lambda e: self.window_root.destroy())
        
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        self.auto_mode_running = False
        self.auto_mode_interval = 1500  
        self.event_log = []
        self.bg_image_ref = None  
        
        self.build_gui_layout()
        self.refresh_display_matrix()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure("ModernCombo.TCombobox", 
                       fieldbackground="#FFFFFF", 
                       background="#FFFFFF", 
                       arrowcolor=Theme.PRIMARY,
                       borderwidth=1,
                       padding=2)
        style.map("ModernCombo.TCombobox",
                 fieldbackground=[("readonly", "#FFFFFF")],
                 background=[("active", "#FFFFFF")])

    def build_gui_layout(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "bg1.png")

        try:
            self.bg_pil_master = Image.open(bg_path)
        except Exception:
            try:
                fallback_path = os.path.join(script_dir, "image_7a5c02.png")
                self.bg_pil_master = Image.open(fallback_path)
            except Exception:
                messagebox.showerror("Asset Error", f"Missing background image inside directory:\n{script_dir}")
                self.window_root.destroy()
                return

        self.canvas = tk.Canvas(self.window_root, width=self.screen_width, height=self.screen_height, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bg_canvas_item = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.window_root.bind("<Configure>", self.on_window_resize)

        self._setup_styles()

        bottom_edge = self.screen_height - cfg.WINDOW_SETUP["bottom_control_panel_height"]
        
        right_card_x = cfg.STATS_LAYOUT["right_edge_offset"]
        right_inputs_x = cfg.INPUTS_LAYOUT["right_edge_offset"]
        btn_x_shift = cfg.INPUTS_LAYOUT["button_x_offset"]
        
        bottom_menu_y = cfg.BOTTOM_MENU_LAYOUT["y_offset_from_bottom"]

        # =========================================================
        # RIGHT SIDE: QUANTITATIVE TRACKING READOUTS
        # =========================================================
        self.lbl_total_space = tk.Label(self.window_root, text="64K", font=cfg.STATS_LAYOUT["font"], fg=Theme.SUCCESS)
        self.canvas.create_window(right_card_x, cfg.STATS_LAYOUT["total_space_y"], window=self.lbl_total_space, anchor=tk.CENTER)

        self.lbl_external_frag = tk.Label(self.window_root, text="0K", font=cfg.STATS_LAYOUT["font"], fg=Theme.WARNING)
        self.canvas.create_window(right_card_x, cfg.STATS_LAYOUT["external_frag_y"], window=self.lbl_external_frag, anchor=tk.CENTER)

        self.lbl_internal_frag = tk.Label(self.window_root, text="0K", font=cfg.STATS_LAYOUT["font"], fg=Theme.ERROR)
        self.canvas.create_window(right_card_x, cfg.STATS_LAYOUT["internal_frag_y"], window=self.lbl_internal_frag, anchor=tk.CENTER)

        # =========================================================
        # RIGHT SIDE: SIDE-BY-SIDE TRANSACTION ENTRY CONTROLS
        # =========================================================
        self.entry_pid = tk.Entry(self.window_root, width=cfg.INPUTS_LAYOUT["entry_width"], font=cfg.INPUTS_LAYOUT["font_entry"], bd=2, relief=tk.GROOVE)
        self.pid_window_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["pid_y_offset"], window=self.entry_pid, anchor=tk.W)

        btn_manual_alloc = tk.Button(self.window_root, text="ALLOCATE", font=cfg.INPUTS_LAYOUT["font_button"], bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, relief=tk.RAISED, bd=2, cursor="hand2", command=self.handle_allocation_trigger)
        self.alloc_button_id = self.canvas.create_window(right_inputs_x + btn_x_shift, bottom_edge + cfg.INPUTS_LAYOUT["alloc_btn_y_offset"], window=btn_manual_alloc, width=cfg.INPUTS_LAYOUT["button_width"], height=cfg.INPUTS_LAYOUT["button_height"], anchor=tk.NW)

        self.entry_size = tk.Entry(self.window_root, width=cfg.INPUTS_LAYOUT["entry_width"], font=cfg.INPUTS_LAYOUT["font_entry"], bd=2, relief=tk.GROOVE)
        self.size_window_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["size_y_offset"], window=self.entry_size, anchor=tk.W)

        btn_manual_dealloc = tk.Button(self.window_root, text="DEALLOCATE", font=cfg.INPUTS_LAYOUT["font_button"], bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, relief=tk.RAISED, bd=2, cursor="hand2", command=self.handle_deallocation_trigger)
        self.dealloc_button_id = self.canvas.create_window(right_inputs_x + btn_x_shift, bottom_edge + cfg.INPUTS_LAYOUT["dealloc_btn_y_offset"], window=btn_manual_dealloc, width=cfg.INPUTS_LAYOUT["button_width"], height=cfg.INPUTS_LAYOUT["button_height"], anchor=tk.NW)

        # =========================================================
        # LEFT SIDE: HISTORICAL EVENT STREAM LOGGER
        # =========================================================
        log_label = tk.Label(self.window_root, text="📜 SYSTEM ACTIVITY HISTORY LOG", font=("Arial", 12, "bold"), fg=Theme.PRIMARY)
        self.canvas.create_window(cfg.EVENT_LOG_LAYOUT["label_x"], cfg.EVENT_LOG_LAYOUT["label_y"], window=log_label, anchor=tk.NW)

        self.event_log_widget = tk.Text(self.window_root, height=cfg.EVENT_LOG_LAYOUT["text_height"], width=cfg.EVENT_LOG_LAYOUT["text_width"], font=cfg.EVENT_LOG_LAYOUT["font"], bg="#FFFFFF", fg=Theme.PRIMARY, relief=tk.GROOVE, bd=2, state="disabled")
        self.canvas.create_window(cfg.EVENT_LOG_LAYOUT["text_x"], cfg.EVENT_LOG_LAYOUT["text_y"], window=self.event_log_widget, anchor=tk.NW)
        
        self.event_log_widget.tag_configure("allocate", foreground=Theme.SUCCESS)
        self.event_log_widget.tag_configure("deallocate", foreground=Theme.ERROR)
        self.event_log_widget.tag_configure("warning", foreground=Theme.WARNING)
        self.event_log_widget.tag_configure("info", foreground=Theme.NEUTRAL)

        # =========================================================
        # BOTTOM FRAME: RESIZED TRANSPARENT CANVAS NAV TEXTS
        # =========================================================
        self.canvas.create_text(cfg.BOTTOM_MENU_LAYOUT["menu_label_x"], bottom_menu_y, text="⬅ MENU", font=cfg.BOTTOM_MENU_LAYOUT["font_nav"], fill=Theme.PRIMARY, anchor=tk.W, tags="btn_menu")
        self.canvas.tag_bind("btn_menu", "<Button-1>", lambda e: self.go_back_to_main_menu())

        self.canvas.create_text(cfg.BOTTOM_MENU_LAYOUT["mode_label_x"], bottom_menu_y, text="MODE:", font=cfg.BOTTOM_MENU_LAYOUT["font_nav"], fill=Theme.PRIMARY, anchor=tk.W)
        
        self.combo_mode = ttk.Combobox(self.window_root, values=["MANUAL", "AUTO"], state="readonly", font=("Arial", 11, "bold"), style="ModernCombo.TCombobox")
        self.combo_mode.set("MANUAL")
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["combo_mode_x"], bottom_menu_y, window=self.combo_mode, width=cfg.BOTTOM_MENU_LAYOUT["combo_mode_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.W)
        self.combo_mode.bind("<<ComboboxSelected>>", self.on_mode_changed)

        self.canvas.create_text(cfg.BOTTOM_MENU_LAYOUT["algo_label_x"], bottom_menu_y, text="ALGO:", font=cfg.BOTTOM_MENU_LAYOUT["font_nav"], fill=Theme.PRIMARY, anchor=tk.W)
        
        algo_selections = [
            "MFT: First Fit", 
            "MFT: Best Fit", 
            "MFT: Best Available", 
            "MVT: First Fit (No Compaction)",
            "MVT: First Fit (Auto Compaction)",
            "MVT: Best Fit (No Compaction)",
            "MVT: Best Fit (Auto Compaction)",
            "MVT: Worst Fit (No Compaction)",
            "MVT: Worst Fit (Auto Compaction)"
        ]
        self.combo_algo = ttk.Combobox(self.window_root, values=algo_selections, state="readonly", font=("Arial", 11, "bold"), style="ModernCombo.TCombobox")
        self.combo_algo.set("MFT: First Fit")
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["combo_algo_x"], bottom_menu_y, window=self.combo_algo, width=cfg.BOTTOM_MENU_LAYOUT["combo_algo_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.W)
        self.combo_algo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display_matrix())

        self.start_text_id = self.canvas.create_text(cfg.BOTTOM_MENU_LAYOUT["btn_start_x"], bottom_menu_y, text="▶ START", font=cfg.BOTTOM_MENU_LAYOUT["font_nav"], fill=Theme.SUCCESS, anchor=tk.W, tags="btn_start")
        self.canvas.tag_bind("btn_start", "<Button-1>", lambda e: self.toggle_auto_mode())

        self.canvas.create_text(cfg.BOTTOM_MENU_LAYOUT["btn_reset_x"], bottom_menu_y, text="🔄 RESET", font=cfg.BOTTOM_MENU_LAYOUT["font_nav"], fill=Theme.ERROR, anchor=tk.W, tags="btn_reset")
        self.canvas.tag_bind("btn_reset", "<Button-1>", lambda e: self.reset_system())

        self.status_text_id = self.canvas.create_text(100, bottom_menu_y + 40, text="System Ready", font=("Arial", 11, "italic"), fill=Theme.NEUTRAL, anchor=tk.NW)

    def on_window_resize(self, event):
        if event.widget == self.window_root:
            new_width = event.width
            new_height = event.height
            if new_width > 0 and new_height > 0:
                resized_pil = self.bg_pil_master.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.bg_image_ref = ImageTk.PhotoImage(resized_pil)
                self.canvas.itemconfig(self.bg_canvas_item, image=self.bg_image_ref)

    def go_back_to_main_menu(self):
        """ Stops all automated processing, cross-launches the root menu shell script, and closes down the current module. """
        if self.auto_mode_running:
            self.toggle_auto_mode()
            
        # Get absolute structural coordinates of main.py relative to memory_management folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        main_py_path = os.path.join(parent_dir, "main.py")
        
        # Spawn the root menu layout script independently
        try:
            subprocess.Popen([sys.executable, main_py_path])
        except Exception as e:
            messagebox.showerror("Navigation Error", f"Could not launch main shell interface:\n{str(e)}")
            return
            
        # Safely shut down the local fullscreen Tkinter environment loop
        self.window_root.destroy()

    def update_status(self, message):
        self.canvas.itemconfig(self.status_text_id, text=message, fill=Theme.PRIMARY)

    def on_mode_changed(self, event=None):
        mode = self.combo_mode.get()
        if mode == "MANUAL":
            self.canvas.itemconfigure(self.pid_window_id, state="normal")
            self.canvas.itemconfigure(self.size_window_id, state="normal")
            self.canvas.itemconfigure(self.alloc_button_id, state="normal")
            self.canvas.itemconfigure(self.dealloc_button_id, state="normal")
            self.update_status("MANUAL active - Handle single explicit job instructions sequentially.")
        else:
            self.canvas.itemconfigure(self.pid_window_id, state="hidden")
            self.canvas.itemconfigure(self.size_window_id, state="hidden")
            self.canvas.itemconfigure(self.alloc_button_id, state="hidden")
            self.canvas.itemconfigure(self.dealloc_button_id, state="hidden")
            self.update_status("AUTO active - Single events execute one-by-one until Stopped.")

    def add_event_log(self, event_text, event_type="INFO"):
        self.event_log_widget.config(state="normal")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        tag = "info"
        if event_type == "ALLOCATE": tag = "allocate"
        elif event_type == "DEALLOCATE": tag = "deallocate"
        elif event_type == "WARNING": tag = "warning"
        
        log_entry = f"[{timestamp}] {event_text}\n"
        self.event_log_widget.insert(tk.END, log_entry, tag)
        self.event_log_widget.see(tk.END)
        self.event_log_widget.config(state="disabled")

    def toggle_auto_mode(self):
        if self.combo_mode.get() != "AUTO":
            messagebox.showwarning("Mode Selection", "Please set bottom control mode context to AUTO first.")
            return
        if not self.auto_mode_running:
            self.auto_mode_running = True
            self.canvas.itemconfig(self.start_text_id, text="⏹ STOP", fill=Theme.WARNING)
            self.add_event_log("Automated clock distribution loop initialized.", "INFO")
            self.run_auto_step()
        else:
            self.auto_mode_running = False
            self.canvas.itemconfig(self.start_text_id, text="▶ START", fill=Theme.SUCCESS)
            self.add_event_log("Automated clock loop paused.", "INFO")

    def execute_mvt_allocation(self, algo_title, process):
        if "First Fit" in algo_title:
            msg = first_fit_mvt(process, self.mvt_manager)
        elif "Best Fit" in algo_title:
            msg = best_fit_mvt(process, self.mvt_manager)
        else:
            msg = worst_fit_mvt(process, self.mvt_manager)

        if "Failed" in msg and "Auto Compaction" in algo_title:
            total_free_memory = sum(b.block_size for b in self.mvt_manager.blocks if b.occupied_process is None)
            if total_free_memory >= process.process_size:
                self.mvt_manager.compact_memory()
                self.add_event_log("⚡ Auto Compaction Triggered: Consolidated dynamic blocks on the fly.", "WARNING")
                if "First Fit" in algo_title: msg = first_fit_mvt(process, self.mvt_manager)
                elif "Best Fit" in algo_title: msg = best_fit_mvt(process, self.mvt_manager)
                else: msg = worst_fit_mvt(process, self.mvt_manager)
                
        return msg

    def run_auto_step(self):
        if not self.auto_mode_running: return
        try:
            algo = self.combo_algo.get()
            command, process = process_user_choice("RANDOM", None, None, None)
            if process is not None:
                if command == "ALLOCATE":
                    if "MFT" in algo:
                        if "First Fit" in algo: msg = first_fit_mft(process, self.mft_manager)
                        elif "Best Fit" in algo: msg = best_fit_mft(process, self.mft_manager)
                        else: msg = best_available_fit_mft(process, self.mft_manager)
                        if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                            self.mft_manager.waiting_queue.append(process)
                            self.add_event_log(f"Inbound Job {process.process_id} ({process.process_size}K) → Halted in Waiting Queue.", "WARNING")
                        elif "Allocated" in msg:
                            self.add_event_log(f"Job {process.process_id} ({process.process_size}K) ↦ Successfully Routed.", "ALLOCATE")
                    else:
                        msg = self.execute_mvt_allocation(algo, process)
                        if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                            self.mvt_manager.waiting_queue.append(process)
                            self.add_event_log(f"Inbound Job {process.process_id} ({process.process_size}K) → Halted in Waiting Queue.", "WARNING")
                        elif "Allocated" in msg:
                            self.add_event_log(f"Job {process.process_id} ({process.process_size}K) ↦ Successfully Routed.", "ALLOCATE")
                elif command == "DEALLOCATE":
                    if "MFT" in algo:
                        self.mft_manager.deallocate_process(process.process_id)
                        for queued_proc in list(self.mft_manager.waiting_queue):
                            if "First Fit" in algo: res = first_fit_mft(queued_proc, self.mft_manager)
                            elif "Best Fit" in algo: res = best_fit_mft(queued_proc, self.mft_manager)
                            else: res = best_available_fit_mft(queued_proc, self.mft_manager)
                            if "Allocated" in res: self.mft_manager.waiting_queue.remove(queued_proc)
                    else:
                        self.mvt_manager.deallocate_process(process.process_id)
                        self.reorder_mvt_queue()
                    self.add_event_log(f"Job {process.process_id} ↤ Evicted/Terminated from active boundary.", "DEALLOCATE")
            
            self.refresh_display_matrix()
            self.window_root.after(self.auto_mode_interval, self.run_auto_step)
        except Exception as e:
            self.auto_mode_running = False
            self.canvas.itemconfig(self.start_text_id, text="▶ START", fill=Theme.SUCCESS)
            messagebox.showerror("Simulation Loop Thread Exception", str(e))

    def reset_system(self):
        if self.auto_mode_running: self.auto_mode_running = False
        self.canvas.itemconfig(self.start_text_id, text="▶ START", fill=Theme.SUCCESS)
        if messagebox.askyesno("Reset", "Purge active memory maps?"):
            for partition in self.mft_manager.partitions:
                partition.occupied_process = None
                partition.internal_fragmentation = 0
            self.mft_manager.waiting_queue = []
            for block in self.mvt_manager.blocks:
                block.occupied_process = None
            self.mvt_manager.waiting_queue = []
            self.event_log_widget.config(state="normal")
            self.event_log_widget.delete(1.0, tk.END)
            self.event_log_widget.config(state="disabled")
            self.add_event_log("All clear.", "INFO")
            self.refresh_display_matrix()

    def handle_allocation_trigger(self):
        try:
            algo = self.combo_algo.get()
            pid = self.entry_pid.get().strip()
            size_str = self.entry_size.get().strip()
            if not pid or not size_str: return
            
            command, process = process_user_choice("MANUAL", "ALLOCATE", pid, int(size_str))
            if "MFT" in algo:
                msg = first_fit_mft(process, self.mft_manager) if "First Fit" in algo else (best_fit_mft(process, self.mft_manager) if "Best Fit" in algo else best_available_fit_mft(process, self.mft_manager))
                if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                    self.mft_manager.waiting_queue.append(process)
                    self.add_event_log(f"Manual Job {process.process_id} pushed to queue.", "WARNING")
                elif "Allocated" in msg:
                    self.add_event_log(f"Manual Job {process.process_id} allocated.", "ALLOCATE")
            else:
                msg = self.execute_mvt_allocation(algo, process)
                if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                    self.mvt_manager.waiting_queue.append(process)
                    self.add_event_log(f"Manual Job {process.process_id} pushed to queue.", "WARNING")
                elif "Allocated" in msg:
                    self.add_event_log(f"Manual Job {process.process_id} allocated.", "ALLOCATE")
            
            self.entry_pid.delete(0, tk.END)
            self.entry_size.delete(0, tk.END)
            self.refresh_display_matrix()
        except Exception as e:
            messagebox.showerror("Allocation Error", str(e))

    def handle_deallocation_trigger(self):
        try:
            algo = self.combo_algo.get()
            pid = self.entry_pid.get().strip()
            if not pid: return
            
            command, process = process_user_choice("MANUAL", "DEALLOCATE", pid, None)
            if "MFT" in algo:
                self.mft_manager.deallocate_process(process.process_id)
                for queued_proc in list(self.mft_manager.waiting_queue):
                    res = first_fit_mft(queued_proc, self.mft_manager) if "First Fit" in algo else (best_fit_mft(queued_proc, self.mft_manager) if "Best Fit" in algo else best_available_fit_mft(queued_proc, self.mft_manager))
                    if "Allocated" in res: self.mft_manager.waiting_queue.remove(queued_proc)
            else:
                self.mvt_manager.deallocate_process(process.process_id)
                self.reorder_mvt_queue()
                
            self.add_event_log(f"Manual Eviction: {process.process_id}.", "DEALLOCATE")
            self.entry_pid.delete(0, tk.END)
            self.refresh_display_matrix()
        except Exception as e:
            messagebox.showerror("Deallocation Error", str(e))

    def reorder_mvt_queue(self):
        algo = self.combo_algo.get()
        for queued_proc in list(self.mvt_manager.waiting_queue):
            res = self.execute_mvt_allocation(algo, queued_proc)
            if "Allocated" in res: self.mvt_manager.waiting_queue.remove(queued_proc)

    def refresh_display_matrix(self):
        self.canvas.delete("mem_element")
        if "MFT" in self.combo_algo.get():
            self.update_mft_display_map()
        else:
            self.update_mvt_display_map()

    # =========================================================
    # CORE LEFT SIDE SIMULATION DRAW ROUTINES
    # =========================================================
    def update_mft_display_map(self):
        total_free_space = 0
        total_internal_frag = 0
        
        self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_title_y"], text="⏳ Waiting Queue:", font=cfg.SIMULATION_PANE_LAYOUT["font_title"], fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mft_manager.waiting_queue:
            self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"], text="[ Queue Empty ]", font=("Courier", 16, "italic"), fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mft_manager.waiting_queue[:12]):
                y_pos = cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"] + (idx * cfg.SIMULATION_PANE_LAYOUT["queue_list_spacing_y"])
                self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], y_pos, text=f"• Job {proc.process_id} ({proc.process_size}K)", font=("Courier", 14, "bold"), fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

        start_y = cfg.SIMULATION_PANE_LAYOUT["ram_column_start_y"]
        x1 = cfg.SIMULATION_PANE_LAYOUT["ram_column_x1"]
        x2 = cfg.SIMULATION_PANE_LAYOUT["ram_column_x2"]
        canvas_scale = cfg.SIMULATION_PANE_LAYOUT["ram_vertical_scale"]
        
        current_accumulation_address = 0
        for partition in self.mft_manager.partitions:
            height = partition.partition_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 20, start_y, text=f"{current_accumulation_address}K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")
            
            if partition.occupied_process:
                proc_height = partition.occupied_process.process_size * canvas_scale
                self.canvas.create_rectangle(x1, y1, x2, y1 + proc_height, fill=Theme.ALLOCATED, outline=Theme.ALLOCATED_DARK, width=3, tags="mem_element")
                self.canvas.create_text(x1 + 125, y1 + (proc_height / 2), text=f"{partition.occupied_process.process_id} ({partition.occupied_process.process_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill="white", tags="mem_element")
                
                if partition.internal_fragmentation > 0:
                    self.canvas.create_rectangle(x1, y1 + proc_height, x2, y2, fill=Theme.FRAG, outline=Theme.FRAG_DARK, width=2, tags="mem_element")
                    self.canvas.create_text(x1 + 125, y1 + proc_height + ((height - proc_height) / 2), text=f"FRAG: {partition.internal_fragmentation}K", font=cfg.SIMULATION_PANE_LAYOUT["font_frag_block"], fill="white", tags="mem_element")
                    total_internal_frag += partition.internal_fragmentation
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 125, y1 + (height / 2), text="✓ FREE", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill=Theme.SUCCESS, tags="mem_element")
                total_free_space += partition.partition_size
                
            start_y += height
            current_accumulation_address += int(partition.partition_size)
            
        self.canvas.create_text(x1 - 20, start_y, text=f"{current_accumulation_address}K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text="0K")
        self.lbl_internal_frag.config(text=f"{total_internal_frag}K")

    def update_mvt_display_map(self):
        total_free_space = 0
        total_external_frag = 0
        free_segments = 0
        
        self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_title_y"], text="⏳ Waiting Queue:", font=cfg.SIMULATION_PANE_LAYOUT["font_title"], fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mvt_manager.waiting_queue:
            self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"], text="[ Queue Empty ]", font=("Courier", 16, "italic"), fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mvt_manager.waiting_queue[:12]):
                y_pos = cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"] + (idx * cfg.SIMULATION_PANE_LAYOUT["queue_list_spacing_y"])
                self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], y_pos, text=f"• Job {proc.process_id} ({proc.process_size}K)", font=("Courier", 14, "bold"), fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

        start_y = cfg.SIMULATION_PANE_LAYOUT["ram_column_start_y"]
        x1 = cfg.SIMULATION_PANE_LAYOUT["ram_column_x1"]
        x2 = cfg.SIMULATION_PANE_LAYOUT["ram_column_x2"]
        canvas_scale = cfg.SIMULATION_PANE_LAYOUT["ram_vertical_scale"]
        
        for block in self.mvt_manager.blocks:
            height = block.block_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 20, y1, text=f"{block.start_address}K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")
            
            if block.occupied_process:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.ALLOCATED, outline=Theme.ALLOCATED_DARK, width=3, tags="mem_element")
                self.canvas.create_text(x1 + 125, y1 + (height / 2), text=f"{block.occupied_process.process_id} ({block.block_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill="white", tags="mem_element")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 125, y1 + (height / 2), text=f"✓ FREE ({block.block_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill=Theme.SUCCESS, tags="mem_element")
                total_free_space += block.block_size
                free_segments += 1
            start_y += height
            
        self.canvas.create_text(x1 - 20, start_y, text="64K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

        if any(b.occupied_process is not None for b in self.mvt_manager.blocks) and free_segments > 1:
            total_external_frag = total_free_space

        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text=f"{total_external_frag}K")
        self.lbl_internal_frag.config(text="0K")

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagementApp(root)
    root.mainloop()