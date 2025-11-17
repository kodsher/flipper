#!/usr/bin/env python3
"""
Debug script to test CSV parsing
"""

import csv
import os

def test_csv_parsing(csv_path):
    print(f"🔍 Debugging CSV: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8') as file:
        # Read the entire file and fix broken lines first
        content = file.read()
        print(f"📄 Original content (first 500 chars):")
        print(repr(content[:500]))
        print("\n" + "="*50 + "\n")

        # Fix the broken CSV format from 15-character line breaks
        lines = content.split('\n')
        fixed_lines = []
        current_line = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            print(f"Line {i}: {repr(line[:50])}")

            # If line starts with a quote and contains comma, it's likely a new row
            if line.startswith('"') and ('",' in line or line.endswith('"')):
                # Save previous line if exists
                if current_line:
                    fixed_lines.append(' '.join(current_line))
                    print(f"  -> Saving previous row: {len(current_line)} parts")
                current_line = [line]
                print(f"  -> Starting new row")
            else:
                # This is a continuation of the previous line
                current_line.append(line)
                print(f"  -> Continuing current row")

            if i >= 10:  # Only debug first 10 lines
                break

        # Don't forget the last row
        if current_line:
            fixed_lines.append(' '.join(current_line))
            print(f"  -> Saving final row")

        print(f"\n📝 Fixed lines ({len(fixed_lines)}):")
        for i, line in enumerate(fixed_lines[:5]):
            print(f"Fixed {i}: {line[:100]}...")

        # Now parse the fixed CSV
        csv_content = '\n'.join(fixed_lines)
        print(f"\n📊 CSV content to parse:")
        print(csv_content[:500])

if __name__ == "__main__":
    csv_path = os.path.expanduser("~/Downloads/scrape_2_51_listings.csv")
    test_csv_parsing(csv_path)