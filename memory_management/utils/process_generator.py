import random

# Part 1: Define what a Process is
class Process:
    def __init__(self, process_number: int, process_size: int = 0):
        self.process_id = f"P{process_number}"          # Set up the process id (strictly "P1" through "P10")
        self.process_size = process_size                # Set up the memory size needed (randomly chosen up to 64K)
        self.is_allocated = False                       # Set up a flag to track if it is currently inside memory (True/False)
        self.partition_id = None                        # Set up a variable to track which memory block/partition ID it is inside


# Part 2: Manual Input Option (MFT / MVT Standard)
def create_manual_process(process_id: str, process_size: int):
    process_id = process_id.strip().upper()             # Clean the input string spaces and force uppercase
    
    # Check if the user entered a valid process number (1 to 10)
    valid_ids = [f"P{i}" for i in range(1, 11)]
    if process_id not in valid_ids:
        raise ValueError("Invalid process ID. Please enter a process ID between P1 and P10.")
    
    # Check if the user entered a valid size (greater than 0 and max 64K)
    if process_size <= 0 or process_size > 64:
        raise ValueError("Invalid process size. Please enter a size between 1K and 64K.")
    
    # Create and return one Process object with the user's ID and size
    return Process(process_number=int(process_id[1:]), process_size=process_size)


# Part 3: Automatic Random Event Generator (Strict MFT/MVT Logic)
# Create a function to choose a random event (Enter or Leave)
    # Track the current state of all 10 processes (P1-P10)
    
    # Decide randomly to either make a process "ENTER" or "LEAVE"
    
    # If the choice is "ENTER":
        # Check if there is any process that has NOT entered yet (is_allocated == False)
        # Randomly pick ONE process from the outside pool (prevents duplication)
        # Assign it a random size up to 64K
        # Return the process with an "ALLOCATE" command string for MFT/MVT to handle
        
    # If the choice is "LEAVE":
        # Check if any process is currently inside memory (is_allocated == True)
        # If memory is empty, cancel and force an "ENTER" instead
        # Randomly pick ONE process currently inside memory
        # Return the process with a "DEALLOCATE" command string so MFT can free the partition or MVT can free the hole


# Part 4: User Choice Router
# Create a function that routes the application based on GUI selection
    # If the user chose "Manual Mode":
        # Process the specific text box inputs and pass them to the layout manager
    # If the user chose "Automatic Mode":
        # Run the random event generator to feed the next dynamic step to MFT or MVT