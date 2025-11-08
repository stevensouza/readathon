#!/usr/bin/env python3
"""
COMPLETE validation of ALL 49 database comparison queries.
Every query is validated against equivalent "ground truth" queries from actual tabs.
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from queries import *

DB_PATH = 'db/readathon_2025.db'

def get_result(query):
    """Execute query and return first row as dict"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_results(query):
    """Execute query and return all rows as list of dicts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def test_metric(num, name, db_comp_query, ground_truth_query, value_key, tolerance=0.01):
    """Test a single metric"""
    db_comp = get_result(db_comp_query)
    ground_truth = get_result(ground_truth_query)

    if not db_comp or not ground_truth:
        print(f"{num}. ❌ {name}: Missing data")
        return False

    db_val = db_comp.get(value_key)
    gt_val = ground_truth.get(value_key)

    if isinstance(db_val, float) and isinstance(gt_val, float):
        if abs(db_val - gt_val) <= tolerance:
            print(f"{num}. ✅ {name}: {db_val:.2f}")
            return True
        else:
            print(f"{num}. ❌ {name}: DB={db_val:.2f}, GroundTruth={gt_val:.2f}")
            return False
    elif db_val == gt_val:
        print(f"{num}. ✅ {name}: {db_val}")
        return True
    else:
        print(f"{num}. ❌ {name}: DB={db_val}, GroundTruth={gt_val}")
        return False

def test_top_winner(num, name, db_comp_query, ground_truth_query, entity_key, value_key, tolerance=0.01):
    """Test queries that return top winner (handles ties)"""
    db_comp_list = get_results(db_comp_query)
    ground_truth_list = get_results(ground_truth_query)

    if not db_comp_list or not ground_truth_list:
        print(f"{num}. ❌ {name}: Missing data")
        return False

    # Verify tie count matches
    if len(db_comp_list) != len(ground_truth_list):
        print(f"{num}. ❌ {name}: Tie count mismatch - DB={len(db_comp_list)}, GT={len(ground_truth_list)}")
        return False

    db_comp = db_comp_list[0]
    ground_truth = ground_truth_list[0]

    db_entity = db_comp.get(entity_key)
    gt_entity = ground_truth.get(entity_key)
    db_val = db_comp.get(value_key)
    gt_val = ground_truth.get(value_key)

    if db_entity != gt_entity:
        print(f"{num}. ❌ {name}: Winner DB={db_entity}, GT={gt_entity}")
        return False

    if isinstance(db_val, float) and isinstance(gt_val, float):
        if abs(db_val - gt_val) <= tolerance:
            print(f"{num}. ✅ {name}: {db_entity} = {db_val:.2f}")
            return True
        else:
            print(f"{num}. ❌ {name}: {db_entity} DB={db_val:.2f}, GT={gt_val:.2f}")
            return False
    elif db_val == gt_val:
        print(f"{num}. ✅ {name}: {db_entity} = {db_val}")
        return True
    else:
        print(f"{num}. ❌ {name}: {db_entity} DB={db_val}, GT={gt_val}")
        return False

print("\n" + "="*80)
print("COMPLETE DATABASE COMPARISON VALIDATION - ALL 49 QUERIES")
print("="*80)

passed = 0
failed = 0

# ===========================================================================
# SCHOOL-LEVEL (10 queries)
# ===========================================================================
print("\n" + "#"*80)
print("# SCHOOL-LEVEL (10 queries)")
print("#"*80 + "\n")

if test_metric(1, "School Fundraising", get_db_comparison_school_fundraising(),
    "SELECT COALESCE(SUM(donation_amount), 0) as total_fundraising FROM Reader_Cumulative",
    'total_fundraising'):
    passed += 1
else:
    failed += 1

if test_metric(2, "School Minutes", get_db_comparison_school_minutes(),
    "SELECT COALESCE(SUM(CASE WHEN minutes_read > 120 THEN 120 ELSE minutes_read END), 0) as total_minutes FROM Daily_Logs WHERE minutes_read > 0",
    'total_minutes'):
    passed += 1
else:
    failed += 1

if test_metric(3, "School Sponsors", get_db_comparison_school_sponsors(),
    "SELECT COALESCE(SUM(sponsors), 0) as total_sponsors FROM Reader_Cumulative",
    'total_sponsors'):
    passed += 1
else:
    failed += 1

if test_metric(4, "School Participation", get_db_comparison_school_participation(),
    "SELECT COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name",
    'participation_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_metric(5, "School Size", get_db_comparison_school_size(),
    "SELECT COUNT(DISTINCT student_name) as student_count FROM Roster",
    'student_count'):
    passed += 1
else:
    failed += 1

if test_metric(6, "School Avg Participation", get_db_comparison_school_avg_participation(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs)
       SELECT ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) /
              (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_pct_base
       FROM Roster r CROSS JOIN TotalDays td LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name""",
    'avg_participation_pct_base', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_metric(7, "School Goal Met", get_db_comparison_school_goal_met(),
    """WITH StudentGoals AS (
           SELECT r.student_name, MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
           FROM Roster r
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.student_name
       )
       SELECT ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct FROM StudentGoals""",
    'goal_met_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_metric(8, "School All Days Active", get_db_comparison_school_all_days_active(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       AllDaysStudents AS (
           SELECT r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.student_name, td.total_days
           HAVING COUNT(DISTINCT dl.log_date) = td.total_days
       )
       SELECT ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Roster), 2) as all_days_active_pct FROM AllDaysStudents""",
    'all_days_active_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_metric(9, "School Goal Met All Days", get_db_comparison_school_goal_met_all_days(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       GoalAllDaysStudents AS (
           SELECT r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.student_name, td.total_days
           HAVING COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) = td.total_days
       )
       SELECT ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Roster), 2) as goal_met_all_days_pct FROM GoalAllDaysStudents""",
    'goal_met_all_days_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_metric(10, "School Color War Points", get_db_comparison_school_color_war_points(),
    """WITH BasePoints AS (
           SELECT COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
           FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       ),
       BonusPoints AS (
           SELECT COALESCE(SUM(bonus_participation_points), 0) as bonus_points FROM Team_Color_Bonus
       )
       SELECT bp.base_points + bop.bonus_points as total_points FROM BasePoints bp, BonusPoints bop""",
    'total_points'):
    passed += 1
