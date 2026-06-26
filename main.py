import tkinter as tk

# Function to launch CPU scheduling algorithms
from logging import root


def launch_cpu_scheduling_algorithms():
    pass

# Function to launch Virtual Memory algorithms
def launch_virtual_memory_algorithms():
    pass

# Function to launch Mass Memory algorithms
def launch_mass_memory_algorithms():
    pass

# Function to launch Memory Management algorithms
def launch_memory_management_algorithms():
    # Hide the main menu window
    root.withdraw()
    
    # Open the memory management simulator window
    sim_window = tk.Toplevel()
    
    # Import and run your memory management app on it
    from memory_management.memory_management_main import MemoryManagementApp
    app = MemoryManagementApp(sim_window)
    
    # Bring back main menu if the simulator window gets closed
    sim_window.bind("<Destroy>", lambda e: root.deiconify() if e.widget == sim_window else None)
    pass

# Main function to build the GUI and run the app
def main():
    # Create the root window
    global root
    root = tk.Tk()
    
    # Add title and window size
    root.title("OS Simulator Suite")
    root.geometry("400x500")
    root.configure(bg="#3D1E6D")
    
    # Header title
    title = tk.Label(root, text="OS Simulator Menu", font=("Arial", 16, "bold"), fg="white", bg="#3D1E6D", pady=20)
    title.pack()
    
    # Add user choice button for Memory Management
    btn1 = tk.Button(root, text="Memory Management", font=("Arial", 12, "bold"), width=22, height=2, command=launch_memory_management_algorithms)
    btn1.pack(pady=10)
    
    # Add user choice button for Virtual Memory
    btn2 = tk.Button(root, text="Virtual Memory", font=("Arial", 12, "bold"), width=22, height=2, state="disabled", command=launch_virtual_memory_algorithms)
    btn2.pack(pady=10)
    
    # Add user choice button for Mass Memory
    btn3 = tk.Button(root, text="Mass Memory", font=("Arial", 12, "bold"), width=22, height=2, state="disabled", command=launch_mass_memory_algorithms)
    btn3.pack(pady=10)
    
    # Add user choice button for CPU Scheduling
    btn4 = tk.Button(root, text="CPU Scheduling", font=("Arial", 12, "bold"), width=22, height=2, state="disabled", command=launch_cpu_scheduling_algorithms)
    btn4.pack(pady=10)
    
    # Run the main window loop
    root.mainloop()
    pass

# Check if the file is run directly
if __name__ == "__main__":
    main()