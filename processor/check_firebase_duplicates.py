#!/usr/bin/env python3
"""
Check for actual duplicates in Firebase database
"""

import requests
import hashlib
from collections import Counter

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

def extract_listing_id_from_link(link):
    """Extract listing ID from Facebook URL"""
    if not link:
        return None

    import re
    match = re.search(r'/item/(\d+)', link)
    if match:
        return match.group(1)
    return None

def generate_listing_hash(listing):
    """Generate unique hash for listing to detect duplicates"""
    link = listing.get('link', '')
    if link:
        listing_id = extract_listing_id_from_link(link)
        if listing_id:
            return hashlib.md5(listing_id.encode()).hexdigest()

    # Fallback
    content = f"{listing.get('title', '')}{listing.get('price', '')}{listing.get('location', '')}"
    return hashlib.md5(content.encode()).hexdigest()

def check_firebase_duplicates():
    print("🔍 Firebase Database Duplicate Analysis")
    print("=" * 60)

    try:
        # Get all listings
        listings_url = f"{firebase_config['databaseURL']}/phone_listings.json?auth={firebase_config['apiKey']}"
        listings_response = requests.get(listings_url, timeout=15)

        if listings_response.status_code != 200 or not listings_response.json():
            print("❌ No listings found in database")
            return

        listings = listings_response.json()
        print(f"📱 Total listings in database: {len(listings)}")

        # Generate hashes and find duplicates
        listing_hashes = {}
        duplicates_by_hash = {}
        listing_id_based = 0
        fallback_based = 0

        for listing_id, listing in listings.items():
            hash_value = generate_listing_hash(listing)
            method = "listing_id" if extract_listing_id_from_link(listing.get('link', '')) else "fallback"

            if method == "listing_id":
                listing_id_based += 1
            else:
                fallback_based += 1

            if hash_value in listing_hashes:
                if hash_value not in duplicates_by_hash:
                    duplicates_by_hash[hash_value] = [listing_hashes[hash_value]]
                duplicates_by_hash[hash_value].append({
                    'id': listing_id,
                    'title': listing.get('title', '')[:50],
                    'price': listing.get('price', ''),
                    'link': listing.get('link', '')[:80],
                    'search_city': listing.get('search_city', 'Unknown'),
                    'found_at': listing.get('found_at', '')
                })
            else:
                listing_hashes[hash_value] = {
                    'id': listing_id,
                    'title': listing.get('title', '')[:50],
                    'price': listing.get('price', ''),
                    'link': listing.get('link', '')[:80],
                    'search_city': listing.get('search_city', 'Unknown'),
                    'found_at': listing.get('found_at', '')
                }

        print(f"📊 Hash Generation Methods:")
        print(f"   Listing ID based: {listing_id_based}")
        print(f"   Fallback based: {fallback_based}")

        print(f"\n🔄 Duplicate Analysis:")
        print(f"   Unique hashes: {len(listing_hashes)}")
        print(f"   Duplicate groups: {len(duplicates_by_hash)}")
        print(f"   Total duplicates: {sum(len(group) - 1 for group in duplicates_by_hash.values())}")

        if duplicates_by_hash:
            print(f"\n🔍 Sample Duplicates (Top 5):")
            for i, (hash_val, group) in enumerate(list(duplicates_by_hash.items())[:5]):
                print(f"\n   {i+1}. Duplicate Group (Hash: {hash_val[:8]}...)")
                for j, listing in enumerate(group):
                    print(f"      {j+1}. {listing['title']}... | ${listing['price']} | {listing['search_city']} | {listing['found_at'][:10]}")
                    print(f"         Link: {listing['link']}...")
                    print(f"         ID: {listing['id']}")

        # Check processed hashes
        hashes_url = f"{firebase_config['databaseURL']}/processed_hashes.json?auth={firebase_config['apiKey']}"
        hashes_response = requests.get(hashes_url, timeout=10)

        if hashes_response.status_code == 200 and hashes_response.json():
            processed_hashes = hashes_response.json()
            print(f"\n🔐 Processed Hashes: {len(processed_hashes)}")

            # Check if processed hashes match our expected hashes
            expected_hashes = set(listing_hashes.keys())
            actual_hashes = set(processed_hashes.keys())

            missing_hashes = expected_hashes - actual_hashes
            extra_hashes = actual_hashes - expected_hashes

            if missing_hashes:
                print(f"⚠️  Missing hashes in processed_hashes: {len(missing_hashes)}")

            if extra_hashes:
                print(f"⚠️  Extra hashes in processed_hashes: {len(extra_hashes)}")

            print(f"✅ Expected hashes match processed_hashes: {len(expected_hashes & actual_hashes)}")

    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_firebase_duplicates()