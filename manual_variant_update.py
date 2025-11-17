#!/usr/bin/env python3
"""
Manual script to add variant data to existing iPhone listings
"""

import requests
import re
import json

def detect_variant(title):
    """Detect iPhone variant from title"""
    if not title:
        return None

    lower_title = title.lower()

    # iPhone 16 variants
    if 'iphone 16' in lower_title:
        if 'pro max' in lower_title or '16 pro max' in lower_title:
            return '16_pro_max'
        if 'pro' in lower_title or '16 pro' in lower_title:
            return '16_pro'
        if 'plus' in lower_title or '16 plus' in lower_title:
            return '16_plus'
        if '16e' in lower_title or '16 e' in lower_title:
            return '16_16e'

    # iPhone 15 variants
    if 'iphone 15' in lower_title:
        if 'pro max' in lower_title or '15 pro max' in lower_title:
            return '15_pro_max'
        if 'pro' in lower_title or '15 pro' in lower_title:
            return '15_pro'
        if 'plus' in lower_title or '15 plus' in lower_title:
            return '15_plus'

    # iPhone 14 variants
    if 'iphone 14' in lower_title:
        if 'pro max' in lower_title or '14 pro max' in lower_title:
            return '14_pro_max'
        if 'pro' in lower_title or '14 pro' in lower_title:
            return '14_pro'
        if 'plus' in lower_title or '14 plus' in lower_title:
            return '14_plus'

    return None

def main():
    print("🔧 Manual Variant Data Update")
    print("=" * 50)

    # Firebase config
    database_url = "https://phone-flipping-default-rtdb.firebaseio.com"
    api_key = "AIzaSyD0Z3tQrP2YcGj3xRxBpHzHhEwC_VP6u_Q"

    try:
        # Fetch all phone listings
        print("📥 Fetching phone listings...")
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

        # Find iPhone listings that need variants
        updates = {}
        iphone_listings = []

        for listing in listings:
            model = listing.get('model', '').lower()
            if 'iphone' in model and not listing.get('variant'):
                iphone_listings.append(listing)

        print(f"📱 Found {len(iphone_listings)} iPhone listings without variants")

        # Detect variants for iPhone listings
        for listing in iphone_listings:
            variant = detect_variant(listing.get('title', ''))
            if variant:
                updates[f"phone_listings/{listing['id']}/variant"] = variant
                print(f"🎯 {listing['title']} → {variant}")

        print(f"\n📊 Found variants for {len(updates)} listings")

        if updates:
            print("📤 Updating database...")
            update_response = requests.patch(
                f"{database_url}/.json?auth={api_key}",
                json=updates,
                timeout=30
            )

            if update_response.status_code == 200:
                print(f"✅ Successfully updated {len(updates)} listings!")
                print("🎉 Variant data has been added to the database")
            else:
                print(f"❌ Error updating database: {update_response.status_code}")
                print(f"Response: {update_response.text}")
        else:
            print("ℹ️ No variants to add")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()