import random

# Part 1: Define what a Process is
class Process:
    def __init__(self, process_number: int, process_size: int = 0):
        self.process_id = f"P{process_number}"          # Set up the process id (strictly "P1" through "P10")
        self.process_size = process_size                # Set up the memory size needed (randomly chosen up to 64K)
        self.is_allocated = False                       # Set up a flag to track if it is currently inside memory (True/False)
        self.partition_id = None                        # Set up a variable to track which memory block/partition ID it is inside


# Global tracking pool for processes P1 through P10 to preserve state across calls
process_pool = {i: Process(process_number=i) for i in range(1, 11)}


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
    process_number = int(process_id[1:])
    process = process_pool[process_number]
    process.process_size = process_size
    
    return process


# Part 3: Automatic Random Event Generator
def generate_random_process_event():
    # Track the current state of all 10 processes (P1-P10)
    allocated_processes = [p for p in process_pool.values() if p.is_allocated]
    unallocated_processes = [p for p in process_pool.values() if not p.is_allocated]

    # Determine possible actions based on availability
    possible_actions = []
    if unallocated_processes:
        possible_actions.append("ENTER")
    if allocated_processes:
        possible_actions.append("LEAVE")
    if not possible_actions:
        return None
    
    # Decide randomly to either make a process "ENTER" or "LEAVE"
    chosen_action = random.choice(possible_actions)
    
    if chosen_action == "ENTER":
        process = random.choice(unallocated_processes)      # Randomly pick ONE process from the outside pool (prevents duplication)
        process.process_size = random.randint(1, 64)        # Assign it a random size up to 64K
        return "ALLOCATE", process                          # Return the process with an "ALLOCATE" command string for MFT/MVT to handle
        
    elif chosen_action == "LEAVE":
        # Randomly pick ONE process currently inside memory
        process = random.choice(allocated_processes)
        return "DEALLOCATE", process                       # Return the process with a "DEALLOCATE"


# Part 4: User Choice Router
def process_user_choice(mode_choice: str, action_type: str = None, process_id: str = None, process_size: int = None):
    mode_choice = mode_choice.strip().upper()
    
    if mode_choice == "MANUAL":
        action_type = action_type.strip().upper()
        if action_type == "ALLOCATE":
            if process_size is None:
                raise ValueError("Manual allocation requires a valid process size calculation entry.")
            return "ALLOCATE" , create_manual_process(process_id, process_size)
        elif action_type == "DEALLOCATE":
            return "DEALLOCATE", terminate_manual_process(process_id)
        else:
            raise ValueError("Invalid action type for manual mode. Please enter 'ALLOCATE' or 'DEALLOCATE'.")
    
    elif mode_choice == "RANDOM":
        return generate_random_process_event()
    else:
        raise ValueError("Invalid mode choice. Please enter 'MANUAL' or 'RANDOM'.")