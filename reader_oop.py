"""
File Reader & Modifier (OOP) — Handles CSV, JSON, and Pickle files.
Uses classes and inheritance for file type handling.

Usage: python reader_oop.py <src> <dst> <change1> <change2> ...

- src:     Path to source file (.csv, .json, or .pickle)
- dst:     Path to save modified file (.csv, .json, or .pickle)
- changeN: Modifications in the format "X,Y,value"
           X = column index (from 0), Y = row index (from 0), value = new cell value

Example:
    python reader_oop.py data.csv output.json "1,0,Hello" "2,3,World"
"""

import sys
import os
import csv
import json
import pickle
from abc import ABC, abstractmethod


# ── Base Class ────────────────────────────────────────────────────────


class FileHandler(ABC):
    """Abstract base class for reading, modifying, displaying, and writing files.

    Subclasses must implement read() and write() for their specific format.
    Common functionality (changes, display) is handled here.
    """

    SUPPORTED_EXTENSIONS = {".csv", ".json", ".pickle"}

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = []  # list of lists (rows of cells)

    @abstractmethod
    def read(self):
        """Read source file and populate self.data as a list of lists."""
        pass

    @abstractmethod
    def write(self, filepath):
        """Write self.data to the destination file."""
        pass

    @staticmethod
    def parse_change(change_str):
        """Parse a change string 'X,Y,value' into (column, row, value).

        The first two commas separate column and row indices;
        everything after the second comma is the value.
        """
        parts = change_str.split(",", 2)
        if len(parts) < 3:
            print(f"  [!] Invalid change format: '{change_str}'. Expected 'X,Y,value'.")
            return None

        try:
            col = int(parts[0].strip())
            row = int(parts[1].strip())
        except ValueError:
            print(f"  [!] Invalid indices in '{change_str}'. X and Y must be integers.")
            return None

        value = parts[2].strip()
        return col, row, value

    def apply_changes(self, raw_changes):
        """Parse and apply a list of change strings to self.data."""
        if not raw_changes:
            print("\n  No changes specified.")
            return

        print(f"\n  Applying {len(raw_changes)} change(s):")
        for change_str in raw_changes:
            parsed = self.parse_change(change_str)
            if parsed is None:
                continue

            col, row, value = parsed

            # Validate row
            if row < 0 or row >= len(self.data):
                print(f"  [!] Row {row} is out of range (0–{len(self.data) - 1}). Skipping.")
                continue

            # Validate column
            if col < 0:
                print(f"  [!] Column {col} is negative. Skipping.")
                continue

            # Extend row if column is beyond current length
            if col >= len(self.data[row]):
                self.data[row].extend([""] * (col - len(self.data[row]) + 1))

            self.data[row][col] = value
            print(f"  ✓ Set [{row}][{col}] = '{value}'")

    def display(self):
        """Display file content as a formatted table in the terminal."""
        if not self.data:
            print("\n  (empty file)")
            return

        # Calculate column widths
        col_widths = []
        for row in self.data:
            for i, cell in enumerate(row):
                if i >= len(col_widths):
                    col_widths.append(len(str(cell)))
                else:
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        separator = "  " + "-" * (sum(col_widths) + 3 * len(col_widths) + 1)

        print("\n  Modified file content:")
        print(separator)

        for row_idx, row in enumerate(self.data):
            cells = []
            for i, cell in enumerate(row):
                width = col_widths[i] if i < len(col_widths) else 0
                cells.append(f" {str(cell):<{width}} ")
            print(f"  |{'|'.join(cells)}|")

            # Separator after header row
            if row_idx == 0:
                print(separator)

        print(separator)

    @staticmethod
    def get_handler(filepath):
        """Factory method — return the correct FileHandler subclass based on extension."""
        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".csv":
            return CSVHandler(filepath)
        elif ext == ".json":
            return JSONHandler(filepath)
        elif ext == ".pickle":
            return PickleHandler(filepath)
        else:
            return None

    @staticmethod
    def get_writer(filepath):
        """Factory method — return a handler for writing to the destination path."""
        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".csv":
            return CSVHandler(filepath)
        elif ext == ".json":
            return JSONHandler(filepath)
        elif ext == ".pickle":
            return PickleHandler(filepath)
        else:
            return None


# ── CSV Handler ───────────────────────────────────────────────────────