else:
    failed += 1

# ===========================================================================
# STUDENT-LEVEL (9 queries)
# ===========================================================================
print("\n" + "#"*80)
print("# STUDENT-LEVEL (9 queries)")
print("#"*80 + "\n")

if test_top_winner(11, "Student Top Fundraiser", get_db_comparison_student_top_fundraiser(),
    """SELECT r.student_name, COALESCE(rc.donation_amount, 0) as fundraising
       FROM Roster r
       LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       WHERE COALESCE(rc.donation_amount, 0) = (
           SELECT MAX(COALESCE(donation_amount, 0)) FROM Reader_Cumulative
       )
       ORDER BY r.student_name""",
    'student_name', 'fundraising'):
    passed += 1
else:
    failed += 1

if test_top_winner(12, "Student Top Reader", get_db_comparison_student_top_reader(),
    """SELECT r.student_name, COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
       FROM Roster r
       LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       WHERE dl.minutes_read > 0
       GROUP BY r.student_name
       HAVING total_minutes = (
           SELECT MAX(total_minutes) FROM (
               SELECT COALESCE(SUM(CASE WHEN minutes_read > 120 THEN 120 ELSE minutes_read END), 0) as total_minutes
               FROM Daily_Logs WHERE minutes_read > 0 GROUP BY student_name
           )
       )
       ORDER BY r.student_name""",
    'student_name', 'total_minutes'):
    passed += 1
else:
    failed += 1

if test_top_winner(13, "Student Top Sponsors", get_db_comparison_student_top_sponsors(),
    """SELECT r.student_name, COALESCE(rc.sponsors, 0) as sponsor_count
       FROM Roster r
       LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       WHERE COALESCE(rc.sponsors, 0) = (
           SELECT MAX(COALESCE(sponsors, 0)) FROM Reader_Cumulative
       )
       ORDER BY r.student_name""",
    'student_name', 'sponsor_count'):
    passed += 1
else:
    failed += 1

