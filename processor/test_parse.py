#!/usr/bin/env python3
"""
Test the CSV parsing and see what we get
"""

import csv
import os

def test_csv_parsing():
    csv_path = os.path.expanduser("~/Downloads/scrape_2_51_listings.csv")

    with open(csv_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Fix the broken CSV format from 15-character line breaks
    lines = content.split('\n')
    header_line = lines[0] if lines else ""
    data_rows = []
    current_row = []

    print(f"Header: {header_line}")

    # Process all lines after the header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # New rows start with a price pattern like "$123", "$45", etc.
        if line.startswith('"$') and '","' in line:
            # Save previous row if exists
            if current_row:
                data_rows.append(' '.join(current_row))
                print(f"Completed row: {data_rows[-1][:100]}...")
            current_row = [line]
            print(f"Starting new row: {line[:50]}...")
        else:
            # This is a continuation of the current row
            current_row.append(line)

    # Don't forget the last row
    if current_row:
        data_rows.append(' '.join(current_row))
        print(f"Completed final row: {data_rows[-1][:100]}...")

    print(f"\n📊 Found {len(data_rows)} data rows")

    # Reconstruct CSV with header and fixed data rows
    fixed_csv = header_line + '\n' + '\n'.join(data_rows)

    # Parse the fixed CSV
    reader = csv.DictReader(fixed_csv.split('\n'))

    for i, row in enumerate(reader):
        if i >= 3:  # Only show first 3 rows
            break
        print(f"\nRow {i}:")
        for key, value in row.items():
            print(f"  {key}: {repr(value)}")

if __name__ == "__main__":
    test_csv_parsing()