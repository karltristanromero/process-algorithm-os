from mvt.variable_partition import MemoryBlock

# Part 1: MVT Best Fit Allocation Logic
def best_fit_mvt(process, memory_manager):
    """
    Scans the entire list of dynamic blocks to find and carve the 
    absolute smallest free hole that can fit the incoming process.
    """
    best_index = -1
    min_leftover = float('inf')  # Set to infinity to easily capture the first valid fit
    
    # Loop through each block in memory_manager.blocks using its index
    for index, block in enumerate(memory_manager.blocks):
        
        # Check if the block is an unallocated free hole and can fit the process size
        if block.occupied_process is None and block.block_size >= process.process_size:
            current_leftover = block.block_size - process.process_size
            
            # Find the absolute tightest fit (smallest leftover hole)
            if current_leftover < min_leftover:
                min_leftover = current_leftover
                best_index = index

    # If a best-fitting free hole index was discovered after the system-wide scan
    if best_index != -1:
        block = memory_manager.blocks[best_index]
        original_hole_size = block.block_size
        
        # Shrink the block to fit the process size exactly
        block.block_size = process.process_size
        block.occupied_process = process
        
        # If leftover space exists from our optimized choice, insert the new smaller free hole
        if min_leftover > 0:
            new_free_address = block.start_address + process.process_size
            new_free_hole = MemoryBlock(start_address=new_free_address, block_size=min_leftover)
            memory_manager.blocks.insert(best_index + 1, new_free_hole)
            
        # Update the process object's tracking flags
        process.is_allocated = True
        process.partition_id = f"Dynamic Block ({block.start_address}K-{block.start_address + process.process_size}K)"
        
        return f"Allocated {process.process_id} ({process.process_size}K) to optimal address {block.start_address}K [Best Fit]."

    # If the loop finishes and no single hole was large enough, check for fragmentation issues
    total_free_memory = sum(b.block_size for b in memory_manager.blocks if b.occupied_process is None)
    
    if total_free_memory >= process.process_size:
        return f"Allocation Failed: External Fragmentation detected. Total free space is {total_free_memory}K, but it is split. Compaction required."
    else:
        return f"Allocation Failed: Insufficient total memory. System only has {total_free_memory}K free."