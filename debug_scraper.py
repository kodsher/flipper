#!/usr/bin/env python3
"""
Debug version of the scraper with better error handling and logging
"""

import time
import urllib.parse
import logging
import traceback
from pynput.keyboard import Key, Controller
from pynput.mouse import Controller as MouseController, Button
import pyperclip

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_search_url(location, search_terms, min_price=None):
    """Creates a Facebook Marketplace search URL"""
    encoded_query = urllib.parse.quote(search_terms)
    url = f"https://www.facebook.com/marketplace/{location}/search?"
    if min_price is not None:
        url += f"minPrice={min_price}&"
    url += f"daysSinceListed=1&deliveryMethod=local_pick_up&query={encoded_query}&exact=false"
    return url

def safe_keyboard_action(keyboard, action_func, description):
    """Safely execute keyboard action with error handling"""
    try:
        logger.info(f"Executing: {description}")
        action_func()
        return True
    except Exception as e:
        logger.error(f"Failed to execute {description}: {e}")
        return False

def safe_mouse_action(mouse, action_func, description):
    """Safely execute mouse action with error handling"""
    try:
        logger.info(f"Executing: {description}")
        action_func()
        return True
    except Exception as e:
        logger.error(f"Failed to execute {description}: {e}")
        return False

def test_single_search(city, search_term, min_price=125):
    """Test a single search with detailed error handling"""
    keyboard = Controller()
    mouse = MouseController()

    logger.info(f"=== Testing: {search_term} in {city} ===")

    try:
        # Generate URL
        search_url = create_search_url(city, search_term, min_price)
        logger.info(f"URL: {search_url}")

        # Test URL generation
        test_url = urllib.parse.unquote(search_url)
        logger.info(f"Decoded URL: {test_url}")

        # Copy to clipboard
        try:
            pyperclip.copy(search_url)
            logger.info("✅ URL copied to clipboard")

            # Verify clipboard content
            clipboard_content = pyperclip.paste()
            if clipboard_content == search_url:
                logger.info("✅ Clipboard content verified")
            else:
                logger.error("❌ Clipboard content mismatch!")
                return False

        except Exception as e:
            logger.error(f"❌ Clipboard operation failed: {e}")
            return False

        # Test address bar selection (optional)
        logger.info("Ready for address bar test...")
        time.sleep(2)

        # Get current mouse position for reference
        current_pos = mouse.position
        logger.info(f"Current mouse position: {current_pos}")

        # Test mouse movement to hardcoded position
        target_x, target_y = 39.05859375, 130.84765625
        logger.info(f"Moving mouse to target position: ({target_x}, {target_y})")

        try:
            mouse.position = (target_x, target_y)
            logger.info("✅ Mouse moved to target position")
            time.sleep(1)

            # Move back to original position
            mouse.position = current_pos
            logger.info("✅ Mouse returned to original position")

        except Exception as e:
            logger.error(f"❌ Mouse movement failed: {e}")
            return False

        logger.info("✅ Single search test completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Single search test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def debug_search_sequence():
    """Debug the exact search sequence that was failing"""
    cities = ["sanantonio", "austin", "houston", "dallas"]
    search_terms = ["iphone 17", "iphone 16", "iphone 15", "iphone 14"]
    min_price = 125

    logger.info("=== DEBUG MODE ===")
    logger.info("Testing the search sequence that stopped at San Antonio iPhone 15")

    # Test the specific failing case first
    logger.info("\n" + "="*50)
    logger.info("TESTING THE FAILING CASE: San Antonio + iPhone 15")
    logger.info("="*50)

    success = test_single_search("sanantonio", "iphone 15", min_price)

    if not success:
        logger.error("❌ The failing case still doesn't work!")
        logger.info("Possible causes:")
        logger.info("1. Mouse position is wrong for your screen")
        logger.info("2. Browser window is not in expected position")
        logger.info("3. Screen resolution has changed")
        logger.info("4. Security software blocking automation")
        return

    logger.info("✅ The failing case now works!")

    # Test a few more cases to make sure
    logger.info("\n" + "="*50)
    logger.info("TESTING A FEW MORE CASES")
    logger.info("="*50)

    test_cases = [
        ("sanantonio", "iphone 14"),
        ("austin", "iphone 15"),
        ("houston", "iphone 15"),
    ]

    for i, (city, term) in enumerate(test_cases, 1):
        logger.info(f"\n--- Test Case {i}/{len(test_cases)} ---")
        success = test_single_search(city, term, min_price)
        if not success:
            logger.error(f"❌ Test case {i} failed!")
            break
        time.sleep(1)  # Brief pause between tests

    logger.info("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    print("Facebook Marketplace Scraper Debug Tool")
    print("=" * 50)
    print("This tool will test the specific case that was failing:")
    print("San Antonio + iPhone 15 (the 10th search)")
    print("\nMake sure your browser is open and visible")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    time.sleep(3)
    debug_search_sequence()