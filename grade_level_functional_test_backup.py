#!/usr/bin/env python3
"""Test that grade filtering works with page reloads"""

import urllib.request
import urllib.parse
import json
import re

BASE_URL = "http://127.0.0.1:5001/classes"

def test_grade_filter(grade, date=None):
    """Test a specific grade filter"""
    params = {}
    if grade != 'all':
        params['grade'] = grade
    if date:
        params['date'] = date

    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}" if params else BASE_URL

    print(f"\nTesting: grade={grade}" + (f", date={date}" if date else ""))
    print(f"  URL: {url}")

    try:
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')

        # Check which grade button is active
        active_pattern = r'<button[^>]*class="[^"]*active[^"]*"[^>]*data-grade="([^"]*)"'
        active_match = re.search(active_pattern, html)
        active_grade = active_match.group(1) if active_match else "UNKNOWN"

        # Count rows in the table for each grade
        row_pattern = r'<tr[^>]*data-grade="([^"]*)"'
        rows = re.findall(row_pattern, html)
        grade_counts = {}
        for row_grade in rows:
            grade_counts[row_grade] = grade_counts.get(row_grade, 0) + 1

        print(f"  Active button: {active_grade}")
        print(f"  Table rows by grade: {grade_counts}")

        # Verify results
        success = True
        if grade == 'all':
            if active_grade != 'all':
                print(f"  ❌ FAIL: Expected 'all' button active, got '{active_grade}'")
                success = False
            if len(grade_counts) == 0:
                print(f"  ❌ FAIL: No table rows found")
                success = False
        else:
            if active_grade != grade:
                print(f"  ❌ FAIL: Expected '{grade}' button active, got '{active_grade}'")
                success = False
            if grade not in grade_counts:
                print(f"  ❌ FAIL: No rows for grade '{grade}'")
                success = False
            unexpected_grades = [g for g in grade_counts if g != grade]
            if unexpected_grades:
                print(f"  ❌ FAIL: Found unexpected grades: {unexpected_grades}")
                success = False

        if success:
            print(f"  ✅ PASS")

        return success
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def main():
    print("=" * 70)
    print("GRADE FILTER RELOAD TEST")
    print("=" * 70)

    tests = [
        ('all', None),
        ('K', None),
        ('1', None),
        ('2', None),
        ('3', None),
        ('4', None),
        ('5', None),
        ('K', '2025-10-11'),
        ('1', '2025-10-11'),
        ('2', '2025-10-11'),
        ('3', '2025-10-11'),
        ('4', '2025-10-11'),
        ('5', '2025-10-11'),
    ]

    passed = 0
    failed = 0

    for grade, date in tests:
        if test_grade_filter(grade, date):
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 70)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
