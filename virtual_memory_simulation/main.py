'''
Entry point — launches the Virtual Memory GUI.
 
Run this file to start the program:
    python main.py
 
Project structure:
vm_simulator/
├── main.py                     ← updated: launches GUI
├── base.py                     ← unchanged
├── display.py                  ← unchanged (terminal version)
├── simulator.py                ← unchanged (terminal version)
├── algorithms/
│   ├── __init__.py
│   ├── fifo.py
│   ├── optimal.py
│   ├── lru.py
│   ├── lru_approximation.py
│   ├── lfu.py
│   └── mfu.py
└── gui/
    ├── __init__.py
    ├── theme.py                                                ← colors, fonts, sizing constants
    ├── widgets.py                                              ← RoundedButton, FrameTraceTable, StatsBar
    ├── algorithm_select.py                                     ← "Pick an Algorithm" screen
    ├── simulation_screen.py                                    ← single algo + Compare All screens
    ├── ALGO_MENU_BG.png                                        ← your Canva background (place here)
    ├── SIMULATION_BG.png                                       ← your Canva background (place here)
    ├── NTBrickSans.ttf                                         ← download from iFonts
    └── TT-Chocolates-Trial-Regular-iF67447a8ce204c.ttf         ← download from DaFonts
'''

from simulator import VMSimulator


def main():
    print("\n" + "╔" + "═" * 56 + "╗")
    print("║   Virtual Memory Page Replacement Simulator            ║")
    print("║   Module 6 — Operating Systems                         ║")
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