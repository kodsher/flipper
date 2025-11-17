#!/usr/bin/env python3
"""
Simple CSV Monitor - Only Link-Based Duplicate Detection
"""

import os
import csv
import time
import hashlib
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleCSVMonitor:
    def __init__(self, firebase_config: Dict):
        self.firebase_config = firebase_config
        self.database_url = firebase_config['databaseURL']
        self.api_key = firebase_config['apiKey']
        self.existing_links = set()
        self.existing_listing_ids = set()  # NEW: Track listing IDs
        self.session = requests.Session()

        # iPhone model detection patterns
        self.iphone_patterns = [
            re.compile(r'iphone\s*(\d+(?:\s*pro)?(?:\s*max)?(?:\s*plus)?(?:\s*air)?)', re.IGNORECASE),
            re.compile(r'iphone\s*(\d+)\s*(pro\s*max|pro|max|plus|air)', re.IGNORECASE),
            re.compile(r'iphone\s*(\d+)(?!\s*(pro|max|plus|air))', re.IGNORECASE)
        ]

        # iPhone variant detection patterns
        self.variant_patterns = [
            # iPhone 17 variants
            re.compile(r'iphone\s*17\s*pro\s*max', re.IGNORECASE),
            re.compile(r'iphone\s*17\s*pro', re.IGNORECASE),
            re.compile(r'iphone\s*17\s*air', re.IGNORECASE),
            re.compile(r'17\s*pro\s*max', re.IGNORECASE),
            re.compile(r'17\s*pro', re.IGNORECASE),
            re.compile(r'17\s*air', re.IGNORECASE),

            # iPhone 16 variants
            re.compile(r'iphone\s*16\s*pro\s*max', re.IGNORECASE),
            re.compile(r'iphone\s*16\s*pro', re.IGNORECASE),
            re.compile(r'iphone\s*16\s*plus', re.IGNORECASE),
            re.compile(r'iphone\s*16\s*e', re.IGNORECASE),
            re.compile(r'16\s*pro\s*max', re.IGNORECASE),
            re.compile(r'16\s*pro', re.IGNORECASE),
            re.compile(r'16\s*plus', re.IGNORECASE),
            re.compile(r'16\s*e', re.IGNORECASE),

            # iPhone 15 variants
            re.compile(r'iphone\s*15\s*pro\s*max', re.IGNORECASE),
            re.compile(r'iphone\s*15\s*pro', re.IGNORECASE),
            re.compile(r'iphone\s*15\s*plus', re.IGNORECASE),
            re.compile(r'15\s*pro\s*max', re.IGNORECASE),
            re.compile(r'15\s*pro', re.IGNORECASE),
            re.compile(r'15\s*plus', re.IGNORECASE),

            # iPhone 14 variants
            re.compile(r'iphone\s*14\s*pro\s*max', re.IGNORECASE),
            re.compile(r'iphone\s*14\s*pro', re.IGNORECASE),
            re.compile(r'iphone\s*14\s*plus', re.IGNORECASE),
            re.compile(r'14\s*pro\s*max', re.IGNORECASE),
            re.compile(r'14\s*pro', re.IGNORECASE),
            re.compile(r'14\s*plus', re.IGNORECASE)
        ]

        # Load existing links and listing IDs at startup
        self._load_existing_links()

    def detect_variant(self, title: str) -> Optional[str]:
        """Detect iPhone variant from title"""
        if not title:
            return None

        title_lower = title.lower()

        # iPhone 17 variants
        if 'iphone 17' in title_lower or ' 17' in title_lower:
            if any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*17\s*pro\s*max', re.IGNORECASE),
                re.compile(r'17\s*pro\s*max', re.IGNORECASE)
            ]):
                return '17_pro_max'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*17\s*pro', re.IGNORECASE),
                re.compile(r'17\s*pro', re.IGNORECASE)
            ]):
                return '17_pro'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*17\s*air', re.IGNORECASE),
                re.compile(r'17\s*air', re.IGNORECASE)
            ]):
                return '17_air'

        # iPhone 16 variants
        if 'iphone 16' in title_lower or ' 16' in title_lower:
            if any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*16\s*pro\s*max', re.IGNORECASE),
                re.compile(r'16\s*pro\s*max', re.IGNORECASE)
            ]):
                return '16_pro_max'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*16\s*pro', re.IGNORECASE),
                re.compile(r'16\s*pro', re.IGNORECASE)
            ]):
                return '16_pro'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*16\s*plus', re.IGNORECASE),
                re.compile(r'16\s*plus', re.IGNORECASE)
            ]):
                return '16_plus'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*16\s*e', re.IGNORECASE),
                re.compile(r'16\s*e', re.IGNORECASE)
            ]):
                return '16_16e'

        # iPhone 15 variants
        if 'iphone 15' in title_lower or ' 15' in title_lower:
            if any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*15\s*pro\s*max', re.IGNORECASE),
                re.compile(r'15\s*pro\s*max', re.IGNORECASE)
            ]):
                return '15_pro_max'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*15\s*pro', re.IGNORECASE),
                re.compile(r'15\s*pro', re.IGNORECASE)
            ]):
                return '15_pro'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*15\s*plus', re.IGNORECASE),
                re.compile(r'15\s*plus', re.IGNORECASE)
            ]):
                return '15_plus'

        # iPhone 14 variants
        if 'iphone 14' in title_lower or ' 14' in title_lower:
            if any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*14\s*pro\s*max', re.IGNORECASE),
                re.compile(r'14\s*pro\s*max', re.IGNORECASE)
            ]):
                return '14_pro_max'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*14\s*pro', re.IGNORECASE),
                re.compile(r'14\s*pro', re.IGNORECASE)
            ]):
                return '14_pro'
            elif any(pattern.search(title) for pattern in [
                re.compile(r'iphone\s*14\s*plus', re.IGNORECASE),
                re.compile(r'14\s*plus', re.IGNORECASE)
            ]):
                return '14_plus'

        return None

    def _load_existing_links(self):
        """Load all existing Facebook marketplace links and listing IDs from database"""
        try:
            url = f"{self.database_url}/phone_listings.json?auth={self.api_key}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200 and response.json():
                listings_data = response.json()
                for listing_id, listing_data in listings_data.items():
                    if 'link' in listing_data and listing_data['link']:
                        self.existing_links.add(listing_data['link'])

                        # Extract and store the listing ID
                        listing_id_from_link = self.extract_listing_id_from_link(listing_data['link'])
                        if listing_id_from_link:
                            self.existing_listing_ids.add(listing_id_from_link)

                logger.info(f"✅ Loaded {len(self.existing_links)} existing links from database")
                logger.info(f"✅ Loaded {len(self.existing_listing_ids)} existing listing IDs")
            else:
                logger.info("ℹ️ No existing listings found in database")

        except Exception as e:
            logger.error(f"❌ Error loading existing links: {e}")

    def extract_listing_id_from_link(self, link: str) -> str:
        """Extract Facebook listing ID from marketplace URL"""
        if not link:
            return ""

        # Extract the ID from /item/{id}/ pattern
        import re
        match = re.search(r'/item/(\d+)', link)
        if match:
            return match.group(1)
        return ""

    def is_duplicate_by_link(self, link: str) -> bool:
        """Check if listing ID is already in the database"""
        if not link:
            return False

        listing_id = self.extract_listing_id_from_link(link)
        if not listing_id:
            return False

        # Check if we've seen this listing ID before
        return listing_id in self.existing_listing_ids

    def extract_model_from_title(self, title: str) -> str:
        """Extract phone, tablet, and computer model from title"""
        if not title:
            return ""

        title_lower = title.lower()

        # MacBook models
        if 'macbook' in title_lower:
            if 'macbook air' in title_lower:
                if 'm3' in title_lower:
                    return 'MacBook Air M3'
                elif 'm2' in title_lower:
                    return 'MacBook Air M2'
                elif 'm1' in title_lower:
                    return 'MacBook Air M1'
                elif '2020' in title_lower:
                    return 'MacBook Air 2020'
                elif '2019' in title_lower:
                    return 'MacBook Air 2019'
                elif '2018' in title_lower:
                    return 'MacBook Air 2018'
                else:
                    return 'MacBook Air'
            elif 'macbook pro' in title_lower:
                if '16"' in title_lower or '16 inch' in title_lower:
                    if 'm3' in title_lower:
                        return 'MacBook Pro 16" M3'
                    elif 'm2' in title_lower:
                        return 'MacBook Pro 16" M2'
                    elif 'm1' in title_lower:
                        return 'MacBook Pro 16" M1'
                    else:
                        return 'MacBook Pro 16"'
                elif '14"' in title_lower or '14 inch' in title_lower:
                    if 'm3' in title_lower:
                        return 'MacBook Pro 14" M3'
                    elif 'm2' in title_lower:
                        return 'MacBook Pro 14" M2'
                    elif 'm1' in title_lower:
                        return 'MacBook Pro 14" M1'
                    else:
                        return 'MacBook Pro 14"'
                elif '13"' in title_lower or '13 inch' in title_lower:
                    if 'm3' in title_lower:
                        return 'MacBook Pro 13" M3'
                    elif 'm2' in title_lower:
                        return 'MacBook Pro 13" M2'
                    elif 'm1' in title_lower:
                        return 'MacBook Pro 13" M1'
                    else:
                        return 'MacBook Pro 13"'
                else:
                    return 'MacBook Pro'
            else:
                return 'MacBook'

        # iPad models
        elif 'ipad' in title_lower:
            if 'ipad pro' in title_lower:
                if '12.9' in title_lower or '12 9' in title_lower:
                    return 'iPad Pro 12.9"'
                elif '11' in title_lower:
                    return 'iPad Pro 11"'
                else:
                    return 'iPad Pro'
            elif 'ipad air' in title_lower:
                if 'm2' in title_lower:
                    return 'iPad Air M2'
                elif 'm1' in title_lower:
                    return 'iPad Air M1'
                else:
                    return 'iPad Air'
            elif 'ipad mini' in title_lower:
                return 'iPad Mini'
            elif '9th' in title_lower or '9 ' in title_lower:
                return 'iPad 9th Gen'
            elif '8th' in title_lower or '8 ' in title_lower:
                return 'iPad 8th Gen'
            elif '10th' in title_lower or '10 ' in title_lower:
                return 'iPad 10th Gen'
            else:
                return 'iPad'

        # iPhone models
        elif 'iphone' in title_lower:
            # Try each pattern in order
            for pattern in self.iphone_patterns:
                match = pattern.search(title_lower)
                if match:
                    model = f"iPhone {match.group(1).upper()}"
                    return model
            return ""

        return ""

    def extract_iphone_model(self, title: str) -> str:
        """Legacy method - use extract_model_from_title instead"""
        return self.extract_model_from_title(title)

    def extract_search_city_from_filename(self, file_path: str) -> str:
        """Extract search city from CSV filename"""
        filename = os.path.basename(file_path)

        # Remove file extension
        base_name = filename.replace('.csv', '')

        # Special numeric to city mapping (same as other scripts)
        numeric_city_mapping = {
            '361': 'corpus christi',  # Corpus Christi area code
            '103103056397247': 'corpus christi',  # Corpus christi base identifier
            'cc': 'corpus christi',   # CC abbreviation
            'corpus': 'corpus christi',  # Partial match
        }

        # Check if the base_name contains any of our mapped numbers/patterns
        for number_pattern, city_name in numeric_city_mapping.items():
            if number_pattern in base_name.lower():
                return city_name

        # Use regex to match text at the beginning before any numbers
        import re
        match = re.match(r'^([a-zA-Z]+)', base_name)

        if match:
            city = match.group(1).lower()
            # Map to proper city names
            city_mapping = {
                'houston': 'Houston',
                'austin': 'Austin',
                'dallas': 'Dallas',
                'corpus': 'corpus christi'
            }
            return city_mapping.get(city, city.title())
        else:
            # Fallback: check for specific text patterns
            filename_lower = filename.lower()
            if 'houston' in filename_lower:
                return 'Houston'
            elif 'austin' in filename_lower:
                return 'Austin'
            elif 'corpuschristi' in filename_lower:
                return 'Corpus Christi'
            elif 'dallas' in filename_lower:
                return 'Dallas'
            else:
                return 'Unknown'

    def process_csv_file(self, file_path: str) -> List[Dict]:
        """Process CSV file with simple link-based duplicate checking"""
        new_listings = []
        total_rows = 0
        duplicates_filtered = 0

        search_city = self.extract_search_city_from_filename(file_path)
        logger.info(f"📂 Processing: {os.path.basename(file_path)} (City: {search_city})")

        try:
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
                        if duplicates_filtered <= 5:  # Show first 5 filtered items
                            logger.info(f"🔄 FILTERED DUPLICATE: {title[:40]}...")
                        continue

                    # Extract model (iPhone, iPad, MacBook)
                    model = self.extract_model_from_title(title)

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

                    # Add model if detected
                    if model:
                        listing['model'] = model

                    # Add variant if detected
                    variant = self.detect_variant(title)
                    if variant:
                        listing['variant'] = variant

                    # Generate hash for tracking
                    listing['hash'] = hashlib.md5(link.encode()).hexdigest()
                    new_listings.append(listing)

        except Exception as e:
            logger.error(f"❌ Error processing CSV: {e}")

        logger.info(f"📊 Results: {total_rows} total rows, {len(new_listings)} new listings, {duplicates_filtered} duplicates filtered")
        return new_listings

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

                    # Also add the listing ID to prevent duplicates
                    listing_id_from_link = self.extract_listing_id_from_link(listing['link'])
                    if listing_id_from_link:
                        self.existing_listing_ids.add(listing_id_from_link)

            logger.info(f"✅ Saved {saved_count}/{len(listings)} listings to Firebase")
            return saved_count > 0

        except Exception as e:
            logger.error(f"❌ Error saving to Firebase: {e}")
            return False


