#!/usr/bin/env python3
"""
Check current Firebase database contents
"""

import requests
from collections import Counter

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAJ788FI8Q_oU8GHJLTeW7t1cuTissy4Ss",
    "databaseURL": "https://phone-flipping-default-rtdb.firebaseio.com",
}

def check_database():
    print("📊 Firebase Database Contents")
    print("=" * 50)

    try:
        # Check phone listings
        listings_url = f"{firebase_config['databaseURL']}/phone_listings.json?auth={firebase_config['apiKey']}"
        listings_response = requests.get(listings_url, timeout=10)

        if listings_response.status_code == 200 and listings_response.json():
            listings = listings_response.json()
            print(f"📱 Total listings in database: {len(listings)}")

            # Count by search city
            search_cities = []
            models = []
            for listing_id, listing in listings.items():
                search_cities.append(listing.get('search_city', 'Unknown'))
                models.append(listing.get('model', 'Unknown'))

            search_city_counts = Counter(search_cities)
            model_counts = Counter(models)

            print(f"\n🏙️ Listings by Search City:")
            for city, count in search_city_counts.most_common():
                print(f"   {city}: {count}")

            print(f"\n📱 Listings by Model (Top 10):")
            for model, count in model_counts.most_common(10):
                print(f"   {model}: {count}")

        else:
            print("❌ No listings found in database")

        # Check processed hashes
        hashes_url = f"{firebase_config['databaseURL']}/processed_hashes.json?auth={firebase_config['apiKey']}"
        hashes_response = requests.get(hashes_url, timeout=10)

        if hashes_response.status_code == 200 and hashes_response.json():
            hashes = hashes_response.json()
            print(f"\n🔐 Total processed hashes: {len(hashes)}")
        else:
            print("\n❌ No processed hashes found")

    except Exception as e:
        print(f"❌ Error checking database: {e}")

    print(f"\n🔗 Dashboard URL: http://localhost:3000")
    print(f"🔗 Firebase Console: https://console.firebase.google.com/project/phone-flipping/database")

if __name__ == "__main__":
    check_database()