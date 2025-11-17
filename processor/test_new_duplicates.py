#!/usr/bin/env python3
"""
Test the new in-memory duplicate detection logic
"""

import os
import csv
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

class NewDuplicateChecker:
    def __init__(self):
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']
        self.existing_listing_hashes = set()
        self.processed_hashes = set()
        self.duplicate_cache = {}

        # Load existing hashes
        self._load_existing_hashes()
        self._load_processed_hashes()

    def _load_existing_hashes(self):
        """Load all existing listing hashes from main phone_listings database"""
        try:
            print("📥 Loading existing listing hashes from database...")
            session = requests.Session()
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            response = session.get(url, timeout=10)

            if response.status_code == 200 and response.json():
                listings_data = response.json()
                for listing_id, listing_data in listings_data.items():
                    if 'hash' in listing_data:
                        self.existing_listing_hashes.add(listing_data['hash'])

                print(f"✅ Loaded {len(self.existing_listing_hashes)} existing listing hashes")
            else:
                print("ℹ️ No existing listings found in database")

        except Exception as e:
            print(f"❌ Error loading existing listing hashes: {e}")

    def _load_processed_hashes(self):
        """Load processed hashes for backwards compatibility"""
        try:
            print("📥 Loading processed hashes...")
            session = requests.Session()
            url = f"{self.database_url}/processed_hashes.json?auth={self.api_key}"
            response = session.get(url, timeout=10)

            if response.status_code == 200 and response.json():
                processed_data = response.json()
                self.processed_hashes = set(processed_data.keys())
                print(f"✅ Loaded {len(self.processed_hashes)} processed hashes")
            else:
                print("ℹ️ No processed hashes found")

        except Exception as e:
            print(f"❌ Error loading processed hashes: {e}")

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

    def is_duplicate(self, listing_hash):
        """Check if listing is duplicate using in-memory hash sets"""
        if listing_hash in self.duplicate_cache:
            return self.duplicate_cache[listing_hash]

        is_duplicate = (listing_hash in self.existing_listing_hashes or
                       listing_hash in self.processed_hashes)

        self.duplicate_cache[listing_hash] = is_duplicate
        return is_duplicate

    def test_csv_file(self, csv_path):
        """Test CSV file with new duplicate detection"""
        print(f"\n📂 Testing CSV file: {os.path.basename(csv_path)}")

        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return

        total_rows = 0
        valid_listings = 0
        new_listings = 0
        duplicate_listings = 0
        samples_new = []
        samples_duplicate = []

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
                is_duplicate = self.is_duplicate(hash_value)

                if is_duplicate:
                    duplicate_listings += 1
                    if len(samples_duplicate) < 3:
                        listing_id = self.extract_listing_id_from_link(link)
                        samples_duplicate.append({
                            'title': title[:50],
                            'id': listing_id,
                            'hash': hash_value[:8]
                        })
                else:
                    new_listings += 1
                    if len(samples_new) < 3:
                        listing_id = self.extract_listing_id_from_link(link)
                        samples_new.append({
                            'title': title[:50],
                            'id': listing_id,
                            'hash': hash_value[:8]
                        })

        print(f"\n📊 Results with NEW Duplicate Detection:")
        print(f"   Total rows: {total_rows}")
        print(f"   Valid listings: {valid_listings}")
        print(f"   New listings: {new_listings}")
        print(f"   Duplicate listings: {duplicate_listings}")
        print(f"   Duplicate rate: {duplicate_listings/valid_listings*100:.1f}%" if valid_listings > 0 else "   Duplicate rate: 0%")

        if samples_new:
            print(f"\n✅ Sample NEW Listings:")
            for i, sample in enumerate(samples_new, 1):
                print(f"   {i}. {sample['title']}... | ID: {sample['id']} | Hash: {sample['hash']}")

        if samples_duplicate:
            print(f"\n🔄 Sample DUPLICATE Listings:")
            for i, sample in enumerate(samples_duplicate, 1):
                print(f"   {i}. {sample['title']}... | ID: {sample['id']} | Hash: {sample['hash']}")

def main():
    print("🔧 Testing NEW In-Memory Duplicate Detection")
    print("=" * 60)

    checker = NewDuplicateChecker()

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

    # Test the 2 most recent files
    recent_files = sorted(csv_files, key=lambda x: x[1], reverse=True)[:2]

    for file_path, _ in recent_files:
        checker.test_csv_file(file_path)

if __name__ == "__main__":
    main()