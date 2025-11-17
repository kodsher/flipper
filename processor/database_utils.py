#!/usr/bin/env python3
"""
Database Utilities for Firebase Management
Provides utilities for managing the Firebase database
"""

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, firebase_config: Dict):
        """Initialize Firebase connection"""
        self.firebase_config = firebase_config
        self.db = None
        self._init_firebase()

    def _init_firebase(self):
        """Initialize Firebase connection"""
        try:
            cred = credentials.Certificate(self.firebase_config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': self.firebase_config.get('databaseURL')
            })
            self.db = db
            logger.info("✅ Firebase initialized successfully")
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {e}")
            raise

    def clear_all_listings(self):
        """Clear all phone listings from the database"""
        try:
            ref = self.db.reference('phone_listings')
            ref.remove()
            logger.info("🗑️ Cleared all phone listings from database")
        except Exception as e:
            logger.error(f"❌ Error clearing listings: {e}")

    def clear_old_listings(self, days: int = 7):
        """Clear listings older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            ref = self.db.reference('phone_listings')

            listings = ref.get()
            if listings:
                removed_count = 0
                for listing_id, listing_data in listings.items():
                    try:
                        listing_date = datetime.fromisoformat(
                            listing_data.get('found_at', listing_data.get('detected_at', ''))
                        )
                        if listing_date < cutoff_date:
                            ref.child(listing_id).remove()
                            removed_count += 1
                    except (ValueError, TypeError):
                        continue

                logger.info(f"🗑️ Cleared {removed_count} listings older than {days} days")
        except Exception as e:
            logger.error(f"❌ Error clearing old listings: {e}")

    def get_all_listings(self) -> Dict:
        """Get all phone listings from database"""
        try:
            ref = self.db.reference('phone_listings')
            listings = ref.get()
            logger.info(f"📊 Retrieved {len(listings) if listings else 0} listings from database")
            return listings or {}
        except Exception as e:
            logger.error(f"❌ Error retrieving listings: {e}")
            return {}

    def get_listing_stats(self) -> Dict:
        """Get statistics about listings in database"""
        try:
            ref = self.db.reference('phone_listings')
            listings = ref.get() or {}

            if not listings:
                return {
                    'total_listings': 0,
                    'total_value': 0,
                    'average_price': 0,
                    'models': {},
                    'price_range': {'min': 0, 'max': 0}
                }

            total_value = 0
            model_counts = {}
            prices = []

            for listing in listings.values():
                price = listing.get('price', 0)
                model = listing.get('model', 'Unknown')

                total_value += price
                prices.append(price)
                model_counts[model] = model_counts.get(model, 0) + 1

            average_price = total_value / len(listings) if listings else 0

            return {
                'total_listings': len(listings),
                'total_value': total_value,
                'average_price': average_price,
                'models': model_counts,
                'price_range': {
                    'min': min(prices) if prices else 0,
                    'max': max(prices) if prices else 0
                }
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}

    def export_listings(self, filepath: str):
        """Export all listings to a JSON file"""
        try:
            listings = self.get_all_listings()

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(listings, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Exported {len(listings)} listings to {filepath}")
        except Exception as e:
            logger.error(f"❌ Error exporting listings: {e}")

    def import_listings(self, filepath: str):
        """Import listings from a JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                listings = json.load(f)

            ref = self.db.reference('phone_listings')

            imported_count = 0
            for listing_id, listing_data in listings.items():
                ref.child(listing_id).set(listing_data)
                imported_count += 1

            logger.info(f"📥 Imported {imported_count} listings from {filepath}")
        except Exception as e:
            logger.error(f"❌ Error importing listings: {e}")

    def hide_listing(self, listing_id: str):
        """Hide a listing"""
        try:
            ref = self.db.reference(f'phone_listings/{listing_id}')
            ref.update({'hidden': True})
            logger.info(f"👁️ Hidden listing {listing_id}")
        except Exception as e:
            logger.error(f"❌ Error hiding listing: {e}")

    def unhide_listing(self, listing_id: str):
        """Unhide a listing"""
        try:
            ref = self.db.reference(f'phone_listings/{listing_id}')
            ref.update({'hidden': False})
            logger.info(f"👁️‍🗨️ Unhidden listing {listing_id}")
        except Exception as e:
            logger.error(f"❌ Error unhiding listing: {e}")

    def favorite_listing(self, listing_id: str, favorited: bool = True):
        """Set favorite status for a listing"""
        try:
            ref = self.db.reference(f'phone_listings/{listing_id}')
            ref.update({'favorited': favorited})
            action = "Favorited" if favorited else "Unfavorited"
            logger.info(f"⭐ {action} listing {listing_id}")
        except Exception as e:
            logger.error(f"❌ Error updating favorite status: {e}")

    def get_hidden_listings(self) -> Dict:
        """Get all hidden listings"""
        try:
            ref = self.db.reference('phone_listings')
            listings = ref.get() or {}

            hidden = {
                listing_id: listing_data
                for listing_id, listing_data in listings.items()
                if listing_data.get('hidden', False)
            }

            logger.info(f"👁️ Found {len(hidden)} hidden listings")
            return hidden
        except Exception as e:
            logger.error(f"❌ Error getting hidden listings: {e}")
            return {}

    def get_favorited_listings(self) -> Dict:
        """Get all favorited listings"""
        try:
            ref = self.db.reference('phone_listings')
            listings = ref.get() or {}

            favorited = {
                listing_id: listing_data
                for listing_id, listing_data in listings.items()
                if listing_data.get('favorited', False)
            }

            logger.info(f"⭐ Found {len(favorited)} favorited listings")
            return favorited
        except Exception as e:
            logger.error(f"❌ Error getting favorited listings: {e}")
            return {}

    def backup_database(self, backup_dir: str = 'backups'):
        """Create a backup of the current database"""
        import os
        from datetime import datetime

        try:
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/database_backup_{timestamp}.json"

            self.export_listings(backup_file)

            logger.info(f"🗄️ Database backed up to {backup_file}")
        except Exception as e:
            logger.error(f"❌ Error backing up database: {e}")

    def restore_database(self, backup_file: str):
        """Restore database from a backup file"""
        try:
            self.clear_all_listings()
            self.import_listings(backup_file)

            logger.info(f"🔄 Database restored from {backup_file}")
        except Exception as e:
            logger.error(f"❌ Error restoring database: {e}")

def main():
    """Example usage of database utilities"""
    # Firebase configuration (update with your actual config)
    firebase_config = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    # Initialize database manager
    db_manager = DatabaseManager(firebase_config)

    # Example operations
    print("📊 Current Stats:")
    stats = db_manager.get_listing_stats()
    print(json.dumps(stats, indent=2))

    # Create backup
    db_manager.backup_database()

if __name__ == "__main__":
    main()