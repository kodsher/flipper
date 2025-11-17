#!/usr/bin/env python3
"""
Optimized Facebook Marketplace CSV Monitor for Mac
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
from functools import lru_cache

# Configure logging - reduce to INFO for better performance
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for better performance
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedPhoneListingMonitor:
    def __init__(self, csv_path: str, firebase_config: Dict):
        self.csv_path = csv_path
        self.processed_hashes: Set[str] = set()
        self.existing_links: Set[str] = set()  # Store existing Facebook marketplace links
        self.firebase_config = firebase_config
        self.batch_size = 1000  # Increased batch size for better efficiency
        self.start_time = time.time()  # Track when script started

        # Initialize Firebase REST API
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']

        # Optimized HTTP session with better performance settings
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,  # Reduced retries for speed
            backoff_factor=0.5,  # Faster backoff
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,  # More connections
            pool_maxsize=50,      # Larger pool
            pool_block=False
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Load previously processed listings
        self._load_processed_listings()
        # Load existing Facebook marketplace links for duplicate detection
        self._load_existing_links()

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

    def _load_existing_links(self):
        """Load all existing Facebook marketplace links from database"""
        try:
            logger.info("📥 Loading existing Facebook marketplace links from database...")
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200 and response.json():
                listings_data = response.json()
                for listing_id, listing_data in listings_data.items():
                    if 'link' in listing_data and listing_data['link']:
                        self.existing_links.add(listing_data['link'])

                logger.info(f"✅ Loaded {len(self.existing_links)} existing Facebook links")
            else:
                logger.info("ℹ️ No existing listings found in database")

        except Exception as e:
            logger.error(f"❌ Error loading existing links: {e}")
            logger.info("ℹ️ Proceeding without existing link data (may cause duplicates)")

    def is_link_already_in_database(self, link: str) -> bool:
        """Check if a Facebook marketplace link already exists in the database"""
        if not link:
            return False
        return link in self.existing_links

    def _is_duplicate_in_firebase(self, listing_hash: str) -> bool:
        """Simplified duplicate check - now mainly for processed_hashes compatibility"""
        # For backwards compatibility with processed_hashes
        return listing_hash in self.processed_hashes

    def _batch_check_duplicates(self, hashes: List[str]) -> Dict[str, bool]:
        """Batch check duplicates - simplified since we use link-based checking"""
        # For backwards compatibility - mainly check processed_hashes
        results = {}
        for hash_val in hashes:
            results[hash_val] = hash_val in self.processed_hashes
        return results

    def _extract_search_city_from_filename(self, file_path: str) -> str:
        """Extract search city from CSV filename"""
        filename = os.path.basename(file_path).lower()

        # Extract city name from various filename patterns
        import re

        # Patterns to try in order:
        city_patterns = [
            # Pattern 1: City name with numbers (houston262.csv, austin182.csv)
            r'(houston|austin|dallas|sanantonio|fortworth|elpaso|arlington|corpuschristi|plano|garland)(\d+)',

            # Pattern 2: City name explicitly mentioned anywhere in filename
            r'(houston|austin|dallas|san.?antonio|fort.?worth|elpaso|arlington|corpus.?christi|plano|garland)',
        ]

        for pattern in city_patterns:
            match = re.search(pattern, filename)
            if match:
                city = match.group(1)
                # Clean up common city name issues
                if city in ['sanantonio', 'san.?antonio']:
                    city = 'San Antonio'
                elif city in ['fortworth', 'fort.?worth']:
                    city = 'Fort Worth'
                elif city in ['corpuschristi', 'corpus.?christi']:
                    city = 'Corpus Christi'
                else:
                    # Capitalize properly
                    city = city.capitalize()

                logger.info(f"🏙️ Extracted search city from filename: {city}")
                return city

        # If no city found, try to infer from recent files or ask for manual input
        # For now, return 'Unknown' - this will be a separate category in the UI
        logger.info(f"🏙️ Could not extract search city from filename: {filename} - using 'Unknown'")
        return 'Unknown'

    @lru_cache(maxsize=1000)
    def _extract_phone_model(self, title: str) -> Optional[str]:
        """Extract iPhone model from title - optimized with caching"""
        if not title:
            return 'Unknown'

        title_lower = title.lower()

        # Fast pattern matching without debug logging
        for i, pattern in enumerate(self.iphone_patterns):
            match = pattern.search(title)
            if match:
                model = f"iPhone {match.group(1).upper()}"

                # Add common suffixes efficiently
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
        """Extract price from price string - optimized"""
        try:
            if not price_str:
                return None

            # Remove currency symbols, commas, and convert to float
            clean_price = re.sub(r'[^\d.]', '', str(price_str))

            if clean_price:
                price = float(clean_price)
                if self.min_price <= price <= self.max_price:
                    return price

        except (ValueError, TypeError):
            pass

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

            # Extract price
            price = self._extract_price(price_str)
            if not price or price <= 0:
                return None

            # Extract phone model (optional - for categorization but not filtering)
            model = self._extract_phone_model(title)
            if model == 'Unknown':
                model = 'General Item'  # Categorize non-phone items as General Items

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

            # Check if duplicate (only filter actual duplicates)
            is_duplicate = self._is_duplicate_in_firebase(listing_hash)
            if is_duplicate:
                return None

            return listing

        except Exception as e:
            logger.error(f"❌ Error processing row: {e}")
            return None

    def _save_batch_to_firebase(self, listings: List[Dict]) -> bool:
        """Save multiple listings to Firebase in batch - optimized with more workers"""
        try:
            # Firebase doesn't support REST batch operations directly,
            # so we'll use parallel requests instead
            success_count = 0
            successful_hashes = []

            def save_single_listing(listing):
                try:
                    url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
                    response = self.session.post(url, json=listing, timeout=2)  # Faster timeout
                    if response.status_code == 200:
                        return True, listing['hash']
                    return False, listing['hash']
                except Exception:
                    return False, listing['hash']

            # Process listings in parallel with more workers
            with ThreadPoolExecutor(max_workers=30) as executor:  # Increased workers
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
        """Process entire CSV file efficiently with link-based duplicate checking"""
        try:
            new_listings = []
            total_rows = 0
            duplicates_skipped = 0

            # Extract search city from filename
            search_city = self._extract_search_city_from_filename(file_path)
            logger.info(f"📂 Opening CSV file: {file_path} (Search City: {search_city})")

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                reader = csv.DictReader(file)

                # Log the headers to understand the CSV structure
                headers = reader.fieldnames
                logger.info(f"📋 CSV Headers: {headers}")

                # Process rows with direct link duplicate checking
                for i, row in enumerate(reader):
                    total_rows += 1

                    # Process with direct duplicate check
                    listing = self._process_listing_with_link_check(row, search_city)
                    if listing:
                        new_listings.append(listing)
                    elif total_rows % 50 == 0:  # Progress update every 50 rows
                        logger.debug(f"Processed {total_rows} rows...")

            logger.info(f"📊 CSV Summary: {total_rows} total rows, {len(new_listings)} new listings")
            if duplicates_skipped > 0:
                logger.info(f"🔄 Skipped {duplicates_skipped} duplicates")
            logger.info(f"🎯 Acceptance rate: {len(new_listings)/total_rows*100:.1f}% ({len(new_listings)}/{total_rows})")
            return new_listings

        except Exception as e:
            logger.error(f"❌ Error processing CSV file {file_path}: {e}")
            return []

    def _process_listing_with_link_check(self, row: Dict, search_city: str) -> Optional[Dict]:
        """Process a single CSV row with link-based duplicate checking"""
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

            # CHECK FOR DUPLICATE BY LINK FIRST
            if self.is_link_already_in_database(link):
                logger.debug(f"🔄 Skipping duplicate: {title[:50]}... (link already exists)")
                return None

            # Extract phone model (optional - for categorization but not filtering)
            model = self._extract_phone_model(title)
            if model == 'Unknown':
                model = 'General Item'  # Categorize non-phone items as General Items

            # Create listing object
            listing = {
                'title': title,
                'price': price,
                'model': model,
                'location': location,
                'link': link,
                'search_city': search_city,  # Add search city from filename
                'source': 'facebook_marketplace',
                'found_at': datetime.now().isoformat(),
                'detected_at': datetime.now().isoformat()
            }

            # Generate hash for processed_hashes tracking
            listing_hash = self._generate_listing_hash(listing)
            listing['hash'] = listing_hash

            logger.debug(f"✅ New listing: {title[:50]}...")
            return listing

        except Exception as e:
            logger.error(f"❌ Error processing row: {e}")
            return None

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

                # Check for the most recent file in Mac Downloads folder
                downloads_dir = os.path.expanduser("~/Downloads")

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

                # Only process if we have a new file or the same file was updated AFTER script started
                if (current_file != self.last_processed_file or
                    current_time > self.last_processed_time + 5) and current_time > self.start_time:  # Only process files downloaded after script start

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
                time.sleep(2)  # Faster checking

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
    """Main function to run the optimized CSV monitor on Mac"""
    logger.info("🚀 Starting Optimized Facebook Marketplace CSV Monitor")

    # Configuration - look for most recent CSV in Mac Downloads
    downloads_dir = os.path.expanduser("~/Downloads")

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