if test_top_winner(14, "Student Top Participation", get_db_comparison_student_top_participation(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       StudentParticipation AS (
           SELECT r.student_name, COUNT(DISTINCT dl.log_date) * 100.0 / td.total_days as participation_pct
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.student_name, td.total_days
       )
       SELECT student_name, participation_pct FROM StudentParticipation
       WHERE participation_pct = (SELECT MAX(participation_pct) FROM StudentParticipation)
       ORDER BY student_name""",
    'student_name', 'participation_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(15, "Student Goal Met (Days)", get_db_comparison_student_goal_met(),
    """WITH StudentGoals AS (
           SELECT r.student_name, COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
           FROM Roster r
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           WHERE dl.minutes_read > 0
           GROUP BY r.student_name
       )
       SELECT student_name, days_met_goal FROM StudentGoals
       WHERE days_met_goal = (SELECT MAX(days_met_goal) FROM StudentGoals)
       ORDER BY student_name""",
    'student_name', 'days_met_goal'):
    passed += 1
else:
    failed += 1

# Test 16-19: These return tied winners, verify top value matches
db_comp = get_results(get_db_comparison_student_all_days_active())
ground_truth = get_results("""
    WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs)
    SELECT r.student_name
    FROM Roster r CROSS JOIN TotalDays td
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    WHERE dl.minutes_read > 0
    GROUP BY r.student_name, td.total_days
    HAVING COUNT(DISTINCT dl.log_date) = td.total_days
    ORDER BY r.student_name
""")
if db_comp and ground_truth and len(db_comp) == len(ground_truth):
    print(f"16. ✅ Student All Days Active: {len(db_comp)} students (matches)")
    passed += 1
else:
    print(f"16. ❌ Student All Days Active: DB={len(db_comp) if db_comp else 0}, GT={len(ground_truth) if ground_truth else 0}")
    failed += 1

db_comp = get_results(get_db_comparison_student_goal_met_all_days())
ground_truth = get_results("""
    WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs)
    SELECT r.student_name
    FROM Roster r CROSS JOIN TotalDays td
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
    GROUP BY r.student_name, td.total_days
    HAVING COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) = td.total_days
    ORDER BY r.student_name
