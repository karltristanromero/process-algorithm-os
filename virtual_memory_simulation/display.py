'''
Handles all terminal output: frame trace table, stats, and comparison summary.
'''

class Display:
    '''Handles all terminal output formatting.'''

    COL_WIDTH = 5   # width of each step column

    @classmethod
    def print_header(cls, title: str):
        print("\n" + "═" * 60)
        print(f" {title}")
        print("═" * 60)

    @classmethod
    def print_frame_trace(cls, algo_name: str, steps: list[SimStep], num_frames: int):
        '''Prints the vertical frame trace table.'''
        if not steps:
            return
        
        w = cls.COL_WIDTH

        print(f"\n{'─' * 6}", end="")
        for _ in steps:
            print(f"{'─' * w}", end="")
        print()

        # Algorithm name
        print(f"  {algo_name}")

        # Reference string row
        print(f"  {'Ref':<4}", end="")
        for s in steps:
            print(f"{s.page:^{w}}", end="")
        print()