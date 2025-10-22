#!/usr/bin/env python3
"""
Test script to verify that "Replaced X existing records" messages
are classified as info instead of warnings
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import ReadathonDB
from datetime import datetime
from io import StringIO

def test_info_messages():
    """Test that replacement messages appear in info, not warnings"""

    print("Testing info message classification...")
    print("=" * 60)

    # Create database instance
    db = ReadathonDB()

    # First, create an initial upload with some data
    print("\n1. Creating initial upload for 2025-10-13...")
    initial_csv = StringIO("""Reader Name,Minutes
Abdul Baset Long,45
Abigail Hill,60
""")

    # Mock file object
    class MockFile:
        def __init__(self, content):
            self.content = content
            self.filename = "initial_upload.csv"

        def read(self):
            return self.content.getvalue().encode('utf-8')

    initial_file = MockFile(initial_csv)
    result1 = db.upload_daily_data('2025-10-13', initial_file)

    print(f"   Success: {result1['success']}")
    print(f"   Minutes processed: {result1['minutes_processed']}")
    print(f"   Warnings: {result1.get('warnings', [])}")
    print(f"   Info: {result1.get('info', [])}")
    print(f"   Errors: {result1.get('errors', [])}")

    if not result1['success']:
        print(f"   ⚠️  Note: Initial upload marked as failed, but this may be due to other reasons")
        print(f"   Errors: {result1.get('errors', [])}")
        # Don't fail the test - continue to test the replacement scenario

    # Now upload again for the same date (should trigger replacement)
    print("\n2. Uploading replacement data for 2025-10-13...")
    replacement_csv = StringIO("""Reader Name,Minutes
Abdul Baset Long,50
Abigail Hill,70
Abigail Owens,30
""")

    replacement_file = MockFile(replacement_csv)
    result2 = db.upload_daily_data('2025-10-13', replacement_file)

    print(f"   Success: {result2['success']}")
    print(f"   Minutes processed: {result2['minutes_processed']}")
    print(f"   Replaced data: {result2.get('replaced_data', False)}")
    print(f"   Records replaced: {result2.get('records_replaced', 0)}")
    print(f"   Warnings: {result2.get('warnings', [])}")
    print(f"   Info: {result2.get('info', [])}")

    # Verify the results
    print("\n3. Verifying results...")

    # Check that replacement happened
    if not result2.get('replaced_data'):
        print("   ❌ FAILED: Expected replaced_data to be True")
        return False
    print("   ✅ PASS: replaced_data is True")

    # Check that records_replaced is > 0 (there were existing records)
    records_replaced = result2.get('records_replaced', 0)
    if records_replaced == 0:
        print(f"   ❌ FAILED: Expected records_replaced to be > 0, got {records_replaced}")
        return False
    print(f"   ✅ PASS: records_replaced is {records_replaced} (> 0)")

    # Check that replacement message is in info, not warnings
    info_messages = result2.get('info', [])
    warning_messages = result2.get('warnings', [])

    has_replacement_in_info = any('Replaced' in msg and 'existing records' in msg for msg in info_messages)
    has_replacement_in_warnings = any('Replaced' in msg and 'existing records' in msg for msg in warning_messages)

    if not has_replacement_in_info:
        print("   ❌ FAILED: Replacement message not found in info")
        print(f"      Info messages: {info_messages}")
        return False
    print("   ✅ PASS: Replacement message found in info")

    if has_replacement_in_warnings:
        print("   ❌ FAILED: Replacement message should NOT be in warnings")
        print(f"      Warning messages: {warning_messages}")
        return False
    print("   ✅ PASS: Replacement message NOT in warnings")

    # Check that warnings array is empty (no actual warnings)
    if len(warning_messages) > 0:
        print(f"   ⚠️  Note: There are {len(warning_messages)} warnings: {warning_messages}")
    else:
        print("   ✅ PASS: No warnings (as expected)")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("   The 'Replaced X existing records' message is now")
    print("   correctly classified as informational, not a warning.")
    return True

if __name__ == '__main__':
    success = test_info_messages()
    sys.exit(0 if success else 1)
