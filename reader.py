"""
CSV Reader & Modifier
Usage: python reader.py <src> <dst> <change1> <change2> ...

- src:     Path to the source CSV file
- dst:     Path where the modified CSV file will be saved
- changeN: Modifications in the format "X,Y,value"
           X = column index (from 0), Y = row index (from 0), value = new cell value

Example:
    python reader.py data.csv output.csv "1,0,Hello" "2,3,World"
"""

import sys
import os
import csv


def display_usage():
    """Display script usage instructions."""
    print("\nUsage: python reader.py <src> <dst> <change1> <change2> ...")
    print('  Each change has the format: "X,Y,value"')
    print("  X = column index (from 0)")
    print("  Y = row index (from 0)")
    print("  value = new cell value")
    print('\nExample: python reader.py data.csv output.csv "1,0,Hello" "2,3,World"')


def parse_change(change_str):
    """Parse a change string 'X,Y,value' into (column, row, value).

    The format is X,Y,value where the first two commas separate
    column and row indices, and everything after the second comma is the value.
    """
    parts = change_str.split(",", 2)  # Split on first 2 commas only
    if len(parts) < 3:
        print(f"  [!] Invalid change format: '{change_str}'. Expected 'X,Y,value'.")
        return None

    try:
        col = int(parts[0])
        row = int(parts[1])
    except ValueError:
        print(f"  [!] Invalid indices in '{change_str}'. X and Y must be integers.")
        return None

    value = parts[2]
    return col, row, value


def read_csv(filepath):
    """Read a CSV file and return its content as a list of lists."""
    rows = []
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
    except UnicodeDecodeError:
        # Fallback to latin-1 if utf-8 fails
        with open(filepath, "r", newline="", encoding="latin-1") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
    return rows


def apply_changes(data, changes):
    """Apply a list of (col, row, value) changes to the CSV data."""
    max_row = len(data)

    for col, row, value in changes:
        # Validate row index
        if row < 0 or row >= max_row:
            print(f"  [!] Row {row} is out of range (0–{max_row - 1}). Skipping.")
            continue

        max_col = len(data[row])

        # Extend the row if column index is beyond current length
        if col < 0:
            print(f"  [!] Column {col} is negative. Skipping.")
            continue

        if col >= max_col:
            data[row].extend([""] * (col - max_col + 1))

        data[row][col] = value
        print(f"  ✓ Set [{row}][{col}] = '{value}'")


def display_csv(data):
    """Display CSV content in a formatted table in the terminal."""
    if not data:
        print("\n  (empty file)")
        return

    # Calculate column widths for alignment
    col_widths = []
    for row in data:
        for i, cell in enumerate(row):
            if i >= len(col_widths):
                col_widths.append(len(str(cell)))
            else:
                col_widths[i] = max(col_widths[i], len(str(cell)))

    print("\n  Modified CSV content:")
    print("  " + "-" * (sum(col_widths) + 3 * len(col_widths) + 1))

    for row_idx, row in enumerate(data):
        cells = []
        for i, cell in enumerate(row):
            width = col_widths[i] if i < len(col_widths) else 0
            cells.append(f" {str(cell):<{width}} ")
        print(f"  |{'|'.join(cells)}|")

        # Separator after header row
        if row_idx == 0:
            print("  " + "-" * (sum(col_widths) + 3 * len(col_widths) + 1))

    print("  " + "-" * (sum(col_widths) + 3 * len(col_widths) + 1))


def save_csv(data, filepath):
    """Save CSV data to a file."""
    try:
        # Create destination directory if it doesn't exist
        dst_dir = os.path.dirname(filepath)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        print(f"\n  ✓ Saved modified CSV to: {filepath}")
    except OSError as e:
        print(f"\n  [!] Error saving file: {e}")


def main():
    # ── Validate arguments ────────────────────────────────────────────
    if len(sys.argv) < 3:
        print("  [!] Not enough arguments.")
        display_usage()
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    raw_changes = sys.argv[3:]

    # ── Validate source file ──────────────────────────────────────────
    if not os.path.exists(src):
        print(f"\n  [!] Error: '{src}' does not exist.")
        directory = os.path.dirname(src) or "."
        if os.path.isdir(directory):
            print(f"\n  Files in '{directory}':")
            for name in sorted(os.listdir(directory)):
                print(f"    - {name}")
        sys.exit(1)

    if not os.path.isfile(src):
        print(f"\n  [!] Error: '{src}' is not a file.")
        directory = os.path.dirname(src) or "."
        if os.path.isdir(directory):
            print(f"\n  Files in '{directory}':")
            for name in sorted(os.listdir(directory)):
                print(f"    - {name}")
        sys.exit(1)

    # ── Read CSV ──────────────────────────────────────────────────────
    print(f"\n  Reading: {src}")
    data = read_csv(src)
    print(f"  Loaded {len(data)} row(s).")

    # ── Parse and apply changes ───────────────────────────────────────
    if raw_changes:
        print(f"\n  Applying {len(raw_changes)} change(s):")
        changes = []
        for change_str in raw_changes:
            parsed = parse_change(change_str)
            if parsed:
                changes.append(parsed)

        apply_changes(data, changes)
    else:
        print("\n  No changes specified.")

    # ── Display and save ──────────────────────────────────────────────
    display_csv(data)
    save_csv(data, dst)


if __name__ == "__main__":
    main()
