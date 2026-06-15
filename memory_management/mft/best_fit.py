# Part 1: Best Fit Allocation Logic
# Define a function named best_fit_mft(process, memory_manager)
    # Track the best partition block found so far (initialize as None)
    # Track the minimum fragmentation value seen so far (initialize to infinity or a very high number)
    
    # Loop through each partition in the memory manager:
        # Check if the partition is NOT occupied AND can fit the process size
            # Calculate the leftover space (internal fragmentation)
            # If this leftover space is smaller than our minimum tracker:
                # Update our minimum tracker with this lower value
                # Update our best partition tracker with this current block
                
    # After checking all blocks, if a best partition tracker was found:
        # 1. Assign the process to that best block
        # 2. Update the block's internal fragmentation matching your tracking calculations
        # 3. Update the process flags (is_allocated = True, partition_id)
        # 4. Return a clean success string
        
    # If no partition was found at all:
        # Evaluate if it's too big for the system entirely or just waiting for a block to clear