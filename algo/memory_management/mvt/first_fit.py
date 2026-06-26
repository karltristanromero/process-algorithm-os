from mvt.variable_partition import MemoryBlock

# Part 1: MVT First Fit Allocation Logic
def first_fit_mvt(process, memory_manager):
    """
    Scans the dynamic blocks list and places the process into the very first 
    free hole that is large enough, carving out a new partition.
    """
    # Loop through each block in memory_manager.blocks using its index
    for index, block in enumerate(memory_manager.blocks):
        
        # Check if the block is an unallocated free hole and can fit the process size
        if block.occupied_process is None and block.block_size >= process.process_size:
            
            # Save the original size of this free hole
            original_hole_size = block.block_size
            
            # Shrink this specific block to match the exact size of the incoming process
            block.block_size = process.process_size
            # Assign the process to this block
            block.occupied_process = process
            
            # Calculate the leftover space remaining from the original hole size
            leftover_space = original_hole_size - process.process_size
            
            # If leftover space exists, insert a new smaller free hole right after this block
            if leftover_space > 0:
                new_free_address = block.start_address + process.process_size
                new_free_hole = MemoryBlock(start_address=new_free_address, block_size=leftover_space)
                memory_manager.blocks.insert(index + 1, new_free_hole)
                
            # Update the process object's tracking flags
            process.is_allocated = True
            process.partition_id = f"Dynamic Block ({block.start_address}K-{block.start_address + process.process_size}K)"
            
            return f"Allocated {process.process_id} ({process.process_size}K) starting at address {block.start_address}K."
            
    # If the loop finishes and no single hole was large enough:
    # Check if the total combined free space in the system could actually fit the process
    total_free_memory = sum(b.block_size for b in memory_manager.blocks if b.occupied_process is None)
    
    if total_free_memory >= process.process_size:
        return f"Allocation Failed: External Fragmentation detected. Total free space is {total_free_memory}K, but it is split. Compaction required."
    else:
        return f"Allocation Failed: Insufficient total memory. System only has {total_free_memory}K free."