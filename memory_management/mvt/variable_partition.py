import random

# Part 1: Define what a Dynamic Memory Block is
class MemoryBlock:
    def __init__(self, start_address: int, block_size: int):
        self.start_address = start_address                # Physical starting address boundary
        self.block_size = block_size                      # Sizing constraint of this memory segment
        self.occupied_process = None                      # Holds a Process object if allocated, None if it is a free hole

# Part 2: Define the Variable Memory Manager Track
class VariableMemoryManager:
    def __init__(self, total_memory_size: int = 64):
        self.total_memory_size = total_memory_size        # Initialize memory track with one 64K free hole
        self.blocks = [MemoryBlock(start_address=0, block_size=total_memory_size)]

    # Method 1: deallocate_process (WITHOUT COMPACTION)
    def deallocate_process(self, process_id: str):
        """
        Locates a running process, frees it, and merges adjacent empty memory blocks (coalescing).
        """
        process_id = process_id.strip().upper()
        found_index = -1

        # 1. Find the process block, clear occupied_process to None
        for i, block in enumerate(self.blocks):
            if block.occupied_process and block.occupied_process.process_id == process_id:
                process = block.occupied_process
                process.is_allocated = False
                process.partition_id = None
                block.occupied_process = None              # Clear occupied_process to None (makes it a hole)
                found_index = i
                break

        if found_index == -1:
            raise ValueError(f"Process {process_id} was not found running in any MVT memory block.")

        # 2. Run the coalescing loop to combine side-by-side free blocks
        temporary_blocks = []
        for current_block in self.blocks:
            if not temporary_blocks:
                temporary_blocks.append(current_block)
            else:
                last_inserted_block = temporary_blocks[-1]
                # Combine side-by-side free blocks
                if last_inserted_block.occupied_process is None and current_block.occupied_process is None:
                    last_inserted_block.block_size += current_block.block_size
                else:
                    temporary_blocks.append(current_block)

        # Correct physical start addresses after merging blocks
        current_address = 0
        for block in temporary_blocks:
            block.start_address = current_address
            current_address += block.block_size

        self.blocks = temporary_blocks
        return True

    # Method 2: compact_memory (WITH COMPACTION)
    def compact_memory(self):
        """
        Shuffles all active processes to the top of memory and combines all free holes into one large block.
        """
        # 1. Collect all running processes from the current blocks list
        running_processes = [block.occupied_process for block in self.blocks if block.occupied_process is not None]
        
        # 2. Calculate the total memory currently used by these processes
        # (This is handled implicitly as we iterate and advance the current_address pointer)
        
        # 3. Clear the entire blocks list array
        self.blocks = []
        current_address = 0

        # 4. Pack all running processes tightly starting from address 0
        for process in running_processes:
            new_block = MemoryBlock(start_address=current_address, block_size=process.process_size)
            new_block.occupied_process = process
            
            # Map tracking data coordinates for visual readout maps
            process.partition_id = f"Dynamic Block ({current_address}K-{current_address + process.process_size}K)"
            
            self.blocks.append(new_block)
            current_address += process.process_size

        # 5. Take the leftover remaining space and create ONE big free block at the end
        remaining_free_space = self.total_memory_size - current_address
        if remaining_free_space > 0:
            free_hole_block = MemoryBlock(start_address=current_address, block_size=remaining_free_space)
            self.blocks.append(free_hole_block)
            
        return f"Compaction Complete! Consolidated {remaining_free_space}K into a single contiguous free block."