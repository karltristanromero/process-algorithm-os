# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import random
import os
from PIL import Image, ImageTk

# Import core structural classes for memory management
from utils.process_generator import process_pool, process_user_choice

from mft.fixed_partition import FixedMemoryManager
from mft.first_fit import first_fit_mft
from mft.best_fit import best_fit_mft
from mft.best_available_fit import best_available_fit_mft

from mvt.variable_partition import VariableMemoryManager
from mvt.first_fit import first_fit_mvt
from mvt.best_fit import best_fit_mvt
from mvt.worst_fit import worst_fit_mvt

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

# Part 2: Main Application Architecture and Layout Structure
class MemoryManagementApp:
    def __init__(self, window_root):
        self.window_root = window_root
        self.window_root.title("Memory Management Simulator")
        
        # Get screen dimensions
        screen_width = self.window_root.winfo_screenwidth()
        screen_height = self.window_root.winfo_screenheight()
        
        # Account for taskbar (typically 40-60 pixels) by reducing height
        taskbar_height = 60
        effective_height = screen_height - taskbar_height
        
        # Set window geometry with taskbar space
        self.window_root.geometry(f"{screen_width}x{effective_height}+0+0")
        self.window_root.state('zoomed')  # Maximize on Windows
        
        # Store screen dimensions for canvas
        self.screen_width = screen_width
        self.screen_height = effective_height
        
        # Bind Escape key to easily close the app
        self.window_root.bind("<Escape>", lambda e: self.window_root.destroy())
        
        # Initialize core partition simulators
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        
        # Sync waiting queues tracking pools
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        # Auto mode control
        self.auto_mode_running = False
        self.auto_mode_interval = 1000  # milliseconds between each auto action
        
        # Event log tracking
        self.event_log = []
        
        # Compile interface overlay
        self.build_gui_layout()
        
        # Execute initial calculations draw
        self.refresh_display_matrix()


    def build_gui_layout(self):
        # Resolve absolute path to prevent folder execution location blocks
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "bg1.png")

        # Load and scale background image to fit screen exactly
        try:
            # Load image using PIL
            bg_pil = Image.open(bg_path)
            # Resize to exact screen dimensions
            bg_pil = bg_pil.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(bg_pil)
        except Exception:
            # Fallback if there is a naming discrepancy
            try:
                fallback_path = os.path.join(script_dir, "image_7a5c02.png")
                bg_pil = Image.open(fallback_path)
                bg_pil = bg_pil.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(bg_pil)
            except Exception:
                messagebox.showerror("Asset Error", f"Missing background image inside directory:\n{script_dir}")
                self.window_root.destroy()
                return

        # Create canvas with screen dimensions
        self.canvas = tk.Canvas(self.window_root, width=self.screen_width, height=self.screen_height, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Configure modern ttk styles
        self._setup_styles()

        # Calculate responsive positions based on screen size
        right_edge = self.screen_width - 120
        bottom_edge = self.screen_height - 120
        
        # =========================================================
        # 1. IMPROVED STATISTICS CARDS WITH BETTER STYLING
        # =========================================================
        # Card 1: Total Free Space
        self.lbl_total_space = tk.Label(
            self.window_root, text="64K", font=("Courier", 32, "bold"), 
            fg=Theme.SUCCESS
        )
        self.canvas.create_window(right_edge, 160, window=self.lbl_total_space, anchor=tk.CENTER)

        # Card 2: External Fragmentation
        self.lbl_external_frag = tk.Label(
            self.window_root, text="0K", font=("Courier", 32, "bold"), 
            fg=Theme.WARNING
        )
        self.canvas.create_window(right_edge, 365, window=self.lbl_external_frag, anchor=tk.CENTER)

        # Card 3: Internal Fragmentation
        self.lbl_internal_frag = tk.Label(
            self.window_root, text="0K", font=("Courier", 32, "bold"), 
            fg=Theme.ERROR
        )
        self.canvas.create_window(right_edge, 570, window=self.lbl_internal_frag, anchor=tk.CENTER)

        # =========================================================
        # 2. IMPROVED INPUT ENTRY FIELDS WITH MODERN STYLING
        # =========================================================
        # Enhanced PID Entry - Better visual feedback (hidden by default, shown in MANUAL mode)
        self.entry_pid = tk.Entry(
            self.window_root, width=8, font=("Arial", 11, "bold"), 
            bd=2, relief=tk.GROOVE, bg="#FFFFFF", fg=Theme.PRIMARY,
            insertbackground=Theme.PRIMARY, cursor="xterm"
        )
        self.entry_pid.config(highlightthickness=1, highlightcolor=Theme.BG_SECONDARY)
        self.pid_window_id = self.canvas.create_window(right_edge - 40, bottom_edge - 250, window=self.entry_pid, anchor=tk.W)

        # Enhanced Size Entry - Better visual feedback (hidden by default, shown in MANUAL mode)
        self.entry_size = tk.Entry(
            self.window_root, width=8, font=("Arial", 11, "bold"), 
            bd=2, relief=tk.GROOVE, bg="#FFFFFF", fg=Theme.PRIMARY,
            insertbackground=Theme.PRIMARY, cursor="xterm"
        )
        self.entry_size.config(highlightthickness=1, highlightcolor=Theme.BG_SECONDARY)
        self.size_window_id = self.canvas.create_window(right_edge - 40, bottom_edge - 195, window=self.entry_size, anchor=tk.W)

        # Manual control buttons (shown in MANUAL mode)
        btn_manual_alloc = tk.Button(
            self.window_root, text="ALLOC", font=("Arial", 9, "bold"), 
            bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, activebackground=Theme.BG_SECONDARY,
            relief=tk.RAISED, bd=2, cursor="hand2", padx=2, pady=2,
            command=self.handle_allocation_trigger
        )
        btn_manual_alloc.config(highlightthickness=0)
        self.alloc_button_id = self.canvas.create_window(right_edge - 40, bottom_edge - 145, window=btn_manual_alloc, width=60, height=35, anchor=tk.NW)

        btn_manual_dealloc = tk.Button(
            self.window_root, text="DEALLOC", font=("Arial", 9, "bold"), 
            bg=Theme.BG_PRIMARY, fg=Theme.PRIMARY, activebackground=Theme.BG_SECONDARY,
            relief=tk.RAISED, bd=2, cursor="hand2", padx=2, pady=2,
            command=self.handle_deallocation_trigger
        )
        btn_manual_dealloc.config(highlightthickness=0)
        self.dealloc_button_id = self.canvas.create_window(right_edge - 40, bottom_edge - 105, window=btn_manual_dealloc, width=60, height=35, anchor=tk.NW)

        # =========================================================
        # 3. BOTTOM MENU BAR WITH REDESIGNED CONTROLS
        # =========================================================
        button_y = bottom_edge + 20
        
        # Menu Label
        menu_label = tk.Label(
            self.window_root, text="MENU", font=("Arial", 12, "bold"), 
            fg=Theme.PRIMARY
        )
        self.canvas.create_window(98, button_y, window=menu_label, anchor=tk.NW)

        # Mode Selection - MANUAL or AUTO
        mode_label = tk.Label(
            self.window_root, text="MODE:", font=("Arial", 10, "bold"), 
            fg=Theme.PRIMARY
        )
        self.canvas.create_window(150, button_y + 5, window=mode_label, anchor=tk.NW)
        
        self.combo_mode = ttk.Combobox(
            self.window_root, values=["MANUAL", "AUTO"], state="readonly", 
            font=("Arial", 10, "bold"), style="ModernCombo.TCombobox", width=8
        )
        self.combo_mode.set("MANUAL")
        self.canvas.create_window(210, button_y, window=self.combo_mode, width=100, height=50, anchor=tk.NW)
        self.combo_mode.bind("<<ComboboxSelected>>", self.on_mode_changed)

        # Algorithm Selection - All algorithms
        algo_label = tk.Label(
            self.window_root, text="ALGO:", font=("Arial", 10, "bold"), 
            fg=Theme.PRIMARY
        )
        self.canvas.create_window(320, button_y + 5, window=algo_label, anchor=tk.NW)
        
        self.combo_algo = ttk.Combobox(
            self.window_root, values=["MFT: First Fit", "MFT: Best Fit", "MFT: Best Available", 
                                      "MVT: First Fit", "MVT: Best Fit", "MVT: Worst Fit"], 
            state="readonly", font=("Arial", 9, "bold"), style="ModernCombo.TCombobox", width=15
        )
        self.combo_algo.set("MFT: First Fit")
        self.canvas.create_window(370, button_y, window=self.combo_algo, width=210, height=50, anchor=tk.NW)
        self.combo_algo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display_matrix())

        # Start Button - For AUTO mode
        btn_start = tk.Button(
            self.window_root, text="START", font=("Arial", 10, "bold"), 
            bg=Theme.SUCCESS, fg="white", activebackground="#1B5E20",
            relief=tk.RAISED, bd=2, cursor="hand2", padx=5, pady=5,
            command=self.toggle_auto_mode
        )
        btn_start.config(highlightthickness=0)
        self.start_button_id = self.canvas.create_window(600, button_y, window=btn_start, width=90, height=50, anchor=tk.NW)
        self.btn_start = btn_start

        # Reset Button - Clear all memory
        btn_reset = tk.Button(
            self.window_root, text="RESET", font=("Arial", 10, "bold"), 
            bg=Theme.ERROR, fg="white", activebackground="#B71C1C",
            relief=tk.RAISED, bd=2, cursor="hand2", padx=5, pady=5,
            command=self.reset_system
        )
        btn_reset.config(highlightthickness=0)
        self.reset_button_id = self.canvas.create_window(710, button_y, window=btn_reset, width=90, height=50, anchor=tk.NW)

        # =========================================================
        # 4. ENHANCED UTILITY BUTTONS & FEEDBACK
        # =========================================================
        # Memory Compaction Button - For MVT only
        self.btn_compaction = tk.Button(
            self.window_root, text="🔨 COMPACT", font=("Arial", 10, "bold"), 
            bg=Theme.WARNING, fg="white", activebackground="#F57C00", 
            relief=tk.RAISED, bd=2, cursor="hand2", padx=3, pady=3,
            command=self.trigger_mvt_compaction
        )
        self.btn_compaction.config(highlightthickness=0, wraplength=200)
        self.compaction_window_id = self.canvas.create_window(right_edge - 20, button_y, window=self.btn_compaction, width=210, height=50, anchor=tk.NW)

        # Status Label - Real-time feedback
        self.status_label = tk.Label(
            self.window_root, text="Ready", font=("Arial", 9, "italic"), 
            fg=Theme.NEUTRAL, justify=tk.LEFT
        )
        self.canvas.create_window(98, bottom_edge + 70, window=self.status_label, anchor=tk.NW)

        # =========================================================
        # 5. EVENT LOG PANEL
        # =========================================================
        # Event log label
        log_label = tk.Label(
            self.window_root, text="EVENT LOG", font=("Arial", 10, "bold"), 
            fg=Theme.PRIMARY
        )
        log_y = bottom_edge - 180
        self.canvas.create_window(right_edge - 240, log_y, window=log_label, anchor=tk.NW)

        # Event log text widget
        self.event_log_widget = tk.Text(
            self.window_root, height=10, width=35, font=("Courier", 8), 
            bg="#FFFFFF", fg=Theme.PRIMARY, relief=tk.GROOVE, bd=1,
            state="disabled"
        )
        log_window_id = self.canvas.create_window(right_edge - 240, log_y + 30, window=self.event_log_widget, anchor=tk.NW)
        
        # Scrollbar for event log
        log_scrollbar = ttk.Scrollbar(self.window_root, orient=tk.VERTICAL, command=self.event_log_widget.yview)
        self.event_log_widget.config(yscrollcommand=log_scrollbar.set)
        
        # Configure text tags for color coding
        self.event_log_widget.tag_configure("allocate", foreground=Theme.SUCCESS, font=("Courier", 8, "bold"))
        self.event_log_widget.tag_configure("deallocate", foreground=Theme.ERROR, font=("Courier", 8, "bold"))
        self.event_log_widget.tag_configure("warning", foreground=Theme.WARNING, font=("Courier", 8))
        self.event_log_widget.tag_configure("error", foreground=Theme.ERROR, font=("Courier", 8))
        self.event_log_widget.tag_configure("info", foreground=Theme.NEUTRAL, font=("Courier", 8, "italic"))
    
    def _setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Modern Combobox style
        style.configure("ModernCombo.TCombobox", 
                       fieldbackground=Theme.BG_PRIMARY, 
                       background=Theme.BG_SECONDARY, 
                       arrowcolor=Theme.PRIMARY,
                       padding=5)
        style.map("ModernCombo.TCombobox",
                 fieldbackground=[("readonly", Theme.BG_PRIMARY)],
                 background=[("active", Theme.BG_SECONDARY)])
    
    def update_status(self, message):
        """Update status bar with feedback"""
        self.status_label.config(text=message, fg=Theme.PRIMARY)
        self.window_root.update_idletasks()


    def on_mode_changed(self, event=None):
        """Handle mode change between MANUAL and AUTO"""
        mode = self.combo_mode.get()
        
        if mode == "MANUAL":
            # Show manual input controls
            self.canvas.itemconfigure(self.pid_window_id, state="normal")
            self.canvas.itemconfigure(self.size_window_id, state="normal")
            self.canvas.itemconfigure(self.alloc_button_id, state="normal")
            self.canvas.itemconfigure(self.dealloc_button_id, state="normal")
            self.entry_pid.configure(state="normal")
            self.entry_size.configure(state="normal")
            self.update_status("MANUAL mode - Enter Process ID and Size, then click ALLOC/DEALLOC")
        else:
            # Hide manual input controls for AUTO mode
            self.canvas.itemconfigure(self.pid_window_id, state="hidden")
            self.canvas.itemconfigure(self.size_window_id, state="hidden")
            self.canvas.itemconfigure(self.alloc_button_id, state="hidden")
            self.canvas.itemconfigure(self.dealloc_button_id, state="hidden")
            self.update_status("AUTO mode - Click START to begin automatic allocation/deallocation")
    
    def add_event_log(self, event_text, event_type="INFO"):
        """Add an event to the event log"""
        self.event_log_widget.config(state="normal")
        
        # Add timestamp and event
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on event type
        tag = "info"
        if event_type == "ALLOCATE":
            tag = "allocate"
        elif event_type == "DEALLOCATE":
            tag = "deallocate"
        elif event_type == "WARNING":
            tag = "warning"
        elif event_type == "ERROR":
            tag = "error"
        
        log_entry = f"[{timestamp}] {event_text}\n"
        self.event_log_widget.insert(tk.END, log_entry, tag)
        self.event_log_widget.see(tk.END)  # Auto-scroll to bottom
        self.event_log_widget.config(state="disabled")
        self.event_log.append(log_entry)
    
    def toggle_auto_mode(self):
        """Toggle AUTO mode on/off"""
        if self.combo_mode.get() != "AUTO":
            messagebox.showwarning("Mode Error", "Please select AUTO mode first")
            return
        
        if not self.auto_mode_running:
            # Start AUTO mode
            self.auto_mode_running = True
            self.btn_start.config(text="STOP", bg=Theme.WARNING, activebackground="#F57C00")
            self.add_event_log("AUTO mode started", "INFO")
            self.update_status("▶ AUTO mode running - Click STOP to pause")
            self.run_auto_step()  # Start the loop
        else:
            # Stop AUTO mode
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS, activebackground="#1B5E20")
            self.add_event_log("AUTO mode stopped", "INFO")
            self.update_status("⏸ AUTO mode paused - Click START to resume")
    
    def run_auto_step(self):
        """Execute one auto allocation/deallocation cycle"""
        if not self.auto_mode_running:
            return
        
        try:
            algo = self.combo_algo.get()
            command, process = process_user_choice("RANDOM", None, None, None)
            
            if process is None:
                self.add_event_log("No processes available", "WARNING")
                # Keep running in case processes are deallocated later
            else:
                if command == "ALLOCATE":
                    if "MFT" in algo:
                        if "First Fit" in algo:
                            msg = first_fit_mft(process, self.mft_manager)
                        elif "Best Fit" in algo:
                            msg = best_fit_mft(process, self.mft_manager)
                        else:
                            msg = best_available_fit_mft(process, self.mft_manager)
                            
                        if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                            self.mft_manager.waiting_queue.append(process)
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) → WAITING", "WARNING")
                        else:
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) ↦ ALLOCATED", "ALLOCATE")
                    else:
                        if "First Fit" in algo:
                            msg = first_fit_mvt(process, self.mvt_manager)
                        elif "Best Fit" in algo:
                            msg = best_fit_mvt(process, self.mvt_manager)
                        else:
                            msg = worst_fit_mvt(process, self.mvt_manager)
                            
                        if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                            self.mvt_manager.waiting_queue.append(process)
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) → WAITING", "WARNING")
                        else:
                            self.add_event_log(f"{process.process_id} ({process.process_size}K) ↦ ALLOCATED", "ALLOCATE")
                
                elif command == "DEALLOCATE":
                    if "MFT" in algo:
                        self.mft_manager.deallocate_process(process.process_id)
                        for queued_proc in list(self.mft_manager.waiting_queue):
                            if "First Fit" in algo:
                                res = first_fit_mft(queued_proc, self.mft_manager)
                            elif "Best Fit" in algo:
                                res = best_fit_mft(queued_proc, self.mft_manager)
                            else:
                                res = best_available_fit_mft(queued_proc, self.mft_manager)
                            if "Allocated" in res:
                                self.mft_manager.waiting_queue.remove(queued_proc)
                    else:
                        self.mvt_manager.deallocate_process(process.process_id)
                        self.reorder_mvt_queue()
                    
                    self.add_event_log(f"{process.process_id} ↤ DEALLOCATED", "DEALLOCATE")
            
            self.refresh_display_matrix()
            
            # Schedule next auto step
            self.window_root.after(self.auto_mode_interval, self.run_auto_step)
        
        except Exception as e:
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS, activebackground="#1B5E20")
            self.add_event_log(f"Error: {str(e)[:40]}", "ERROR")
            messagebox.showerror("AUTO Mode Error", str(e))
    
    def reset_system(self):
        """Reset the entire system - stop AUTO mode and clear memory"""
        # Stop AUTO mode if running
        if self.auto_mode_running:
            self.auto_mode_running = False
            self.btn_start.config(text="START", bg=Theme.SUCCESS, activebackground="#1B5E20")
        
        if messagebox.askyesno("Reset System", "Clear all allocations and event log?"):
            try:
                # Clear MFT
                for partition in self.mft_manager.partitions:
                    partition.occupied_process = None
                    partition.internal_fragmentation = 0
                self.mft_manager.waiting_queue = []
                
                # Clear MVT
                for block in self.mvt_manager.blocks:
                    block.occupied_process = None
                self.mvt_manager.waiting_queue = []
                
                # Clear event log
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
            mode = self.combo_mode.get()
            
            # Only allow manual allocation in MANUAL mode
            if mode != "MANUAL":
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
                if "First Fit" in algo:
                    msg = first_fit_mft(process, self.mft_manager)
                elif "Best Fit" in algo:
                    msg = best_fit_mft(process, self.mft_manager)
                else:
                    msg = best_available_fit_mft(process, self.mft_manager)
                    
                if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                    self.mft_manager.waiting_queue.append(process)
                    self.update_status(f"⚠ Process {process.process_id} added to waiting queue")
                else:
                    self.update_status(f"✓ Process {process.process_id} allocated ({process.process_size}K)")
            else:
                if "First Fit" in algo:
                    msg = first_fit_mvt(process, self.mvt_manager)
                elif "Best Fit" in algo:
                    msg = best_fit_mvt(process, self.mvt_manager)
                else:
                    msg = worst_fit_mvt(process, self.mvt_manager)
                    
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
            mode = self.combo_mode.get()
            
            # Only allow manual deallocation in MANUAL mode
            if mode != "MANUAL":
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
                    if "First Fit" in algo:
                        res = first_fit_mft(queued_proc, self.mft_manager)
                    elif "Best Fit" in algo:
                        res = best_fit_mft(queued_proc, self.mft_manager)
                    else:
                        res = best_available_fit_mft(queued_proc, self.mft_manager)
                    if "Allocated" in res:
                        self.mft_manager.waiting_queue.remove(queued_proc)
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
            if "First Fit" in algo:
                res = first_fit_mvt(queued_proc, self.mvt_manager)
            elif "Best Fit" in algo:
                res = best_fit_mvt(queued_proc, self.mvt_manager)
            else:
                res = worst_fit_mvt(queued_proc, self.mvt_manager)
            if "Allocated" in res:
                self.mvt_manager.waiting_queue.remove(queued_proc)


    def refresh_display_matrix(self):
        # Clear specific tagged elements drawn inside the tracking list frame area
        self.canvas.delete("mem_element")
        
        if "MFT" in self.combo_algo.get():
            self.canvas.itemconfigure(self.compaction_window_id, state="hidden")
            self.update_mft_display_map()
        else:
            self.canvas.itemconfigure(self.compaction_window_id, state="normal")
            self.update_mvt_display_map()


    def update_mft_display_map(self):
        total_free_space = 0
        total_internal_frag = 0
        
        # Draw Waiting Queue entries with improved styling
        self.canvas.create_text(640, 100, text="⏳ Waiting Queue:", font=("Courier", 22, "bold"), 
                               fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mft_manager.waiting_queue:
            self.canvas.create_text(640, 150, text="[ Queue Empty ]", font=("Courier", 18, "italic"), 
                                   fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mft_manager.waiting_queue[:15]):
                self.canvas.create_text(640, 150 + (idx * 35), 
                                       text=f"• Process {proc.process_id} ({proc.process_size}K)", 
                                       font=("Courier", 16, "bold"), fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

        # Vertical box geometry scaling vectors
        start_y = 100
        x1, x2 = 320, 560
        canvas_scale = 10.0
        
        for partition in self.mft_manager.partitions:
            height = partition.partition_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 20, start_y, text=f"{int(partition.partition_size)}K", 
                                   font=("Courier", 14, "bold"), anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")
            
            if partition.occupied_process:
                proc_height = partition.occupied_process.process_size * canvas_scale
                
                # Active allocation block with improved styling
                self.canvas.create_rectangle(x1, y1, x2, y1 + proc_height, fill=Theme.ALLOCATED, 
                                           outline=Theme.ALLOCATED_DARK, width=3, tags="mem_element")
                self.canvas.create_text(x1 + 120, y1 + (proc_height / 2), 
                                       text=f"{partition.occupied_process.process_id}\n({partition.occupied_process.process_size}K)", 
                                       font=("Arial", 13, "bold"), fill="white", tags="mem_element")
                
                # Internal fragmentation with improved styling
                if partition.internal_fragmentation > 0:
                    self.canvas.create_rectangle(x1, y1 + proc_height, x2, y2, fill=Theme.FRAG, 
                                               outline=Theme.FRAG_DARK, width=2, tags="mem_element")
                    self.canvas.create_text(x1 + 120, y1 + proc_height + ((height - proc_height) / 2), 
                                           text=f"FRAG: {partition.internal_fragmentation}K", 
                                           font=("Arial", 11, "bold"), fill="white", tags="mem_element")
                    total_internal_frag += partition.internal_fragmentation
            else:
                # Open free space with improved styling
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, 
                                           outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 120, y1 + (height / 2), text="✓ FREE HOLE", 
                                       font=("Arial", 13, "bold"), fill=Theme.SUCCESS, tags="mem_element")
                total_free_space += partition.partition_size
                
            start_y += height
            
        self.canvas.create_text(x1 - 20, start_y, text="64K", font=("Courier", 14, "bold"), 
                               anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

        # Push summaries to status dashboard
        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text="0K")
        self.lbl_internal_frag.config(text=f"{total_internal_frag}K")


    def update_mvt_display_map(self):
        total_free_space = 0
        total_external_frag = 0
        free_hole_segments_count = 0
        
        # Draw Waiting Queue with improved styling
        self.canvas.create_text(640, 100, text="⏳ Waiting Queue:", font=("Courier", 22, "bold"), 
                               fill=Theme.PRIMARY, anchor=tk.W, tags="mem_element")
        if not self.mvt_manager.waiting_queue:
            self.canvas.create_text(640, 150, text="[ Queue Empty ]", font=("Courier", 18, "italic"), 
                                   fill=Theme.NEUTRAL, anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mvt_manager.waiting_queue[:15]):
                self.canvas.create_text(640, 150 + (idx * 35), 
                                       text=f"• Process {proc.process_id} ({proc.process_size}K)", 
                                       font=("Courier", 16, "bold"), fill=Theme.WAITING, anchor=tk.W, tags="mem_element")

        start_y = 100
        x1, x2 = 320, 560
        canvas_scale = 10.0
        
        for block in self.mvt_manager.blocks:
            height = block.block_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 20, y1, text=f"{block.start_address}K", 
                                   font=("Courier", 14, "bold"), anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")
            
            if block.occupied_process:
                # Allocated block with improved styling
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.ALLOCATED, 
                                           outline=Theme.ALLOCATED_DARK, width=3, tags="mem_element")
                self.canvas.create_text(x1 + 120, y1 + (height / 2), 
                                       text=f"{block.occupied_process.process_id}\n({block.block_size}K)", 
                                       font=("Arial", 13, "bold"), fill="white", tags="mem_element")
            else:
                # Free hole with improved styling
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.FREE, 
                                           outline=Theme.FREE_BORDER, width=2, tags="mem_element")
                self.canvas.create_text(x1 + 120, y1 + (height / 2), 
                                       text=f"✓ FREE HOLE\n({block.block_size}K)", 
                                       font=("Arial", 12, "bold"), fill=Theme.SUCCESS, tags="mem_element")
                total_free_space += block.block_size
                free_hole_segments_count += 1
                
            start_y += height
            
        self.canvas.create_text(x1 - 20, start_y, text="64K", font=("Courier", 14, "bold"), 
                               anchor=tk.E, fill=Theme.PRIMARY, tags="mem_element")

        # Evaluate variable partition metrics
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