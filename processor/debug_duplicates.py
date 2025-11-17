#!/usr/bin/env python3
"""
Debug script to analyze CSV listings vs database duplicates
"""

import os
import time
import csv
import re
import hashlib
import requests
from datetime import datetime

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

def generate_listing_hash(listing):
    """Generate unique hash for listing to detect duplicates"""
    link = listing.get('link', '')
    if link:
        # Extract listing ID from Facebook URL
        match = re.search(r'/item/(\d+)', link)
        if match:
            listing_id = match.group(1)
            return hashlib.md5(listing_id.encode()).hexdigest()

    # Fallback to title + price if no unique link
    content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
    return hashlib.md5(content.encode()).hexdigest()

def check_duplicate_in_firebase(listing_hash):
    """Check if a listing hash already exists in Firebase"""
    try:
        url = f"{firebase_config['databaseURL']}/processed_hashes/{listing_hash}.json?auth={firebase_config['apiKey']}"
        response = requests.get(url, timeout=5)
        return response.status_code == 200 and response.json() is not None
    except Exception:
        return False

def analyze_csv_file(csv_path):
    """Analyze CSV file for duplicates"""
    print(f"📂 Analyzing CSV file: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    total_rows = 0
    valid_listings = 0
    new_listings = 0
    duplicate_listings = 0
    samples = []

    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            total_rows += 1

            # Extract basic data
            title = str(row.get('Title', '') or row.get('title', '')).strip()
            price_str = str(row.get('Price', '') or row.get('price', '')).strip()
            location = str(row.get('Location', '') or row.get('location', '')).strip()
            link = str(row.get('Link', '') or row.get('link', '')).strip()

            # Basic validation
            if not title or not price_str:
                continue

            valid_listings += 1

            # Create listing object
            listing = {
                'title': title,
                'price': price_str,
                'location': location,
                'link': link
            }

            # Generate hash
            listing_hash = generate_listing_hash(listing)

            # Check if duplicate
            is_duplicate = check_duplicate_in_firebase(listing_hash)

            if is_duplicate:
                duplicate_listings += 1
            else:
                new_listings += 1

                # Store sample of new listings
                if len(samples) < 5:
                    samples.append({
                        'title': title[:50] + '...' if len(title) > 50 else title,
                        'price': price_str,
                        'location': location,
                        'hash': listing_hash
                    })

    # Print results
    print(f"\n📊 Analysis Results:")
    print(f"   Total CSV rows: {total_rows}")
    print(f"   Valid listings: {valid_listings}")
    print(f"   New listings: {new_listings}")
    print(f"   Duplicate listings: {duplicate_listings}")
    print(f"   Duplicate rate: {duplicate_listings/valid_listings*100:.1f}%" if valid_listings > 0 else "   Duplicate rate: 0%")

    print(f"\n🔍 Firebase Console Links:")
    print(f"   Main Database: https://console.firebase.google.com/project/phone-flipping/database/phone-flipping-default-rtdb/data/~2Fphone_listings")
    print(f"   CSV Monitor: https://console.firebase.google.com/project/phone-flipping/database/phone-flipping-default-rtdb/data/~2Fprocessed_hashes")

    if samples:
        print(f"\n🆕 Sample New Listings:")
        for i, sample in enumerate(samples, 1):
            print(f"   {i}. {sample['title']} - {sample['price']} - {sample['location']}")

def main():
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

    print("🔍 CSV Duplicate Analysis Tool")
    print("=" * 50)
    analyze_csv_file(csv_path)

if __name__ == "__main__":
    main()