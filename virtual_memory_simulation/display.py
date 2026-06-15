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

        print(f"{'─' * 6}", end="")
        for _ in steps:
            print(f"{'─' * w}", end="")
        print()

        # Frame rows
        for frame_idx in range(num_frames):
            print(f"  F{frame_idx + 1}  ", end="")
            for s in steps:
                val = s.frames[frame_idx]
                cell = str(val) if val is not None else "·"
                print(f"{cell:^{w}}", end="")
            print()

        print(f"{'─' * 6}", end="")
        for _ in steps:
            print(f"{'─' * w}", end="")
        print()

        # Fault / Hit status row
        print(f"  {'':4}", end="")
        for s in steps:
            marker = "F" if s.is_fault else "H"
            print(f"{marker:^{w}}", end="")
        print()

        print(f"{'─' * 6}", end="")
        for _ in steps:
            print(f"{'─' * w}", end="")
        print()

    @classmethod
    def print_stats(cls, algorithm: PageReplacementAlgorithm):
        """Prints fault/hit summary for one algorithm."""
        total = algorithm.fault_count + algorithm.hit_count
        print(f"\n  Page faults : {algorithm.fault_count} / {total}")
        print(f"  Page hits   : {algorithm.hit_count} / {total}")
        print(f"  Hit rate    : {algorithm.hit_rate:.1f}%")

    @classmethod
    def print_comparison(cls, results: list[tuple]):
        """
        Prints a comparison summary table across all algorithms.
        results: list of (name, fault_count, hit_count, hit_rate)
        """
        cls.print_header("COMPARISON SUMMARY")
        col = 30
        print(f"\n  {'Algorithm':<{col}} {'Faults':>8} {'Hits':>8} {'Hit Rate':>10}")
        print(f"  {'─' * col} {'─' * 8} {'─' * 8} {'─' * 10}")

        sorted_results = sorted(results, key=lambda x: x[1])  # sort by fault count
        best_faults = sorted_results[0][1]

        for name, faults, hits, rate in sorted_results:
            marker = " ← best" if faults == best_faults else ""
            print(f"  {name:<{col}} {faults:>8} {hits:>8} {rate:>9.1f}%{marker}")
        print()