""")
if db_comp and ground_truth and len(db_comp) == len(ground_truth):
    print(f"17. ✅ Student Goal Met All Days: {len(db_comp)} students (matches)")
    passed += 1
else:
    print(f"17. ❌ Student Goal Met All Days: DB={len(db_comp) if db_comp else 0}, GT={len(ground_truth) if ground_truth else 0}")
    failed += 1

if test_top_winner(18, "Student Avg Minutes/Day", get_db_comparison_student_avg_minutes_per_day(),
    """WITH StudentAvgMinutes AS (
           SELECT r.student_name, ROUND(COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) * 1.0 /
                  NULLIF(COUNT(DISTINCT dl.log_date), 0), 2) as avg_minutes_per_day
           FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.student_name
       )
       SELECT student_name, avg_minutes_per_day FROM StudentAvgMinutes
       WHERE avg_minutes_per_day = (SELECT MAX(avg_minutes_per_day) FROM StudentAvgMinutes)
       ORDER BY student_name""",
    'student_name', 'avg_minutes_per_day'):
    passed += 1
else:
    failed += 1

if test_top_winner(19, "Student Total Days", get_db_comparison_student_total_days(),
    """WITH StudentTotalDays AS (
           SELECT r.student_name, COUNT(DISTINCT dl.log_date) as total_days
           FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.student_name
       )
       SELECT student_name, total_days FROM StudentTotalDays
       WHERE total_days = (SELECT MAX(total_days) FROM StudentTotalDays)
       ORDER BY student_name""",
    'student_name', 'total_days'):
    passed += 1
else:
    failed += 1

# ===========================================================================
# TEAM-LEVEL (10 queries)
# ===========================================================================
print("\n" + "#"*80)
print("# TEAM-LEVEL (10 queries)")
print("#"*80 + "\n")

if test_top_winner(20, "Team Fundraising", get_db_comparison_team_top('fundraising'),
    """SELECT r.team_name, COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
       FROM Roster r LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       GROUP BY r.team_name ORDER BY total_fundraising DESC LIMIT 1""",
    'team_name', 'total_fundraising'):
    passed += 1
else:
    failed += 1

if test_top_winner(21, "Team Minutes", get_db_comparison_team_top('minutes'),
    """SELECT r.team_name, COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
       FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       WHERE dl.minutes_read > 0
       GROUP BY r.team_name ORDER BY total_minutes DESC LIMIT 1""",
    'team_name', 'total_minutes'):
    passed += 1
else:
    failed += 1

if test_top_winner(22, "Team Size", get_db_comparison_team_top('size'),
    """SELECT r.team_name, COUNT(DISTINCT r.student_name) as student_count
       FROM Roster r GROUP BY r.team_name ORDER BY student_count DESC LIMIT 1""",
    'team_name', 'student_count'):
    passed += 1
else:
    failed += 1

if test_top_winner(23, "Team Sponsors", get_db_comparison_team_sponsors(),
    """SELECT r.team_name, COALESCE(SUM(rc.sponsors), 0) as total_sponsors
       FROM Roster r LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       GROUP BY r.team_name ORDER BY total_sponsors DESC LIMIT 1""",
    'team_name', 'total_sponsors'):
    passed += 1
else:
    failed += 1

if test_top_winner(24, "Team Participation", get_db_comparison_team_participation(),
    """SELECT r.team_name, COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
           NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct
       FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       GROUP BY r.team_name ORDER BY participation_pct DESC LIMIT 1""",
    'team_name', 'participation_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(25, "Team Avg Participation", get_db_comparison_team_avg_participation(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       TeamBonusData AS (
           SELECT ci.team_name, SUM(tcb.bonus_participation_points) as total_bonus
           FROM Team_Color_Bonus tcb
           INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
           GROUP BY ci.team_name
       )
       SELECT r.team_name,
              ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(tbd.total_bonus, 0)) /
                    (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_with_color
       FROM Roster r CROSS JOIN TotalDays td
       LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       LEFT JOIN TeamBonusData tbd ON r.team_name = tbd.team_name
       WHERE td.total_days > 0
       GROUP BY r.team_name, td.total_days, tbd.total_bonus
       ORDER BY avg_participation_with_color DESC LIMIT 1""",
    'team_name', 'avg_participation_with_color', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(26, "Team Goal Met", get_db_comparison_team_goal_met(),
    """WITH TeamStudentGoals AS (
           SELECT r.team_name, r.student_name,
                  MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
           FROM Roster r
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.team_name, r.student_name
       )
       SELECT team_name, ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct
       FROM TeamStudentGoals GROUP BY team_name ORDER BY goal_met_pct DESC LIMIT 1""",
    'team_name', 'goal_met_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(27, "Team All Days Active", get_db_comparison_team_all_days_active(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       TeamAllDaysStudents AS (
           SELECT r.team_name, r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.team_name, r.student_name, td.total_days
           HAVING COUNT(DISTINCT dl.log_date) = td.total_days
       ),
       TeamTotals AS (
           SELECT team_name, COUNT(*) as all_days_count
           FROM TeamAllDaysStudents GROUP BY team_name
       )
       SELECT r.team_name, ROUND(COALESCE(tt.all_days_count, 0) * 100.0 / COUNT(DISTINCT r.student_name), 2) as all_days_active_pct
       FROM Roster r
       LEFT JOIN TeamTotals tt ON r.team_name = tt.team_name
       GROUP BY r.team_name, tt.all_days_count
       ORDER BY all_days_active_pct DESC LIMIT 1""",
    'team_name', 'all_days_active_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(28, "Team Goal Met All Days", get_db_comparison_team_goal_met_all_days(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       TeamGoalAllDaysStudents AS (
           SELECT r.team_name, r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.team_name, r.student_name, td.total_days
           HAVING COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) = td.total_days
       ),
       TeamTotals AS (
           SELECT team_name, COUNT(*) as goal_all_days_count
           FROM TeamGoalAllDaysStudents GROUP BY team_name
       )
       SELECT r.team_name, ROUND(COALESCE(tt.goal_all_days_count, 0) * 100.0 / COUNT(DISTINCT r.student_name), 2) as goal_met_all_days_pct
       FROM Roster r
       LEFT JOIN TeamTotals tt ON r.team_name = tt.team_name
       GROUP BY r.team_name, tt.goal_all_days_count
       ORDER BY goal_met_all_days_pct DESC LIMIT 1""",
    'team_name', 'goal_met_all_days_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(29, "Team Color War Points", get_db_comparison_team_color_war_points(),
    """WITH TeamBasePoints AS (
           SELECT r.team_name,
                  COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
           FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           GROUP BY r.team_name
       ),
       TeamBonusPoints AS (
           SELECT ci.team_name, COALESCE(SUM(tcb.bonus_participation_points), 0) as bonus_points
           FROM Team_Color_Bonus tcb
           INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
           GROUP BY ci.team_name
       )
       SELECT tbp.team_name, tbp.base_points + COALESCE(tbo.bonus_points, 0) as total_points
       FROM TeamBasePoints tbp
       LEFT JOIN TeamBonusPoints tbo ON tbp.team_name = tbo.team_name
       ORDER BY total_points DESC LIMIT 1""",
    'team_name', 'total_points'):
    passed += 1
