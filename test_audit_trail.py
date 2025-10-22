#!/usr/bin/env python3
"""
Test script for audit trail functionality
Tests multi-day and cumulative upload audit tracking
"""

import os
import sys
import json
import tempfile
from datetime import datetime
from database import ReadathonDB

# Test database
TEST_DB = 'test_audit_trail.db'

def cleanup():
    """Remove test database if it exists"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        print(f"✓ Cleaned up test database: {TEST_DB}")

def setup_test_db():
    """Create test database with sample roster"""
    cleanup()

    db = ReadathonDB(TEST_DB)
    print(f"✓ Created test database: {TEST_DB}")

    # Load roster data
    roster_csv = """student_name,class_name,home_room,teacher_name,grade_level,team_name
John Doe,Class A,Room 101,Ms. Spencer,3,Red Team
Jane Spencer,Class A,Room 101,Ms. Spencer,3,Red Team
Bob Terry,Class B,Room 102,Mr. Snyder,4,Blue Team
Alice Hayes,Class B,Room 102,Mr. Snyder,4,Blue Team
Charlie Brown,Class C,Room 103,Mrs. Stone,5,Green Team"""

    db.load_roster_data(roster_csv)
    print("✓ Loaded roster data (5 students)")

    # Load class info
    class_csv = """class_name,home_room,teacher_name,grade_level,team_name,total_students
Class A,Room 101,Ms. Spencer,3,Red Team,2
Class B,Room 102,Mr. Snyder,4,Blue Team,2
Class C,Room 103,Mrs. Stone,5,Green Team,1"""

    db.load_class_info_data(class_csv)
    print("✓ Loaded class info data")

    # Load grade rules
    grade_rules_csv = """grade_level,min_daily_minutes,max_daily_minutes_credit
3,20,120
4,25,120
5,30,120"""

    db.load_grade_rules_data(grade_rules_csv)
    print("✓ Loaded grade rules data")

    return db

def create_temp_csv(content):
    """Create a temporary CSV file"""
    class TempFile:
        def __init__(self, content, filename):
            self.content = content.encode('utf-8')
            self.filename = filename
            self.position = 0

        def read(self):
            return self.content

        def seek(self, position):
            self.position = position

    return TempFile(content, 'test.csv')

def test_multiday_upload_new_data(db):
    """Test 1: Multi-day upload with new data (no existing records)"""
    print("\n=== Test 1: Multi-day Upload (New Data) ===")

    csv_content = """date,student_name,minutes
2025-10-01,John Doe,45
2025-10-01,Jane Spencer,30
2025-10-02,John Doe,50
2025-10-02,Jane Spencer,35"""

    file_obj = create_temp_csv(csv_content)
    result = db.upload_multiday_data(file_obj)

    print(f"Success: {result['success']}")
    print(f"Rows processed: {result['rows_processed']}")
    print(f"Dates affected: {result['dates_affected']}")

    # Check upload history
    history = db.get_upload_history(limit=1)
    if history:
        h = history[0]
        print(f"\nUpload History:")
        print(f"  Action taken: {h['action_taken']}")
        print(f"  Records replaced: {h['records_replaced']}")

        if h['audit_details']:
            audit = json.loads(h['audit_details'])
            print(f"\nAudit Details:")
            print(f"  Dates processed: {audit.get('dates_processed', [])}")
            print(f"  Records replaced: {audit.get('records_replaced', 0)}")
            print(f"  Records added: {audit.get('records_added', 0)}")

            if 'date_breakdown' in audit:
                print(f"  Date breakdown:")
                for date, info in audit['date_breakdown'].items():
                    print(f"    {date}: existing={info['existing_count']}, new={info['new_count']}, minutes={info['total_minutes']}")

        # Validate
        assert h['action_taken'] == 'inserted', "Should be 'inserted' for new data"
        assert h['records_replaced'] == 0, "Should have 0 records replaced"
        print("\n✓ Test 1 PASSED: New data upload tracked correctly")
    else:
        print("❌ Test 1 FAILED: No upload history found")
        return False

    return True

def test_multiday_upload_replacement(db):
    """Test 2: Multi-day upload with replacement (existing records)"""
    print("\n=== Test 2: Multi-day Upload (Replacement) ===")

    csv_content = """date,student_name,minutes
