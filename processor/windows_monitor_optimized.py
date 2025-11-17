#!/usr/bin/env python3
"""
Optimized Facebook Marketplace CSV Monitor for Windows
Monitors CSV files for new phone listings and updates Firebase database with batch processing
"""

import os
import time
import csv
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for detailed logging
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedPhoneListingMonitor:
    def __init__(self, csv_path: str, firebase_config: Dict):
        self.csv_path = csv_path
        self.processed_hashes: Set[str] = set()
        self.firebase_config = firebase_config
        self.batch_size = 500  # Firebase batch limit

        # Initialize Firebase REST API
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']

        # Optimized HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Load previously processed listings
        self._load_processed_listings()

        # Phone model patterns (compiled regex for better performance)
        # All patterns require "iphone" to be present to avoid false positives
        self.iphone_patterns = [
            re.compile(r'iphone\s*(\d+(?:\s*pro)?(?:\s*max)?(?:\s*plus)?(?:\s*air)?)', re.IGNORECASE),
            re.compile(r'iphone\s*(\d+)\s*(pro\s*max|pro|max|plus|air)', re.IGNORECASE),
            re.compile(r'iphone\s*(\d+)(?!\s*(pro|max|plus|air))', re.IGNORECASE),
        ]

        # Price range filter
        self.min_price = 50
        self.max_price = 2000

    def _load_processed_listings(self):
        """Load hashes of previously processed listings"""
        logger.info("✅ Will check Firebase for duplicates in real-time")

    def _is_duplicate_in_firebase(self, listing_hash: str) -> bool:
        """Check if a listing hash already exists in Firebase (real-time check)"""
        try:
            url = f"{self.database_url}/processed_hashes/{listing_hash}.json?auth={self.api_key}"
            response = self.session.get(url, timeout=2)
            return response.status_code == 200 and response.json() is not None
        except Exception:
            return False

    def _extract_phone_model(self, title: str) -> Optional[str]:
        """Extract iPhone model from title - optimized"""
        if not title:
            return 'Unknown'

        title_lower = title.lower()

        # Debug logging
        logger.debug(f"🔍 Extracting model from title: '{title}'")

        for i, pattern in enumerate(self.iphone_patterns):
            match = pattern.search(title)
            if match:
                model = f"iPhone {match.group(1).upper()}"
                logger.debug(f"✅ Pattern {i+1} matched: {model} from '{match.group(1)}'")

                # Add common suffixes if they're in the title
                if 'pro max' in title_lower:
                    model += ' Pro Max'
                    logger.debug("➕ Added 'Pro Max' suffix")
                elif 'pro' in title_lower and 'max' not in title_lower:
                    model += ' Pro'
                    logger.debug("➕ Added 'Pro' suffix")
                elif 'plus' in title_lower:
                    model += ' Plus'
                    logger.debug("➕ Added 'Plus' suffix")
                elif 'max' in title_lower:
                    model += ' Max'
                    logger.debug("➕ Added 'Max' suffix")
                elif 'air' in title_lower:
                    model += ' Air'
                    logger.debug("➕ Added 'Air' suffix")

                logger.debug(f"🎯 Final model: {model}")
                return model

        # Check for other phone brands
        if any(brand in title_lower for brand in ['samsung', 'galaxy']):
            logger.debug("📱 Detected Samsung Galaxy")
            return 'Samsung Galaxy'
        elif any(brand in title_lower for brand in ['google pixel', 'pixel']):
            logger.debug("📱 Detected Google Pixel")
            return 'Google Pixel'
        elif any(brand in title_lower for brand in ['oneplus']):
            logger.debug("📱 Detected OnePlus")
            return 'OnePlus'

        logger.debug(f"❌ No phone model detected in: '{title}'")
        return 'Unknown'

    def _extract_price(self, price_str: str) -> Optional[float]:
        """Extract price from price string - optimized"""
        try:
            logger.debug(f"💰 Extracting price from: '{price_str}'")

            if not price_str:
                logger.debug("❌ Empty price string")
                return None

            # Remove currency symbols, commas, and convert to float
            clean_price = re.sub(r'[^\d.]', '', str(price_str))
            logger.debug(f"🧹 Cleaned price: '{clean_price}'")

            if clean_price:
                price = float(clean_price)
                logger.debug(f"🔢 Converted to float: ${price}")

                if self.min_price <= price <= self.max_price:
                    logger.debug(f"✅ Price in range: ${price}")
                    return price
                else:
                    logger.debug(f"❌ Price out of range: ${price} (min: ${self.min_price}, max: ${self.max_price})")
            else:
                logger.debug("❌ No digits found in price string")

        except (ValueError, TypeError) as e:
            logger.debug(f"❌ Price extraction error: {e}")

        return None

    def _generate_listing_hash(self, listing: Dict) -> str:
        """Generate unique hash for listing to detect duplicates - using link for uniqueness"""
        # Use the link as primary identifier since it should be unique per listing
        link = listing.get('link', '')
        if link:
            # Extract listing ID from Facebook URL
            import re
            match = re.search(r'/item/(\d+)', link)
            if match:
                listing_id = match.group(1)
                return hashlib.md5(listing_id.encode()).hexdigest()

        # Fallback to title + price if no unique link
        content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_already_processed(self, listing_hash: str) -> bool:
        """Check if a listing has already been processed by querying Firebase directly"""
        try:
            url = f"{self.database_url}/processed_hashes/{listing_hash}.json?auth={self.api_key}"
            response = self.session.get(url, timeout=2)
            return response.status_code == 200 and response.json() is not None
        except Exception:
            return False

    def _process_listing(self, row: Dict) -> Optional[Dict]:
        """Process a single CSV row into a listing - optimized (accepts all items)"""
        try:
            # Handle both column name patterns
            title = str(row.get('Title', '') or row.get('title', '')).strip()
            price_str = str(row.get('Price', '') or row.get('price', '')).strip()
            location = str(row.get('Location', '') or row.get('location', '')).strip()
            link = str(row.get('Link', '') or row.get('link', '')).strip()

            logger.debug(f"📋 Processing row: Title='{title}', Price='{price_str}', Location='{location}'")

            # Extract price
            price = self._extract_price(price_str)
            if not price or price <= 0:
                logger.debug(f"❌ Invalid price: {price_str} -> {price}")
                return None

            logger.debug(f"💰 Valid price extracted: ${price}")

            # Extract phone model (optional - for categorization but not filtering)
            model = self._extract_phone_model(title)
            if model == 'Unknown':
                model = 'General Item'  # Categorize non-phone items as General Items
            logger.debug(f"📱 Category: {model}")

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

            # Generate hash
            listing_hash = self._generate_listing_hash(listing)
            listing['hash'] = listing_hash
            logger.debug(f"🔐 Generated hash: {listing_hash}")

            # Check if duplicate (only filter actual duplicates)
            is_duplicate = self._is_duplicate_in_firebase(listing_hash)
            logger.debug(f"🔍 Checking duplicate: {listing_hash} -> {'DUPLICATE' if is_duplicate else 'NEW'}")
            if is_duplicate:
                logger.debug(f"🚫 Filtering duplicate: {title[:50]}...")
                return None

            logger.debug(f"✅ New listing accepted: {model} - ${price} - {title[:50]}...")
            return listing

        except Exception as e:
            logger.error(f"❌ Error processing row: {e}")
            return None

    def _save_batch_to_firebase(self, listings: List[Dict]) -> bool:
        """Save multiple listings to Firebase in batch - optimized"""
        try:
            # Firebase doesn't support REST batch operations directly,
            # so we'll use parallel requests instead
            success_count = 0
            successful_hashes = []

            def save_single_listing(listing):
                try:
                    url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
                    response = self.session.post(url, json=listing, timeout=3)
                    if response.status_code == 200:
                        return True, listing['hash']
                    return False, listing['hash']
                except Exception:
                    return False, listing['hash']

            # Process listings in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_listing = {executor.submit(save_single_listing, listing): listing for listing in listings}

                for future in as_completed(future_to_listing):
                    success, listing_hash = future.result()
                    if success:
                        success_count += 1
                        successful_hashes.append(listing_hash)

            # Batch save processed hashes
            if success_count > 0:
                self._batch_save_processed_hashes(successful_hashes)

            logger.info(f"✅ Saved {success_count}/{len(listings)} listings to Firebase")
            return success_count > 0

        except Exception as e:
            logger.error(f"❌ Error saving batch to Firebase: {e}")
            return False

    def _batch_save_processed_hashes(self, hashes: List[str]):
        """Save multiple processed hashes in a single request"""
        try:
            data = {hash_val: {'processed_at': datetime.now().isoformat()} for hash_val in hashes}
            url = f"{self.database_url}/processed_hashes.json?auth={self.api_key}"
            self.session.patch(url, json=data, timeout=3)
        except Exception as e:
            logger.error(f"❌ Error saving processed hashes batch: {e}")

    def process_csv_file(self, file_path: str) -> List[Dict]:
        """Process entire CSV file efficiently"""
        try:
            new_listings = []
            total_rows = 0

            logger.info(f"📂 Opening CSV file: {file_path}")

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                reader = csv.DictReader(file)

                # Log the headers to understand the CSV structure
                headers = reader.fieldnames
                logger.info(f"📋 CSV Headers: {headers}")

                # Process all rows first, then batch upload
                for i, row in enumerate(reader):
                    total_rows += 1
                    logger.debug(f"📖 Reading row {i+1}: {dict(row)}")

                    listing = self._process_listing(row)
                    if listing:
                        new_listings.append(listing)

            logger.info(f"📊 CSV Summary: {total_rows} total rows, {len(new_listings)} valid listings")
            logger.info(f"🎯 Acceptance rate: {len(new_listings)/total_rows*100:.1f}% ({len(new_listings)}/{total_rows})")
            return new_listings

        except Exception as e:
            logger.error(f"❌ Error processing CSV file {file_path}: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []

    def monitor_csv(self):
        """Monitor CSV file for new listings - optimized"""
        self.last_processed_file = None
        self.last_processed_time = 0
        consecutive_errors = 0
        max_consecutive_errors = 5

        if not os.path.exists(self.csv_path):
            logger.error(f"❌ Initial CSV file not found: {self.csv_path}")
            return

        while True:
            try:
                consecutive_errors = 0  # Reset error counter on success

                # Check for the most recent file in Windows Downloads folder
                downloads_dir = "C:\\Users\\kodysherman\\Downloads"

                if not os.path.exists(downloads_dir):
                    logger.error(f"❌ Downloads directory not found: {downloads_dir}")
                    time.sleep(30)
                    continue

                csv_files = []
                try:
                    for file in os.listdir(downloads_dir):
                        if file.endswith('.csv'):
                            file_path = os.path.join(downloads_dir, file)
                            if os.path.isfile(file_path):  # Ensure it's a file, not directory
                                csv_files.append((file_path, os.path.getmtime(file_path)))
                except Exception as e:
                    logger.error(f"❌ Error listing files in Downloads: {e}")
                    time.sleep(30)
                    continue

                if not csv_files:
                    logger.info("📂 No CSV files found in Downloads, waiting...")
                    time.sleep(30)
                    continue

                # Find the most recent file
                current_file = max(csv_files, key=lambda x: x[1])[0]
                current_time = os.path.getmtime(current_file)

                # Only process if we have a new file or the same file was updated
                if (current_file != self.last_processed_file or
                    current_time > self.last_processed_time + 5):  # 5-second buffer for file writes

                    logger.info(f"📁 Processing new/updated CSV: {os.path.basename(current_file)}")

                    # Process the entire file
                    start_time = time.time()
                    new_listings = self.process_csv_file(current_file)
                    processing_time = time.time() - start_time

                    if new_listings:
                        logger.info(f"📊 Found {len(new_listings)} new listings in {processing_time:.2f}s")

                        # Process in batches
                        total_saved = 0
                        for i in range(0, len(new_listings), self.batch_size):
                            batch = new_listings[i:i + self.batch_size]
                            batch_start = time.time()

                            if self._save_batch_to_firebase(batch):
                                total_saved += len(batch)

                            batch_time = time.time() - batch_start
                            logger.info(f"📦 Batch {i//self.batch_size + 1}: {len(batch)} listings in {batch_time:.2f}s")

                        logger.info(f"🎉 Total saved: {total_saved}/{len(new_listings)} listings")
                    else:
                        logger.info("ℹ️ No new listings found in CSV file")

                    # Update tracking
                    self.last_processed_file = current_file
                    self.last_processed_time = current_time

                # Wait before next check (reduced for better responsiveness)
                time.sleep(5)

            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ Error in monitor loop ({consecutive_errors}/{max_consecutive_errors}): {e}")

                if consecutive_errors >= max_consecutive_errors:
                    logger.error("🚨 Too many consecutive errors, waiting 60 seconds...")
                    consecutive_errors = 0
                    time.sleep(60)
                else:
                    time.sleep(10)

def main():
    """Main function to run the optimized CSV monitor on Windows"""
    logger.info("🚀 Starting Optimized Facebook Marketplace CSV Monitor")

    # Configuration - look for most recent CSV in Windows Downloads
    downloads_dir = "C:\\Users\\kodysherman\\Downloads"

    if not os.path.exists(downloads_dir):
        logger.error(f"❌ Downloads directory not found: {downloads_dir}")
        return

    # Find the most recent CSV file
    csv_files = []
    for file in os.listdir(downloads_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                csv_files.append((file_path, os.path.getmtime(file_path)))

    if not csv_files:
        logger.error("❌ No CSV files found in Downloads")
        return

    # Use the most recent file
    csv_path = max(csv_files, key=lambda x: x[1])[0]
    logger.info(f"📂 Initial CSV file: {os.path.basename(csv_path)}")

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

    # Start optimized monitoring
    monitor = OptimizedPhoneListingMonitor(csv_path, firebase_config)
    monitor.monitor_csv()

if __name__ == "__main__":
    main()