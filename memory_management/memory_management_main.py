# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import random

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

# Part 2: Main Application Architecture and Layout Structure
class MemoryManagementApp:
    def __init__(self, window_root):
        self.window_root = window_root
        self.window_root.title("Memory Management Simulator - MFT & MVT")
        
        # Set window size
        self.window_root.geometry("1920x1080")
        
        # Initialize core memory engines
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        
        # Track waiting processes that cannot currently fit into active vlocks
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        # Build the layout grids
        self.build_gui_layout()
        
        # Initial draw of both workspace components to calculate starting free spaces
        self.update_mft_display_map()
        self.update_mvt_display_map()


    def build_gui_layout(self):
       # Crate a central notebook layout element spanning the whole viewport
        self.notebook = ttk.Notebook(self.window_root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.mft_tab = ttk.Frame(self.notebook)
        self.mvt_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.mft_tab, text="   MFT (Fixed Partitioning Mode)   ")
        self.notebook.add(self.mvt_tab, text="   MVT (Variable Partitioning Mode)   ")


        # 1. MFT INTERFACE GRID PANEL DESIGN
        # Real-time Stats Header bar for MFT (Shows free space all the time)
        self.mft_stats_bar = ttk.LabelFrame(self.mft_tab, text=" Real-Time MFT Memory Status Indicators ")
        self.mft_stats_bar.pack(fill=tk.X, padx=15, pady=10)
        
        self.lbl_mft_free_space = ttk.Label(self.mft_stats_bar, text="Total Unallocated Free Space: 64K", font=("Arial", 13, "bold"), foreground="green")
        self.lbl_mft_free_space.pack(side=tk.LEFT, padx=30, pady=10)
        
        self.lbl_mft_internal_frag = ttk.Label(self.mft_stats_bar, text="Total Internal Fragmentation: 0K", font=("Arial", 13, "bold"), foreground="red")
        self.lbl_mft_internal_frag.pack(side=tk.LEFT, padx=30, pady=10)
        
        # Split Bottom Layout into Control (Left) and Maps (Right)
        mft_body_frame = ttk.Frame(self.mft_tab)
        mft_body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        mft_left_control = ttk.Frame(mft_body_frame, width=450)
        mft_left_control.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        mft_left_control.pack_propagate(False)
        
        mft_right_display = ttk.Frame(mft_body_frame)
        mft_right_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Manual input entry panels for MFT
        mft_manual_box = ttk.LabelFrame(mft_left_control, text=" Manual Process Control Board ")
        mft_manual_box.pack(fill=tk.X, pady=10, ipady=5)
        
        ttk.Label(mft_manual_box, text="Process ID (P1-P10):").grid(row=0, column=0, padx=10, pady=8, sticky=tk.W)
        self.entry_mft_pid = ttk.Entry(mft_manual_box, width=15)
        self.entry_mft_pid.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        
        ttk.Label(mft_manual_box, text="Size (1K - 32K):").grid(row=1, column=0, padx=10, pady=8, sticky=tk.W)
        self.entry_mft_size = ttk.Entry(mft_manual_box, width=15)
        self.entry_mft_size.grid(row=1, column=1, padx=10, pady=8, sticky=tk.W)
        
        ttk.Label(mft_manual_box, text="Select Allocation Fit:").grid(row=2, column=0, padx=10, pady=8, sticky=tk.W)
        self.combo_mft_algo = ttk.Combobox(mft_manual_box, values=["First Fit", "Best Fit", "Best Available Fit"], state="readonly", width=18)
        self.combo_mft_algo.set("First Fit")
        self.combo_mft_algo.grid(row=2, column=1, padx=10, pady=8, sticky=tk.W)
        
        btn_mft_alloc = ttk.Button(mft_manual_box, text="EXECUTE ALLOCATE", command=lambda: self.execute_mft_action("MANUAL", "ALLOCATE"))
        btn_mft_alloc.grid(row=3, column=0, padx=10, pady=12, sticky=tk.E)
        
        btn_mft_dealloc = ttk.Button(mft_manual_box, text="EXECUTE DEALLOCATE", command=lambda: self.execute_mft_action("MANUAL", "DEALLOCATE"))
        btn_mft_dealloc.grid(row=3, column=1, padx=10, pady=12, sticky=tk.W)
        
        # Automated random panels for MFT
        mft_auto_box = ttk.LabelFrame(mft_left_control, text=" Automated Dynamic Workload Board ")
        mft_auto_box.pack(fill=tk.X, pady=15, ipady=10)
        
        btn_mft_random = ttk.Button(mft_auto_box, text="INJECT NEXT RANDOM EVENT STEP", command=lambda: self.execute_mft_action("RANDOM"))
        btn_mft_random.pack(padx=20, pady=15, fill=tk.X)
        
        # Text Console Output log panel for MFT
        mft_log_box = ttk.LabelFrame(mft_left_control, text=" System Event Activity Log Readout ")
        mft_log_box.pack(fill=tk.BOTH, expand=True, pady=10)
        self.txt_mft_log = tk.Text(mft_log_box, height=15, width=40, state="disabled", wrap=tk.WORD, bg="#f0f0f0")
        self.txt_mft_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right Graphical Canvas Mapping for MFT
        self.mft_canvas = tk.Canvas(mft_right_display, bg="white", bd=2, relief=tk.SUNKEN)
        self.mft_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        
        # 2. MVT INTERFACE GRID PANEL DESIGN
        # Real-time Stats Header bar for MVT (Shows free space all the time)
        self.mvt_stats_bar = ttk.LabelFrame(self.mvt_tab, text=" Real-Time MVT Memory Status Indicators ")
        self.mvt_stats_bar.pack(fill=tk.X, padx=15, pady=10)
        
        self.lbl_mvt_free_space = ttk.Label(self.mvt_stats_bar, text="Total Unallocated Free Space: 64K", font=("Arial", 13, "bold"), foreground="green")
        self.lbl_mvt_free_space.pack(side=tk.LEFT, padx=30, pady=10)
        
        self.lbl_mvt_external_frag = ttk.Label(self.mvt_stats_bar, text="Total External Fragmentation: 0K", font=("Arial", 13, "bold"), foreground="orange")
        self.lbl_mvt_external_frag.pack(side=tk.LEFT, padx=30, pady=10)
        
        # Split Bottom Layout into Control (Left) and Maps (Right)
        mvt_body_frame = ttk.Frame(self.mvt_tab)
        mvt_body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        mvt_left_control = ttk.Frame(mvt_body_frame, width=450)
        mvt_left_control.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        mvt_left_control.pack_propagate(False)
        
        mvt_right_display = ttk.Frame(mvt_body_frame)
        mvt_right_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Manual input entry panels for MVT
        mvt_manual_box = ttk.LabelFrame(mvt_left_control, text=" Manual Process Control Board ")
        mvt_manual_box.pack(fill=tk.X, pady=10, ipady=5)
        
        ttk.Label(mvt_manual_box, text="Process ID (P1-P10):").grid(row=0, column=0, padx=10, pady=8, sticky=tk.W)
        self.entry_mvt_pid = ttk.Entry(mvt_manual_box, width=15)
        self.entry_mvt_pid.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        
        ttk.Label(mvt_manual_box, text="Size (1K - 32K):").grid(row=1, column=0, padx=10, pady=8, sticky=tk.W)
        self.entry_mvt_size = ttk.Entry(mvt_manual_box, width=15)
        self.entry_mvt_size.grid(row=1, column=1, padx=10, pady=8, sticky=tk.W)
        
        ttk.Label(mvt_manual_box, text="Select Allocation Fit:").grid(row=2, column=0, padx=10, pady=8, sticky=tk.W)
        self.combo_mvt_algo = ttk.Combobox(mvt_manual_box, values=["First Fit", "Best Fit", "Worst Fit"], state="readonly", width=18)
        self.combo_mvt_algo.set("First Fit")
        self.combo_mvt_algo.grid(row=2, column=1, padx=10, pady=8, sticky=tk.W)
        
        btn_mvt_alloc = ttk.Button(mvt_manual_box, text="EXECUTE ALLOCATE", command=lambda: self.execute_mvt_action("MANUAL", "ALLOCATE"))
        btn_mvt_alloc.grid(row=3, column=0, padx=10, pady=12, sticky=tk.E)
        
        btn_mvt_dealloc = ttk.Button(mvt_manual_box, text="EXECUTE DEALLOCATE", command=lambda: self.execute_mvt_action("MANUAL", "DEALLOCATE"))
        btn_mvt_dealloc.grid(row=3, column=1, padx=10, pady=12, sticky=tk.W)
        
        # Automated random panels for MVT + compaction trigger
        mvt_auto_box = ttk.LabelFrame(mvt_left_control, text=" Automated Dynamic Workload Board ")
        mvt_auto_box.pack(fill=tk.X, pady=15, ipady=5)
        
        btn_mvt_random = ttk.Button(mvt_auto_box, text="INJECT NEXT RANDOM EVENT STEP", command=lambda: self.execute_mvt_action("RANDOM"))
        btn_mvt_random.pack(padx=20, pady=10, fill=tk.X)
        
        btn_mvt_compact = ttk.Button(mvt_auto_box, text="EXECUTE MEMORY COMPACTION [WITH COMPACTION]", command=self.trigger_mvt_compaction)
        btn_mvt_compact.pack(padx=20, pady=10, fill=tk.X)
        
        # Text Console Output log panel for MVT
        mvt_log_box = ttk.LabelFrame(mvt_left_control, text=" System Event Activity Log Readout ")
        mvt_log_box.pack(fill=tk.BOTH, expand=True, pady=10)
        self.txt_mvt_log = tk.Text(mvt_log_box, height=15, width=40, state="disabled", wrap=tk.WORD, bg="#f0f0f0")
        self.txt_mvt_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right Graphical Canvas Mapping for MVT
        self.mvt_canvas = tk.Canvas(mvt_right_display, bg="white", bd=2, relief=tk.SUNKEN)
        self.mvt_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        
