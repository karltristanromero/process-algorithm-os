# Part 1: First Fit Allocation Logic
# Define a function named allocate_first_fit(process, memory_manager)
    # Loop through each partition in memory_manager.partitions:
        
        # Check if the partition is NOT occupied AND if the partition_size >= process.process_size:
            # 1. Assign the process to the partition: partition.occupied_process = process
            
            # 2. Update internal fragmentation: partition.internal_fragmentation = partition.partition_size - process.process_size
            
            # 3. Update process flags to reflect its new state:
                # process.is_allocated = True
                # process.partition_id = partition.partition_id
                
            # 4. Return a success message or tuple indicating where it was placed
            
    # If the loop finishes and no partition was found:
        # Return a message or raise a flag indicating the process could not be allocated 
        # (either because memory is full or the process is too large for any free block)