#!/usr/bin/env python3
import os

def create_simple_icon(filename, color, text):
    # Create a simple SVG icon
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect width="128" height="128" rx="20" fill="{color}"/>
  <text x="64" y="75" text-anchor="middle" font-family="Arial, sans-serif" font-size="48" font-weight="bold" fill="white">{text}</text>
</svg>'''

    with open(filename, 'w') as f:
        f.write(svg_content)
    print(f'Created {filename}')

# Create icons with Google colors
create_simple_icon('icon.svg', '#4285F4', 'G')
create_simple_icon('icon16.svg', '#4285F4', 'G')
create_simple_icon('icon32.svg', '#4285F4', 'G')
create_simple_icon('icon48.svg', '#4285F4', 'G')
create_simple_icon('icon128.svg', '#4285F4', 'G')

print('All icon SVGs created successfully!')