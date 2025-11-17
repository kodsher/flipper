#!/usr/bin/env python3
"""
Clean CSV Monitor - Simple Link-Based Duplicate Detection Only
"""

import os
import csv
import time
import hashlib
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CleanCSVMonitor:
    def __init__(self, firebase_config: Dict):
        self.firebase_config = firebase_config
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']
        self.existing_links = set()
        self.session = requests.Session()

        # Load existing links at startup
        self._load_existing_links()

    def _load_existing_links(self):
        """Load all existing Facebook marketplace links from database"""
        try:
            logger.info("📥 Loading existing Facebook marketplace links...")
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200 and response.json():
                listings_data = response.json()
                for listing_id, listing_data in listings_data.items():
                    if 'link' in listing_data and listing_data['link']:
                        self.existing_links.add(listing_data['link'])

                logger.info(f"✅ Loaded {len(self.existing_links)} existing links")
            else:
                logger.info("ℹ️ No existing listings found in database")

        except Exception as e:
            logger.error(f"❌ Error loading existing links: {e}")

    def is_duplicate_by_link(self, link: str) -> bool:
        """Simple check: is this link already in the database?"""
        if not link:
            return False
        return link in self.existing_links

    def _extract_search_city_from_filename(self, file_path: str) -> str:
        """Extract search city from CSV filename"""
        filename = os.path.basename(file_path).lower()

        # Common Texas cities pattern
        if 'houston' in filename:
            return 'Houston'
        elif 'austin' in filename:
            return 'Austin'
        elif 'dallas' in filename:
            return 'Dallas'
        else:
            return 'Unknown'

    def process_csv_file(self, file_path: str) -> List[Dict]:
        """Process CSV file with simple link-based duplicate checking"""
        try:
            new_listings = []
            total_rows = 0
            duplicates_filtered = 0

            search_city = self._extract_search_city_from_filename(file_path)
            logger.info(f"📂 Processing: {os.path.basename(file_path)} (City: {search_city})")

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    total_rows += 1

                    # Get basic data
                    title = str(row.get('Title', '') or row.get('title', '')).strip()
                    link = str(row.get('Link', '') or row.get('link', '')).strip()
                    price_str = str(row.get('Price', '') or row.get('price', '')).strip()
                    location = str(row.get('Location', '') or row.get('location', '')).strip()

                    if not title or not link:
                        continue

                    # DUPLICATE CHECK BY LINK
                    if self.is_duplicate_by_link(link):
                        duplicates_filtered += 1
                        logger.debug(f"🔄 FILTERED: {title[:30]}... (duplicate link)")
                        continue

                    # Extract and validate price
                    try:
                        price = float(price_str.replace('$', '').replace(',', ''))
                        if price <= 0:
                            continue
                    except:
                        continue

                    # Create listing
                    listing = {
                        'title': title,
                        'price': price,
                        'location': location,
                        'link': link,
                        'search_city': search_city,
                        'source': 'facebook_marketplace',
                        'found_at': datetime.now().isoformat(),
                        'detected_at': datetime.now().isoformat()
                    }

                    # Generate hash for tracking
                    listing['hash'] = hashlib.md5(link.encode()).hexdigest()
                    new_listings.append(listing)

            logger.info(f"📊 Results: {total_rows} total, {len(new_listings)} new, {duplicates_filtered} filtered")
            return new_listings

        except Exception as e:
            logger.error(f"❌ Error processing CSV: {e}")
            return []

    def save_to_firebase(self, listings: List[Dict]) -> bool:
        """Save listings to Firebase"""
        try:
            if not listings:
                logger.info("ℹ️ No listings to save")
                return True

            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            saved_count = 0

            for listing in listings:
                response = self.session.post(url, json=listing, timeout=5)
                if response.status_code == 200:
                    saved_count += 1
                    # Add to existing links to prevent immediate duplicates
                    self.existing_links.add(listing['link'])

            logger.info(f"✅ Saved {saved_count}/{len(listings)} listings to Firebase")
            return saved_count > 0

        except Exception as e:
            logger.error(f"❌ Error saving to Firebase: {e}")
            return False


def main():
    """Clean CSV Monitor Main Function"""
    firebase_config = {
        "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
        "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
    }

    # Find most recent CSV
    downloads_dir = os.path.expanduser("~/Downloads")
    csv_files = []

    for file in os.listdir(downloads_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                csv_files.append((file_path, os.path.getmtime(file_path)))

    if not csv_files:
        logger.error("❌ No CSV files found")
        return

    csv_path = max(csv_files, key=lambda x: x[1])[0]
    logger.info(f"📁 Using: {os.path.basename(csv_path)}")

    # Process CSV
    monitor = CleanCSVMonitor(firebase_config)
    new_listings = monitor.process_csv_file(csv_path)

    # Save to Firebase
    if new_listings:
        monitor.save_to_firebase(new_listings)
    else:
        logger.info("ℹ️ No new listings to save")

    logger.info("🎉 CSV processing complete!")


if __name__ == "__main__":
    main()