class CSVHandler(FileHandler):
    """Handles reading and writing CSV files."""

    def read(self):
        """Read CSV file into self.data (list of lists)."""
        try:
            with open(self.filepath, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.data = [row for row in reader]
        except UnicodeDecodeError:
            with open(self.filepath, "r", newline="", encoding="latin-1") as f:
                reader = csv.reader(f)
                self.data = [row for row in reader]

        print(f"  Loaded CSV: {len(self.data)} row(s)")

    def write(self, filepath):
        """Write self.data to a CSV file."""
        dst_dir = os.path.dirname(filepath)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(self.data)

        print(f"  ✓ Saved as CSV: {filepath}")


# ── JSON Handler ──────────────────────────────────────────────────────


class JSONHandler(FileHandler):
    """Handles reading and writing JSON files (list of lists)."""

    def read(self):
        """Read JSON file into self.data (list of lists)."""
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            # Ensure each row is a list of strings
            self.data = [[str(cell) for cell in row] if isinstance(row, list) else [str(row)] for row in data]
        else:
            print("  [!] JSON file is not a list. Wrapping in a list.")
            self.data = [[str(data)]]

        print(f"  Loaded JSON: {len(self.data)} row(s)")

    def write(self, filepath):
        """Write self.data to a JSON file (list of lists)."""
        dst_dir = os.path.dirname(filepath)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

        print(f"  ✓ Saved as JSON: {filepath}")


# ── Pickle Handler ────────────────────────────────────────────────────


class PickleHandler(FileHandler):
    """Handles reading and writing Pickle files (list of lists)."""

    def read(self):
        """Read Pickle file into self.data (list of lists)."""
        with open(self.filepath, "rb") as f:
            data = pickle.load(f)

        if isinstance(data, list):
            self.data = [[str(cell) for cell in row] if isinstance(row, list) else [str(row)] for row in data]
        else:
            print("  [!] Pickle file is not a list. Wrapping in a list.")
            self.data = [[str(data)]]

        print(f"  Loaded Pickle: {len(self.data)} row(s)")

    def write(self, filepath):
        """Write self.data to a Pickle file (list of lists)."""
        dst_dir = os.path.dirname(filepath)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        with open(filepath, "wb") as f:
            pickle.dump(self.data, f)

        print(f"  ✓ Saved as Pickle: {filepath}")


# ── Utility Functions ─────────────────────────────────────────────────


def display_usage():
    """Display script usage instructions."""
    print("\nUsage: python reader_oop.py <src> <dst> <change1> <change2> ...")
    print('  Each change has the format: "X,Y,value"')
    print("  X = column index (from 0)")
    print("  Y = row index (from 0)")
    print("  value = new cell value")
    print("\nSupported formats: .csv, .json, .pickle")
    print('\nExample: python reader_oop.py data.csv output.json "1,0,Hello" "2,3,World"')


def validate_source(src):
    """Validate that source file exists and is a supported type."""
    if not os.path.exists(src):
        print(f"\n  [!] Error: '{src}' does not exist.")
        directory = os.path.dirname(src) or "."
        if os.path.isdir(directory):
            print(f"\n  Files in '{directory}':")
            for name in sorted(os.listdir(directory)):
                print(f"    - {name}")
        return False

    if not os.path.isfile(src):
        print(f"\n  [!] Error: '{src}' is not a file.")
        directory = os.path.dirname(src) or "."
        if os.path.isdir(directory):
            print(f"\n  Files in '{directory}':")
            for name in sorted(os.listdir(directory)):
                print(f"    - {name}")
        return False

    ext = os.path.splitext(src)[1].lower()
    if ext not in FileHandler.SUPPORTED_EXTENSIONS:
        print(f"\n  [!] Unsupported file type: '{ext}'.")
        print(f"  Supported: {', '.join(sorted(FileHandler.SUPPORTED_EXTENSIONS))}")
        return False

    return True


def validate_destination(dst):
    """Validate that destination file has a supported extension."""
    ext = os.path.splitext(dst)[1].lower()
    if ext not in FileHandler.SUPPORTED_EXTENSIONS:
        print(f"\n  [!] Unsupported destination type: '{ext}'.")
        print(f"  Supported: {', '.join(sorted(FileHandler.SUPPORTED_EXTENSIONS))}")
        return False
    return True


# ── Main ──────────────────────────────────────────────────────────────


def main():
    # Validate arguments
    if len(sys.argv) < 3:
        print("  [!] Not enough arguments.")
        display_usage()
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    raw_changes = sys.argv[3:]

    # Validate source and destination
    if not validate_source(src):
        sys.exit(1)

    if not validate_destination(dst):
        sys.exit(1)

    # Read source file using appropriate handler
    print(f"\n  Reading: {src}")
    reader = FileHandler.get_handler(src)
    try:
        reader.read()
    except Exception as e:
        print(f"  [!] Error reading file: {e}")
        sys.exit(1)

    # Apply changes
    reader.apply_changes(raw_changes)

    # Display modified content
    reader.display()

    # Write to destination using appropriate handler
    writer = FileHandler.get_writer(dst)
    writer.data = reader.data
    try:
        writer.write(dst)
    except Exception as e:
        print(f"\n  [!] Error saving file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
