# Part 1: Define what a Dynamic Memory Block is (Remains the same)
# Create a class named MemoryBlock
    # Set up starting address, size, and occupied_process tracker

# Part 2: Define the Variable Memory Manager Track
# Create a class named VariableMemoryManager
    # __init__: Initialize memory track with one 64K free hole

    # Method 1: deallocate_process (WITHOUT COMPACTION)
        # 1. Find the process block, clear occupied_process to None
        # 2. Run the coalescing loop to combine side-by-side free blocks

    # Method 2: compact_memory (WITH COMPACTION)
        # 1. Collect all running processes from the current blocks list
        # 2. Calculate the total memory currently used by these processes
        # 3. Clear the entire blocks list array
        # 4. Pack all running processes tightly starting from address 0
        # 5. Take the leftover remaining space and create ONE big free block at the end