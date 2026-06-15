# Part 1: First Fit Allocation Logic
def first_fit_mft(process, memory_manager):
    # Loop through each partition in memory_manager.partitions:
    for partition in memory_manager.partitions:
        
        # Check if the partition is NOT occupied AND if the partition_size >= process.process_size:
        if partition.occupied_process is None and partition.partition_size >= process.process_size:
            
            # 1. Assign the process to the partition: partition.occupied_process = process
            partition.occupied_process = process
            
            # 2. Update internal fragmentation: partition.internal_fragmentation = partition.partition_size - process.process_size
            partition.internal_fragmentation = partition.partition_size - process.process_size
            
            # 3. Update process flags to reflect its new state:
            process.is_allocated = True
            process.partition_id = partition.partition_id
                
            # 4. Return a success message or tuple indicating where it was placed
            return f"Allocated {process.process_id} ({process.process_size}K) to {partition.partition_id}. Internal Fragmentation: {partition.internal_fragmentation}K."
        
    # If the loop finishes and no partition was found:
    Check if the process is simply too big for ANY partition in the entire system configuration
    max_system_partition = max(partition.partition_size for partition in memory_manager.partitions)
    
    if process.process_size > max_system_partition:
        return f"Allocation Failed: {process.process_id} ({process.process_size}K) is larger than the maximum system partition ({max_system_partition}K)."
    else:
        return f"Allocation Failed: No available partition is large enough right now for {process.process_id} ({process.process_size}K). Placed in waiting queue."