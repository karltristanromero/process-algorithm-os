import random

# Part 1: Define what a Fixed Partition Block is
class PartitionBlock:
    def __init__(self, partition_id: int, partition_size: int):
        self.partition_id = f"Block {partition_id}"     # Set up a partition id
        self.partition_size = partition_size            # Set up the total physical capacity of this block
        self.occupied_process = None                    # Set up a variable to hold a Process object if it is occupied
        self.internal_fragmentation = 0                 # Set up a tracking variable for internal fragmentation


# Part 2: Define the Fixed Memory Manager Track
class FixedMemoryManager:
    def __init__(self, total_memory_size: int = 64):
        self.total_memory_size = total_memory_size      # Initialize the total system RAM to 64K
        self.partitions = []                            # Set up an array list to hold the PartitionBlock structures

        # Determine a random number of partitions
        number_of_partitions = random.randint(3, 8)        # Randomly choose between 2 and 8 partitions
        
        # Generate random sizes that perfectly sum up to 64:
        break_points = sorted(random.sample(range(1, total_memory_size), number_of_partitions - 1))
        milestones = [0] + break_points + [total_memory_size]
            
        # Calculate individual partition size and spawn the PartitionBlock object
        for i in range(number_of_partitions):
            partition_size = milestones[i + 1] - milestones[i]
            self.partitions.append(PartitionBlock(partition_id = i + 1, partition_size = partition_size))
    
    def deallocate_process(self, process_id: str):
        """
        Looks up an occupied block by its process ID and releases it cleanly.
        """
        process_id = process_id.strip().upper()
        
        # Search for the running process ID inside the static partitions
        for partition in self.partitions:
            if partition.occupied_process and partition.occupied_process.process_id == process_id:
                process = partition.occupied_process
                
                # Reset its flags and clear the partition back to free
                process.is_allocated = False
                process.partition_id = None
                
                # Clear out the block's current process field and fragmentation tracker
                partition.occupied_process = None
                partition.internal_fragmentation = 0
                return True
                
        raise ValueError(f"Process {process_id} was not found running in any MFT partition.")