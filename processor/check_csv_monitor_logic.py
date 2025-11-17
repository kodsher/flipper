#!/usr/bin/env python3
"""
Check if the current CSV monitor has the correct link-based duplicate detection logic
"""

import os

def check_csv_monitor_logic():
    """Check if csv_monitor.py has the correct logic"""
    csv_monitor_path = "/Users/admin/Desktop/claude/phone-flipping/processor/csv_monitor.py"

    if not os.path.exists(csv_monitor_path):
        print("❌ csv_monitor.py not found")
        return

    with open(csv_monitor_path, 'r') as f:
        content = f.read()

    # Check for key components of the new logic
    checks = [
        ("_load_existing_links", "Loads existing links function"),
        ("existing_links", "Uses existing_links variable"),
        ("is_link_already_in_database", "Has link-based duplicate check function"),
        ("_process_listing_with_link_check", "Uses new processing function")
    ]

    print("🔍 Checking CSV Monitor Logic:")
    print("=" * 50)

    all_good = True
    for check_name, description in checks:
        if check_name in content:
            print(f"✅ {description}: FOUND")
        else:
            print(f"❌ {description}: NOT FOUND")
            all_good = False

    # Check for old logic that should be replaced
    old_logic_checks = [
        ("existing_listing_hashes", "Old hash-based logic (should be removed)"),
        ("_batch_check_duplicates", "Old batch duplicate logic (might need updating)")
    ]

    print(f"\n🔍 Checking for Old Logic:")
    for check_name, description in old_logic_checks:
        if check_name in content:
            print(f"⚠️  {description}: PRESENT (may cause issues)")
            all_good = False
        else:
            print(f"✅ {description}: NOT FOUND (good)")

    # Check for the key logic in _process_listing_with_link_check
    if "_process_listing_with_link_check" in content:
        with open(csv_monitor_path, 'r') as f:
            lines = f.readlines()

        in_function = False
        has_link_check = False
        for i, line in enumerate(lines):
            if "def _process_listing_with_link_check" in line:
                in_function = True
                continue
            elif in_function and line.strip().startswith("def "):
                break
            elif in_function and "is_link_already_in_database" in line:
                has_link_check = True
                break

        if has_link_check:
            print(f"✅ Link-based duplicate check found in processing function")
        else:
            print(f"❌ Link-based duplicate check NOT found in processing function")
            all_good = False

    # Check process_csv_file function
    if "process_csv_file" in content:
        with open(csv_monitor_path, 'r') as f:
            content_lower = content.lower()

        if "_process_listing_with_link_check" in content_lower:
            print(f"✅ process_csv_file calls the new link-checking function")
        else:
            print(f"❌ process_csv_file might be calling old function")
            all_good = False

    print(f"\n📊 Overall Assessment:")
    if all_good:
        print("✅ CSV Monitor appears to have correct link-based duplicate detection")
    else:
        print("❌ CSV Monitor may have issues with duplicate detection logic")

    # Show the actual functions that are called
    print(f"\n🔧 Function Calls in process_csv_file:")
    if "process_csv_file" in content:
        start_idx = content.find("def process_csv_file")
        if start_idx != -1:
            # Find the end of the function
            end_idx = content.find("def ", start_idx + 1)
            if end_idx == -1:
                end_idx = len(content)

            function_content = content[start_idx:end_idx]
            if "_process_listing_with_link_check" in function_content:
                print("✅ Calls: _process_listing_with_link_check (NEW)")
            if "_process_listing_no_duplicate_check" in function_content:
                print("⚠️  Calls: _process_listing_no_duplicate_check (OLD)")

if __name__ == "__main__":
    check_csv_monitor_logic()