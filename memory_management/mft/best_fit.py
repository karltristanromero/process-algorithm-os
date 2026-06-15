# Part 1: Best Fit Allocation Logic
def best_fit_mft(process, memory_manager):
    best_partition = None
    min_fragmentation = float('inf')  # Set to infinity so the first valid block will easily beat it
    
    # Loop through each partition in memory_manager.partitions
    for partition in memory_manager.partitions:
        
        # Check if the partition is NOT occupied AND if the partition_size >= process.process_size
        if partition.occupied_process is None and partition.partition_size >= process.process_size:
            current_fragmentation = partition.partition_size - process.process_size
            
            # Look for the absolute tightest fit (smallest leftover internal fragmentation)
            if current_fragmentation < min_fragmentation:
                min_fragmentation = current_fragmentation
                best_partition = partition

    # If a best fitting partition block was found after scanning the entire matrix
    if best_partition is not None:
        # 1. Assign the process to the partition
        best_partition.occupied_process = process
        
        # 2. Update internal fragmentation matching our chosen block
        best_partition.internal_fragmentation = min_fragmentation
        
        # 3. Update process flags to reflect its new state
        process.is_allocated = True
        process.partition_id = best_partition.partition_id
        
        # 4. Return a success message indicating where it was placed
        return f"Allocated {process.process_id} ({process.process_size}K) to {best_partition.partition_id} [Best Fit]. Internal Fragmentation: {best_partition.internal_fragmentation}K."

    # If the loop finishes and no partition was found, determine the configuration issue
    max_system_partition = max(partition.partition_size for partition in memory_manager.partitions)
    
    if process.process_size > max_system_partition:
        return f"Allocation Failed: {process.process_id} ({process.process_size}K) is larger than the maximum system partition ({max_system_partition}K)."
    else:
        return f"Allocation Failed: No available partition is large enough right now for {process.process_id} ({process.process_size}K). Placed in waiting queue."