# Part 1: Define what a Fixed Partition Block is
# Create a class named PartitionBlock
    # Set up a partition id
    # Set up the total physical capacity of this block
    # Set up a variable to hold a Process object if it is occupied
    # Set up a tracking variable for internal fragmentation
    # Set up a tracking variable for External fragmentation


# Part 2: Define the Fixed Memory Manager Track
# Create a class named FixedMemoryManager
    # Initialize the total system RAM 64K
    # Divide that RAM into static partitions
    # Create an array list containing these PartitionBlock structures

    # Method to Deallocate/Free a partition block
        # Look up the target block ID or searching for the matching process ID
        # If found:
            # Change the process's internal is_allocated flag back to False
            # Clear out the block's current process field to None
            # Reset the internal fragmentation tracking space back to 0