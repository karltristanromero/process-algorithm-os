# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
import sys
from PIL import Image, ImageTk

# --- OS SCALE & DPI AWARENESS FIX ---
# Forces Windows to bypass virtual stretching so a 1920x1080 canvas 
# renders at a sharp 1:1 pixel scale regardless of OS display settings.
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

# Import structural classes for memory management
from utils.process_generator import process_pool, process_user_choice
from mft.fixed_partition import FixedMemoryManager
from mft.first_fit import first_fit_mft
from mft.best_fit import best_fit_mft
from mft.best_available_fit import best_available_fit_mft

from mvt.variable_partition import VariableMemoryManager
from mvt.first_fit import first_fit_mvt
from mvt.best_fit import best_fit_mvt
from mvt.worst_fit import worst_fit_mvt

# IMPORT COORDINATES CONFIG COMPONENT ENGINE
import gui_config as cfg

# Modern theme colors
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
        
        # FIXED DIMENSION MATRIX FRAMEWAY
        self.screen_width = cfg.WINDOW_SETUP["base_width"]
        self.screen_height = cfg.WINDOW_SETUP["base_height"]
        self.window_root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        self.window_root.bind("<Escape>", lambda e: self.window_root.destroy())
        
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        self.auto_mode_running = False
        self.auto_mode_interval = 1500  # Deliberate one-by-one sequential step speed
        self.event_log = []
        self.bg_image_ref = None  # Image data tracker reference
        
        self.build_gui_layout()
        self.refresh_display_matrix()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("ModernCombo.TCombobox", 
                       fieldbackground=Theme.BG_PRIMARY, 
                       background=Theme.BG_SECONDARY, 
                       arrowcolor=Theme.PRIMARY,
                       padding=5)
        style.map("ModernCombo.TCombobox",
                 fieldbackground=[("readonly", Theme.BG_PRIMARY)],
                 background=[("active", Theme.BG_SECONDARY)])

    def build_gui_layout(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "bg1.png")

        # Load and maintain persistent master reference to raw asset file
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

        # Initialize canvas block container
        self.canvas = tk.Canvas(self.window_root, width=self.screen_width, height=self.screen_height, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Place initial unscaled image holder item
        self.bg_canvas_item = self.canvas.create_image(0, 0, anchor=tk.NW)

        # Bind configuration layout resize listener
        self.window_root.bind("<Configure>", self.on_window_resize)

        self._setup_styles()

        # Dynamic variable calculations fetched straight from centralized config dictionary map
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
        # ROW 1: Process ID Input Box + ALLOCATE Button
        self.entry_pid = tk.Entry(self.window_root, width=cfg.INPUTS_LAYOUT["entry_width"], font=cfg.INPUTS_LAYOUT["font_entry"], bd=2, relief=tk.GROOVE)
        self.pid_window_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["pid_y_offset"], window=self.entry_pid, anchor=tk.W)

        btn_manual_alloc = tk.Button(self.window_root, text="ALLOCATE", font=cfg.INPUTS_LAYOUT["font_button"], bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, relief=tk.RAISED, bd=2, cursor="hand2", command=self.handle_allocation_trigger)
        self.alloc_button_id = self.canvas.create_window(right_inputs_x + btn_x_shift, bottom_edge + cfg.INPUTS_LAYOUT["alloc_btn_y_offset"], window=btn_manual_alloc, width=cfg.INPUTS_LAYOUT["button_width"], height=cfg.INPUTS_LAYOUT["button_height"], anchor=tk.NW)

        # ROW 2: Process Size Input Box + DEALLOCATE Button
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
        # BOTTOM: DOCK ACTION CONTROL LANE
        # =========================================================
        btn_main_menu = tk.Button(self.window_root, text="⬅ MENU", font=("Arial", 11, "bold"), bg=Theme.PRIMARY, fg="white", relief=tk.RAISED, bd=2, command=self.go_back_to_main_menu)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["menu_label_x"], bottom_menu_y, window=btn_main_menu, width=120, height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        mode_label = tk.Label(self.window_root, text="MODE:", font=("Arial", 11, "bold"), fg=Theme.PRIMARY)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["mode_label_x"], bottom_menu_y + 10, window=mode_label, anchor=tk.NW)
        
        self.combo_mode = ttk.Combobox(self.window_root, values=["MANUAL", "AUTO"], state="readonly", font=("Arial", 11, "bold"), style="ModernCombo.TCombobox")
        self.combo_mode.set("MANUAL")
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["combo_mode_x"], bottom_menu_y, window=self.combo_mode, width=cfg.BOTTOM_MENU_LAYOUT["combo_mode_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)
        self.combo_mode.bind("<<ComboboxSelected>>", self.on_mode_changed)

        algo_label = tk.Label(self.window_root, text="ALGO:", font=("Arial", 11, "bold"), fg=Theme.PRIMARY)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["algo_label_x"], bottom_menu_y + 10, window=algo_label, anchor=tk.NW)
        
        self.combo_algo = ttk.Combobox(self.window_root, values=["MFT: First Fit", "MFT: Best Fit", "MFT: Best Available", "MVT: First Fit", "MVT: Best Fit", "MVT: Worst Fit"], state="readonly", font=("Arial", 11, "bold"), style="ModernCombo.TCombobox")
        self.combo_algo.set("MFT: First Fit")
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["combo_algo_x"], bottom_menu_y, window=self.combo_algo, width=cfg.BOTTOM_MENU_LAYOUT["combo_algo_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)
        self.combo_algo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display_matrix())

        self.btn_start = tk.Button(self.window_root, text="START", font=("Arial", 11, "bold"), bg=Theme.SUCCESS, fg="white", relief=tk.RAISED, bd=2, command=self.toggle_auto_mode)
        self.start_button_id = self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["btn_start_x"], bottom_menu_y, window=self.btn_start, width=cfg.BOTTOM_MENU_LAYOUT["action_btn_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        btn_reset = tk.Button(self.window_root, text="RESET", font=("Arial", 11, "bold"), bg=Theme.ERROR, fg="white", relief=tk.RAISED, bd=2, command=self.reset_system)
        self.reset_button_id = self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["btn_reset_x"], bottom_menu_y, window=btn_reset, width=cfg.BOTTOM_MENU_LAYOUT["action_btn_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        self.btn_compaction = tk.Button(self.window_root, text="🔨 COMPACT", font=("Arial", 11, "bold"), bg=Theme.WARNING, fg="white", relief=tk.RAISED, bd=2, command=self.trigger_mvt_compaction)
        self.compaction_window_id = self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["btn_compaction_x"], bottom_menu_y, window=self.btn_compaction, width=cfg.BOTTOM_MENU_LAYOUT["compaction_btn_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        self.status_label = tk.Label(self.window_root, text="System Ready", font=("Arial", 10, "italic"), fg=Theme.NEUTRAL)
        self.canvas.create_window(100, bottom_menu_y + 60, window=self.status_label, anchor=tk.NW)

    def on_window_resize(self, event):
        """ Dynamically scales and redraws the background image asset to track the window dimension frame configurations. """
        if event.widget == self.window_root:
            new_width = event.width
            new_height = event.height

            if new_width > 0 and new_height > 0:
                resized_pil = self.bg_pil_master.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.bg_image_ref = ImageTk.PhotoImage(resized_pil)
                self.canvas.itemconfig(self.bg_canvas_item, image=self.bg_image_ref)

    def go_back_to_main_menu(self):
        if self.auto_mode_running:
            self.toggle_auto_mode()
        messagebox.showinfo("Menu Navigation", "Returning back to Main System Menu Shell...")

    def update_status(self, message):
        self.status_label.config(text=message, fg=Theme.PRIMARY)

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
            self.btn_start.config(text="STOP", bg=Theme.WARNING)
            self.add_event_log("Automated clock distribution loop initialized.", "INFO")
            self.run_auto_step()
        else:
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS)
            self.add_event_log("Automated clock loop paused.", "INFO")

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
                        if "First Fit" in algo: msg = first_fit_mvt(process, self.mvt_manager)
                        elif "Best Fit" in algo: msg = best_fit_mvt(process, self.mvt_manager)
                        else: msg = worst_fit_mvt(process, self.mvt_manager)
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
            self.btn_start.config(text="START", bg=Theme.SUCCESS)
            messagebox.showerror("Simulation Loop Thread Exception", str(e))

    def reset_system(self):
        if self.auto_mode_running: self.auto_mode_running = False
        self.btn_start.config(text="START", bg=Theme.SUCCESS)
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
                msg = first_fit_mvt(process, self.mvt_manager) if "First Fit" in algo else (best_fit_mvt(process, self.mvt_manager) if "Best Fit" in algo else worst_fit_mvt(process, self.mvt_manager))
                if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                    self.mft_manager.waiting_queue.append(process)
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

    def trigger_mvt_compaction(self):
        try:
            msg = self.mvt_manager.compact_memory()
            self.reorder_mvt_queue()
            self.add_event_log("Memory core defragmented/compacted.", "INFO")
            self.refresh_display_matrix()
            messagebox.showinfo("Compaction Engine Active", msg)
        except Exception as e:
            messagebox.showerror("Compaction Fault", str(e))

    def reorder_mvt_queue(self):
        algo = self.combo_algo.get()
        for queued_proc in list(self.mvt_manager.waiting_queue):
            res = first_fit_mvt(queued_proc, self.mvt_manager) if "First Fit" in algo else (best_fit_mvt(queued_proc, self.mvt_manager) if "Best Fit" in algo else worst_fit_mvt(queued_proc, self.mvt_manager))
            if "Allocated" in res: self.mvt_manager.waiting_queue.remove(queued_proc)

    def refresh_display_matrix(self):
        self.canvas.delete("mem_element")
        if "MFT" in self.combo_algo.get():
            self.canvas.itemconfigure(self.compaction_window_id, state="hidden")
            self.update_mft_display_map()
        else:
            self.canvas.itemconfigure(self.compaction_window_id, state="normal")
            self.update_mvt_display_map()

    # =========================================================
    # CORE LEFT SIDE SIMULATION DRAW ROUTINES
    # =========================================================
    def update_mft_display_map(self):
        total_free_space = 0
        total_internal_frag = 0
        
        # Waiting Queue column placement
        self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_title_y"], text="⏳ Waiting Queue:", font=cfg.SIMULATION_PANE_LAYOUT["font_title"], fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mft_manager.waiting_queue:
            self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"], text="[ Queue Empty ]", font=("Courier", 16, "italic"), fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mft_manager.waiting_queue[:12]):
                y_pos = cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"] + (idx * cfg.SIMULATION_PANE_LAYOUT["queue_list_spacing_y"])
                self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], y_pos, text=f"• Job {proc.process_id} ({proc.process_size}K)", font=("Courier", 14, "bold"), fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

        # Memory visualization stack
        start_y = cfg.SIMULATION_PANE_LAYOUT["ram_column_start_y"]
        x1 = cfg.SIMULATION_PANE_LAYOUT["ram_column_x1"]
        x2 = cfg.SIMULATION_PANE_LAYOUT["ram_column_x2"]
        canvas_scale = cfg.SIMULATION_PANE_LAYOUT["ram_vertical_scale"]
        
        for partition in self.mft_manager.partitions:
            height = partition.partition_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 20, start_y, text=f"{int(partition.partition_size)}K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")
            
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
            
        self.canvas.create_text(x1 - 20, start_y, text="64K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

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
                self.canvas.create_text(x1 + 125, y1 + (height / 2), text=f"{block.occupied_process.process_id}\n({block.block_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill="white", tags="mem_element")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 125, y1 + (height / 2), text=f"✓ FREE\n({block.block_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill=Theme.SUCCESS, tags="mem_element")
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