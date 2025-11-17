#!/usr/bin/env python3
"""
Test script to verify search city extraction from CSV filenames
"""

import os
import re

def extract_search_city_from_filename(file_path: str) -> str:
    """Extract search city from CSV filename"""
    filename = os.path.basename(file_path).lower()

    # Extract city name from patterns like "houston262.csv" or "austin182.csv"
    # Look for city names before numbers

    # Common Texas cities pattern
    city_patterns = [
        r'(houston|austin|dallas|sanantonio|fortworth|elpaso|arlington|corpuschristi|plano|garland)',
        r'([a-zA-Z]+)(\d+)',  # Generic pattern: letters followed by numbers
    ]

    for pattern in city_patterns:
        match = re.search(pattern, filename)
        if match:
            city = match.group(1)
            # Clean up common city name issues
            if city == 'sanantonio':
                city = 'San Antonio'
            elif city == 'fortworth':
                city = 'Fort Worth'
            elif city == 'corpuschristi':
                city = 'Corpus Christi'
            else:
                # Capitalize properly
                city = city.capitalize()

            return city

    return 'Unknown'

def main():
    print("🔍 Search City Extraction Test")
    print("=" * 50)

    # Test with sample filenames
    test_files = [
        "/Users/admin/Downloads/houston262.csv",
        "/Users/admin/Downloads/austin182.csv",
        "/Users/admin/Downloads/dallas145.csv",
        "/Users/admin/Downloads/sanantonio200.csv",
        "/Users/admin/Downloads/fortworth89.csv",
        "/Users/admin/Downloads/0_listings.csv",
        "/Users/admin/Downloads/105_listings.csv"
    ]

    for file_path in test_files:
        city = extract_search_city_from_filename(file_path)
        print(f"📁 {os.path.basename(file_path)} -> 🏙️ {city}")

    # Test with actual files in Downloads
    print(f"\n📂 Actual CSV files in Downloads:")
    downloads_dir = os.path.expanduser("~/Downloads")

    csv_files = []
    for file in os.listdir(downloads_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                csv_files.append(file_path)

    if csv_files:
        for file_path in csv_files[:10]:  # Show first 10
            city = extract_search_city_from_filename(file_path)
            print(f"📁 {os.path.basename(file_path)} -> 🏙️ {city}")
    else:
        print("❌ No CSV files found in Downloads")

if __name__ == "__main__":
    main()