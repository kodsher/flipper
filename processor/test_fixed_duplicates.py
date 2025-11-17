#!/usr/bin/env python3
"""
Test the fixed duplicate detection logic
"""

import os
import csv
import hashlib
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

class DuplicateChecker:
    def __init__(self):
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']
        self.duplicate_cache = {}

        # Optimized HTTP session
        self.session = requests.Session()
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=50)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def extract_listing_id_from_link(self, link):
        """Extract listing ID from Facebook URL"""
        if not link:
            return None

        import re
        match = re.search(r'/item/(\d+)', link)
        if match:
            return match.group(1)
        return None

    def generate_listing_hash(self, listing):
        """Generate unique hash for listing to detect duplicates"""
        link = listing.get('link', '')
        if link:
            listing_id = self.extract_listing_id_from_link(link)
            if listing_id:
                return hashlib.md5(listing_id.encode()).hexdigest()

        # Fallback
        content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    def is_duplicate_in_firebase(self, listing_hash):
        """Check if a listing hash already exists in Firebase (fixed logic)"""
        # Check cache first
        if listing_hash in self.duplicate_cache:
            return self.duplicate_cache[listing_hash]

        try:
            # First check if hash exists in processed_hashes (for backwards compatibility)
            url = f"{self.database_url}/processed_hashes/{listing_hash}.json?auth={self.api_key}"
            response = self.session.get(url, timeout=1)
            if response.status_code == 200 and response.json() is not None:
                self.duplicate_cache[listing_hash] = True
                return True

            # If not in processed_hashes, check main phone_listings database
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}&orderBy=\"hash\"&equalTo=\"{listing_hash}\""
            response = self.session.get(url, timeout=2)

            is_duplicate = (response.status_code == 200 and response.json() is not None and
                          len(response.json()) > 0)

            # Cache the result
            self.duplicate_cache[listing_hash] = is_duplicate
            return is_duplicate

        except Exception as e:
            print(f"Error checking {listing_hash}: {e}")
            # Assume not duplicate on error to avoid missing listings
            self.duplicate_cache[listing_hash] = False
            return False

    def test_csv_file(self, csv_path):
        """Test CSV file with fixed duplicate detection"""
        print(f"📂 Testing CSV file: {os.path.basename(csv_path)}")

        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return

        total_rows = 0
        valid_listings = 0
        new_listings = 0
        duplicate_listings = 0

        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.DictReader(file)

            for i, row in enumerate(reader):
                total_rows += 1

                title = str(row.get('Title', '') or row.get('title', '')).strip()
                link = str(row.get('Link', '') or row.get('link', '')).strip()
                price = str(row.get('Price', '') or row.get('price', '')).strip()

                if not title or not link:
                    continue

                valid_listings += 1

                listing = {
                    'title': title,
                    'price': price,
                    'link': link,
                    'location': str(row.get('Location', '') or row.get('location', '')).strip()
                }

                hash_value = self.generate_listing_hash(listing)
                is_duplicate = self.is_duplicate_in_firebase(hash_value)

                if is_duplicate:
                    duplicate_listings += 1
                else:
                    new_listings += 1
                    if new_listings <= 3:  # Show first 3 new listings
                        print(f"   ✅ NEW: {title[:50]}... | {hash_value[:8]}")

        print(f"\n📊 Results with Fixed Duplicate Detection:")
        print(f"   Total rows: {total_rows}")
        print(f"   Valid listings: {valid_listings}")
        print(f"   New listings: {new_listings}")
        print(f"   Duplicate listings: {duplicate_listings}")
        print(f"   Duplicate rate: {duplicate_listings/valid_listings*100:.1f}%" if valid_listings > 0 else "   Duplicate rate: 0%")

def main():
    print("🔧 Testing Fixed Duplicate Detection")
    print("=" * 50)

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

    checker = DuplicateChecker()
    checker.test_csv_file(csv_path)

if __name__ == "__main__":
    main()