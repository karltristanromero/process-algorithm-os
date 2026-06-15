# Part 1: Define what a Dynamic Memory Block is
# Create a class named MemoryBlock
    # Set up a starting address (e.g., 0, 16, 32 tracking physical bounds)
    # Set up the block size (in KB)
    # Set up a flag or variable to hold an allocated Process object (None if it's an empty hole)


# Part 2: Define the Variable Memory Manager Track
# Create a class named VariableMemoryManager
    # Initialize total system RAM to 64K
    # Set up an array list named 'blocks' containing exactly ONE initial free MemoryBlock
    # (Starts at address 0, size 64, occupied_process = None)

    # Method to Deallocate/Free an allocated process block
        # Loop through the blocks array to find the process matching process_id
        # If found:
            # Clear out the block's occupied_process reference to None
            # Core MVT cleanup: Merge adjacent empty blocks (coalescing)
            # (If the block before or after it is also a free hole, combine them into one big block!)