else:
    failed += 1

# ===========================================================================
# GRADE-LEVEL (10 queries)
# ===========================================================================
print("\n" + "#"*80)
print("# GRADE-LEVEL (10 queries)")
print("#"*80 + "\n")

if test_top_winner(30, "Grade Fundraising", get_db_comparison_grade_top('fundraising'),
    """SELECT r.grade_level, COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
       FROM Roster r LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       GROUP BY r.grade_level ORDER BY total_fundraising DESC LIMIT 1""",
    'grade_level', 'total_fundraising'):
    passed += 1
else:
    failed += 1

if test_top_winner(31, "Grade Minutes", get_db_comparison_grade_top('minutes'),
    """SELECT r.grade_level, COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
       FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       WHERE dl.minutes_read > 0
       GROUP BY r.grade_level ORDER BY total_minutes DESC LIMIT 1""",
    'grade_level', 'total_minutes'):
    passed += 1
else:
    failed += 1

if test_top_winner(32, "Grade Size", get_db_comparison_grade_top('size'),
    """SELECT r.grade_level, COUNT(DISTINCT r.student_name) as student_count
       FROM Roster r GROUP BY r.grade_level ORDER BY student_count DESC LIMIT 1""",
    'grade_level', 'student_count'):
    passed += 1
else:
    failed += 1

if test_top_winner(33, "Grade Sponsors", get_db_comparison_grade_sponsors(),
    """SELECT r.grade_level, COALESCE(SUM(rc.sponsors), 0) as total_sponsors
       FROM Roster r LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       GROUP BY r.grade_level ORDER BY total_sponsors DESC LIMIT 1""",
    'grade_level', 'total_sponsors'):
    passed += 1
else:
    failed += 1

