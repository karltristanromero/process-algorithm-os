'''
Entry point for the Virtual Memory Page Replacement Simulator.
 
Run this file to start the program:
    python main.py
 
Project structure:
virtual_memory_simulation/
├── main.py                     ← you are here
├── base.py                     ← SimStep + PageReplacementAlgorithm (abstract base)
├── display.py                  ← Display class (frame trace, stats, comparison)
├── simulator.py                ← VMSimulator controller (input + flow)
└── algorithms/
    ├── __init__.py             ← package exports
    ├── first_in_first_out.py
    ├── optimal.py
    ├── least_recent_used.py
    ├── least_recent_used_approximation.py
    ├── least_frequently_used.py
    ├── most_frequently_used.py
'''

from simulator import VMSimulator


def main():
    print("\n" + "╔" + "═" * 56 + "╗")
    print("║   Virtual Memory Page Replacement Simulator          ║")
    print("║   Module 6 — Operating Systems                       ║")
    print("╚" + "═" * 56 + "╝")
    print(f"\n  Default number of frames: 4")

    simulator = VMSimulator(num_frames=4)

    while True:
        ref = simulator.get_reference_string()
        print(f"\n  Reference string ({len(ref)} refs): {' '.join(map(str, ref))}")
 
        choice = simulator.choose_algorithm()
 
        if choice == "7":
            simulator.run_all(ref)
        else:
            simulator.run_one(choice, ref)
 
        again = input("\n  Run another simulation? [y/n]: ").strip().lower()
        if again != "y":
            print("\n  Goodbye! Thank you for trying Virtual Memory Simulator!\n")
            break


if __name__ == "__main__":
    main()