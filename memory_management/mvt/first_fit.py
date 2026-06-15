# Part 1: MVT First Fit Allocation Logic
# Define a function named first_fit_mvt(process, memory_manager)
    # Loop through each block in memory_manager.blocks using its index:
        
        # Check if the block is a free hole (block.occupied_process is None) 
        # AND if block.block_size >= process.process_size:
            
            # Save the original size of this free hole
            # Shrink this specific block to match the exact size of the incoming process
            # Assign the process to this block: block.occupied_process = process
            
            # Calculate the leftover space remaining from the original hole size
            # If leftover space > 0:
                # 1. Create a brand-new MemoryBlock (a smaller free hole)
                # 2. Set its start_address to (block.start_address + process.process_size)
                # 3. Set its size to the leftover space
                # 4. Insert this new free hole block right after the newly allocated block in the list
                
            # Update the process object's tracking flags:
                # process.is_allocated = True
                # process.partition_id = f"Dynamic Block ({block.start_address}K-{block.start_address + process.process_size}K)"
                
            # Return a clean success string with the starting address details
            
    # If the loop completely runs out of elements without finding a block:
        # Check if the total sum of ALL free holes combined in the system is >= process.process_size
        # If yes -> Return an "Allocation Failed: External Fragmentation detected. Compaction required." message.
        # If no  -> Return an "Allocation Failed: Insufficient total memory." message.