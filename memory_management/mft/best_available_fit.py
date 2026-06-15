# Part 1: Best Available Fit Allocation Logic
# Define a function named best_available_fit_mft(process, memory_manager)
    # Track the best available partition found (initialize as None)
    # Track the tightest size difference found (initialize to infinity)
    
    # Loop through each partition in the memory manager:
        # Check if the partition is currently empty (partition.occupied_process is None)
            # Check if the partition size can hold the process size
                # Calculate the exact size difference
                # If this difference is smaller than our current tightest match tracker:
                    # Update our trackers with this partition block
                    
    # If we found an available matching block after checking the list:
        # 1. Assign the process to that best available block
        # 2. Compute internal fragmentation
        # 3. Toggle process allocation state flags
        # 4. Return success metrics
        
    # If no partition was found:
        # Check if the process exceeds the max system capability or if memory is just fully packed