def monitor_continuously():
    """Run CSV monitor continuously, watching for new CSV files"""
    firebase_config = {
        "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
        "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
    }

    downloads_dir = os.path.expanduser("~/Downloads")
    start_time = time.time()
    processed_files = set()  # Track processed files to avoid reprocessing
    monitor = SimpleCSVMonitor(firebase_config)

    logger.info("🚀 Starting Continuous CSV Monitor")
    logger.info("📍 Watching folder: ~/Downloads")
    logger.info("🔄 Will process CSV files downloaded after startup")
    logger.info("⏹️  Press Ctrl+C to stop monitoring")

    try:
        # Continuous monitoring loop - start immediately, no existing file processing
        while True:
            try:
                # Look for CSV files with modification times after script start
                csv_files = []
                for file in os.listdir(downloads_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(downloads_dir, file)
                        if os.path.isfile(file_path):
                            mtime = os.path.getmtime(file_path)
                            # Only include files downloaded after script started
                            if mtime >= start_time:
                                csv_files.append((file_path, mtime))

                if csv_files:
                    # Sort by modification time, newest first
                    csv_files.sort(key=lambda x: x[1], reverse=True)
                    logger.info(f"📁 Found {len(csv_files)} CSV files downloaded since startup")

                    # Process files that haven't been processed yet
                    for csv_path, mtime in csv_files:
                        file_key = (csv_path, mtime)

                        if file_key not in processed_files:
                            logger.info(f"🆕 Detected new CSV: {os.path.basename(csv_path)} (downloaded {time.ctime(mtime)})")

                            # Add small delay to ensure file is fully downloaded
                            time.sleep(2)

                            # Process the file
                            new_listings = monitor.process_csv_file(csv_path)

                            # Save to Firebase if we have new listings
                            if new_listings:
                                success = monitor.save_to_firebase(new_listings)
                                if success:
                                    logger.info(f"🎉 Successfully processed {len(new_listings)} new listings!")
                                else:
                                    logger.error("❌ Failed to save listings to Firebase")
                            else:
                                logger.info("ℹ️ No new listings to save (all were duplicates)")

                            # Mark as processed
                            processed_files.add(file_key)

                # Wait before checking again
                time.sleep(5)  # Check every 5 seconds

            except KeyboardInterrupt:
                logger.info("\n👋 Stopping CSV monitor...")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                logger.info("⏳ Continuing monitoring in 10 seconds...")
                time.sleep(10)

    except Exception as e:
        logger.error(f"❌ Fatal error in CSV monitor: {e}")

def main():
    """Main entry point"""
    logger.info("🔍 Continuous Facebook Marketplace CSV Monitor")
    logger.info("=" * 60)
    logger.info("This script will:")
    logger.info("1. Watch ~/Downloads folder for NEW CSV files only")
    logger.info("2. Process CSV files downloaded AFTER script starts")
    logger.info("3. Filter out duplicates by Facebook marketplace link")
    logger.info("4. Save new listings to Firebase database")
    logger.info("5. Continue monitoring indefinitely")
    logger.info("⚠️  Existing CSV files in Downloads will be IGNORED")
    logger.info("=" * 60)

    monitor_continuously()


if __name__ == "__main__":
    main()