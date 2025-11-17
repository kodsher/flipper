#!/usr/bin/env python3
"""
Test exact link duplicate detection by simulating the scenario
"""

import requests
import hashlib
from collections import defaultdict

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

def load_existing_links_from_firebase():
    """Load all existing links from Firebase"""
    try:
        print("📥 Loading existing links from Firebase...")
        session = requests.Session()
        url = f"{firebase_config['databaseURL']}/phone_listings.json?auth={firebase_config['apiKey']}"
        response = session.get(url, timeout=15)

        if response.status_code == 200 and response.json():
            listings_data = response.json()
            existing_links = set()
            for listing_id, listing_data in listings_data.items():
                if 'link' in listing_data and listing_data['link']:
                    existing_links.add(listing_data['link'])

            print(f"✅ Loaded {len(existing_links)} existing links from database")
            return existing_links
        else:
            print("ℹ️ No existing listings found in database")
            return set()
    except Exception as e:
        print(f"❌ Error loading existing links: {e}")
        return set()

def simulate_csv_monitor_logic(test_links):
    """Simulate what the CSV monitor should do with test links"""
    existing_links = load_existing_links_from_firebase()

    print(f"\n🧪 Testing {len(test_links)} links against {len(existing_links)} existing links:")

    results = {
        'total': len(test_links),
        'would_be_added': 0,
        'would_be_filtered': 0,
        'new_links': [],
        'duplicate_links': []
    }

    for i, link in enumerate(test_links, 1):
        is_duplicate = link in existing_links

        if is_duplicate:
            results['would_be_filtered'] += 1
            results['duplicate_links'].append({
                'index': i,
                'link': link[:80] + '...',
                'reason': 'Link already exists in database'
            })
            print(f"   {i}. ❌ FILTERED (duplicate): {link[:50]}...")
        else:
            results['would_be_added'] += 1
            results['new_links'].append({
                'index': i,
                'link': link[:80] + '...'
            })
            print(f"   {i}. ✅ WOULD BE ADDED: {link[:50]}...")

    return results

def find_duplicate_links_in_database():
    """Find links that appear multiple times in the current database"""
    try:
        print("🔍 Analyzing current database for duplicate links...")
        session = requests.Session()
        url = f"{firebase_config['databaseURL']}/phone_listings.json?auth={firebase_config['apiKey']}"
        response = session.get(url, timeout=15)

        if response.status_code == 200 and response.json():
            listings_data = response.json()
            link_counts = defaultdict(list)

            for listing_id, listing_data in listings_data.items():
                if 'link' in listing_data and listing_data['link']:
                    link_counts[listing_data['link']].append({
                        'id': listing_id,
                        'title': listing_data.get('title', '')[:50],
                        'price': listing_data.get('price', ''),
                        'search_city': listing_data.get('search_city', '')
                    })

            duplicates = {link: items for link, items in link_counts.items() if len(items) > 1}

            print(f"📊 Database Analysis:")
            print(f"   Total listings: {len(listings_data)}")
            print(f"   Unique links: {len(link_counts)}")
            print(f"   Duplicate links: {len(duplicates)}")

            if duplicates:
                print(f"\n🔄 FOUND {len(duplicates)} DUPLICATE LINKS IN DATABASE:")
                for i, (link, items) in enumerate(list(duplicates.items())[:5], 1):
                    print(f"\n   {i}. Link appears {len(items)} times:")
                    print(f"      {link[:80]}...")
                    for item in items:
                        print(f"         • ID: {item['id']} | {item['title']}... | ${item['price']} | {item['search_city']}")

            return duplicates
        else:
            print("ℹ️ No listings found in database")
            return {}
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return {}

def main():
    print("🔧 Testing Exact Link Duplicate Detection")
    print("=" * 60)

    # First, check if there are already duplicates in the database
    database_duplicates = find_duplicate_links_in_database()

    # Then test the current CSV monitor logic
    print(f"\n" + "="*60)
    print("🧪 Testing CSV Monitor Logic")
    print("="*60)

    # Test with some sample links that should exist in database
    if database_duplicates:
        # Extract a few duplicate links to test
        test_links = []
        for link in list(database_duplicates.keys())[:3]:
            test_links.append(link)

        # Add a fake link that shouldn't exist
        test_links.append("https://www.facebook.com/marketplace/item/9999999999999999/")

        results = simulate_csv_monitor_logic(test_links)

        print(f"\n📊 Results:")
        print(f"   Links tested: {results['total']}")
        print(f"   Would be added: {results['would_be_added']}")
        print(f"   Would be filtered: {results['would_be_filtered']}")

        if results['would_be_filtered'] > 0:
            print(f"\n❌ CSV Monitor Logic WORKING - {results['would_be_filtered']} duplicates would be filtered")
        else:
            print(f"\n⚠️  CSV Monitor Logic NOT WORKING - no duplicates would be filtered")

if __name__ == "__main__":
    main()