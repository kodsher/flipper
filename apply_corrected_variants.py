#!/usr/bin/env python3
"""
Apply corrected variant detection rules to all iPhone listings
"""

import requests
import json

def corrected_detect_variant(title, model):
    """Corrected iPhone variant detection"""
    if not title or not model:
        return None

    title_lower = title.lower()
    model_lower = model.lower()

    # Only process iPhones
    if not model_lower or 'iphone' not in model_lower:
        return None

    # iPhone 17 variants
    if 'iphone 17' in title_lower:
        if 'pro max' in title_lower or '17 pro max' in title_lower:
            return '17_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '17_pro'
        if 'air' in title_lower:
            return '17_air'
        # Regular iPhone 17 (no specific variant mentioned)
        if not ('pro' in title_lower or 'air' in title_lower or 'max' in title_lower):
            return '17'

    # iPhone 16 variants
    if 'iphone 16' in title_lower:
        if 'pro max' in title_lower or '16 pro max' in title_lower:
            return '16_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '16_pro'
        if 'plus' in title_lower:
            return '16_plus'
        if '16e' in title_lower or '16 e' in title_lower:
            return '16_16e'
        # Regular iPhone 16 (no specific variant mentioned)
        if not ('pro' in title_lower or 'plus' in title_lower or '16e' in title_lower or 'max' in title_lower):
            return '16'

    # iPhone 15 variants
    if 'iphone 15' in title_lower:
        if 'pro max' in title_lower or '15 pro max' in title_lower:
            return '15_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '15_pro'
        if 'plus' in title_lower:
            return '15_plus'
        # Regular iPhone 15 (no specific variant mentioned)
        if not ('pro' in title_lower or 'plus' in title_lower or 'max' in title_lower):
            return '15'

    # iPhone 14 variants
    if 'iphone 14' in title_lower:
        if 'pro max' in title_lower or '14 pro max' in title_lower:
            return '14_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '14_pro'
        if 'plus' in title_lower:
            return '14_plus'
        # Regular iPhone 14 (no specific variant mentioned)
        if not ('pro' in title_lower or 'plus' in title_lower or 'max' in title_lower):
            return '14'

    # iPhone 13 and older - all categorized as "older_model"
    if ('iphone 13' in title_lower or 'iphone 12' in title_lower or
        'iphone 11' in title_lower or 'iphone x' in title_lower or
        'iphone 10' in title_lower or 'iphone 8' in title_lower or
        'iphone 7' in title_lower or 'iphone 6' in title_lower or
        'iphone 5' in title_lower or 'iphone 4' in title_lower):
        return 'older_model'

    return None

def main():
    print("🔧 Applying Corrected iPhone Variant Labels")
    print("=" * 60)

    # Firebase config
    database_url = "https://phone-flipping-default-rtdb.firebaseio.com"
    api_key = "AIzaSyD0Z3tQrP2YcGj3xRxBpHzHhEwC_VP6u_Q"

    try:
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

        # Find iPhone listings that need variant updates
        updates = {}
        update_count = 0
        variant_summary = {}

        for listing in listings:
            model = listing.get('model', '').lower()
            if 'iphone' in model:
                detected_variant = corrected_detect_variant(
                    listing.get('title', ''),
                    listing.get('model', '')
                )
                existing_variant = listing.get('variant')

                # Update if we detected a variant and it's different from existing
                if detected_variant and detected_variant != existing_variant:
                    updates[f"phone_listings/{listing['id']}/variant"] = detected_variant
                    update_count += 1

                    # Track variant statistics
                    if detected_variant not in variant_summary:
                        variant_summary[detected_variant] = 0
                    variant_summary[detected_variant] += 1

                    if update_count <= 20:  # Show first 20 examples
                        print(f"🎯 {listing['title'][:60]}{'...' if len(listing['title']) > 60 else ''}")
                        print(f"   Model: {listing.get('model', '')}")
                        print(f"   Old Variant: {existing_variant or 'None'}")
                        print(f"   New Variant: {detected_variant}")
                        print()

        print(f"📊 Found {update_count} iPhone listings to update with corrected variants")

        if updates:
            print("📤 Updating database with corrected variants...")
            update_response = requests.patch(
                f"{database_url}/.json?auth={api_key}",
                json=updates,
                timeout=60
            )

            if update_response.status_code == 200:
                print(f"✅ Successfully updated {update_count} listings!")

                print(f"\n📊 Corrected Variant Update Summary:")
                for variant, count in sorted(variant_summary.items()):
                    print(f"  {variant}: {count} listings")

                print(f"\n🎉 Corrected variant data has been applied to the database!")
                print(f"🔍 Check http://localhost:8000 to see the updated variant column!")
                print(f"💡 Key changes:")
                print(f"   - iPhone 13+ → 'Older Model'")
                print(f"   - Regular models → Generation numbers (17, 16, 15, 14)")
                print(f"   - No more generation headings above variants")
            else:
                print(f"❌ Error updating database: {update_response.status_code}")
                print(f"Response: {update_response.text}")
        else:
            print("ℹ️ No new variant data to add - all listings already have correct variants")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()