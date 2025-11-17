# Phone Flipping Processor Scripts

This directory contains the core processing scripts for the phone flipping dashboard.

## 📁 Files Overview

### Core Scripts

- **`csv_monitor.py`** - Main CSV monitoring script that watches for new Facebook Marketplace listings and updates Firebase
- **`clean_data.py`** - Data cleaning utilities for processing and standardizing phone listing data
- **`database_utils.py`** - Firebase database management utilities

### Configuration

- **`requirements.txt`** - Python dependencies required for the processor scripts

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd processor
pip install -r requirements.txt
```

### 2. Set up Firebase

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Realtime Database
3. Create a service account and download the JSON key file
4. Update the Firebase configuration in the scripts

### 3. Configure CSV Monitoring

The `csv_monitor.py` script expects a CSV file at `../prices/listings.csv` with the following columns:
- `title` - Listing title
- `price` - Listing price
- `location` - Location
- `link` - URL to the listing

## 📋 Usage

### Run the CSV Monitor

```bash
python csv_monitor.py
```

This will:
- Monitor the CSV file for new listings every 30 seconds
- Extract phone models and validate listings
- Save valid listings to Firebase
- Skip duplicates using hash-based detection

### Clean Existing Data

```bash
python clean_data.py
```

This will:
- Clean and standardize listing data
- Remove duplicates
- Filter valid phone listings
- Save cleaned data to `../prices/cleaned_listings.csv`

### Database Management

```python
# Interactive use
from database_utils import DatabaseManager

# Initialize with your Firebase config
db = DatabaseManager(firebase_config)

# Get stats
stats = db.get_listing_stats()
print(stats)

# Clear old listings (older than 7 days)
db.clear_old_listings(days=7)

# Export backup
db.backup_database()
```

## 📱 Phone Model Detection

The scripts automatically detect and categorize:

### iPhone Models
- iPhone 13, iPhone 13 Pro, iPhone 13 Pro Max, etc.
- iPhone 14, iPhone 14 Plus, etc.
- iPhone SE, iPhone mini variants

### Other Brands
- Samsung Galaxy (S series, Note series, A series)
- Google Pixel (including Pro and 'a' variants)
- OnePlus devices

## 🧹 Data Cleaning Features

### Price Processing
- Extracts prices from various formats ($999, 999 USD, etc.)
- Filters by configurable price ranges
- Handles currency symbols and formatting

### Title Processing
- Normalizes phone model names
- Extracts storage capacity (GB/TB)
- Identifies condition (New, Like New, Good, Poor)

### Deduplication
- Hash-based duplicate detection
- Configurable duplicate handling strategies
- Preserves oldest or newest entries

## 🔧 Configuration Options

### Price Filtering
```python
# In csv_monitor.py
self.min_price = 50    # Minimum price to consider
self.max_price = 2000  # Maximum price to consider
```

### Monitoring Frequency
```python
# In csv_monitor.py
time.sleep(30)  # Check every 30 seconds
```

### Data Retention
```python
# In database_utils.py
db.clear_old_listings(days=7)  # Remove listings older than 7 days
```

## 📊 Firebase Database Structure

```
phone_listings/
├── {listing_id}/
│   ├── title
│   ├── price
│   ├── model
│   ├── location
│   ├── link
│   ├── source
│   ├── found_at
│   ├── detected_at
│   ├── hidden (boolean)
│   └── favorited (boolean)
└── processed_hashes/
    └── {hash}/
        └── processed_at
```

## 🛠️ Development

### Running Tests

```bash
# If pytest is installed
pytest tests/

# Run specific script with verbose output
python -v csv_monitor.py
```

### Code Style

```bash
# Format code with black
black *.py

# Check for linting issues
flake8 *.py
```

## 📝 Logging

All scripts include comprehensive logging:

- ✅ Success messages (green in supported terminals)
- ⚠️ Warning messages (yellow)
- ❌ Error messages (red)
- 📊 Information messages (blue)

## 🔒 Security Notes

- Never commit Firebase service account keys to version control
- Use environment variables for sensitive configuration
- Regularly rotate service account keys
- Implement proper Firebase security rules

## 🚨 Common Issues

### Firebase Connection Issues
```bash
# Check Firebase service account credentials
python -c "from firebase_admin import credentials; print('Firebase imports OK')"
```

### CSV File Not Found
```bash
# Ensure CSV file exists and has correct permissions
ls -la ../prices/listings.csv
```

### Python Dependencies
```bash
# Update pip and reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

For issues with:
- **Firebase setup**: Check Firebase console documentation
- **CSV format**: Verify column headers match expected format
- **Python environment**: Ensure Python 3.7+ is installed

## 🔄 Updates

The processor scripts are designed to be:
- **Idempotent** - Safe to run multiple times
- **Resilient** - Handle network errors gracefully
- **Configurable** - Easy to adjust parameters
- **Monitorable** - Comprehensive logging