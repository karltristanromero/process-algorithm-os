# Part 1: MVT Best Fit Allocation Logic
# Define a function named best_fit_mvt(process, memory_manager)
    # Track the index of the best matching hole found (initialize as -1)
    # Track the minimum leftover space seen so far (initialize to infinity)
    
    # Loop through each block in memory_manager.blocks using its index:
        # Check if the block is a free hole AND block.block_size >= process.process_size:
            # Calculate the potential leftover space (block.block_size - process.process_size)
            # If this leftover space is smaller than our minimum tracker:
                # Update our minimum tracker with this lower value
                # Update our best index tracker with this current index
                
    # After checking all blocks, if a best index tracker was found (index != -1):
        # 1. Grab that best block from memory_manager.blocks[best_index]
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