if test_top_winner(34, "Grade Participation", get_db_comparison_grade_participation(),
    """SELECT r.grade_level, COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
           NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct
       FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       GROUP BY r.grade_level ORDER BY participation_pct DESC LIMIT 1""",
    'grade_level', 'participation_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(35, "Grade Avg Participation", get_db_comparison_grade_avg_participation(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       GradeBonusData AS (
           SELECT ci.grade_level, SUM(tcb.bonus_participation_points) as total_bonus
           FROM Team_Color_Bonus tcb
           INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
           GROUP BY ci.grade_level
       )
       SELECT r.grade_level,
              ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(gbd.total_bonus, 0)) /
                    (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_with_color
       FROM Roster r CROSS JOIN TotalDays td
       LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       LEFT JOIN GradeBonusData gbd ON r.grade_level = gbd.grade_level
       WHERE td.total_days > 0
       GROUP BY r.grade_level, td.total_days, gbd.total_bonus
       ORDER BY avg_participation_with_color DESC LIMIT 1""",
    'grade_level', 'avg_participation_with_color', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(36, "Grade Goal Met", get_db_comparison_grade_goal_met(),
    """WITH GradeStudentGoals AS (
           SELECT r.grade_level, r.student_name,
                  MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
           FROM Roster r
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.grade_level, r.student_name
       )
       SELECT grade_level, ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct
       FROM GradeStudentGoals GROUP BY grade_level ORDER BY goal_met_pct DESC LIMIT 1""",
    'grade_level', 'goal_met_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(37, "Grade All Days Active", get_db_comparison_grade_all_days_active(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       GradeAllDaysStudents AS (
           SELECT r.grade_level, r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.grade_level, r.student_name, td.total_days
           HAVING COUNT(DISTINCT dl.log_date) = td.total_days
       ),
       GradeTotals AS (
           SELECT grade_level, COUNT(*) as all_days_count
           FROM GradeAllDaysStudents GROUP BY grade_level
       )
       SELECT r.grade_level, ROUND(COALESCE(gt.all_days_count, 0) * 100.0 / COUNT(DISTINCT r.student_name), 2) as all_days_active_pct
       FROM Roster r
       LEFT JOIN GradeTotals gt ON r.grade_level = gt.grade_level
       GROUP BY r.grade_level, gt.all_days_count
       ORDER BY all_days_active_pct DESC LIMIT 1""",
    'grade_level', 'all_days_active_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(38, "Grade Goal Met All Days", get_db_comparison_grade_goal_met_all_days(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       GradeGoalAllDaysStudents AS (
           SELECT r.grade_level, r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.grade_level, r.student_name, td.total_days
           HAVING COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) = td.total_days
       ),
       GradeTotals AS (
           SELECT grade_level, COUNT(*) as goal_all_days_count
           FROM GradeGoalAllDaysStudents GROUP BY grade_level
       )
       SELECT r.grade_level, ROUND(COALESCE(gt.goal_all_days_count, 0) * 100.0 / COUNT(DISTINCT r.student_name), 2) as goal_met_all_days_pct
       FROM Roster r
       LEFT JOIN GradeTotals gt ON r.grade_level = gt.grade_level
       GROUP BY r.grade_level, gt.goal_all_days_count
       ORDER BY goal_met_all_days_pct DESC LIMIT 1""",
    'grade_level', 'goal_met_all_days_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(39, "Grade Color War Points", get_db_comparison_grade_color_war_points(),
    """WITH GradeBasePoints AS (
           SELECT r.grade_level,
                  COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
           FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           GROUP BY r.grade_level
       ),
       GradeBonusPoints AS (
           SELECT ci.grade_level, COALESCE(SUM(tcb.bonus_participation_points), 0) as bonus_points
           FROM Class_Info ci
           LEFT JOIN Team_Color_Bonus tcb ON ci.class_name = tcb.class_name
           GROUP BY ci.grade_level
       )
       SELECT gbp.grade_level, gbp.base_points + COALESCE(gbo.bonus_points, 0) as total_points
       FROM GradeBasePoints gbp
       LEFT JOIN GradeBonusPoints gbo ON gbp.grade_level = gbo.grade_level
       ORDER BY total_points DESC LIMIT 1""",
    'grade_level', 'total_points'):
    passed += 1
else:
    failed += 1

# ===========================================================================
# CLASS-LEVEL (10 queries)
# ===========================================================================
print("\n" + "#"*80)
print("# CLASS-LEVEL (10 queries)")
print("#"*80 + "\n")

if test_top_winner(40, "Class Fundraising", get_db_comparison_class_top('fundraising'),
    """SELECT ci.class_name, COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
       FROM Class_Info ci
       LEFT JOIN Roster r ON ci.class_name = r.class_name
       LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       GROUP BY ci.class_name ORDER BY total_fundraising DESC LIMIT 1""",
    'class_name', 'total_fundraising'):
    passed += 1
else:
    failed += 1

if test_top_winner(41, "Class Minutes", get_db_comparison_class_top('minutes'),
    """SELECT ci.class_name, COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
       FROM Class_Info ci
       LEFT JOIN Roster r ON ci.class_name = r.class_name
       LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       WHERE dl.minutes_read > 0
       GROUP BY ci.class_name ORDER BY total_minutes DESC LIMIT 1""",
    'class_name', 'total_minutes'):
    passed += 1
else:
    failed += 1

if test_top_winner(42, "Class Sponsors", get_db_comparison_class_top('sponsors'),
    """SELECT ci.class_name, COALESCE(SUM(rc.sponsors), 0) as total_sponsors
       FROM Class_Info ci
       LEFT JOIN Roster r ON ci.class_name = r.class_name
       LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
       GROUP BY ci.class_name ORDER BY total_sponsors DESC LIMIT 1""",
    'class_name', 'total_sponsors'):
    passed += 1
else:
    failed += 1

if test_top_winner(43, "Class Participation", get_db_comparison_class_participation(),
    """SELECT ci.class_name, COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
           NULLIF(ci.total_students, 0) as participation_pct
       FROM Class_Info ci
       LEFT JOIN Roster r ON ci.class_name = r.class_name
       LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       GROUP BY ci.class_name, ci.total_students
       ORDER BY participation_pct DESC LIMIT 1""",
    'class_name', 'participation_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(44, "Class Size", get_db_comparison_class_top('size'),
    """SELECT ci.class_name, ci.total_students
       FROM Class_Info ci ORDER BY total_students DESC LIMIT 1""",
    'class_name', 'total_students'):
    passed += 1
else:
    failed += 1

if test_top_winner(45, "Class Avg Participation", get_db_comparison_class_avg_participation(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       ClassBonusData AS (
           SELECT class_name, SUM(bonus_participation_points) as total_bonus
           FROM Team_Color_Bonus
           GROUP BY class_name
       )
       SELECT ci.class_name,
              ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(cbd.total_bonus, 0)) /
                    (ci.total_students * td.total_days), 2) as avg_participation_with_color
       FROM Class_Info ci
       CROSS JOIN TotalDays td
       LEFT JOIN Roster r ON ci.class_name = r.class_name
       LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
       LEFT JOIN ClassBonusData cbd ON ci.class_name = cbd.class_name
       WHERE td.total_days > 0
       GROUP BY ci.class_name, ci.total_students, td.total_days, cbd.total_bonus
       ORDER BY avg_participation_with_color DESC LIMIT 1""",
    'class_name', 'avg_participation_with_color', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(46, "Class Goal Met", get_db_comparison_class_goal_met(),
    """WITH ClassStudentGoals AS (
           SELECT r.class_name, r.student_name,
                  MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
           FROM Roster r
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.class_name, r.student_name
       )
       SELECT class_name, ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct
       FROM ClassStudentGoals GROUP BY class_name ORDER BY goal_met_pct DESC LIMIT 1""",
    'class_name', 'goal_met_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(47, "Class All Days Active", get_db_comparison_class_all_days_active(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       ClassAllDaysStudents AS (
           SELECT r.class_name, r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           WHERE dl.minutes_read > 0
           GROUP BY r.class_name, r.student_name, td.total_days
           HAVING COUNT(DISTINCT dl.log_date) = td.total_days
       ),
       ClassTotals AS (
           SELECT class_name, COUNT(*) as all_days_count
           FROM ClassAllDaysStudents GROUP BY class_name
       )
       SELECT ci.class_name, ROUND(COALESCE(ct.all_days_count, 0) * 100.0 / ci.total_students, 2) as all_days_active_pct
       FROM Class_Info ci
       LEFT JOIN ClassTotals ct ON ci.class_name = ct.class_name
       ORDER BY all_days_active_pct DESC LIMIT 1""",
    'class_name', 'all_days_active_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(48, "Class Goal Met All Days", get_db_comparison_class_goal_met_all_days(),
    """WITH TotalDays AS (SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs),
       ClassGoalAllDaysStudents AS (
           SELECT r.class_name, r.student_name
           FROM Roster r CROSS JOIN TotalDays td
           LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
           GROUP BY r.class_name, r.student_name, td.total_days
           HAVING COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) = td.total_days
       ),
       ClassTotals AS (
           SELECT class_name, COUNT(*) as goal_all_days_count
           FROM ClassGoalAllDaysStudents GROUP BY class_name
       )
       SELECT ci.class_name, ROUND(COALESCE(ct.goal_all_days_count, 0) * 100.0 / ci.total_students, 2) as goal_met_all_days_pct
       FROM Class_Info ci
       LEFT JOIN ClassTotals ct ON ci.class_name = ct.class_name
       ORDER BY goal_met_all_days_pct DESC LIMIT 1""",
    'class_name', 'goal_met_all_days_pct', tolerance=0.1):
    passed += 1
else:
    failed += 1

if test_top_winner(49, "Class Color War Points", get_db_comparison_class_color_war_points(),
    """WITH ClassBasePoints AS (
           SELECT r.class_name,
                  COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
           FROM Roster r LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
           GROUP BY r.class_name
       ),
       ClassBonusPoints AS (
           SELECT class_name, COALESCE(SUM(bonus_participation_points), 0) as bonus_points
           FROM Team_Color_Bonus GROUP BY class_name
       )
       SELECT cbp.class_name, cbp.base_points + COALESCE(cbo.bonus_points, 0) as total_points
       FROM ClassBasePoints cbp
       LEFT JOIN ClassBonusPoints cbo ON cbp.class_name = cbo.class_name
       ORDER BY total_points DESC LIMIT 1""",
    'class_name', 'total_points'):
    passed += 1
else:
    failed += 1

# ===========================================================================
# SUMMARY
# ===========================================================================
print("\n\n" + "="*80)
print("FINAL VALIDATION SUMMARY")
print("="*80)
print(f"Total Queries: 49")
print(f"✅ Validated & Matching: {passed}")
print(f"❌ Mismatches: {failed}")
print(f"Accuracy: {(passed/49)*100:.1f}%")
print("="*80)

if failed == 0:
    print("\n🎉 SUCCESS! All 49 database comparison queries return correct data!")
else:
    print(f"\n⚠️  {failed} queries need fixing")

sys.exit(0 if failed == 0 else 1)
