#!/usr/bin/env python3
"""
Debug the current CSV files to understand why duplicates aren't being detected
"""

import os
import csv
import re
import hashlib
from collections import defaultdict

def extract_listing_id_from_link(link):
    """Extract listing ID from Facebook URL"""
    if not link:
        return None

    match = re.search(r'/item/(\d+)', link)
    if match:
        return match.group(1)
    return None

def generate_listing_hash(listing):
    """Generate unique hash for listing to detect duplicates"""
    link = listing.get('link', '')
    if link:
        listing_id = extract_listing_id_from_link(link)
        if listing_id:
            return hashlib.md5(listing_id.encode()).hexdigest()

    # Fallback
    content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
    return hashlib.md5(content.encode()).hexdigest()

def analyze_csv_for_duplicates(csv_path):
    """Analyze a CSV file for duplicates by examining links and hashes"""
    print(f"📂 Analyzing CSV file: {os.path.basename(csv_path)}")
    print("=" * 60)

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    listings = []
    hash_groups = defaultdict(list)
    link_groups = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            title = str(row.get('Title', '') or row.get('title', '')).strip()
            link = str(row.get('Link', '') or row.get('link', '')).strip()
            price = str(row.get('Price', '') or row.get('price', '')).strip()
            location = str(row.get('Location', '') or row.get('location', '')).strip()

            if not title or not link:
                continue

            listing = {
                'title': title,
                'price': price,
                'location': location,
                'link': link,
                'row_number': i + 1
            }

            listings.append(listing)

            # Group by hash
            hash_value = generate_listing_hash(listing)
            hash_groups[hash_value].append(listing)

            # Group by link
            if link:
                link_groups[link].append(listing)

    print(f"📊 Total listings: {len(listings)}")

    # Check for duplicate links
    duplicate_links = {link: items for link, items in link_groups.items() if len(items) > 1}
    duplicate_hashes = {hash_val: items for hash_val, items in hash_groups.items() if len(items) > 1}

    print(f"🔗 Duplicate Links: {len(duplicate_links)} groups")
    print(f"🔐 Duplicate Hashes: {len(duplicate_hashes)} groups")

    if duplicate_links:
        print(f"\n🔗 DUPLICATE LINKS (Most problematic):")
        for i, (link, items) in enumerate(list(duplicate_links.items())[:10], 1):
            print(f"\n   {i}. Link: {link[:80]}...")
            print(f"      Appears {len(items)} times:")
            for item in items:
                listing_id = extract_listing_id_from_link(link)
                print(f"         Row {item['row_number']}: {item['title'][:50]}... | ${item['price']} | ID: {listing_id}")

    if duplicate_hashes:
        print(f"\n🔐 DUPLICATE HASHES:")
        for i, (hash_val, items) in enumerate(list(duplicate_hashes.items())[:5], 1):
            print(f"\n   {i}. Hash: {hash_val[:8]}... (Appears {len(items)} times)")
            for item in items:
                listing_id = extract_listing_id_from_link(item['link'])
                print(f"         Row {item['row_number']}: {item['title'][:50]}... | ${item['price']} | ID: {listing_id}")

    # Show some sample listing IDs
    print(f"\n📋 Sample Listing IDs:")
    listing_ids = set()
    for listing in listings[:20]:
        listing_id = extract_listing_id_from_link(listing['link'])
        if listing_id:
            listing_ids.add(listing_id)
            print(f"   {listing_id} - {listing['title'][:40]}...")

    print(f"\n✅ Unique Listing IDs: {len(listing_ids)}")
    print(f"⚠️  Issue: {len(listings) - len(listing_ids)} potential duplicates")

def main():
    print("🔍 Debugging Current CSV Duplicate Detection")
    print("=" * 70)

    # Find most recent CSV in Downloads
    downloads_dir = os.path.expanduser("~/Downloads")

    csv_files = []
    for file in os.listdir(downloads_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                csv_files.append((file_path, os.path.getmtime(file_path)))

    if not csv_files:
        print("❌ No CSV files found in Downloads")
        return

    # Analyze the most recent file
    csv_path = max(csv_files, key=lambda x: x[1])[0]

    analyze_csv_for_duplicates(csv_path)

if __name__ == "__main__":
    main()