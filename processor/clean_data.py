#!/usr/bin/env python3
"""
Data Cleaning Utilities for Phone Listings
Cleans and standardizes phone listing data
"""

import pandas as pd
import re
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhoneDataCleaner:
    def __init__(self):
        # Common abbreviations and their full forms
        self.abbreviations = {
            'gb': 'GB',
            'g': 'GB',
            'tb': 'TB',
            't': 'TB',
            'mini': 'mini',
            'plus': '+',
            'pro': 'Pro',
            'max': 'Max'
        }

        # Price cleaning patterns
        self.price_patterns = [
            r'\$([0-9,]+\.?\d*)',
            r'([0-9,]+\.?\d*)\s*dollars?',
            r'([0-9,]+\.?\d*)\s*usd'
        ]

    def clean_price(self, price_str: str) -> Optional[float]:
        """Clean and standardize price strings"""
        if not price_str or pd.isna(price_str):
            return None

        price_str = str(price_str).lower().strip()

        for pattern in self.price_patterns:
            match = re.search(pattern, price_str)
            if match:
                try:
                    price = float(match.group(1).replace(',', ''))
                    return price
                except ValueError:
                    continue

        return None

    def clean_storage_size(self, text: str) -> Optional[str]:
        """Extract and standardize storage size"""
        if not text:
            return None

        text = str(text).lower()

        # Look for storage patterns like "128gb", "256 GB", "1tb"
        storage_match = re.search(r'(\d+(?:\.\d+)?)\s*(gb|tb|g|t)', text)
        if storage_match:
            size = storage_match.group(1)
            unit = storage_match.group(2)

            # Standardize unit
            if unit in ['g', 'gb']:
                return f"{size}GB"
            elif unit in ['t', 'tb']:
                return f"{size}TB"

        return None

    def extract_phone_model(self, title: str) -> str:
        """Extract and standardize phone model from title"""
        if not title:
            return "Unknown"

        title = str(title).lower()

        # iPhone patterns
        iphone_match = re.search(r'iphone\s*(\d+(?:\s*pro)?(?:\s*max)?(?:\s*plus)?)', title)
        if iphone_match:
            model = iphone_match.group(1).upper()
            # Add iPhone prefix
            model = model.replace('PRO', ' Pro').replace('MAX', ' Max').replace('PLUS', ' Plus')
            return f"iPhone {model}"

        # Samsung Galaxy patterns
        samsung_match = re.search(r'samsung\s*galaxy\s*(s\d+(?:\s*plus)?|note\s*\d+|a\d+)', title)
        if samsung_match:
            return f"Samsung Galaxy {samsung_match.group(1).upper()}"

        # Google Pixel patterns
        pixel_match = re.search(r'google\s*pixel\s*(\d+(?:\s*pro)?(?:\s*a)?)', title)
        if pixel_match:
            return f"Google Pixel {pixel_match.group(1).upper()}"

        # OnePlus patterns
        oneplus_match = re.search(r'oneplus\s*(\d+(?:\s*pro)?)', title)
        if oneplus_match:
            return f"OnePlus {oneplus_match.group(1).upper()}"

        return "Other"

    def clean_condition(self, text: str) -> str:
        """Extract and standardize condition"""
        if not text:
            return "Unknown"

        text = str(text).lower()

        if any(word in text for word in ['new', 'sealed', 'brand new']):
            return "New"
        elif any(word in text for word in ['like new', 'excellent', 'mint', 'pristine']):
            return "Like New"
        elif any(word in text for word in ['good', 'used', 'fair']):
            return "Good"
        elif any(word in text for word in ['poor', 'damaged', 'broken']):
            return "Poor"

        return "Unknown"

    def clean_location(self, location: str) -> str:
        """Clean and standardize location"""
        if not location:
            return "Unknown"

        location = str(location).strip()

        # Remove extra whitespace
        location = re.sub(r'\s+', ' ', location)

        # Standardize common abbreviations
        location = location.replace('US', 'USA')

        return location

    def is_valid_phone_listing(self, row: pd.Series) -> bool:
        """Check if a row is a valid phone listing"""
        title = str(row.get('title', '')).lower()
        price = row.get('price')

        # Must have a title
        if not title or title == 'nan':
            return False

        # Must have a valid price
        if price is None or pd.isna(price):
            return False

        # Title must contain phone-related keywords
        phone_keywords = ['iphone', 'samsung', 'galaxy', 'pixel', 'oneplus', 'phone']
        if not any(keyword in title for keyword in phone_keywords):
            return False

        # Skip obvious non-phone listings
        skip_keywords = ['case', 'charger', 'cable', 'accessory', 'parts', 'repair']
        if any(keyword in title for keyword in skip_keywords):
            return False

        return True

    def clean_listing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main cleaning function for listing data"""
        logger.info(f"🧹 Starting with {len(df)} raw listings")

        # Filter valid phone listings
        df = df[df.apply(self.is_valid_phone_listing, axis=1)].copy()
        logger.info(f"📱 Filtered to {len(df)} valid phone listings")

        # Clean each field
        df['cleaned_price'] = df['price'].apply(self.clean_price)
        df['model'] = df['title'].apply(self.extract_phone_model)
        df['condition'] = df['title'].apply(self.clean_condition)
        df['storage'] = df['title'].apply(self.clean_storage_size)
        df['cleaned_location'] = df['location'].apply(self.clean_location)

        # Remove rows with invalid prices after cleaning
        df = df[df['cleaned_price'].notna()].copy()

        # Add cleaned timestamp
        df['cleaned_at'] = datetime.now().isoformat()

        logger.info(f"✅ Cleaning complete. {len(df)} listings remain")

        return df

    def deduplicate_listings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate listings based on title and price"""
        original_count = len(df)

        # Create a unique key based on normalized title and price
        df['title_normalized'] = df['title'].str.lower().str.replace(r'[^\w\s]', '', '').str.replace(r'\s+', ' ', regex=True)
        df['unique_key'] = df['title_normalized'] + '_' + df['cleaned_price'].astype(str)

        # Keep first occurrence of each unique key
        df_deduped = df.drop_duplicates(subset=['unique_key'], keep='first')

        logger.info(f"🔄 Removed {original_count - len(df_deduped)} duplicates")

        return df_deduped

def main():
    """Main function to clean data"""
    # Example usage
    cleaner = PhoneDataCleaner()

    # Load CSV data (adjust path as needed)
    input_path = '../prices/listings.csv'
    output_path = '../prices/cleaned_listings.csv'

    try:
        # Read the CSV
        df = pd.read_csv(input_path)
        logger.info(f"📊 Loaded {len(df)} listings from {input_path}")

        # Clean the data
        df_cleaned = cleaner.clean_listing_data(df)

        # Remove duplicates
        df_deduped = cleaner.deduplicate_listings(df_cleaned)

        # Save cleaned data
        df_deduped.to_csv(output_path, index=False)
        logger.info(f"💾 Saved {len(df_deduped)} cleaned listings to {output_path}")

    except Exception as e:
        logger.error(f"❌ Error cleaning data: {e}")

if __name__ == "__main__":
    main()