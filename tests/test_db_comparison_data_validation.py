#!/usr/bin/env python3
"""
Validate database comparison query results against actual tab data.

This test ensures that database comparison metrics match the corresponding
data shown on School, Teams, Grade, and Class tabs.
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from queries import *
from database import ReadathonDB

DB_PATH = 'db/readathon_2025.db'

def get_query_result(query):
    """Execute query and return first row as dict"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_query_results(query):
    """Execute query and return all rows as list of dicts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def compare_values(name, db_comp_value, tab_value, tolerance=0.01):
    """Compare two values with optional tolerance for floats"""
    if isinstance(db_comp_value, float) and isinstance(tab_value, float):
        if abs(db_comp_value - tab_value) <= tolerance:
            print(f"  ✅ {name}: {db_comp_value:.2f} (matches tab)")
            return True
        else:
            print(f"  ❌ {name}: DB Comp={db_comp_value:.2f}, Tab={tab_value:.2f} (MISMATCH)")
            return False
    elif db_comp_value == tab_value:
        print(f"  ✅ {name}: {db_comp_value} (matches tab)")
        return True
    else:
        print(f"  ❌ {name}: DB Comp={db_comp_value}, Tab={tab_value} (MISMATCH)")
        return False

print("\n" + "="*80)
print("DATABASE COMPARISON DATA VALIDATION")
print("Comparing DB Comparison results vs. Actual Tab Data")
print("="*80)

passed = 0
failed = 0

# ===========================================================================
# SCHOOL-LEVEL VALIDATION
# ===========================================================================
print("\n" + "#"*80)
print("# SCHOOL-LEVEL COMPARISONS")
print("#"*80)

print("\n--- School Fundraising ---")
db_comp = get_query_result(get_db_comparison_school_fundraising())
# School tab query (from QUERY_SCHOOL_SUMMARY)
school_tab = get_query_result("""
    SELECT
        COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
    FROM Reader_Cumulative rc
""")
if compare_values("Total Fundraising", db_comp['total_fundraising'], school_tab['total_fundraising']):
    passed += 1
else:
    failed += 1

print("\n--- School Minutes (Capped) ---")
db_comp = get_query_result(get_db_comparison_school_minutes())
school_tab = get_query_result("""
    SELECT
        COALESCE(SUM(CASE WHEN minutes_read > 120 THEN 120 ELSE minutes_read END), 0) as total_minutes
    FROM Daily_Logs
    WHERE minutes_read > 0
""")
if compare_values("Total Minutes", db_comp['total_minutes'], school_tab['total_minutes']):
    passed += 1
else:
    failed += 1

print("\n--- School Sponsors ---")
db_comp = get_query_result(get_db_comparison_school_sponsors())
school_tab = get_query_result("""
    SELECT
        COALESCE(SUM(rc.sponsors), 0) as total_sponsors
    FROM Reader_Cumulative rc
""")
if compare_values("Total Sponsors", db_comp['total_sponsors'], school_tab['total_sponsors']):
    passed += 1
else:
    failed += 1

print("\n--- School Participation ---")
db_comp = get_query_result(get_db_comparison_school_participation())
school_tab = get_query_result("""
    SELECT
        COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
        NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct
    FROM Roster r
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
""")
if compare_values("Participation %", db_comp['participation_pct'], school_tab['participation_pct'], tolerance=0.1):
    passed += 1
else:
    failed += 1

# ===========================================================================
# TEAM-LEVEL VALIDATION
# ===========================================================================
print("\n" + "#"*80)
print("# TEAM-LEVEL COMPARISONS")
print("#"*80)

print("\n--- Team Fundraising (Top Team) ---")
db_comp_results = get_query_results(get_db_comparison_team_top('fundraising'))
db_comp = db_comp_results[0] if db_comp_results else None

# Teams tab query
teams_tab = get_query_result("""
    SELECT
        r.team_name,
        COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    GROUP BY r.team_name
    ORDER BY total_fundraising DESC
    LIMIT 1
""")

if db_comp and teams_tab:
    match = True
    if not compare_values("Team Name", db_comp['team_name'], teams_tab['team_name']):
        match = False
    if not compare_values("Fundraising", db_comp['total_fundraising'], teams_tab['total_fundraising']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

print("\n--- Team Minutes (Top Team) ---")
db_comp_results = get_query_results(get_db_comparison_team_top('minutes'))
db_comp = db_comp_results[0] if db_comp_results else None

teams_tab = get_query_result("""
    SELECT
        r.team_name,
        COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
    FROM Roster r
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    WHERE dl.minutes_read > 0
    GROUP BY r.team_name
    ORDER BY total_minutes DESC
    LIMIT 1
