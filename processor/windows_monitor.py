#!/usr/bin/env python3
"""
Facebook Marketplace CSV Monitor for Windows
Monitors CSV files for new phone listings and updates Firebase database
"""

import os
import time
import csv
import json
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PhoneListingMonitor:
    def __init__(self, csv_path: str, firebase_config: Dict):
        self.csv_path = csv_path
        self.processed_hashes = set()
        self.firebase_config = firebase_config

        # Initialize Firebase REST API
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']

        # Load previously processed listings
        self._load_processed_listings()

        # Phone model patterns
        self.iphone_patterns = [
            r'iphone\s*(\d+(?:\s*pro)?(?:\s*max)?(?:\s*plus)?)',
            r'iphone\s*(\d+)'
        ]

        # Price range filter
        self.min_price = 50
        self.max_price = 2000


    def _load_processed_listings(self):
        """Load hashes of previously processed listings"""
        try:
            url = f"{self.database_url}/processed_hashes.json?auth={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json() or {}
                self.processed_hashes = set(data.keys())
            else:
                pass
        except Exception as e:
            pass

    def _save_processed_hash(self, listing_hash: str):
        """Save a listing hash to prevent duplicates"""
        try:
            url = f"{self.database_url}/processed_hashes/{listing_hash}.json?auth={self.api_key}"
            data = {
                'processed_at': datetime.now().isoformat()
            }
            response = requests.patch(url, json=data)
            if response.status_code == 200:
                self.processed_hashes.add(listing_hash)
            else:
                pass
        except Exception as e:
            pass

    def _extract_phone_model(self, title: str) -> Optional[str]:
        """Extract iPhone model from title"""
        if not title:
            return 'Unknown'
        title_lower = title.lower()

        # Expanded iPhone patterns
        iphone_patterns = [
            r'iphone\s*(\d+(?:\s*pro)?(?:\s*max)?(?:\s*plus)?(?:\s*air)?)',
            r'iphone\s*(\d+)',
            r'(\d+)\s*pro\s*max',  # "16 pro max"
            r'(\d+)\s*pro',        # "16 pro"
            r'(\d+)\s*plus',       # "16 plus"
            r'(\d+)\s*max',        # "16 max"
            r'(\d+)\s*air',        # "16 air"
        ]

        for pattern in iphone_patterns:
            match = re.search(pattern, title_lower)
            if match:
                model = f"iPhone {match.group(1).upper()}"
                # Add common suffixes if they're in the title
                if 'pro max' in title_lower:
                    model += ' Pro Max'
                elif 'pro' in title_lower and 'max' not in title_lower:
                    model += ' Pro'
                elif 'plus' in title_lower:
                    model += ' Plus'
                elif 'max' in title_lower:
                    model += ' Max'
                elif 'air' in title_lower:
                    model += ' Air'
                return model

        # Check for other phone brands
        if any(brand in title_lower for brand in ['samsung', 'galaxy']):
            return 'Samsung Galaxy'
        elif any(brand in title_lower for brand in ['google pixel', 'pixel']):
            return 'Google Pixel'
        elif any(brand in title_lower for brand in ['oneplus']):
            return 'OnePlus'
        return 'Unknown'

    def _extract_price(self, price_str: str) -> Optional[float]:
        """Extract price from price string"""
        try:
            if not price_str:
                return None
            # Remove currency symbols, commas, and convert to float
            clean_price = re.sub(r'[^\d.]', '', str(price_str))
            if clean_price:
                price = float(clean_price)
                if self.min_price <= price <= self.max_price:
                    return price
            else:
                pass
        except (ValueError, TypeError):
            pass
        return None

    def _generate_listing_hash(self, listing: Dict) -> str:
        """Generate unique hash for listing to detect duplicates"""
        import hashlib
        content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    def _process_listing(self, row: Dict) -> Optional[Dict]:
        """Process a single CSV row into a phone listing"""
        try:
            # Handle both column name patterns
            title = str(row.get('Title', '') or row.get('title', '')).strip()
            price_str = str(row.get('Price', '') or row.get('price', '')).strip()
            location = str(row.get('Location', '') or row.get('location', '')).strip()
            link = str(row.get('Link', '') or row.get('link', '')).strip()

            # Extract price
            price = self._extract_price(price_str)
            if not price or price <= 0:
                return None

            # Extract phone model
            model = self._extract_phone_model(title)

            # Skip if no valid phone model found
            if model == 'Unknown':
                return None

            # Create listing object
            listing = {
                'title': title,
                'price': price,
                'model': model,
                'location': location,
                'link': link,
                'source': 'facebook_marketplace',
                'found_at': datetime.now().isoformat(),
                'detected_at': datetime.now().isoformat()
            }

            # Check if already processed
            listing_hash = self._generate_listing_hash(listing)
            if listing_hash in self.processed_hashes:
                return None

            return listing

        except Exception as e:
            pass
            return None

    def _save_to_firebase(self, listing: Dict):
        """Save a single listing to Firebase"""
        try:
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            response = requests.post(url, json=listing)

            if response.status_code == 200:
                # Save to processed hashes
                listing_hash = self._generate_listing_hash(listing)
                self._save_processed_hash(listing_hash)
            else:
                pass

        except Exception as e:
            pass

    def monitor_csv(self):
        """Monitor CSV file for new listings"""
        self.last_processed_file = None
        self.last_processed_time = 0

        if not os.path.exists(self.csv_path):
            return

        while True:
            try:
                # Check for the most recent file in Windows Downloads folder
                downloads_dir = "C:\\Users\\kodysherman\\Downloads"
                csv_files = []
                for file in os.listdir(downloads_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(downloads_dir, file)
                        csv_files.append((file_path, os.path.getmtime(file_path)))

                if not csv_files:
                    time.sleep(60)
                    continue

                current_file = max(csv_files, key=lambda x: x[1])[0]
                current_time = os.path.getmtime(current_file)

                # Only process if we have a new file or the same file was updated
                if (current_file != self.last_processed_file or
                    current_time > self.last_processed_time):

                    self.csv_path = current_file
                    logger.info(f"📁 New CSV detected: {os.path.basename(current_file)}")

                    new_listings = []

                    with open(self.csv_path, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        rows = list(reader)

                        for row in rows:
                            listing = self._process_listing(row)
                            if listing:
                                new_listings.append(listing)

                    if new_listings:
                        logger.info(f"✅ Processed {len(new_listings)} new listings from {os.path.basename(current_file)}")

                        for listing in new_listings:
                            self._save_to_firebase(listing)
                            time.sleep(0.1)

                    # Update tracking
                    self.last_processed_file = current_file
                    self.last_processed_time = current_time

                # Wait before next check
                time.sleep(10)  # Check every 10 seconds for new files

            except Exception as e:
                time.sleep(60)

def main():
    """Main function to run the CSV monitor on Windows"""
    # Configuration - look for most recent CSV in Windows Downloads
    downloads_dir = "C:\\Users\\kodysherman\\Downloads"

    # Find the most recent CSV file
    csv_files = []
    for file in os.listdir(downloads_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(downloads_dir, file)
            csv_files.append((file_path, os.path.getmtime(file_path)))

    if not csv_files:
        logger.error("❌ No CSV files found in Downloads")
        return

    # Use the most recent file (no time limit to catch all downloads)
    csv_path = max(csv_files, key=lambda x: x[1])[0]

    # Firebase configuration from your web app
    firebase_config = {
        "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
        "authDomain": "phone-flipping.firebaseapp.com",
        "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
        "projectId": "phone-flipping",
        "storageBucket": "phone-flipping.firebasestorage.app",
        "messagingSenderId": "523828027077",
        "appId": "1:523828027077:web:048a5003d81e6f3982daac"
    }

    # Start monitoring
    monitor = PhoneListingMonitor(csv_path, firebase_config)
    monitor.monitor_csv()

if __name__ == "__main__":
    main()