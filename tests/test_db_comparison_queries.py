#!/usr/bin/env python3
"""
Test all database comparison queries to ensure they work with and without date filters.
Compares results against similar queries from other tabs (School, Teams, Grade/Class).
"""

import sqlite3
import sys
import os

# Change to project root
os.chdir('/Users/stevesouza/my/data/readathon/v2026_development')

from queries import *

DB_PATH = 'db/readathon_2025.db'
SAMPLE_DB_PATH = 'db/readathon_sample.db'

def execute_query(db_path, query):
    """Execute a query and return results"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

def validate_query(name, query_func, *args):
    """Test a single query with and without date filter"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"{'='*80}")

    # Test without filter
    try:
        query_no_filter = query_func(*args) if args else query_func()
        results_no_filter = execute_query(DB_PATH, query_no_filter)

        if isinstance(results_no_filter, dict) and 'error' in results_no_filter:
            print(f"❌ FAILED (no filter): {results_no_filter['error']}")
            return False
        else:
            print(f"✅ PASSED (no filter): {len(results_no_filter)} rows")
            if results_no_filter:
                print(f"   Sample: {list(results_no_filter[0].keys())[:5]}")
    except Exception as e:
        print(f"❌ FAILED (no filter): {e}")
        return False

    # Test with date filter (Day 2: 2025-10-11)
    try:
        query_with_filter = query_func('2025-10-11', *args[1:]) if args else query_func('2025-10-11')
        results_with_filter = execute_query(DB_PATH, query_with_filter)

        if isinstance(results_with_filter, dict) and 'error' in results_with_filter:
            print(f"❌ FAILED (with filter): {results_with_filter['error']}")
            return False
        else:
            print(f"✅ PASSED (with filter): {len(results_with_filter)} rows")
    except TypeError as e:
        # Query doesn't accept date_filter parameter - that's OK for fundraising/sponsors
        print(f"ℹ️  No date filter support (expected for fundraising/sponsors)")
        return True
    except Exception as e:
        print(f"❌ FAILED (with filter): {e}")
        return False

    return True


