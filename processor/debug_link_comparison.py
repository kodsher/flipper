#!/usr/bin/env python3
"""
Debug script to compare links between different CSV files
"""

import os
import csv
from collections import defaultdict

def load_links_from_csv(csv_path):
    """Load all links from a CSV file"""
    links = []
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)

        for row in reader:
            title = str(row.get('Title', '') or row.get('title', '')).strip()
            link = str(row.get('Link', '') or row.get('link', '')).strip()
            price = str(row.get('Price', '') or row.get('price', '')).strip()

            if title and link and price:
                links.append({
                    'title': title,
                    'link': link,
                    'price': price,
                    'csv_file': os.path.basename(csv_path)
                })

    return links

def find_duplicate_links(csv_files):
    """Find duplicate links across multiple CSV files"""
    all_links = []
    link_map = defaultdict(list)

    # Load all links from all CSV files
    for csv_path in csv_files:
        if os.path.exists(csv_path):
            print(f"📂 Loading links from: {os.path.basename(csv_path)}")
            links = load_links_from_csv(csv_path)
            for link_info in links:
                link_map[link_info['link']].append(link_info)
                all_links.append(link_info)

    # Find duplicates
    duplicate_links = {link: items for link, items in link_map.items() if len(items) > 1}

    return all_links, duplicate_links

def main():
    print("🔍 Debug Link Comparison Across CSV Files")
    print("=" * 60)

    # Find most recent CSV files in Downloads
    downloads_dir = os.path.expanduser("~/Downloads")

    csv_files = []
    for file in os.listdir(downloads_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                csv_files.append((file_path, os.path.getmtime(file_path)))

    if len(csv_files) < 2:
        print("❌ Need at least 2 CSV files to compare")
        return

    # Get the 3 most recent files
    recent_files = sorted(csv_files, key=lambda x: x[1], reverse=True)[:3]
    csv_paths = [file_path for file_path, _ in recent_files]

    print(f"📁 Comparing {len(csv_paths)} most recent CSV files:")
    for i, path in enumerate(csv_paths, 1):
        print(f"   {i}. {os.path.basename(path)}")

    all_links, duplicate_links = find_duplicate_links(csv_paths)

    print(f"\n📊 Results:")
    print(f"   Total links across all files: {len(all_links)}")
    print(f"   Duplicate links: {len(duplicate_links)}")
    print(f"   Duplicates rate: {len(duplicate_links)/len(all_links)*100:.1f}%" if len(all_links) > 0 else "   Duplicates rate: 0%")

    if duplicate_links:
        print(f"\n🔄 DUPLICATE LINKS FOUND:")
        for i, (link, items) in enumerate(list(duplicate_links.items())[:10], 1):
            print(f"\n   {i}. Link appears {len(items)} times:")
            print(f"      {link[:80]}...")
            for item in items:
                print(f"         • {item['csv_file']}: {item['title'][:50]}... (${item['price']})")
    else:
        print(f"\n✅ No duplicate links found across the compared CSV files")

    # Show sample unique links
    print(f"\n📋 Sample UNIQUE Links:")
    unique_count = 0
    for link, items in duplicate_links.items():
        if len(items) == 1 and unique_count < 5:
            item = items[0]
            print(f"   • {item['csv_file']}: {item['title'][:50]}... (${item['price']})")
            print(f"     {link[:60]}...")
            unique_count += 1

    # Also check some items that might be unique
    all_link_map = {}
    for link_info in all_links:
        link = link_info['link']
        if link not in all_link_map:
            all_link_map[link] = []
        all_link_map[link].append(link_info)

    unique_links = [link for link, items in all_link_map.items() if len(items) == 1]
    print(f"\n   Actually unique links: {len(unique_links)}")

if __name__ == "__main__":
    main()