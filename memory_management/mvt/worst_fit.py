# Part 1: MVT Worst Fit Allocation Logic
# Define a function named worst_fit_mvt(process, memory_manager)
    # Track the index of the worst matching hole found (initialize as -1)
    # Track the maximum leftover space seen so far (initialize to -1)
    
    # Loop through each block in memory_manager.blocks using its index:
        # Check if the block is an unallocated free hole AND block.block_size >= process.process_size:
            # Calculate the potential leftover space (block.block_size - process.process_size)
            # If this leftover space is larger than our maximum tracker:
                # Update our maximum tracker with this higher value
                # Update our worst index tracker with this current index
                
    # After checking all blocks, if a valid index was found (index != -1):
        # 1. Grab that worst block from memory_manager.blocks[worst_index]
        # 2. Save its original hole size
        # 3. Shrink its block_size to match the process size exactly
        # 4. Assign the process to it: block.occupied_process = process
        
        # 5. If leftover space > 0:
            # Create a new MemoryBlock for the leftover free hole
            # Set its start_address to (block.start_address + process.process_size)
            # Insert it right after the newly allocated block in the list array
            
        # 6. Toggle process tracking flags (is_allocated = True, partition_id)
        # 7. Return a success details string
        
    # If no single hole was large enough:
        # Check total free space to determine if External Fragmentation requires Compaction