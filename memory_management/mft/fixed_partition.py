# Part 1: Define what a Fixed Partition Block is
class PartitionBlock:
    def __init__(self, partition_id: int, partition_size: int):
        self.partition_id = f"Block {partition_id}"     # Set up a partition id
        self.partition_size = partition_size            # Set up the total physical capacity of this block
        self.occupied_process = None                    # Set up a variable to hold a Process object if it is occupied
        self.internal_fragmentation = 0                 # Set up a tracking variable for internal fragmentation


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