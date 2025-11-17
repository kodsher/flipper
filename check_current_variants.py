#!/usr/bin/env python3
"""
Check current variant data in the database to debug filtering issue
"""

import requests
import json

def main():
    print("🔍 Checking Current Variant Data in Database")
    print("=" * 50)

    # Firebase config
    database_url = "https://phone-flipping-default-rtdb.firebaseio.com"
    api_key = "AIzaSyD0Z3tQrP2YcGj3xRxBpHzHhEwC_VP6u_Q"

    try:
        response = requests.get(f"{database_url}/phone_listings.json?auth={api_key}", timeout=30)

        if response.status_code != 200:
            print(f"❌ Error fetching data: {response.status_code}")
            return

        data = response.json()
        if not data:
            print("❌ No data found")
            return

        listings = []
        for listing_id, listing_data in data.items():
            listings.append({
                'id': listing_id,
                **listing_data
            })

        print(f"✅ Found {len(listings)} total listings")

        # Find iPhone 17 listings with variants
        iphone_17_variants = {}
        for listing in listings:
            model = listing.get('model', '')
            variant = listing.get('variant', '')

            # Check if it's an iPhone 17 listing
            is_iphone17 = model and 'iphone 17' in model.lower()
            variant_starts_with_17 = variant and str(variant).startswith('17')

            if is_iphone17 or variant_starts_with_17:
                title = listing.get('title', '')[:50]
                if variant not in iphone_17_variants:
                    iphone_17_variants[variant] = []
                iphone_17_variants[variant].append(title)

        print(f"\n📱 iPhone 17 Variants Found:")
        for variant, titles in sorted(iphone_17_variants.items()):
            print(f"  {variant}: {len(titles)} listings")
            if len(titles) <= 3:
                for title in titles:
                    print(f"    - {title}")
            else:
                print(f"    - {titles[0]}")
                print(f"    - {titles[1]}")
                print(f"    - {titles[2]}")
                print(f"    ... and {len(titles) - 3} more")
            print()

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()