# Part 3: Operational Controllers and Memory Routing Rules
    def execute_mft_action(self, mode, action: str = None):
        try:
            # 1. Query process context properties from router based on mode
            pid = self.entry_mft_pid.get().strip() if mode == "MANUAL" else None
            size_val = int(self.entry_mft_size.get().strip()) if (mode == "MANUAL" and action == "ALLOCATE") else None
            
            command, process = process_user_choice(mode, action, pid, size_val)
            algo = self.combo_mft_algo.get()
            
            # 2. Direct process size to selected fit strategy (First Fit, Best Fit, Best Available Fit)
            if command == "ALLOCATE":
                if algo == "First Fit":
                    msg = first_fit_mft(process, self.mft_manager)
                elif algo == "Best Fit":
                    msg = best_fit_mft(process, self.mft_manager)
                else:
                    msg = best_available_fit_mft(process, self.mft_manager)
            
                # 3. If allocation fails, drop the process into the MFT waiting queue
                if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                    self.mft_manager.waiting_queue.append(process)
                self.log_message(self.txt_mft_log, msg)
                
            # 4. If action is deallocate, free the partition block and retry waiting queue list
            elif command == "DEALLOCATE":
                self.mft_manager.deallocate_process(process.process_id)
                self.log_message(self.txt_mft_log, f"Deallocated {process.process_id} from fixed configuration memory map.")
                
                # Scan waiting list to see if freshly cleared spaces can support waiting items
                for queued_proc in list(self.mft_manager.waiting_queue):
                    if algo == "First Fit":
                        res = first_fit_mft(queued_proc, self.mft_manager)
                    elif algo == "Best Fit":
                        res = best_fit_mft(queued_proc, self.mft_manager)
                    else:
                        res = best_available_fit_mft(queued_proc, self.mft_manager)
                        
                    if "Allocated" in res:
                        self.mft_manager.waiting_queue.remove(queued_proc)
                        self.log_message(self.txt_mft_log, f"[Queue Release] {res}")
            
            # 5. Refresh MFT canvas
            self.update_mft_display_map()
        
        except Exception as e:
            messagebox.showerror("MFT Operational Error", str(e))
         
            
    def execute_mvt_action(self, mode: str, action: str = None):
        try:
            # 1. Query process context from router based on mode
            pid = self.entry_mvt_pid.get().strip() if mode == "MANUAL" else None
            size_val = int(self.entry_mvt_size.get().strip()) if (mode == "MANUAL" and action == "ALLOCATE") else None
            
            command, process = process_user_choice(mode, action, pid, size_val)
            algo = self.combo_mvt_algo.get()
            
            # 2. Route process payload to dynamic fit strategy (First Fit, Best Fit, Worst Fit)
            if command == "ALLOCATE":
                if algo == "First Fit":
                    msg = first_fit_mvt(process, self.mvt_manager)
                elif algo == "Best Fit":
                    msg = best_fit_mvt(process, self.mvt_manager)
                else:
                    msg = worst_fit_mvt(process, self.mvt_manager)
           
                # 3. If allocation fails, drop the process into the MVT waiting queue
                if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                    self.mvt_manager.waiting_queue.append(process)
                self.log_message(self.txt_mvt_log, msg)
           
            # 4. If action is deallocate, invoke manager without compaction and reorder queue
            elif command == "DEALLOCATE":
                self.mvt_manager.deallocate_process(process.process_id)
                self.log_message(self.txt_mvt_log, f"Deallocated {process.process_id} from dynamic block configurations.")
                
                # Check waiting targets against newly coalesced spaces
                self.reorder_mvt_queue()
           
            # 5. Refresh MVT canvas
            self.update_mvt_display_map()
            
        except Exception as e:
            messagebox.showerror("MVT Operational Error", str(e))


    def trigger_mvt_compaction(self):
        """
        # 1. Invoke memory compaction sequence on dynamic manager
        # 2. Cycle through MVT waiting queue to pack newly unified free holes
        # 3. Refresh MVT canvas
        """
        try:
            msg = self.mvt_manager.compact_memory()
            self.log_message(self.txt_mvt_log, msg)
            
            # Attempt to allocate elements now that scattered external fragments are merged
            self.reorder_mvt_queue()
            self.update_mvt_display_map()
        except Exception as e:
            messagebox.showerror("MVT Compaction Error", str(e))

    def reorder_mvt_queue(self):
        """ Helper sequence to automatically test waiting elements against dynamic holes. """
        algo = self.combo_mvt_algo.get()
        for queued_proc in list(self.mvt_manager.waiting_queue):
            if algo == "First Fit":
                res = first_fit_mvt(queued_proc, self.mvt_manager)
            elif algo == "Best Fit":
                res = best_fit_mvt(queued_proc, self.mvt_manager)
            else:
                res = worst_fit_mvt(queued_proc, self.mvt_manager)
                
            if "Allocated" in res:
                self.mvt_manager.waiting_queue.remove(queued_proc)
                self.log_message(self.txt_mvt_log, f"[Queue Release] {res}")

# Part 4: Physical Canvas Rendering Engines (Vertical Box Track)
    # Method update_mft_display_map():
        # 1. Clear MFT canvas tracking elements
        # 2. Render vertical text listings for the current Waiting Queue
        # 3. Iterate through partition arrays and stack rectangle blocks vertically (Y coordinates)
        # 4. Render process tags in occupied portions and red-hatched bars for internal fragmentation
        # 5. Update header labels to display total free space continuously

    # Method update_mvt_display_map():
        # 1. Clear MVT canvas tracking elements
        # 2. Render vertical text listings for the current Waiting Queue
        # 3. Iterate through dynamic block arrays and stack slots vertically using start_address parameters
        # 4. Render blue boxes for packed processes and green-hatched bars for empty holes
        # 5. Evaluate scattered spaces to calculate external fragmentation metrics
        # 6. Update header labels to display total free space continuously