2025-10-01,John Doe,60
2025-10-01,Jane Spencer,40
2025-10-03,Bob Terry,55"""

    file_obj = create_temp_csv(csv_content)
    result = db.upload_multiday_data(file_obj)

    print(f"Success: {result['success']}")
    print(f"Rows processed: {result['rows_processed']}")
    print(f"Dates affected: {result['dates_affected']}")

    # Check upload history (should be 2nd record)
    history = db.get_upload_history(limit=2)
    if len(history) >= 2:
        h = history[0]  # Most recent
        print(f"\nUpload History (latest):")
        print(f"  Action taken: {h['action_taken']}")
        print(f"  Records replaced: {h['records_replaced']}")

        if h['audit_details']:
            audit = json.loads(h['audit_details'])
            print(f"\nAudit Details:")
            print(f"  Dates processed: {audit.get('dates_processed', [])}")
            print(f"  Records replaced: {audit.get('records_replaced', 0)}")
            print(f"  Records added: {audit.get('records_added', 0)}")

            if 'date_breakdown' in audit:
                print(f"  Date breakdown:")
                for date, info in audit['date_breakdown'].items():
                    print(f"    {date}: existing={info['existing_count']}, new={info['new_count']}, minutes={info['total_minutes']}")

        # Validate
        assert h['action_taken'] == 'replaced', "Should be 'replaced' when existing data found"
        assert h['records_replaced'] > 0, "Should have records replaced"
        print("\n✓ Test 2 PASSED: Replacement upload tracked correctly")
    else:
        print("❌ Test 2 FAILED: Not enough upload history records")
        return False

    return True

def test_cumulative_upload_new_data(db):
    """Test 3: Cumulative upload with new data"""
    print("\n=== Test 3: Cumulative Upload (New Data) ===")

    csv_content = """"Reader Name",Teacher,Raised,Sponsors,Minutes
John Doe,Ms. Spencer,100.00,5,95
Jane Spencer,Ms. Spencer,75.00,3,65
Bob Terry,Mr. Snyder,50.00,2,105"""

    file_obj = create_temp_csv(csv_content)
    result = db.upload_cumulative_stats(file_obj)

    print(f"Success: {result['success']}")
    print(f"Rows processed: {result['rows_processed']}")
    print(f"Students matched: {result['students_matched']}")

    # Check upload history
    history = db.get_upload_history(limit=1)
    if history:
        h = history[0]
        print(f"\nUpload History:")
        print(f"  Action taken: {h['action_taken']}")
        print(f"  Records replaced: {h['records_replaced']}")

        if h['audit_details']:
            audit = json.loads(h['audit_details'])
            print(f"\nAudit Details:")
            print(f"  Previous total: {audit.get('previous_total', 0)}")
            print(f"  New total: {audit.get('new_total', 0)}")
            print(f"  Students removed: {audit.get('students_removed', 0)}")
            print(f"  Students added: {audit.get('students_added', 0)}")
            print(f"  Students updated: {audit.get('students_updated', 0)}")

        # Validate
        assert h['action_taken'] == 'inserted', "Should be 'inserted' for first cumulative upload"
        assert h['records_replaced'] == 0, "Should have 0 records replaced (first upload)"
        print("\n✓ Test 3 PASSED: New cumulative upload tracked correctly")
    else:
        print("❌ Test 3 FAILED: No upload history found")
        return False

    return True

def test_cumulative_upload_replacement(db):
    """Test 4: Cumulative upload with replacement"""
    print("\n=== Test 4: Cumulative Upload (Replacement) ===")

    # Upload different students (some added, some removed)
    csv_content = """"Reader Name",Teacher,Raised,Sponsors,Minutes
