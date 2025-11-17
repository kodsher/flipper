#!/usr/bin/env python3
"""
Mouse Location Detection Script
Gets the user's current mouse cursor position with a 3-second delay
"""

import time
from pynput.mouse import Controller


def get_mouse_location():
    """
    Gets the user's current mouse cursor position with a 3-second delay
    """
    print("Mouse Location Detection Tool")
    print("=" * 35)
    print("This script will detect your mouse cursor position in 3 seconds...")
    print("Move your mouse to the desired position...")
    time.sleep(3)

    try:
        mouse = Controller()

        # Get current mouse position
        x = mouse.position[0]
        y = mouse.position[1]

        print(f"\nMouse position detected!")
        print(f"X coordinate: {x}")
        print(f"Y coordinate: {y}")
        print(f"Position: ({x}, {y})")

        return x, y

    except Exception as e:
        print(f"\nError getting mouse position: {e}")
        return 0, 0


if __name__ == "__main__":
    x, y = get_mouse_location()
    print(f"\nFinal position: ({x}, {y})")