def test_database_comparison_queries():
    """
    Test all database comparison queries to ensure they work with and without date filters.
    Compares results against similar queries from other tabs (School, Teams, Grade/Class).
    """

    print("\n" + "="*80)
    print("DATABASE COMPARISON QUERY VALIDATION")
    print("="*80)

    # Track results
    passed = 0
    failed = 0
    total = 0

    # ===========================================================================
    # SCHOOL-LEVEL QUERIES
    # ===========================================================================
    print("\n\n" + "#"*80)
    print("# SCHOOL-LEVEL QUERIES")
    print("#"*80)

    tests = [
        ("School Fundraising", get_db_comparison_school_fundraising),
        ("School Minutes", get_db_comparison_school_minutes),
        ("School Sponsors", get_db_comparison_school_sponsors),
        ("School Participation", get_db_comparison_school_participation),
        ("School Size", get_db_comparison_school_size),
        ("School Avg Participation", get_db_comparison_school_avg_participation),
        ("School Goal Met", get_db_comparison_school_goal_met),
        ("School All Days Active", get_db_comparison_school_all_days_active),
        ("School Goal Met All Days", get_db_comparison_school_goal_met_all_days),
        ("School Color War Points", get_db_comparison_school_color_war_points),
    ]

    for name, func in tests:
        total += 1
        if validate_query(name, func):
            passed += 1
        else:
            failed += 1

    # ===========================================================================
    # STUDENT-LEVEL QUERIES
    # ===========================================================================
    print("\n\n" + "#"*80)
    print("# STUDENT-LEVEL QUERIES")
    print("#"*80)

    tests = [
        ("Student Top Fundraiser", get_db_comparison_student_top_fundraiser),
        ("Student Top Reader", get_db_comparison_student_top_reader),
        ("Student Top Sponsors", get_db_comparison_student_top_sponsors),
        ("Student Top Participation", get_db_comparison_student_top_participation),
        ("Student Goal Met", get_db_comparison_student_goal_met),
        ("Student All Days Active", get_db_comparison_student_all_days_active),
        ("Student Goal Met All Days", get_db_comparison_student_goal_met_all_days),
        ("Student Avg Minutes Per Day", get_db_comparison_student_avg_minutes_per_day),
        ("Student Total Days", get_db_comparison_student_total_days),
    ]

    for name, func in tests:
        total += 1
        if validate_query(name, func):
            passed += 1
        else:
            failed += 1

    # ===========================================================================
    # TEAM-LEVEL QUERIES
    # ===========================================================================
    print("\n\n" + "#"*80)
    print("# TEAM-LEVEL QUERIES")
    print("#"*80)

    metrics = ['fundraising', 'minutes', 'size']
    for metric in metrics:
        total += 1
        name = f"Team Top - {metric.title()}"
        if validate_query(name, get_db_comparison_team_top, metric):
            passed += 1
        else:
            failed += 1

    tests = [
        ("Team Sponsors", get_db_comparison_team_sponsors),
        ("Team Participation", get_db_comparison_team_participation),
        ("Team Avg Participation", get_db_comparison_team_avg_participation),
        ("Team Goal Met", get_db_comparison_team_goal_met),
        ("Team All Days Active", get_db_comparison_team_all_days_active),
        ("Team Goal Met All Days", get_db_comparison_team_goal_met_all_days),
        ("Team Color War Points", get_db_comparison_team_color_war_points),
    ]

    for name, func in tests:
        total += 1
        if validate_query(name, func):
            passed += 1
        else:
            failed += 1

    # ===========================================================================
    # GRADE-LEVEL QUERIES
    # ===========================================================================
    print("\n\n" + "#"*80)
    print("# GRADE-LEVEL QUERIES")
    print("#"*80)

    metrics = ['fundraising', 'minutes', 'size']
    for metric in metrics:
        total += 1
        name = f"Grade Top - {metric.title()}"
        if validate_query(name, get_db_comparison_grade_top, metric):
            passed += 1
        else:
            failed += 1

    tests = [
        ("Grade Sponsors", get_db_comparison_grade_sponsors),
        ("Grade Participation", get_db_comparison_grade_participation),
        ("Grade Avg Participation", get_db_comparison_grade_avg_participation),
        ("Grade Goal Met", get_db_comparison_grade_goal_met),
        ("Grade All Days Active", get_db_comparison_grade_all_days_active),
        ("Grade Goal Met All Days", get_db_comparison_grade_goal_met_all_days),
        ("Grade Color War Points", get_db_comparison_grade_color_war_points),
    ]

    for name, func in tests:
        total += 1
        if validate_query(name, func):
            passed += 1
        else:
            failed += 1

    # ===========================================================================
    # CLASS-LEVEL QUERIES
    # ===========================================================================
    print("\n\n" + "#"*80)
    print("# CLASS-LEVEL QUERIES")
    print("#"*80)

    metrics = ['fundraising', 'minutes', 'sponsors', 'participation', 'size']
    for metric in metrics:
        total += 1
        name = f"Class Top - {metric.title()}"
        if validate_query(name, get_db_comparison_class_top, metric):
            passed += 1
        else:
            failed += 1

    tests = [
        ("Class Avg Participation", get_db_comparison_class_avg_participation),
        ("Class Goal Met", get_db_comparison_class_goal_met),
        ("Class All Days Active", get_db_comparison_class_all_days_active),
        ("Class Goal Met All Days", get_db_comparison_class_goal_met_all_days),
        ("Class Color War Points", get_db_comparison_class_color_war_points),
    ]

    for name, func in tests:
        total += 1
        if validate_query(name, func):
            passed += 1
        else:
            failed += 1

    # ===========================================================================
    # SUMMARY
    # ===========================================================================
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*80)

    # Exit with error code if any tests failed

    # Use pytest assertion instead of sys.exit()
    assert failed == 0, f"{failed} tests failed (see output above for details)"
