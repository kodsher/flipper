#!/usr/bin/env python3
"""
Test the new link-based duplicate detection
"""

import os
import csv
import requests
import hashlib

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

class LinkBasedDuplicateChecker:
    def __init__(self):
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']
        self.existing_links = set()

        # Load existing links
        self._load_existing_links()

    def _load_existing_links(self):
        """Load all existing Facebook marketplace links from database"""
        try:
            print("📥 Loading existing Facebook marketplace links from database...")
            session = requests.Session()
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            response = session.get(url, timeout=15)

            if response.status_code == 200 and response.json():
                listings_data = response.json()
                for listing_id, listing_data in listings_data.items():
                    if 'link' in listing_data and listing_data['link']:
                        self.existing_links.add(listing_data['link'])

                print(f"✅ Loaded {len(self.existing_links)} existing Facebook links")
            else:
                print("ℹ️ No existing listings found in database")

        except Exception as e:
            print(f"❌ Error loading existing links: {e}")

    def is_link_already_in_database(self, link: str) -> bool:
        """Check if a Facebook marketplace link already exists in the database"""
        if not link:
            return False
        return link in self.existing_links

    def test_csv_file(self, csv_path):
        """Test CSV file with new link-based duplicate detection"""
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
                location = str(row.get('Location', '') or row.get('location', '')).strip()

                if not title or not link:
                    continue

                valid_listings += 1

                # Check for duplicate by link
                is_duplicate = self.is_link_already_in_database(link)

                if is_duplicate:
                    duplicate_listings += 1
                    if len(samples_duplicate) < 5:
                        samples_duplicate.append({
                            'title': title[:60],
                            'link': link[:80],
                            'price': price,
                            'location': location
                        })
                else:
                    new_listings += 1
                    if len(samples_new) < 5:
                        samples_new.append({
                            'title': title[:60],
                            'link': link[:80],
                            'price': price,
                            'location': location
                        })

        print(f"\n📊 Results with NEW Link-Based Duplicate Detection:")
        print(f"   Total rows: {total_rows}")
        print(f"   Valid listings: {valid_listings}")
        print(f"   New listings: {new_listings}")
        print(f"   Duplicate listings: {duplicate_listings}")
        print(f"   Duplicate rate: {duplicate_listings/valid_listings*100:.1f}%" if valid_listings > 0 else "   Duplicate rate: 0%")

        if samples_new:
            print(f"\n✅ Sample NEW Listings:")
            for i, sample in enumerate(samples_new, 1):
                print(f"   {i}. {sample['title']}...")
                print(f"      ${sample['price']} | {sample['location']}")
                print(f"      Link: {sample['link']}...")

        if samples_duplicate:
            print(f"\n🔄 Sample DUPLICATE Listings (Already in Database):")
            for i, sample in enumerate(samples_duplicate, 1):
                print(f"   {i}. {sample['title']}...")
                print(f"      ${sample['price']} | {sample['location']}")
                print(f"      Link: {sample['link']}...")

def main():
    print("🔧 Testing NEW Link-Based Duplicate Detection")
    print("=" * 60)

    checker = LinkBasedDuplicateChecker()

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

    # Test the most recent file
    csv_path = max(csv_files, key=lambda x: x[1])[0]

    checker.test_csv_file(csv_path)

if __name__ == "__main__":
    main()