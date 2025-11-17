#!/usr/bin/env python3
"""
Enhanced variant detection with more comprehensive patterns
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
    print("🔧 Enhanced iPhone Variant Analysis")
    print("=" * 50)

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

        # Analyze iPhone listings
        iphone_listings = []
        variant_stats = {}
        base_model_stats = {}

        for listing in listings:
            model = listing.get('model', '').lower()
            if 'iphone' in model:
                iphone_listings.append(listing)
                detected_variant = enhanced_detect_variant(
                    listing.get('title', ''),
                    listing.get('model', '')
                )
                existing_variant = listing.get('variant')

                # Track variant statistics
                if detected_variant:
                    if detected_variant not in variant_stats:
                        variant_stats[detected_variant] = {'detected': 0, 'existing': 0, 'new': 0}
                    variant_stats[detected_variant]['detected'] += 1

                if existing_variant:
                    if existing_variant not in variant_stats:
                        variant_stats[existing_variant] = {'detected': 0, 'existing': 0, 'new': 0}
                    variant_stats[existing_variant]['existing'] += 1

                # Track if this is a new variant detection
                if detected_variant and detected_variant != existing_variant:
                    variant_stats[detected_variant]['new'] += 1

                # Track base models (no specific variant)
                if detected_variant and detected_variant.endswith('_base'):
                    base_model = detected_variant.split('_')[0]
                    if base_model not in base_model_stats:
                        base_model_stats[base_model] = 0
                    base_model_stats[base_model] += 1

        print(f"📱 Found {len(iphone_listings)} iPhone listings")

        # Show variant statistics
        print(f"\n📊 Variant Statistics:")
        print(f"{'Variant':<15} {'Detected':<10} {'Existing':<10} {'New':<10}")
        print("-" * 50)

        total_detected = 0
        total_existing = 0
        total_new = 0

        for variant in sorted(variant_stats.keys()):
            stats = variant_stats[variant]
            total_detected += stats['detected']
            total_existing += stats['existing']
            total_new += stats['new']
            print(f"{variant:<15} {stats['detected']:<10} {stats['existing']:<10} {stats['new']:<10}")

        print("-" * 50)
        print(f"{'TOTAL':<15} {total_detected:<10} {total_existing:<10} {total_new:<10}")

        # Show base model statistics
        if base_model_stats:
            print(f"\n📱 Base Model Statistics (no specific variant):")
            for model, count in sorted(base_model_stats.items()):
                print(f"iPhone {model} (base): {count} listings")

        # Show some examples of listings with variants
        print(f"\n📝 Sample iPhone Listings with Variants:")
        sample_count = 0
        for listing in iphone_listings[:20]:  # Check first 20 iPhone listings
            title = listing.get('title', '')
            model = listing.get('model', '')
            detected_variant = enhanced_detect_variant(title, model)
            existing_variant = listing.get('variant')

            if detected_variant or existing_variant:
                sample_count += 1
                print(f"\n{sample_count}. {title}")
                print(f"   Model: {model}")
                print(f"   Existing Variant: {existing_variant}")
                print(f"   Detected Variant: {detected_variant}")
                if detected_variant != existing_variant:
                    print(f"   ⚠️  MISMATCH - Would update to: {detected_variant}")

            if sample_count >= 10:  # Show first 10 examples
                break

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()