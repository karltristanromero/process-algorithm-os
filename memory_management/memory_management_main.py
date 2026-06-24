# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
from PIL import Image, ImageTk

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
        
        screen_width = self.window_root.winfo_screenwidth()
        screen_height = self.window_root.winfo_screenheight()
        
        taskbar_height = 60
        effective_height = screen_height - taskbar_height
        
        self.window_root.geometry(f"{screen_width}x{effective_height}+0+0")
        self.window_root.state('zoomed')
        
        self.screen_width = screen_width
        self.screen_height = effective_height
        
        self.window_root.bind("<Escape>", lambda e: self.window_root.destroy())
        
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        self.auto_mode_running = False
        self.auto_mode_interval = 1000
        self.event_log = []
        
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

        try:
            bg_pil = Image.open(bg_path)
            bg_pil = bg_pil.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(bg_pil)
        except Exception:
            try:
                fallback_path = os.path.join(script_dir, "image_7a5c02.png")
                bg_pil = Image.open(fallback_path)
                bg_pil = bg_pil.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(bg_pil)
            except Exception:
                messagebox.showerror("Asset Error", f"Missing background image inside directory:\n{script_dir}")
                self.window_root.destroy()
                return

        self.canvas = tk.Canvas(self.window_root, width=self.screen_width, height=self.screen_height, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        self._setup_styles()

        # Dynamic calculated edge bounds matching display configurations
        right_card_x = self.screen_width - cfg.STATS_LAYOUT["right_edge_offset"]
        right_inputs_x = self.screen_width - cfg.INPUTS_LAYOUT["right_edge_offset"]
        bottom_edge = self.screen_height - 120
        button_y = bottom_edge + cfg.BOTTOM_MENU_LAYOUT["y_offset_from_bottom"]

        # =========================================================
        # 1. STATISTICS CARDS (COORDINATES IN MAP)
        # =========================================================
        self.lbl_total_space = tk.Label(self.window_root, text="64K", font=cfg.STATS_LAYOUT["font"], fg=Theme.SUCCESS)
        self.canvas.create_window(right_card_x, cfg.STATS_LAYOUT["total_space_y"], window=self.lbl_total_space, anchor=tk.CENTER)

        self.lbl_external_frag = tk.Label(self.window_root, text="0K", font=cfg.STATS_LAYOUT["font"], fg=Theme.WARNING)
        self.canvas.create_window(right_card_x, cfg.STATS_LAYOUT["external_frag_y"], window=self.lbl_external_frag, anchor=tk.CENTER)

        self.lbl_internal_frag = tk.Label(self.window_root, text="0K", font=cfg.STATS_LAYOUT["font"], fg=Theme.ERROR)
        self.canvas.create_window(right_card_x, cfg.STATS_LAYOUT["internal_frag_y"], window=self.lbl_internal_frag, anchor=tk.CENTER)

        # =========================================================
        # 2. INPUT ENTRY FIELDS & CONTROL ACTION BUTTONS
        # =========================================================
        self.entry_pid = tk.Entry(self.window_root, width=cfg.INPUTS_LAYOUT["entry_width"], font=cfg.INPUTS_LAYOUT["font_entry"], bd=2, relief=tk.GROOVE, bg="#FFFFFF", fg=Theme.PRIMARY)
        self.pid_window_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["pid_y_offset"], window=self.entry_pid, anchor=tk.W)

        self.entry_size = tk.Entry(self.window_root, width=cfg.INPUTS_LAYOUT["entry_width"], font=cfg.INPUTS_LAYOUT["font_entry"], bd=2, relief=tk.GROOVE, bg="#FFFFFF", fg=Theme.PRIMARY)
        self.size_window_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["size_y_offset"], window=self.entry_size, anchor=tk.W)

        btn_manual_alloc = tk.Button(self.window_root, text="ALLOC", font=cfg.INPUTS_LAYOUT["font_button"], bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, activebackground=Theme.BG_SECONDARY, relief=tk.RAISED, bd=2, cursor="hand2", command=self.handle_allocation_trigger)
        self.alloc_button_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["alloc_btn_y_offset"], window=btn_manual_alloc, width=cfg.INPUTS_LAYOUT["button_width"], height=cfg.INPUTS_LAYOUT["button_height"], anchor=tk.NW)

        btn_manual_dealloc = tk.Button(self.window_root, text="DEALLOC", font=cfg.INPUTS_LAYOUT["font_button"], bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, activebackground=Theme.BG_SECONDARY, relief=tk.RAISED, bd=2, cursor="hand2", command=self.handle_deallocation_trigger)
        self.dealloc_button_id = self.canvas.create_window(right_inputs_x, bottom_edge + cfg.INPUTS_LAYOUT["dealloc_btn_y_offset"], window=btn_manual_dealloc, width=cfg.INPUTS_LAYOUT["button_width"], height=cfg.INPUTS_LAYOUT["button_height"], anchor=tk.NW)

        # =========================================================
        # 3. BOTTOM MENU CONTROL LANE INTERFACES
        # =========================================================
        menu_label = tk.Label(self.window_root, text="MENU", font=("Arial", 12, "bold"), fg=Theme.PRIMARY)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["menu_label_x"], button_y + 5, window=menu_label, anchor=tk.NW)

        mode_label = tk.Label(self.window_root, text="MODE:", font=("Arial", 10, "bold"), fg=Theme.PRIMARY)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["mode_label_x"], button_y + 5, window=mode_label, anchor=tk.NW)
        
        self.combo_mode = ttk.Combobox(self.window_root, values=["MANUAL", "AUTO"], state="readonly", font=("Arial", 10, "bold"), style="ModernCombo.TCombobox")
        self.combo_mode.set("MANUAL")
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["combo_mode_x"], button_y, window=self.combo_mode, width=cfg.BOTTOM_MENU_LAYOUT["combo_mode_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)
        self.combo_mode.bind("<<ComboboxSelected>>", self.on_mode_changed)

        algo_label = tk.Label(self.window_root, text="ALGO:", font=("Arial", 10, "bold"), fg=Theme.PRIMARY)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["algo_label_x"], button_y + 5, window=algo_label, anchor=tk.NW)
        
        self.combo_algo = ttk.Combobox(self.window_root, values=["MFT: First Fit", "MFT: Best Fit", "MFT: Best Available", "MVT: First Fit", "MVT: Best Fit", "MVT: Worst Fit"], state="readonly", font=("Arial", 9, "bold"), style="ModernCombo.TCombobox")
        self.combo_algo.set("MFT: First Fit")
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["combo_algo_x"], button_y, window=self.combo_algo, width=cfg.BOTTOM_MENU_LAYOUT["combo_algo_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)
        self.combo_algo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display_matrix())

        self.btn_start = tk.Button(self.window_root, text="START", font=("Arial", 10, "bold"), bg=Theme.SUCCESS, fg="white", activebackground="#1B5E20", relief=tk.RAISED, bd=2, cursor="hand2", command=self.toggle_auto_mode)
        self.start_button_id = self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["btn_start_x"], button_y, window=self.btn_start, width=cfg.BOTTOM_MENU_LAYOUT["action_btn_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        btn_reset = tk.Button(self.window_root, text="RESET", font=("Arial", 10, "bold"), bg=Theme.ERROR, fg="white", activebackground="#B71C1C", relief=tk.RAISED, bd=2, cursor="hand2", command=self.reset_system)
        self.reset_button_id = self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["btn_reset_x"], button_y, window=btn_reset, width=cfg.BOTTOM_MENU_LAYOUT["action_btn_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        self.btn_compaction = tk.Button(self.window_root, text="🔨 COMPACT", font=("Arial", 10, "bold"), bg=Theme.WARNING, fg="white", activebackground="#F57C00", relief=tk.RAISED, bd=2, cursor="hand2", command=self.trigger_mvt_compaction)
        self.compaction_window_id = self.canvas.create_window(self.screen_width + cfg.BOTTOM_MENU_LAYOUT["btn_compaction_offset_right"], button_y, window=self.btn_compaction, width=cfg.BOTTOM_MENU_LAYOUT["compaction_btn_width"], height=cfg.BOTTOM_MENU_LAYOUT["row_height"], anchor=tk.NW)

        self.status_label = tk.Label(self.window_root, text="Ready", font=("Arial", 9, "italic"), fg=Theme.NEUTRAL, justify=tk.LEFT)
        self.canvas.create_window(cfg.BOTTOM_MENU_LAYOUT["menu_label_x"], bottom_edge + cfg.BOTTOM_MENU_LAYOUT["status_label_y_offset"], window=self.status_label, anchor=tk.NW)

        # =========================================================
        # 4. EVENT LOG STREAM TERMINAL PANEL
        # =========================================================
        log_label = tk.Label(self.window_root, text="EVENT LOG", font=("Arial", 10, "bold"), fg=Theme.PRIMARY)
        log_y = bottom_edge + cfg.EVENT_LOG_LAYOUT["y_offset_from_bottom"]
        log_x = self.screen_width + cfg.EVENT_LOG_LAYOUT["right_edge_offset"]
        self.canvas.create_window(log_x, log_y, window=log_label, anchor=tk.NW)

        self.event_log_widget = tk.Text(self.window_root, height=cfg.EVENT_LOG_LAYOUT["text_widget_height"], width=cfg.EVENT_LOG_LAYOUT["text_widget_width"], font=cfg.EVENT_LOG_LAYOUT["font"], bg="#FFFFFF", fg=Theme.PRIMARY, relief=tk.GROOVE, bd=1, state="disabled")
        self.canvas.create_window(log_x, log_y + 30, window=self.event_log_widget, anchor=tk.NW)
        
        self.event_log_widget.tag_configure("allocate", foreground=Theme.SUCCESS, font=("Courier", 8, "bold"))
        self.event_log_widget.tag_configure("deallocate", foreground=Theme.ERROR, font=("Courier", 8, "bold"))
        self.event_log_widget.tag_configure("warning", foreground=Theme.WARNING, font=("Courier", 8))
        self.event_log_widget.tag_configure("error", foreground=Theme.ERROR, font=("Courier", 8))
        self.event_log_widget.tag_configure("info", foreground=Theme.NEUTRAL, font=("Courier", 8, "italic"))

    def update_status(self, message):
        self.status_label.config(text=message, fg=Theme.PRIMARY)
        self.window_root.update_idletasks()

    def on_mode_changed(self, event=None):
        mode = self.combo_mode.get()
        if mode == "MANUAL":
            self.canvas.itemconfigure(self.pid_window_id, state="normal")
            self.canvas.itemconfigure(self.size_window_id, state="normal")
            self.canvas.itemconfigure(self.alloc_button_id, state="normal")
            self.canvas.itemconfigure(self.dealloc_button_id, state="normal")
            self.update_status("MANUAL mode - Enter Process ID and Size, then click ALLOC/DEALLOC")
        else:
            self.canvas.itemconfigure(self.pid_window_id, state="hidden")
            self.canvas.itemconfigure(self.size_window_id, state="hidden")
            self.canvas.itemconfigure(self.alloc_button_id, state="hidden")
            self.canvas.itemconfigure(self.dealloc_button_id, state="hidden")
            self.update_status("AUTO mode - Click START to begin automatic allocation/deallocation")

    def add_event_log(self, event_text, event_type="INFO"):
        self.event_log_widget.config(state="normal")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        tag = "info"
        if event_type == "ALLOCATE": tag = "allocate"
        elif event_type == "DEALLOCATE": tag = "deallocate"
        elif event_type == "WARNING": tag = "warning"
        elif event_type == "ERROR": tag = "error"
        
        log_entry = f"[{timestamp}] {event_text}\n"
        self.event_log_widget.insert(tk.END, log_entry, tag)
        self.event_log_widget.see(tk.END)
        self.event_log_widget.config(state="disabled")
        self.event_log.append(log_entry)

    def toggle_auto_mode(self):
        if self.combo_mode.get() != "AUTO":
            messagebox.showwarning("Mode Error", "Please select AUTO mode first")
            return
        if not self.auto_mode_running:
            self.auto_mode_running = True
            self.btn_start.config(text="STOP", bg=Theme.WARNING, activebackground="#F57C00")
            self.add_event_log("AUTO mode started", "INFO")
            self.update_status("▶ AUTO mode running - Click STOP to pause")
            self.run_auto_step()
        else:
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS, activebackground="#1B5E20")
            self.add_event_log("AUTO mode stopped", "INFO")
            self.update_status("⏸ AUTO mode paused - Click START to resume")

    def run_auto_step(self):
        if not self.auto_mode_running: return
        try:
            algo = self.combo_algo.get()
            command, process = process_user_choice("RANDOM", None, None, None)
            if process is None:
                self.add_event_log("No processes available", "WARNING")
            else:
                if command == "ALLOCATE":
                    if "MFT" in algo:
                        if "First Fit" in algo: msg = first_fit_mft(process, self.mft_manager)
                        elif "Best Fit" in algo: msg = best_fit_mft(process, self.mft_manager)
                        else: msg = best_available_fit_mft(process, self.mft_manager)
                        if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                            self.mft_manager.waiting_queue.append(process)
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) → WAITING", "WARNING")
                        else:
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) ↦ ALLOCATED", "ALLOCATE")
                    else:
                        if "First Fit" in algo: msg = first_fit_mvt(process, self.mvt_manager)
                        elif "Best Fit" in algo: msg = best_fit_mvt(process, self.mvt_manager)
                        else: msg = worst_fit_mvt(process, self.mvt_manager)
                        if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                            self.mvt_manager.waiting_queue.append(process)
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) → WAITING", "WARNING")
                        else:
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) ↦ ALLOCATED", "ALLOCATE")
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
                    self.add_event_log(f"{process.process_id} ↤ DEALLOCATED", "DEALLOCATE")
            self.refresh_display_matrix()
            self.window_root.after(self.auto_mode_interval, self.run_auto_step)
        except Exception as e:
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS, activebackground="#1B5E20")
            self.add_event_log(f"Error: {str(e)[:40]}", "ERROR")
            messagebox.showerror("AUTO Mode Error", str(e))

    def reset_system(self):
        if self.auto_mode_running:
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS, activebackground="#1B5E20")
        if messagebox.askyesno("Reset System", "Clear all allocations and event log?"):
            try:
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
                self.event_log = []
                self.update_status("✓ System reset")
                self.add_event_log("System reset - Memory cleared", "INFO")
                self.refresh_display_matrix()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def handle_allocation_trigger(self):
        try:
            self.update_status("⟳ Allocating...")
            if self.combo_mode.get() != "MANUAL":
                messagebox.showwarning("Mode Error", "Use AUTO mode's START button or switch to MANUAL")
                return
            algo = self.combo_algo.get()
            pid = self.entry_pid.get().strip()
            size_val_str = self.entry_size.get().strip()
            if not pid or not size_val_str:
                self.update_status("✗ Please enter Process ID and Size")
                messagebox.showerror("Input Error", "Please enter both Process ID and Size")
                return
            try:
                size_val = int(size_val_str)
            except ValueError:
                self.update_status("✗ Size must be a number")
                messagebox.showerror("Input Error", "Size must be a valid number")
                return
            
            command, process = process_user_choice("MANUAL", "ALLOCATE", pid, size_val)
            if "MFT" in algo:
                if "First Fit" in algo: msg = first_fit_mft(process, self.mft_manager)
                elif "Best Fit" in algo: msg = best_fit_mft(process, self.mft_manager)
                else: msg = best_available_fit_mft(process, self.mft_manager)
                if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                    self.mft_manager.waiting_queue.append(process)
                    self.update_status(f"⚠ Process {process.process_id} added to waiting queue")
                else:
                    self.update_status(f"✓ Process {process.process_id} allocated ({process.process_size}K)")
            else:
                if "First Fit" in algo: msg = first_fit_mvt(process, self.mvt_manager)
                elif "Best Fit" in algo: msg = best_fit_mvt(process, self.mvt_manager)
                else: msg = worst_fit_mvt(process, self.mvt_manager)
                if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                    self.mvt_manager.waiting_queue.append(process)
                    self.update_status(f"⚠ Process {process.process_id} added to waiting queue")
                else:
                    self.update_status(f"✓ Process {process.process_id} allocated ({process.process_size}K)")
            self.entry_pid.delete(0, tk.END)
            self.entry_size.delete(0, tk.END)
            self.refresh_display_matrix()
        except Exception as e:
            self.update_status(f"✗ Allocation failed")
            messagebox.showerror("Allocation Error", str(e))

    def handle_deallocation_trigger(self):
        try:
            self.update_status("⟳ Deallocating...")
            if self.combo_mode.get() != "MANUAL":
                messagebox.showwarning("Mode Error", "Use AUTO mode or switch to MANUAL")
                return
            algo = self.combo_algo.get()
            pid = self.entry_pid.get().strip()
            if not pid:
                self.update_status("✗ Please enter Process ID")
                messagebox.showerror("Input Error", "Please enter a Process ID to deallocate")
                return
            command, process = process_user_choice("MANUAL", "DEALLOCATE", pid, None)
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
            self.update_status(f"✓ Process {process.process_id} deallocated")
            self.entry_pid.delete(0, tk.END)
            self.refresh_display_matrix()
        except Exception as e:
            self.update_status("✗ Deallocation failed")
            messagebox.showerror("Deallocation Error", str(e))

    def trigger_mvt_compaction(self):
        try:
            self.update_status("⟳ Compacting memory...")
            msg = self.mvt_manager.compact_memory()
            self.reorder_mvt_queue()
            self.update_status("✓ Memory compacted successfully")
            self.refresh_display_matrix()
            messagebox.showinfo("Compaction Complete", msg)
        except Exception as e:
            self.update_status("✗ Compaction failed")
            messagebox.showerror("Compaction Error", str(e))

    def reorder_mvt_queue(self):
        algo = self.combo_algo.get()
        for queued_proc in list(self.mvt_manager.waiting_queue):
            if "First Fit" in algo: res = first_fit_mvt(queued_proc, self.mvt_manager)
            elif "Best Fit" in algo: res = best_fit_mvt(queued_proc, self.mvt_manager)
            else: res = worst_fit_mvt(queued_proc, self.mvt_manager)
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
    # 5. CORE SIMULATION PANE RENDERING (READS DIRECT FROM CONFIG)
    # =========================================================
    def update_mft_display_map(self):
        total_free_space = 0
        total_internal_frag = 0
        
        self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_title_y"], 
                               text="⏳ Waiting Queue:", font=cfg.SIMULATION_PANE_LAYOUT["font_title"], fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mft_manager.waiting_queue:
            self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"], 
                                   text="[ Queue Empty ]", font=("Courier", 18, "italic"), fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mft_manager.waiting_queue[:15]):
                y_pos = cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"] + (idx * cfg.SIMULATION_PANE_LAYOUT["queue_list_spacing_y"])
                self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], y_pos, 
                                       text=f"• Process {proc.process_id} ({proc.process_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_waiting_proc"], fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

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
                self.canvas.create_text(x1 + 120, y1 + (proc_height / 2), text=f"{partition.occupied_process.process_id}\n({partition.occupied_process.process_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill="white", tags="mem_element")
                
                if partition.internal_fragmentation > 0:
                    self.canvas.create_rectangle(x1, y1 + proc_height, x2, y2, fill=Theme.FRAG, outline=Theme.FRAG_DARK, width=2, tags="mem_element")
                    self.canvas.create_text(x1 + 120, y1 + proc_height + ((height - proc_height) / 2), text=f"FRAG: {partition.internal_fragmentation}K", font=cfg.SIMULATION_PANE_LAYOUT["font_frag_block"], fill="white", tags="mem_element")
                    total_internal_frag += partition.internal_fragmentation
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 120, y1 + (height / 2), text="✓ FREE HOLE", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill=Theme.SUCCESS, tags="mem_element")
                total_free_space += partition.partition_size
            start_y += height
            
        self.canvas.create_text(x1 - 20, start_y, text="64K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text="0K")
        self.lbl_internal_frag.config(text=f"{total_internal_frag}K")

    def update_mvt_display_map(self):
        total_free_space = 0
        total_external_frag = 0
        free_hole_segments_count = 0
        
        self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_title_y"], 
                               text="⏳ Waiting Queue:", font=cfg.SIMULATION_PANE_LAYOUT["font_title"], fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mvt_manager.waiting_queue:
            self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"], 
                                   text="[ Queue Empty ]", font=("Courier", 18, "italic"), fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mvt_manager.waiting_queue[:15]):
                y_pos = cfg.SIMULATION_PANE_LAYOUT["queue_list_start_y"] + (idx * cfg.SIMULATION_PANE_LAYOUT["queue_list_spacing_y"])
                self.canvas.create_text(cfg.SIMULATION_PANE_LAYOUT["queue_title_x"], y_pos, 
                                       text=f"• Process {proc.process_id} ({proc.process_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_waiting_proc"], fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

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
                self.canvas.create_text(x1 + 120, y1 + (height / 2), text=f"{block.occupied_process.process_id}\n({block.block_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill="white", tags="mem_element")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 120, y1 + (height / 2), text=f"✓ FREE HOLE\n({block.block_size}K)", font=cfg.SIMULATION_PANE_LAYOUT["font_allocated_block"], fill=Theme.SUCCESS, tags="mem_element")
                total_free_space += block.block_size
                free_hole_segments_count += 1
            start_y += height
            
        self.canvas.create_text(x1 - 20, start_y, text="64K", font=cfg.SIMULATION_PANE_LAYOUT["font_address_label"], anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

        active_allocations = any(b.occupied_process is not None for b in self.mvt_manager.blocks)
        if active_allocations and free_hole_segments_count > 1:
            total_external_frag = total_free_space
        elif active_allocations and free_hole_segments_count == 1:
            if self.mvt_manager.blocks[-1].occupied_process is not None:
                total_external_frag = total_free_space

        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text=f"{total_external_frag}K")
        self.lbl_internal_frag.config(text="0K")


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagementApp(root)
    root.mainloop()