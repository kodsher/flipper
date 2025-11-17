#!/usr/bin/env python3
"""
Simple Data Collection Script for Facebook Marketplace iPhone Search
Uses pynput for keyboard control and pyperclip for clipboard operations
"""

import time
import urllib.parse
from pynput.keyboard import Key, Controller
from pynput.mouse import Controller as MouseController, Button
import pyperclip


def create_search_url(location, search_terms, min_price=None):
    """
    Creates a Facebook Marketplace search URL with properly encoded search terms and optional price filtering

    Args:
        location (str): Location for marketplace (e.g., 'austin')
        search_terms (str): Search terms to encode (e.g., 'iphone 16')
        min_price (int, optional): Minimum price filter (e.g., 125)

    Returns:
        str: Complete search URL with encoded query parameter and optional price filter
    """
    # Encode the search terms for URL (spaces become %20, etc.)
    encoded_query = urllib.parse.quote(search_terms)

    # Start with base URL and minPrice if provided
    url = f"https://www.facebook.com/marketplace/{location}/search?"
    if min_price is not None:
        url += f"minPrice={min_price}&"

    # Add remaining parameters
    url += f"daysSinceListed=1&deliveryMethod=local_pick_up&query={encoded_query}&exact=false"

    return url


def search_facebook_marketplace():
    """
    Automates searching for items on Facebook Marketplace across multiple cities and search terms
    """
    keyboard = Controller()
    mouse = MouseController()

    # Hardcoded values - cities and search terms
    cities = [
    "sanantonio",
    #"103103056397247",
    "austin",
    "houston",
    #"phoenix",
    "dallas"
    ]  # Corpus Christi ID: 103103056397247
    search_terms = ["iphone 17", "iphone 16", "iphone 15", "iphone 14", 
                    #"iphone 17 pro max", "iphone 16 pro max", "iphone 15 pro max", "iphone 14 pro max"
                    ]
    min_price = 125

    total_searches = len(cities) * len(search_terms)

    # Display cities with proper names
    city_names = []
    for city in cities:
        if city == "103103056397247":
            city_names.append("Corpus Christi")
        if city == "103103056397247":
            city_names.append("Corpus Christi")
        else:
            city_names.append(city.capitalize())

    print(f"Searching for {len(search_terms)} items across {len(cities)} cities:")
    print(f"Total searches per cycle: {total_searches}")
    print(f"Cities: {', '.join(city_names)}")
    print(f"Search terms: {', '.join(search_terms)}")
    print(f"Minimum price: ${min_price}")

    print(f"\nStarting searches...")
    print("You have 3 seconds to focus on your browser...")
    time.sleep(3)

    # Infinite loop to cycle through cities and search terms
    cycle_count = 0
    while True:
        cycle_count += 1
        if cycle_count > 1:
            print(f"\n--- Cycle {cycle_count} ---")

        search_count = 0

        # Outer loop: cycle through each city
        for city_idx, city in enumerate(cities, 1):
            # Display proper city name
            display_name = "Corpus Christi" if city == "103103056397247" else city.capitalize()
            print(f"\n--- City {city_idx}/{len(cities)}: '{display_name}' ---")

            # Inner loop: cycle through each search term for this city
            for term_idx, search_term in enumerate(search_terms, 1):
                search_count += 1
                print(f"\n--- Search {search_count}/{total_searches}: '{search_term}' in '{display_name}' ---")

                # Create the search URL dynamically
                search_url = create_search_url(city, search_term, min_price)
                print(f"URL: {search_url}")

                try:
                    # Select address bar using Command+L
                    print("Selecting address bar...")
                    keyboard.press(Key.cmd)
                    keyboard.press('l')
                    keyboard.release('l')
                    keyboard.release(Key.cmd)

                    # Wait a moment for address bar to be selected
                    time.sleep(0.5)

                    # Copy URL to clipboard
                    print("Copying URL to clipboard...")
                    pyperclip.copy(search_url)

                    # Paste URL into address bar
                    print("Pasting URL into address bar...")
                    keyboard.press(Key.cmd)
                    keyboard.press('v')
                    keyboard.release('v')
                    keyboard.release(Key.cmd)

                    # Wait a moment for URL to be pasted
                    time.sleep(0.5)

                    # Press Enter to navigate
                    print("Pressing Enter to navigate...")
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)

                    print("Search completed successfully!")

                    # Wait for page to load
                    print("Waiting for page to load...")
                    time.sleep(2.5)

                    # Hardcoded mouse position
                    click_x = 39.05859375
                    click_y = 130.84765625

                    print(f"Clicking at position: ({click_x}, {click_y})")

                    # Move mouse to position and click
                    mouse.position = (click_x, click_y)
                    time.sleep(1)
                    mouse.click(Button.left, 1)

                    print("Click completed!")

                except Exception as e:
                    print(f"An error occurred during search '{search_term}' in '{city}': {e}")
                    continue

                # Wait for bookmarklet to complete
                print("Waiting for bookmarklet to complete...")
                time.sleep(22)

        # Continue cycling through all cities and search terms indefinitely
        print("\n" + "="*50)
        print(f"✅ Completed cycle {cycle_count} - all {total_searches} searches done!")
        print("Starting next cycle of searches...")
        print("Press Ctrl+C to stop the script")
        print("="*50)

        # Short pause between cycles
        time.sleep(2)


if __name__ == "__main__":
    print("Facebook Marketplace Multi-City Multi-Search Tool")
    print("=" * 50)
    print("This script will:")
    print("1. Loop through cities: Austin, Houston, Corpus Christi")
    print("2. For each city, search for: iphone 17, iphone 16, iphone 15, iphone 14")
    print("3. Use minimum price filter: $125")
    print("4. Create proper search URLs with encoded queries")
    print("5. Select browser address bar (Cmd+L)")
    print("6. Copy and paste each search URL sequentially")
    print("7. Navigate to each page and click bookmarklet")
    print("8. Wait 2 seconds for bookmarklet to complete")
    print("9. Repeat cycle indefinitely (12 searches per cycle)")
    print("\nPress Ctrl+C to stop the script")
    print()

    search_facebook_marketplace()