""")

if db_comp and teams_tab:
    match = True
    if not compare_values("Team Name", db_comp['team_name'], teams_tab['team_name']):
        match = False
    if not compare_values("Minutes", db_comp['total_minutes'], teams_tab['total_minutes']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

# ===========================================================================
# GRADE-LEVEL VALIDATION
# ===========================================================================
print("\n" + "#"*80)
print("# GRADE-LEVEL COMPARISONS")
print("#"*80)

print("\n--- Grade Fundraising (Top Grade) ---")
db_comp_results = get_query_results(get_db_comparison_grade_top('fundraising'))
db_comp = db_comp_results[0] if db_comp_results else None

grade_tab = get_query_result("""
    SELECT
        r.grade_level,
        COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    GROUP BY r.grade_level
    ORDER BY total_fundraising DESC
    LIMIT 1
""")

if db_comp and grade_tab:
    match = True
    if not compare_values("Grade Level", db_comp['grade_level'], grade_tab['grade_level']):
        match = False
    if not compare_values("Fundraising", db_comp['total_fundraising'], grade_tab['total_fundraising']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

print("\n--- Grade Minutes (Top Grade) ---")
db_comp_results = get_query_results(get_db_comparison_grade_top('minutes'))
db_comp = db_comp_results[0] if db_comp_results else None

grade_tab = get_query_result("""
    SELECT
        r.grade_level,
        COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
    FROM Roster r
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    WHERE dl.minutes_read > 0
    GROUP BY r.grade_level
    ORDER BY total_minutes DESC
    LIMIT 1
""")

if db_comp and grade_tab:
    match = True
    if not compare_values("Grade Level", db_comp['grade_level'], grade_tab['grade_level']):
        match = False
    if not compare_values("Minutes", db_comp['total_minutes'], grade_tab['total_minutes']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

# ===========================================================================
# CLASS-LEVEL VALIDATION
# ===========================================================================
print("\n" + "#"*80)
print("# CLASS-LEVEL COMPARISONS")
print("#"*80)

print("\n--- Class Fundraising (Top Class) ---")
db_comp_results = get_query_results(get_db_comparison_class_top('fundraising'))
db_comp = db_comp_results[0] if db_comp_results else None

class_tab = get_query_result("""
    SELECT
        ci.class_name,
        ci.teacher_name,
        COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
    FROM Class_Info ci
    LEFT JOIN Roster r ON ci.class_name = r.class_name
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    GROUP BY ci.class_name, ci.teacher_name
    ORDER BY total_fundraising DESC
    LIMIT 1
""")

if db_comp and class_tab:
    match = True
    if not compare_values("Class Name", db_comp['class_name'], class_tab['class_name']):
        match = False
    if not compare_values("Fundraising", db_comp['total_fundraising'], class_tab['total_fundraising']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

print("\n--- Class Minutes (Top Class) ---")
db_comp_results = get_query_results(get_db_comparison_class_top('minutes'))
db_comp = db_comp_results[0] if db_comp_results else None

class_tab = get_query_result("""
    SELECT
        ci.class_name,
        ci.teacher_name,
        COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
    FROM Class_Info ci
    LEFT JOIN Roster r ON ci.class_name = r.class_name
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    WHERE dl.minutes_read > 0
    GROUP BY ci.class_name, ci.teacher_name
    ORDER BY total_minutes DESC
    LIMIT 1
""")

if db_comp and class_tab:
    match = True
    if not compare_values("Class Name", db_comp['class_name'], class_tab['class_name']):
        match = False
    if not compare_values("Minutes", db_comp['total_minutes'], class_tab['total_minutes']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

# ===========================================================================
# STUDENT-LEVEL VALIDATION
# ===========================================================================
print("\n" + "#"*80)
print("# STUDENT-LEVEL COMPARISONS")
print("#"*80)

print("\n--- Student Top Fundraiser ---")
db_comp_results = get_query_results(get_db_comparison_student_top_fundraiser())
db_comp = db_comp_results[0] if db_comp_results else None

student_tab = get_query_result("""
    SELECT
        r.student_name,
        COALESCE(rc.donation_amount, 0) as fundraising
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    ORDER BY fundraising DESC
    LIMIT 1
""")

if db_comp and student_tab:
    match = True
    if not compare_values("Student Name", db_comp['student_name'], student_tab['student_name']):
        match = False
    if not compare_values("Fundraising", db_comp['fundraising'], student_tab['fundraising']):
        match = False
    if match:
        passed += 1
    else:
        failed += 1
else:
    print("  ❌ Missing data")
    failed += 1

# ===========================================================================
# SUMMARY
# ===========================================================================
print("\n\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)
print(f"Total Comparisons: {passed + failed}")
print(f"✅ Matching: {passed}")
print(f"❌ Mismatches: {failed}")
print(f"Accuracy: {(passed/(passed+failed)*100):.1f}%")
print("="*80)

# Exit with error if any mismatches
sys.exit(0 if failed == 0 else 1)
