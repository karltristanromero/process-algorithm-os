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