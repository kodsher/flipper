#!/usr/bin/env python3
"""
Apply enhanced variant detection to all iPhone listings
"""

import requests
import json

def enhanced_detect_variant(title, model):
    """Enhanced iPhone variant detection"""
    if not title or not model:
        return None

    title_lower = title.lower()
    model_lower = model.lower()

    # Only process iPhones
    if 'iphone' not in model_lower:
        return None

    # iPhone 17 variants
    if 'iphone 17' in title_lower or ' 17 ' in title_lower or model_lower == 'iphone 17':
        if 'pro max' in title_lower or '17 pro max' in title_lower:
            return '17_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '17_pro'
        if 'air' in title_lower:
            return '17_air'
        if 'se' in title_lower or 'standard' in title_lower:
            return '17_se'
        # If just iPhone 17, categorize as base model
        if 'iphone 17' in title_lower and not any(x in title_lower for x in ['pro', 'air', 'se', 'plus', 'max']):
            return '17_base'

    # iPhone 16 variants
    if 'iphone 16' in title_lower or ' 16 ' in title_lower or 'iphone 16' in model_lower:
        if 'pro max' in title_lower or '16 pro max' in title_lower:
            return '16_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '16_pro'
        if 'plus' in title_lower:
            return '16_plus'
        if '16e' in title_lower or '16 e' in title_lower or 'se' in title_lower:
            return '16_16e'
        # If just iPhone 16, categorize as base model
        if 'iphone 16' in title_lower and not any(x in title_lower for x in ['pro', 'plus', '16e', 'se', 'max']):
            return '16_base'

    # iPhone 15 variants
    if 'iphone 15' in title_lower or ' 15 ' in title_lower or 'iphone 15' in model_lower:
        if 'pro max' in title_lower or '15 pro max' in title_lower:
            return '15_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '15_pro'
        if 'plus' in title_lower:
            return '15_plus'
        # If just iPhone 15, categorize as base model
        if 'iphone 15' in title_lower and not any(x in title_lower for x in ['pro', 'plus', 'max']):
            return '15_base'

    # iPhone 14 variants
    if 'iphone 14' in title_lower or ' 14 ' in title_lower or 'iphone 14' in model_lower:
        if 'pro max' in title_lower or '14 pro max' in title_lower:
            return '14_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '14_pro'
        if 'plus' in title_lower:
            return '14_plus'
        if 'mini' in title_lower:
            return '14_mini'
        # If just iPhone 14, categorize as base model
        if 'iphone 14' in title_lower and not any(x in title_lower for x in ['pro', 'plus', 'max', 'mini']):
            return '14_base'

    # iPhone 13 variants
    if 'iphone 13' in title_lower or ' 13 ' in title_lower or 'iphone 13' in model_lower:
        if 'pro max' in title_lower or '13 pro max' in title_lower:
            return '13_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '13_pro'
        if 'plus' in title_lower:
            return '13_plus'
        if 'mini' in title_lower:
            return '13_mini'
        # If just iPhone 13, categorize as base model
        if 'iphone 13' in title_lower and not any(x in title_lower for x in ['pro', 'plus', 'max', 'mini']):
            return '13_base'

    # iPhone 12 variants
    if 'iphone 12' in title_lower or ' 12 ' in title_lower or 'iphone 12' in model_lower:
        if 'pro max' in title_lower or '12 pro max' in title_lower:
            return '12_pro_max'
        if 'pro' in title_lower and 'pro max' not in title_lower:
            return '12_pro'
        if 'plus' in title_lower:
            return '12_plus'
        if 'mini' in title_lower:
            return '12_mini'
        # If just iPhone 12, categorize as base model
        if 'iphone 12' in title_lower and not any(x in title_lower for x in ['pro', 'plus', 'max', 'mini']):
            return '12_base'

    return None

def main():
    print("🔧 Applying Enhanced iPhone Variant Labels")
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
                detected_variant = enhanced_detect_variant(
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

                    print(f"🎯 {listing['title'][:60]}{'...' if len(listing['title']) > 60 else ''}")
                    print(f"   Model: {listing.get('model', '')}")
                    print(f"   Old Variant: {existing_variant or 'None'}")
                    print(f"   New Variant: {detected_variant}")
                    print()

        print(f"📊 Found {update_count} iPhone listings to update with variants")

        if updates:
            print("📤 Updating database with enhanced variants...")
            update_response = requests.patch(
                f"{database_url}/.json?auth={api_key}",
                json=updates,
                timeout=60
            )

            if update_response.status_code == 200:
                print(f"✅ Successfully updated {update_count} listings!")

                print(f"\n📊 Variant Update Summary:")
                for variant, count in sorted(variant_summary.items()):
                    print(f"  {variant}: {count} listings")

                print(f"\n🎉 Enhanced variant data has been added to the database!")
                print(f"🔍 Check http://localhost:8000 to see the updated variant column!")
            else:
                print(f"❌ Error updating database: {update_response.status_code}")
                print(f"Response: {update_response.text}")
        else:
            print("ℹ️ No new variant data to add - all listings already have correct variants")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()