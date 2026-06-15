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
