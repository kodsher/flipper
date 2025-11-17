#!/usr/bin/env python3
"""
Debug script to check Facebook Marketplace URLs in CSV files
"""

import os
import csv
import re
import hashlib

def extract_listing_id_from_link(link):
    """Extract listing ID from Facebook URL"""
    if not link:
        return None, "No link provided"

    # Pattern 1: /item/(\d+)
    match = re.search(r'/item/(\d+)', link)
    if match:
        return match.group(1), "Found /item/ pattern"

    # Pattern 2: Look for other common Facebook URL patterns
    match2 = re.search(r'marketplace/item/(\d+)', link)
    if match2:
        return match2.group(1), "Found marketplace/item/ pattern"

    # Pattern 3: Try to find any numeric ID
    match3 = re.search(r'(\d{10,})', link)  # Look for long numbers
    if match3:
        return match3.group(1), "Found long number pattern"

    return None, "No pattern matched"

def generate_listing_hash(listing):
    """Generate unique hash for listing to detect duplicates"""
    link = listing.get('link', '')
    if link:
        listing_id, pattern = extract_listing_id_from_link(link)
        if listing_id:
            return hashlib.md5(listing_id.encode()).hexdigest(), f"ID: {listing_id}, Pattern: {pattern}"

    # Fallback
    content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
    return hashlib.md5(content.encode()).hexdigest(), "Fallback to title+price+location"

def analyze_csv_file(csv_path):
    """Analyze URLs in CSV file"""
    print(f"📂 Analyzing CSV file: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    unique_hashes = {}
    duplicate_hashes = {}
    total_rows = 0
    sample_urls = []

    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            total_rows += 1

            title = str(row.get('Title', '') or row.get('title', '')).strip()
            link = str(row.get('Link', '') or row.get('link', '')).strip()
            price = str(row.get('Price', '') or row.get('price', '')).strip()

            if not title or not link:
                continue

            listing = {
                'title': title,
                'price': price,
                'link': link,
                'location': str(row.get('Location', '') or row.get('location', '')).strip()
            }

            hash_value, method = generate_listing_hash(listing)

            if hash_value in unique_hashes:
                duplicate_hashes[hash_value] = duplicate_hashes.get(hash_value, 0) + 1
                print(f"🔄 DUPLICATE: Hash {hash_value[:8]}...")
                print(f"   Original: {unique_hashes[hash_value]['title'][:50]}... | {unique_hashes[hash_value]['link'][:80]}...")
                print(f"   Current:  {title[:50]}... | {link[:80]}...")
                print(f"   Method: {method}")
                print()
            else:
                unique_hashes[hash_value] = {
                    'title': title,
                    'link': link,
                    'method': method
                }

            # Store sample URLs
            if len(sample_urls) < 10:
                listing_id, pattern = extract_listing_id_from_link(link)
                sample_urls.append({
                    'title': title[:50],
                    'link': link[:100],
                    'listing_id': listing_id,
                    'pattern': pattern,
                    'hash': hash_value[:8]
                })

    print(f"\n📊 Results:")
    print(f"   Total rows: {total_rows}")
    print(f"   Unique listings: {len(unique_hashes)}")
    print(f"   Duplicate groups: {len(duplicate_hashes)}")
    print(f"   Duplicate rate: {len(duplicate_hashes)/len(unique_hashes)*100:.1f}%" if len(unique_hashes) > 0 else "   Duplicate rate: 0%")

    print(f"\n🔗 Sample URLs:")
    for i, sample in enumerate(sample_urls, 1):
        print(f"   {i}. {sample['title']}...")
        print(f"      Link: {sample['link']}...")
        print(f"      ID: {sample['listing_id']}")
        print(f"      Pattern: {sample['pattern']}")
        print(f"      Hash: {sample['hash']}")
        print()

def main():
    print("🔍 Facebook Marketplace URL Analysis")
    print("=" * 60)

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

    # Use the most recent file
    csv_path = max(csv_files, key=lambda x: x[1])[0]

    print(f"📁 Using most recent file: {os.path.basename(csv_path)}")
    print()
    analyze_csv_file(csv_path)

if __name__ == "__main__":
    main()