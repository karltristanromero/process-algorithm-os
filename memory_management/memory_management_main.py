# Part 1: System Imports and Boot Environment
import tkinter as tk
from tkinter import ttk, messagebox
import random
import os

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
        self.window_root.title("Memory Management Simulator - Retro Arcade Edition")
        
        # Explicit bounds matching your pixel art aspect ratio scale
        self.window_root.geometry("960x540")
        self.window_root.resizable(False, False)
        
        # Initialize core partition simulators
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        
        # Sync waiting queues tracking pools
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        # Compile interface overlay
        self.build_gui_layout()
        
        # Execute initial calculations draw
        self.refresh_display_matrix()


    def build_gui_layout(self):
        # Resolve absolute directory to prevent execution file path crashes
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path_1 = os.path.join(script_dir, "bg1.png")
        bg_path_2 = os.path.join(script_dir, "image_7a5c02.png")

        # Load file reference with dynamic failback
        try:
            self.bg_image = tk.PhotoImage(file=bg_path_1)
        except Exception:
            try:
                self.bg_image = tk.PhotoImage(file=bg_path_2)
            except Exception:
                messagebox.showerror("Asset Error", f"Missing background asset images inside directory:\n{script_dir}")
                self.window_root.destroy()
                return

        # Single canvas to overlay elements cleanly without frames breaking backgrounds
        self.canvas = tk.Canvas(self.window_root, width=960, height=540, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Dropdown Combobox retro theme overrides
        combobox_style = ttk.Style()
        combobox_style.theme_use('default')
        combobox_style.configure("TCombobox", fieldbackground="#F5E3B5", background="#CBB279", arrowcolor="#3D1E6D")

        # ==========================================
        # 1. LIVE VALUE TEXT LABELS (OVER CARDS)
        # ==========================================
        self.lbl_total_space = tk.Label(self.window_root, text="64K", font=("Courier", 16, "bold"), fg="#2E7D32", bg="#F1D199")
        self.canvas.create_window(780, 125, window=self.lbl_total_space)

        self.lbl_external_frag = tk.Label(self.window_root, text="0K", font=("Courier", 16, "bold"), fg="#E65100", bg="#F1D199")
        self.canvas.create_window(780, 265, window=self.lbl_external_frag)

        self.lbl_internal_frag = tk.Label(self.window_root, text="0K", font=("Courier", 16, "bold"), fg="#C62828", bg="#F1D199")
        self.canvas.create_window(780, 415, window=self.lbl_internal_frag)

        # ==========================================
        # 2. ENTRY TEXT INPUT FIELDS
        # ==========================================
        self.entry_pid = tk.Entry(self.window_root, width=6, font=("Courier", 11, "bold"), bd=1, relief=tk.SOLID)
        self.canvas.create_window(780, 545, window=self.entry_pid, anchor=tk.W)

        self.entry_size = tk.Entry(self.window_root, width=6, font=("Courier", 11, "bold"), bd=1, relief=tk.SOLID)
        self.canvas.create_window(780, 590, window=self.entry_size, anchor=tk.W)

        # ==========================================
        # 3. ACTION CONTROLS & BOTTOM DROPDOWNS
        # ==========================================
        # EXECUTE ALLOCATION OVER THE 1ST BRICK
        btn_alloc = tk.Button(self.window_root, text="EXEC ALLOC", font=("Arial", 9, "bold"), bg="#F5E3B5", fg="#3D1E6D", activebackground="#CBB279", bd=0, command=self.handle_allocation_trigger)
        self.canvas.create_window(115, 505, window=btn_alloc, width=130, height=25)

        # MODE SELECTION DROPDOWN OVER 2ND BRICK
        self.combo_mode = ttk.Combobox(self.window_root, values=["MANUAL", "RANDOM"], state="readonly", font=("Arial", 9, "bold"), style="TCombobox")
        self.combo_mode.set("MANUAL")
        self.canvas.create_window(285, 505, window=self.combo_mode, width=130)
        self.combo_mode.bind("<<ComboboxSelected>>", self.toggle_input_fields_access)

        # ALGORITHM COMPILATION DROPDOWN OVER 3RD BRICK
        self.combo_algo = ttk.Combobox(self.window_root, values=["MFT: First Fit", "MFT: Best Fit", "MFT: Best Available", "MVT: First Fit", "MVT: Best Fit", "MVT: Worst Fit"], state="readonly", font=("Arial", 8, "bold"), style="TCombobox")
        self.combo_algo.set("MFT: First Fit")
        self.canvas.create_window(455, 505, window=self.combo_algo, width=130)
        self.combo_algo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display_matrix())

        # EXECUTE DEALLOCATION OVER 4TH BRICK
        btn_dealloc = tk.Button(self.window_root, text="EXEC DEALLOC", font=("Arial", 9, "bold"), bg="#F5E3B5", fg="#3D1E6D", activebackground="#CBB279", bd=0, command=self.handle_deallocation_trigger)
        self.canvas.create_window(625, 505, window=btn_dealloc, width=130, height=25)

        # FLOATING MEMORY COMPACTION BUTTON
        self.btn_compaction = tk.Button(self.window_root, text="COMPACT MEMORY", font=("Arial", 8, "bold"), bg="#FF9800", fg="white", activebackground="#F57C00", bd=1, command=self.trigger_mvt_compaction)
        self.compaction_window_id = self.canvas.create_window(780, 470, window=self.btn_compaction, state="hidden")


    def toggle_input_fields_access(self, event=None):
        """ Prevents field spamming when randomized workload triggers are selected. """
        if self.combo_mode.get() == "RANDOM":
            self.entry_pid.configure(state="disabled")
            self.entry_size.configure(state="disabled")
        else:
            self.entry_pid.configure(state="normal")
            self.entry_size.configure(state="normal")


    def handle_allocation_trigger(self):
        try:
            mode = self.combo_mode.get()
            algo = self.combo_algo.get()
            
            pid = self.entry_pid.get().strip() if mode == "MANUAL" else None
            size_val = int(self.entry_size.get().strip()) if mode == "MANUAL" else None
            
            command, process = process_user_choice(mode, "ALLOCATE", pid, size_val)
            
            if "MFT" in algo:
                if "First Fit" in algo:
                    msg = first_fit_mft(process, self.mft_manager)
                elif "Best Fit" in algo:
                    msg = best_fit_mft(process, self.mft_manager)
                else:
                    msg = best_available_fit_mft(process, self.mft_manager)
                    
                if "Failed" in msg and process not in self.mft_manager.waiting_queue:
                    self.mft_manager.waiting_queue.append(process)
            else:
                if "First Fit" in algo:
                    msg = first_fit_mvt(process, self.mvt_manager)
                elif "Best Fit" in algo:
                    msg = best_fit_mvt(process, self.mvt_manager)
                else:
                    msg = worst_fit_mvt(process, self.mvt_manager)
                    
                if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                    self.mvt_manager.waiting_queue.append(process)
                
            self.refresh_display_matrix()
        except Exception as e:
            messagebox.showerror("Allocation Error", str(e))


    def handle_deallocation_trigger(self):
        try:
            mode = self.combo_mode.get()
            algo = self.combo_algo.get()
            pid = self.entry_pid.get().strip() if mode == "MANUAL" else None
            
            command, process = process_user_choice(mode, "DEALLOCATE", pid, None)
            
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
                
            self.refresh_display_matrix()
        except Exception as e:
            messagebox.showerror("Deallocation Error", str(e))


    def trigger_mvt_compaction(self):
        try:
            msg = self.mvt_manager.compact_memory()
            self.reorder_mvt_queue()
            self.refresh_display_matrix()
            messagebox.showinfo("Compaction Complete", msg)
        except Exception as e:
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
        # Flush dynamic block visuals tagged as 'mem_element'
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
        
        # Redraw the Waiting Queue text readout list inside the left container canvas empty zones
        self.canvas.create_text(320, 50, text="Waiting Queue:", font=("Courier", 11, "bold"), fill="#3D1E6D", anchor=tk.W, tags="mem_element")
        if not self.mft_manager.waiting_queue:
            self.canvas.create_text(320, 75, text="[ Empty ]", font=("Courier", 10, "italic"), fill="grey", anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mft_manager.waiting_queue[:12]):
                self.canvas.create_text(320, 75 + (idx * 18), text=f"• {proc.process_id} ({proc.process_size}K)", font=("Courier", 9, "bold"), fill="#C62828", anchor=tk.W, tags="mem_element")

        # Vertical axis tracking setup
        start_y = 50
        x1, x2 = 160, 280   
        canvas_scale = 6.2  # Coordinates perfectly match 64K boundaries inside the 400px vertical whitespace lane
        
        for partition in self.mft_manager.partitions:
            height = partition.partition_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 10, start_y, text=f"{int(partition.partition_size)}K", font=("Courier", 8, "bold"), anchor=tk.E, tags="mem_element")
            
            if partition.occupied_process:
                proc_height = partition.occupied_process.process_size * canvas_scale
                
                # Render allocated active block
                self.canvas.create_rectangle(x1, y1, x2, y1 + proc_height, fill="#007ACC", outline="#005A9C", width=1, tags="mem_element")
                self.canvas.create_text(x1 + 60, y1 + (proc_height / 2), text=partition.occupied_process.process_id, font=("Arial", 8, "bold"), fill="white", tags="mem_element")
                
                # Render wasted internal fragmentation remainder
                if partition.internal_fragmentation > 0:
                    self.canvas.create_rectangle(x1, y1 + proc_height, x2, y2, fill="#FF5252", outline="#D32F2F", width=1, tags="mem_element")
                    self.canvas.create_text(x1 + 60, y1 + proc_height + ((height - proc_height) / 2), text="FRAG", font=("Arial", 7, "bold"), fill="white", tags="mem_element")
                    total_internal_frag += partition.internal_fragmentation
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#E8F5E9", outline="#81C784", width=1, tags="mem_element")
                self.canvas.create_text(x1 + 60, y1 + (height / 2), text="FREE", font=("Arial", 8, "bold"), fill="#2E7D32", tags="mem_element")
                total_free_space += partition.partition_size
                
            start_y += height
            
        self.canvas.create_text(x1 - 10, start_y, text="64K", font=("Courier", 8, "bold"), anchor=tk.E, tags="mem_element")

        # Config card value readouts
        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text="0K")
        self.lbl_internal_frag.config(text=f"{total_internal_frag}K")


    def update_mvt_display_map(self):
        total_free_space = 0
        total_external_frag = 0
        free_hole_segments_count = 0
        
        self.canvas.create_text(320, 50, text="Waiting Queue:", font=("Courier", 11, "bold"), fill="#3D1E6D", anchor=tk.W, tags="mem_element")
        if not self.mvt_manager.waiting_queue:
            self.canvas.create_text(320, 75, text="[ Empty ]", font=("Courier", 10, "italic"), fill="grey", anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mvt_manager.waiting_queue[:12]):
                self.canvas.create_text(320, 75 + (idx * 18), text=f"• {proc.process_id} ({proc.process_size}K)", font=("Courier", 9, "bold"), fill="#C62828", anchor=tk.W, tags="mem_element")

        start_y = 50
        x1, x2 = 160, 280
        canvas_scale = 6.2
        
        for block in self.mvt_manager.blocks:
            height = block.block_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            self.canvas.create_text(x1 - 10, y1, text=f"{block.start_address}K", font=("Courier", 8, "bold"), anchor=tk.E, tags="mem_element")
            
            if block.occupied_process:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#007ACC", outline="#005A9C", width=1, tags="mem_element")
                self.canvas.create_text(x1 + 60, y1 + (height / 2), text=f"{block.occupied_process.process_id}\n({block.block_size}K)", font=("Arial", 8, "bold"), fill="white", tags="mem_element")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#E1F5FE", outline="#4FC3F7", width=1, tags="mem_element")
                self.canvas.create_text(x1 + 60, y1 + (height / 2), text=f"HOLE\n{block.block_size}K", font=("Arial", 8, "bold"), fill="#0288D1", tags="mem_element")
                total_free_space += block.block_size
                free_hole_segments_count += 1
                
            start_y += height
            
        self.canvas.create_text(x1 - 10, start_y, text="64K", font=("Courier", 8, "bold"), anchor=tk.E, tags="mem_element")

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