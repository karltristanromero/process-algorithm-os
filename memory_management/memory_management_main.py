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
        self.window_root.title("Memory Management Simulator - Retro Edition")
        
        # Set exact dimensions to match your background design scaling comfortably
        self.window_root.geometry("960x540")
        self.window_root.resizable(False, False)
        
        # Initialize core memory engines
        self.mft_manager = FixedMemoryManager(total_memory_size=64)
        self.mvt_manager = VariableMemoryManager(total_memory_size=64)
        
        # Track waiting processes inside manager tracks
        self.mft_manager.waiting_queue = []
        self.mvt_manager.waiting_queue = []
        
        # Build the layout canvas board
        self.build_gui_layout()
        
        # Initial draw of engine calculations onto the canvas view maps
        self.refresh_display_matrix()


    def build_gui_layout(self):
        # Load your pixel art background asset file
        try:
            self.bg_image = tk.PhotoImage(file="bg1.png")
        except Exception:
            # Fallback if there's a naming mismatch during testing
            self.bg_image = tk.PhotoImage(file="image_7a5c02.png")

        # Create master canvas layout map
        self.canvas = tk.Canvas(self.window_root, width=960, height=540, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Place background asset image at base layer position
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        # Config styles for TCombobox dropdown layers to fit the retro look
        combobox_style = ttk.Style()
        combobox_style.theme_use('default')
        combobox_style.configure("TCombobox", fieldbackground="#F5E3B5", background="#CBB279", arrowcolor="#3D1E6D")

        # ==========================================
        # 1. LIVE VALUE LABELS OVER CARD OBJECTS
        # ==========================================
        self.lbl_total_space = tk.Label(self.window_root, text="64K", font=("Courier", 16, "bold"), fg="#2E7D32", bg="#F1D199")
        self.canvas.create_window(780, 125, window=self.lbl_total_space)

        self.lbl_external_frag = tk.Label(self.window_root, text="0K", font=("Courier", 16, "bold"), fg="#E65100", bg="#F1D199")
        self.canvas.create_window(780, 265, window=self.lbl_external_frag)

        self.lbl_internal_frag = tk.Label(self.window_root, text="0K", font=("Courier", 16, "bold"), fg="#C62828", bg="#F1D199")
        self.canvas.create_window(780, 415, window=self.lbl_internal_frag)

        # ==========================================
        # 2. ENTRY INPUTS INSIDE PROCESS FORM CARD
        # ==========================================
        self.entry_pid = tk.Entry(self.window_root, width=6, font=("Courier", 11, "bold"), bd=1, relief=tk.SOLID, bg="#FFFFFF")
        self.canvas.create_window(780, 545, window=self.entry_pid, anchor=tk.W)

        self.entry_size = tk.Entry(self.window_root, width=6, font=("Courier", 11, "bold"), bd=1, relief=tk.SOLID, bg="#FFFFFF")
        self.canvas.create_window(780, 590, window=self.entry_size, anchor=tk.W)

        # ==========================================
        # 3. INTERACTIVE CONTROL WIDGETS AT BOTTOM
        # ==========================================
        # MENU BUTTON LINK
        btn_menu = tk.Button(self.window_root, text="EXEC ALLOC", font=("Arial", 9, "bold"), bg="#F5E3B5", fg="#3D1E6D", activebackground="#CBB279", bd=0, command=self.handle_allocation_trigger)
        self.canvas.create_window(115, 505, window=btn_menu, width=130, height=25)

        # CHOOSE MODE DROPDOWN
        self.combo_mode = ttk.Combobox(self.window_root, values=["MANUAL", "RANDOM"], state="readonly", width=12, font=("Arial", 9, "bold"), style="TCombobox")
        self.combo_mode.set("MANUAL")
        self.canvas.create_window(285, 505, window=self.combo_mode, width=130)
        self.combo_mode.bind("<<ComboboxSelected>>", self.toggle_input_fields_access)

        # CHOOSE STRATEGY ALGORITHM DROPDOWN
        self.combo_algo = ttk.Combobox(self.window_root, values=["MFT: First Fit", "MFT: Best Fit", "MFT: Best Available", "MVT: First Fit", "MVT: Best Fit", "MVT: Worst Fit"], state="readonly", width=16, font=("Arial", 8, "bold"), style="TCombobox")
        self.combo_algo.set("MFT: First Fit")
        self.canvas.create_window(455, 505, window=self.combo_algo, width=130)
        self.combo_algo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display_matrix())

        # DEALLOCATE / RESET BUTTON TRIGGER
        btn_reset = tk.Button(self.window_root, text="EXEC DEALLOC", font=("Arial", 9, "bold"), bg="#F5E3B5", fg="#3D1E6D", activebackground="#CBB279", bd=0, command=self.handle_deallocation_trigger)
        self.canvas.create_window(625, 505, window=btn_reset, width=130, height=25)

        # COMPACTION DYNAMIC FLOATING TRIGGER
        self.btn_compaction = tk.Button(self.window_root, text="COMPACT MEMORY", font=("Arial", 8, "bold"), bg="#FF9800", fg="white", activebackground="#F57C00", bd=1, command=self.trigger_mvt_compaction)
        # Hidden initially because MFT mode doesn't support compaction arrays
        self.compaction_window_id = self.canvas.create_window(780, 470, window=self.btn_compaction, state="hidden")


    def toggle_input_fields_access(self, event=None):
        """ Locks process entry logs out completely if running an automated randomized loop step. """
        mode = self.combo_mode.get()
        if mode == "RANDOM":
            self.entry_pid.configure(state="disabled")
            self.entry_size.configure(state="disabled")
        else:
            self.entry_pid.configure(state="normal")
            self.entry_size.configure(state="normal")


    def handle_allocation_trigger(self):
        """ Routes input properties to either MFT or MVT engine metrics depending on dropdown state selection. """
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
                print(f"[MFT Log]: {msg}")
            else:
                if "First Fit" in algo:
                    msg = first_fit_mvt(process, self.mvt_manager)
                elif "Best Fit" in algo:
                    msg = best_fit_mvt(process, self.mvt_manager)
                else:
                    msg = worst_fit_mvt(process, self.mvt_manager)
                    
                if "Failed" in msg and process not in self.mvt_manager.waiting_queue:
                    self.mvt_manager.waiting_queue.append(process)
                print(f"[MVT Log]: {msg}")
                
            self.refresh_display_matrix()
        except Exception as e:
            messagebox.showerror("Allocation Error", str(e))


    def handle_deallocation_trigger(self):
        """ Identifies active running processes, safely clears them, and cycles waiting entries. """
        try:
            mode = self.combo_mode.get()
            algo = self.combo_algo.get()
            pid = self.entry_pid.get().strip() if mode == "MANUAL" else None
            
            command, process = process_user_choice(mode, "DEALLOCATE", pid, None)
            
            if "MFT" in algo:
                self.mft_manager.deallocate_process(process.process_id)
                # Cycle MFT waiting queue tracks
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
            messagebox.showinfo("Compaction Sequence", msg)
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
        """ Evaluates selected engine algorithm type to draw corresponding column layers. """
        algo = self.combo_algo.get()
        
        # Clear out previous memory stick rectangles to redraw cleanly
        self.canvas.delete("mem_element")
        
        if "MFT" in algo:
            self.canvas.itemconfigure(self.compaction_window_id, state="hidden")
            self.update_mft_display_map()
        else:
            self.canvas.itemconfigure(self.compaction_window_id, state="normal")
            self.update_mvt_display_map()


    def update_mft_display_map(self):
        total_free_space = 0
        total_internal_frag = 0
        
        # Render Waiting Queue listings inside the left canvas frame area
        self.canvas.create_text(320, 50, text="Waiting Queue:", font=("Courier", 11, "bold"), fill="#3D1E6D", anchor=tk.W, tags="mem_element")
        if not self.mft_manager.waiting_queue:
            self.canvas.create_text(320, 75, text="[ Empty ]", font=("Courier", 10, "italic"), fill="grey", anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mft_manager.waiting_queue[:12]): # Constraint bounds limit to 12 items visually
                self.canvas.create_text(320, 75 + (idx * 18), text=f"• {proc.process_id} ({proc.process_size}K)", font=("Courier", 9, "bold"), fill="#C62828", anchor=tk.W, tags="mem_element")

        # Set vertical geometry positions inside blank lane bounds
        start_y = 50
        x1, x2 = 160, 280   # Sleek centered column dimension metrics
        canvas_scale = 6.2  # Dynamic vertical fit scalar to cleanly scale 64K to 400 pixels maximum height
        
        for partition in self.mft_manager.partitions:
            height = partition.partition_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            # Print boundaries beside the module blocks
            self.canvas.create_text(x1 - 10, start_y, text=f"{int(partition.partition_size)}K", font=("Courier", 8, "bold"), anchor=tk.E, tags="mem_element")
            
            if partition.occupied_process:
                proc_height = partition.occupied_process.process_size * canvas_scale
                
                # Render primary process block element
                self.canvas.create_rectangle(x1, y1, x2, y1 + proc_height, fill="#007ACC", outline="#005A9C", width=1, tags="mem_element")
                self.canvas.create_text(x1 + 60, y1 + (proc_height / 2), text=partition.occupied_process.process_id, font=("Arial", 8, "bold"), fill="white", tags="mem_element")
                
                # Render unallocated remainder as internal fragmentation hazard
                if partition.internal_fragmentation > 0:
                    self.canvas.create_rectangle(x1, y1 + proc_height, x2, y2, fill="#FF5252", outline="#D32F2F", width=1, tags="mem_element")
                    self.canvas.create_text(x1 + 60, y1 + proc_height + ((height - proc_height) / 2), text="FRAG", font=("Arial", 7, "bold"), fill="white", tags="mem_element")
                    total_internal_frag += partition.internal_fragmentation
            else:
                # Open system hole slot space
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#E8F5E9", outline="#81C784", width=1, tags="mem_element")
                self.canvas.create_text(x1 + 60, y1 + (height / 2), text="FREE", font=("Arial", 8, "bold"), fill="#2E7D32", tags="mem_element")
                total_free_space += partition.partition_size
                
            start_y += height
            
        self.canvas.create_text(x1 - 10, start_y, text="64K", font=("Courier", 8, "bold"), anchor=tk.E, tags="mem_element")

        # Push calculations to card dashboard views
        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text="0K") # Fixed partition models do not exhibit external fragmentation attributes
        self.lbl_internal_frag.config(text=f"{total_internal_frag}K")


    def update_mvt_display_map(self):
        total_free_space = 0
        total_external_frag = 0
        free_hole_segments_count = 0
        
        # Render Waiting Queue listings inside the left canvas frame area
        self.canvas.create_text(320, 50, text="Waiting Queue:", font=("Courier", 11, "bold"), fill="#3D1E6D", anchor=tk.W, tags="mem_element")
        if not self.mvt_manager.waiting_queue:
            self.canvas.create_text(320, 75, text="[ Empty ]", font=("Courier", 10, "italic"), fill="grey", anchor=tk.W, tags="mem_element")
        else:
            for idx, proc in enumerate(self.mvt_manager.waiting_queue[:12]):
                self.canvas.create_text(320, 75 + (idx * 18), text=f"• {proc.process_id} ({proc.process_size}K)", font=("Courier", 9, "bold"), fill="#C62828", anchor=tk.W, tags="mem_element")

        # Set vertical layout coordinate tracks
        start_y = 50
        x1, x2 = 160, 280
        canvas_scale = 6.2
        
        for block in self.mvt_manager.blocks:
            height = block.block_size * canvas_scale
            y1, y2 = start_y, start_y + height
            
            # Print physical boundary memory tracking addresses
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

        # Evaluate external fragments metrics
        active_allocations = any(b.occupied_process is not None for b in self.mvt_manager.blocks)
        if active_allocations and free_hole_segments_count > 1:
            total_external_frag = total_free_space
        elif active_allocations and free_hole_segments_count == 1:
            if self.mvt_manager.blocks[-1].occupied_process is not None:
                total_external_frag = total_free_space

        # Push structural data summaries to card metrics
        self.lbl_total_space.config(text=f"{total_free_space}K")
        self.lbl_external_frag.config(text=f"{total_external_frag}K")
        self.lbl_internal_frag.config(text="0K") # Variable dynamic partitions feature zero internal fragmentation waste


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagementApp(root)
    root.mainloop()