John Doe,Ms. Spencer,120.00,6,150
Alice Hayes,Mr. Snyder,80.00,4,130
Charlie Brown,Mrs. Stone,60.00,3,110"""

    file_obj = create_temp_csv(csv_content)
    result = db.upload_cumulative_stats(file_obj)

    print(f"Success: {result['success']}")
    print(f"Rows processed: {result['rows_processed']}")
    print(f"Students matched: {result['students_matched']}")

    # Check upload history
    history = db.get_upload_history(limit=1)
    if history:
        h = history[0]
        print(f"\nUpload History:")
        print(f"  Action taken: {h['action_taken']}")
        print(f"  Records replaced: {h['records_replaced']}")

        if h['audit_details']:
            audit = json.loads(h['audit_details'])
            print(f"\nAudit Details:")
            print(f"  Previous total: {audit.get('previous_total', 0)}")
            print(f"  New total: {audit.get('new_total', 0)}")
            print(f"  Students removed: {audit.get('students_removed', 0)}")
            print(f"  Students added: {audit.get('students_added', 0)}")
            print(f"  Students updated: {audit.get('students_updated', 0)}")

            # Previous: John Doe, Bob Terry (removed), Alice Hayes (new), Charlie Brown (new)
            # So: removed=2 (Jane Spencer, Bob Terry), added=2 (Alice Hayes, Charlie Brown), updated=1 (John Doe)

        # Validate
        assert h['action_taken'] == 'replaced', "Should be 'replaced' for subsequent cumulative upload"
        assert h['records_replaced'] > 0, "Should have records replaced"
        assert audit.get('students_removed', 0) > 0, "Should have students removed"
        assert audit.get('students_added', 0) > 0, "Should have students added"
        print("\n✓ Test 4 PASSED: Cumulative replacement tracked correctly")
    else:
        print("❌ Test 4 FAILED: No upload history found")
        return False

    return True

def test_error_tracking(db):
    """Test 5: Error tracking in audit trail"""
    print("\n=== Test 5: Error Tracking in Audit ===")

    # Upload with invalid student (not in roster)
    csv_content = """date,student_name,minutes
2025-10-05,John Doe,45
2025-10-05,Unknown Student,30"""

    file_obj = create_temp_csv(csv_content)
    result = db.upload_multiday_data(file_obj)

    print(f"Success: {result['success']}")
    print(f"Warnings: {len(result.get('warnings', []))}")

    # Check upload history
    history = db.get_upload_history(limit=1)
    if history:
        h = history[0]
        print(f"\nUpload History:")
        print(f"  Status: {h['status']}")

        if h['audit_details']:
            audit = json.loads(h['audit_details'])
            print(f"\nAudit Details:")
            if 'warnings' in audit:
                print(f"  Warnings captured: {len(audit['warnings'])}")
                for warn in audit['warnings']:
                    print(f"    - {warn}")

        # Validate
        assert h['status'] == 'warning', "Should have warning status"
        assert 'warnings' in audit, "Should have warnings in audit"
        print("\n✓ Test 5 PASSED: Warnings tracked correctly in audit")
    else:
        print("❌ Test 5 FAILED: No upload history found")
        return False

    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("AUDIT TRAIL FUNCTIONALITY TESTS")
    print("=" * 60)

    try:
        # Setup
        db = setup_test_db()

        # Run tests
        tests = [
            test_multiday_upload_new_data,
            test_multiday_upload_replacement,
            test_cumulative_upload_new_data,
            test_cumulative_upload_replacement,
            test_error_tracking
        ]

        results = []
        for test_func in tests:
            try:
                result = test_func(db)
                results.append((test_func.__name__, result))
            except Exception as e:
                print(f"\n❌ Test {test_func.__name__} FAILED with exception:")
                print(f"   {str(e)}")
                results.append((test_func.__name__, False))

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
            return_code = 0
        else:
            print("\n❌ SOME TESTS FAILED ❌")
            return_code = 1

        # Cleanup
        db.close()
        cleanup()

        return return_code

    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        cleanup()
        return 1

if __name__ == '__main__':
    sys.exit(main())
