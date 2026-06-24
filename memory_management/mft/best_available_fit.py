# Part 1: Best Available Fit Allocation Logic
def best_available_fit_mft(process, memory_manager):
    best_available_partition = None
    min_difference = float('inf')  # Set to infinity to easily capture the first valid free block
    
    # Loop through each partition in memory_manager.partitions
    for partition in memory_manager.partitions:
        
        # Check if the partition is NOT occupied AND if the partition_size >= process.process_size
        if partition.occupied_process is None and partition.partition_size >= process.process_size:
            current_difference = partition.partition_size - process.process_size
            
            # Identify the closest matching size among available slots
            if current_difference < min_difference:
                min_difference = current_difference
                best_available_partition = partition

    # If a suitable unallocated partition block was found
    if best_available_partition is not None:
        # 1. Assign the process to the partition
        best_available_partition.occupied_process = process
        
        # 2. Update internal fragmentation based on this assignment
        best_available_partition.internal_fragmentation = min_difference
        
        # 3. Update process flags to reflect its new state
        process.is_allocated = True
        process.partition_id = best_available_partition.partition_id
        
        # 4. Return a success message details for your visual readout panels
        return f"Allocated {process.process_id} ({process.process_size}K) to {best_available_partition.partition_id} [Best Available Fit]. Internal Fragmentation: {best_available_partition.internal_fragmentation}K."

    # If the loop finishes and no partition was found, handle system limits
    max_system_partition = max(partition.partition_size for partition in memory_manager.partitions)
    
    if process.process_size > max_system_partition:
        return f"Allocation Failed: {process.process_id} ({process.process_size}K) is larger than the maximum system partition ({max_system_partition}K)."
    else:
        return f"Allocation Failed: No available partition is large enough right now for {process.process_id} ({process.process_size}K). Placed in waiting queue."