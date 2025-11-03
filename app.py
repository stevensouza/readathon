"""
Read-a-Thon Web Application
Flask-based browser interface for managing and reporting on read-a-thon data
"""

from flask import Flask, render_template, request, jsonify, send_file, Response, session
from database import ReadathonDB, ReportGenerator
from queries import get_grade_level_classes_query, get_grade_aggregations_query, get_school_wide_leaders_query
import csv
import io
from datetime import datetime
import os
import argparse
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'readathon-secret-key-change-in-production'  # For session management

# Configuration file for persistent database preference
CONFIG_FILE = '.readathon_config'

def read_config():
    """Read configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('default_database', 'sample')
        except:
            return 'sample'
    return 'sample'

def write_config(database):
    """Write configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'default_database': database}, f)
    except:
        pass  # Silently fail if can't write config

# Parse command line arguments
parser = argparse.ArgumentParser(description='Read-a-Thon Management System')
parser.add_argument('--db', choices=['sample', 'prod'],
                   help='Database to use (sample or prod). Overrides config file.')
args, unknown = parser.parse_known_args()

# Determine default database: CLI > Config File > 'sample'
DEFAULT_DATABASE = args.db if args.db else read_config()

# Persist the database choice for next startup
write_config(DEFAULT_DATABASE)

print(f"🗄️  Starting with database: {DEFAULT_DATABASE}")
if args.db:
    print(f"   (Specified via command line: --db {args.db})")
else:
    print(f"   (Using remembered preference from {CONFIG_FILE})")

# Initialize databases for both environments
db_prod = ReadathonDB('readathon_prod.db')
db_sample = ReadathonDB('readathon_sample.db')

def get_current_db():
    """Get the database based on current environment selection"""
    env = session.get('environment', DEFAULT_DATABASE)
    return db_prod if env == 'prod' else db_sample

def get_current_reports():
    """Get report generator for current environment"""
    return ReportGenerator(get_current_db())


@app.route('/')
@app.route('/school')
def school_tab():
    """School overview dashboard (landing page)"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()
    reports = get_current_reports()

    # Get filter parameter (optional)
    date_filter = request.args.get('date', 'all')

    # Get all available dates
    dates = db.get_all_dates()

    # Build WHERE clause based on filter (cumulative through selected date)
    date_where = ""
    date_where_no_alias = ""  # For subqueries without table alias
    if date_filter != 'all' and date_filter in dates:
        date_where = f"AND dl.log_date <= '{date_filter}'"
        date_where_no_alias = f"AND log_date <= '{date_filter}'"

    # Get total roster count
    roster_query = "SELECT COUNT(*) as total FROM Roster"
    roster_result = db.execute_query(roster_query)
    total_roster = roster_result[0]['total'] if roster_result else 411

    # === METRICS BANNER ===
    metrics = {}

    # Calculate full contest date range (always shown in dropdown, regardless of filter)
    sorted_dates = sorted(dates)  # Oldest to newest
    total_days = len(sorted_dates)  # Total number of days in contest

    if sorted_dates:
        start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').strftime('%b %d')
        end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').strftime('%b %d, %Y')
        full_contest_range = f"{start_date}-{end_date}"
    else:
        full_contest_range = "Oct 10-15, 2025"  # Fallback if no dates

    # Current day calculation - date-aware
    if date_filter != 'all' and date_filter in dates:
        # Find position of selected date (1-based)
        metrics['current_day'] = sorted_dates.index(date_filter) + 1
        metrics['campaign_date'] = date_filter  # Store for subtitle display
    else:
        # Full contest - show total days
        metrics['current_day'] = total_days
        metrics['campaign_date'] = full_contest_range

    metrics['total_days'] = total_days
    metrics['total_roster'] = total_roster

    # Fundraising metrics
    fundraising_query = f"""
        SELECT
            COALESCE(SUM(rc.donation_amount), 0) as total_fundraising,
            COUNT(DISTINCT CASE WHEN rc.donation_amount > 0 THEN rc.student_name END) as fundraising_students
        FROM Reader_Cumulative rc
    """
    fundraising_result = db.execute_query(fundraising_query)
    if fundraising_result and fundraising_result[0]:
        metrics['total_fundraising'] = fundraising_result[0]['total_fundraising'] or 0
        metrics['fundraising_students'] = fundraising_result[0]['fundraising_students'] or 0
    else:
        metrics['total_fundraising'] = 0
        metrics['fundraising_students'] = 0

    metrics['fundraising_pct'] = (metrics['fundraising_students'] / total_roster * 100) if total_roster > 0 else 0

    # Reading minutes (capped at 120 per day) + Team Color Bonus
    reading_query = f"""
        WITH TeamColorBonus AS (
            SELECT COALESCE(SUM(bonus_minutes), 0) as total_bonus
            FROM Team_Color_Bonus
        )
        SELECT
            SUM(MIN(dl.minutes_read, 120)) as total_minutes_base,
            (SELECT total_bonus FROM TeamColorBonus) as bonus_minutes,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) as participating_students
        FROM Daily_Logs dl
        WHERE 1=1 {date_where}
    """
    reading_result = db.execute_query(reading_query)
    if reading_result and reading_result[0]:
        base_minutes = int(reading_result[0]['total_minutes_base'] or 0)
        bonus_minutes = int(reading_result[0]['bonus_minutes'] or 0)
        metrics['total_minutes'] = base_minutes + bonus_minutes
        metrics['participating_students'] = reading_result[0]['participating_students'] or 0
    else:
        metrics['total_minutes'] = 0
        metrics['participating_students'] = 0

    metrics['total_hours'] = metrics['total_minutes'] // 60
    metrics['participation_pct'] = (metrics['participating_students'] / total_roster * 100) if total_roster > 0 else 0

    # Average Daily Participation (With Color) - school-wide
    # Calculate average daily participation percentage across all students
    school_participation_query = f"""
        SELECT
            AVG(daily_pct) as avg_participation
        FROM (
            SELECT
                dl.log_date,
                (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / {total_roster}) as daily_pct
            FROM Daily_Logs dl
            WHERE 1=1 {date_where}
            GROUP BY dl.log_date
        )
    """
    school_participation_result = db.execute_query(school_participation_query)
    base_school_participation = school_participation_result[0]['avg_participation'] or 0 if school_participation_result and school_participation_result[0] else 0

    # Get total color bonus points across all classes
    school_color_bonus_query = """
        SELECT COALESCE(SUM(bonus_participation_points), 0) as total_bonus
        FROM Team_Color_Bonus
    """
    school_color_bonus_result = db.execute_query(school_color_bonus_query)
    school_color_bonus = school_color_bonus_result[0]['total_bonus'] if school_color_bonus_result and school_color_bonus_result[0] else 0

    # Calculate total days in date range for color bonus calculation
    total_days_query = f"""
        SELECT COUNT(DISTINCT dl.log_date) as total_days
        FROM Daily_Logs dl
        WHERE 1=1 {date_where}
    """
    total_days_result = db.execute_query(total_days_query)
    total_days = total_days_result[0]['total_days'] if total_days_result and total_days_result[0] else 1

    # Apply color bonus: color points act as "free" participation days
    metrics['avg_participation_with_color'] = base_school_participation + (school_color_bonus * 100.0 / (total_roster * total_days)) if total_roster > 0 and total_days > 0 else base_school_participation

    # Goals met calculation
    goals_met_query = f"""
        SELECT
            COUNT(DISTINCT dl.student_name) as goals_met_students
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE dl.minutes_read >= gr.min_daily_minutes {date_where}
    """
    goals_met_result = db.execute_query(goals_met_query)
    if goals_met_result and goals_met_result[0]:
        metrics['goals_met_students'] = goals_met_result[0]['goals_met_students'] or 0
    else:
        metrics['goals_met_students'] = 0

    metrics['goals_met_pct'] = (metrics['goals_met_students'] / total_roster * 100) if total_roster > 0 else 0

    # === TEAM COMPETITION ===
    # Get actual team names from database (sorted alphabetically for consistency)
    team_names_query = "SELECT DISTINCT team_name FROM Roster ORDER BY team_name"
    team_names_result = db.execute_query(team_names_query)
    team_names = [row['team_name'] for row in team_names_result] if team_names_result else []

    # Ensure we have exactly 2 teams
    if len(team_names) != 2:
        return jsonify({'error': f'Expected 2 teams, found {len(team_names)}'}), 500

    team1_name = team_names[0]  # First team alphabetically
    team2_name = team_names[1]  # Second team alphabetically

    teams = {}

    # Team 1 (cumulative through selected date)
    team1_where = f"AND dl.log_date <= '{date_filter}'" if date_filter != 'all' and date_filter in dates else ""

    # Separate query for fundraising to avoid row multiplication from Daily_Logs join
    team1_fundraising_query = f"""
        SELECT
            COALESCE(SUM(rc.donation_amount), 0) as fundraising
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        WHERE LOWER(r.team_name) = LOWER('{team1_name}')
    """
    team1_fundraising_result = db.execute_query(team1_fundraising_query)
    team1_fundraising = team1_fundraising_result[0]['fundraising'] if team1_fundraising_result and team1_fundraising_result[0] else 0

    # Query for minutes and other stats
    team1_query = f"""
        WITH TeamBonus AS (
            SELECT SUM(tcb.bonus_minutes) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            WHERE LOWER(ci.team_name) = LOWER('{team1_name}')
        )
        SELECT
            COUNT(DISTINCT r.class_name) as classes,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base,
            COALESCE((SELECT total_bonus FROM TeamBonus), 0) as bonus_minutes,
            COUNT(DISTINCT r.student_name) as students
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE LOWER(r.team_name) = LOWER('{team1_name}') {team1_where}
    """
    team1_result = db.execute_query(team1_query)
    if team1_result and team1_result[0]:
        minutes_base = int(team1_result[0]['total_minutes_base'] or 0)
        bonus_min = int(team1_result[0]['bonus_minutes'] or 0)
        minutes_with_color = minutes_base + bonus_min
        teams[team1_name] = {
            'display_name': team1_name.upper(),
            'classes': team1_result[0]['classes'] or 0,
            'fundraising': team1_fundraising,
            'minutes_base': minutes_base,
            'bonus_minutes': bonus_min,
            'minutes_with_color': minutes_with_color,
            'hours_base': minutes_base // 60,
            'hours_with_color': minutes_with_color // 60,
            'students': team1_result[0]['students'] or 0
        }
    else:
        teams[team1_name] = {'display_name': team1_name.upper(), 'classes': 0, 'fundraising': team1_fundraising, 'minutes_base': 0, 'bonus_minutes': 0, 'minutes_with_color': 0, 'hours_base': 0, 'hours_with_color': 0, 'students': 0}

    # Team 2
    # Separate query for fundraising to avoid row multiplication from Daily_Logs join
    team2_fundraising_query = f"""
        SELECT
            COALESCE(SUM(rc.donation_amount), 0) as fundraising
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        WHERE LOWER(r.team_name) = LOWER('{team2_name}')
    """
    team2_fundraising_result = db.execute_query(team2_fundraising_query)
    team2_fundraising = team2_fundraising_result[0]['fundraising'] if team2_fundraising_result and team2_fundraising_result[0] else 0

    # Query for minutes and other stats
    team2_query = f"""
        WITH TeamBonus AS (
            SELECT SUM(tcb.bonus_minutes) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            WHERE LOWER(ci.team_name) = LOWER('{team2_name}')
        )
        SELECT
            COUNT(DISTINCT r.class_name) as classes,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base,
            COALESCE((SELECT total_bonus FROM TeamBonus), 0) as bonus_minutes,
            COUNT(DISTINCT r.student_name) as students
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE LOWER(r.team_name) = LOWER('{team2_name}') {team1_where}
    """
    team2_result = db.execute_query(team2_query)
    if team2_result and team2_result[0]:
        minutes_base = int(team2_result[0]['total_minutes_base'] or 0)
        bonus_min = int(team2_result[0]['bonus_minutes'] or 0)
        minutes_with_color = minutes_base + bonus_min
        teams[team2_name] = {
            'display_name': team2_name.upper(),
            'classes': team2_result[0]['classes'] or 0,
            'fundraising': team2_fundraising,
            'minutes_base': minutes_base,
            'bonus_minutes': bonus_min,
            'minutes_with_color': minutes_with_color,
            'hours_base': minutes_base // 60,
            'hours_with_color': minutes_with_color // 60,
            'students': team2_result[0]['students'] or 0
        }
    else:
        teams[team2_name] = {'display_name': team2_name.upper(), 'classes': 0, 'fundraising': team2_fundraising, 'minutes_base': 0, 'bonus_minutes': 0, 'minutes_with_color': 0, 'hours_base': 0, 'hours_with_color': 0, 'students': 0}

    # Team 1 - Average Daily Participation Percentage (with and without color bonus)
    # Get total days and team size for calculations
    total_days_query = f"""
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
        WHERE 1=1 {team1_where.replace('dl.', '')}
    """
    total_days_result = db.execute_query(total_days_query)
    total_days = total_days_result[0]['total_days'] if total_days_result and total_days_result[0] else 1

    team1_size = teams[team1_name]['students']
    team1_participation_query = f"""
        SELECT
            AVG(daily_pct) as avg_participation
        FROM (
            SELECT
                dl.log_date,
                (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                 (SELECT COUNT(*) FROM Roster WHERE LOWER(team_name) = LOWER('{team1_name}'))) as daily_pct
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = LOWER('{team1_name}') {team1_where}
            GROUP BY dl.log_date
        )
    """
    team1_participation_result = db.execute_query(team1_participation_query)
    teams[team1_name]['participation_pct'] = team1_participation_result[0]['avg_participation'] or 0 if team1_participation_result and team1_participation_result[0] else 0

    # Calculate participation with color bonus for Team 1
    team1_bonus_query = f"""
        SELECT SUM(tcb.bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        WHERE LOWER(ci.team_name) = LOWER('{team1_name}')
    """
    team1_bonus_result = db.execute_query(team1_bonus_query)
    team1_color_bonus = team1_bonus_result[0]['total_bonus'] if team1_bonus_result and team1_bonus_result[0] and team1_bonus_result[0]['total_bonus'] else 0
    teams[team1_name]['color_bonus_points'] = team1_color_bonus
    teams[team1_name]['participation_pct_with_color'] = teams[team1_name]['participation_pct'] + (team1_color_bonus * 100.0 / (team1_size * total_days)) if team1_size > 0 and total_days > 0 else teams[team1_name]['participation_pct']

    # Team 2 - Average Daily Participation Percentage (with and without color bonus)
    team2_size = teams[team2_name]['students']
    team2_participation_query = f"""
        SELECT
            AVG(daily_pct) as avg_participation
        FROM (
            SELECT
                dl.log_date,
                (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                 (SELECT COUNT(*) FROM Roster WHERE LOWER(team_name) = LOWER('{team2_name}'))) as daily_pct
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = LOWER('{team2_name}') {team1_where}
            GROUP BY dl.log_date
        )
    """
    team2_participation_result = db.execute_query(team2_participation_query)
    teams[team2_name]['participation_pct'] = team2_participation_result[0]['avg_participation'] or 0 if team2_participation_result and team2_participation_result[0] else 0

    # Calculate participation with color bonus for Team 2
    team2_bonus_query = f"""
        SELECT SUM(tcb.bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        WHERE LOWER(ci.team_name) = LOWER('{team2_name}')
    """
    team2_bonus_result = db.execute_query(team2_bonus_query)
    team2_color_bonus = team2_bonus_result[0]['total_bonus'] if team2_bonus_result and team2_bonus_result[0] and team2_bonus_result[0]['total_bonus'] else 0
    teams[team2_name]['color_bonus_points'] = team2_color_bonus
    teams[team2_name]['participation_pct_with_color'] = teams[team2_name]['participation_pct'] + (team2_color_bonus * 100.0 / (team2_size * total_days)) if team2_size > 0 and total_days > 0 else teams[team2_name]['participation_pct']

    # Determine leader and calculate gaps for each metric
    # Note: Different teams may lead different metrics - gaps show which team is ahead in each category
    if teams[team1_name]['fundraising'] > teams[team2_name]['fundraising']:
        teams['leader'] = team1_name.upper()
        teams['fundraising_gap'] = teams[team1_name]['fundraising'] - teams[team2_name]['fundraising']
        teams['fundraising_leader'] = team1_name.upper()
    else:
        teams['leader'] = team2_name.upper()
        teams['fundraising_gap'] = teams[team2_name]['fundraising'] - teams[team1_name]['fundraising']
        teams['fundraising_leader'] = team2_name.upper()

    # Reading gap - base version
    if teams[team1_name]['hours_base'] > teams[team2_name]['hours_base']:
        teams['reading_gap'] = teams[team1_name]['hours_base'] - teams[team2_name]['hours_base']
        teams['reading_leader'] = team1_name.upper()
    else:
        teams['reading_gap'] = teams[team2_name]['hours_base'] - teams[team1_name]['hours_base']
        teams['reading_leader'] = team2_name.upper()

    # Reading gap - with color version
    if teams[team1_name]['hours_with_color'] > teams[team2_name]['hours_with_color']:
        teams['reading_gap_with_color'] = teams[team1_name]['hours_with_color'] - teams[team2_name]['hours_with_color']
        teams['reading_leader_with_color'] = team1_name.upper()
    else:
        teams['reading_gap_with_color'] = teams[team2_name]['hours_with_color'] - teams[team1_name]['hours_with_color']
        teams['reading_leader_with_color'] = team2_name.upper()

    # Participation gap - base version
    if teams[team1_name]['participation_pct'] > teams[team2_name]['participation_pct']:
        teams['participation_gap'] = teams[team1_name]['participation_pct'] - teams[team2_name]['participation_pct']
        teams['participation_leader'] = team1_name.upper()
    else:
        teams['participation_gap'] = teams[team2_name]['participation_pct'] - teams[team1_name]['participation_pct']
        teams['participation_leader'] = team2_name.upper()

    # Participation gap - with color version
    if teams[team1_name]['participation_pct_with_color'] > teams[team2_name]['participation_pct_with_color']:
        teams['participation_gap_with_color'] = teams[team1_name]['participation_pct_with_color'] - teams[team2_name]['participation_pct_with_color']
        teams['participation_leader_with_color'] = team1_name.upper()
    else:
        teams['participation_gap_with_color'] = teams[team2_name]['participation_pct_with_color'] - teams[team1_name]['participation_pct_with_color']
        teams['participation_leader_with_color'] = team2_name.upper()

    # Goal Met calculations per team (students who met goal at least once)
    # Team 1 goals met
    team1_goals_met_query = f"""
        SELECT COUNT(DISTINCT dl.student_name) as goals_met_students
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE LOWER(r.team_name) = LOWER('{team1_name}')
          AND dl.minutes_read >= gr.min_daily_minutes {date_where}
    """
    team1_goals_met_result = db.execute_query(team1_goals_met_query)
    teams[team1_name]['goals_met_students'] = team1_goals_met_result[0]['goals_met_students'] or 0 if team1_goals_met_result and team1_goals_met_result[0] else 0
    teams[team1_name]['goals_met_pct'] = (teams[team1_name]['goals_met_students'] / teams[team1_name]['students'] * 100) if teams[team1_name]['students'] > 0 else 0

    # Team 2 goals met
    team2_goals_met_query = f"""
        SELECT COUNT(DISTINCT dl.student_name) as goals_met_students
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE LOWER(r.team_name) = LOWER('{team2_name}')
          AND dl.minutes_read >= gr.min_daily_minutes {date_where}
    """
    team2_goals_met_result = db.execute_query(team2_goals_met_query)
    teams[team2_name]['goals_met_students'] = team2_goals_met_result[0]['goals_met_students'] or 0 if team2_goals_met_result and team2_goals_met_result[0] else 0
    teams[team2_name]['goals_met_pct'] = (teams[team2_name]['goals_met_students'] / teams[team2_name]['students'] * 100) if teams[team2_name]['students'] > 0 else 0

    # Goals met leader
    if teams[team1_name]['goals_met_pct'] > teams[team2_name]['goals_met_pct']:
        teams['goals_met_gap'] = teams[team1_name]['goals_met_pct'] - teams[team2_name]['goals_met_pct']
        teams['goals_met_leader'] = team1_name.upper()
    else:
        teams['goals_met_gap'] = teams[team2_name]['goals_met_pct'] - teams[team1_name]['goals_met_pct']
        teams['goals_met_leader'] = team2_name.upper()

    # Sponsors calculations per team (total sponsors count + students with sponsors)
    # Team 1 sponsors
    team1_sponsors_query = f"""
        SELECT
            COALESCE(SUM(rc.sponsors), 0) as total_sponsors,
            COUNT(DISTINCT CASE WHEN rc.sponsors > 0 THEN rc.student_name END) as students_with_sponsors
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        WHERE LOWER(r.team_name) = LOWER('{team1_name}')
    """
    team1_sponsors_result = db.execute_query(team1_sponsors_query)
    teams[team1_name]['total_sponsors'] = int(team1_sponsors_result[0]['total_sponsors'] or 0) if team1_sponsors_result and team1_sponsors_result[0] else 0
    teams[team1_name]['sponsors_students'] = team1_sponsors_result[0]['students_with_sponsors'] or 0 if team1_sponsors_result and team1_sponsors_result[0] else 0
    teams[team1_name]['sponsors_pct'] = (teams[team1_name]['sponsors_students'] / teams[team1_name]['students'] * 100) if teams[team1_name]['students'] > 0 else 0

    # Team 2 sponsors
    team2_sponsors_query = f"""
        SELECT
            COALESCE(SUM(rc.sponsors), 0) as total_sponsors,
            COUNT(DISTINCT CASE WHEN rc.sponsors > 0 THEN rc.student_name END) as students_with_sponsors
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        WHERE LOWER(r.team_name) = LOWER('{team2_name}')
    """
    team2_sponsors_result = db.execute_query(team2_sponsors_query)
    teams[team2_name]['total_sponsors'] = int(team2_sponsors_result[0]['total_sponsors'] or 0) if team2_sponsors_result and team2_sponsors_result[0] else 0
    teams[team2_name]['sponsors_students'] = team2_sponsors_result[0]['students_with_sponsors'] or 0 if team2_sponsors_result and team2_sponsors_result[0] else 0
    teams[team2_name]['sponsors_pct'] = (teams[team2_name]['sponsors_students'] / teams[team2_name]['students'] * 100) if teams[team2_name]['students'] > 0 else 0

    # Sponsors leader (team with more total sponsors)
    if teams[team1_name]['total_sponsors'] > teams[team2_name]['total_sponsors']:
        teams['sponsors_gap'] = teams[team1_name]['total_sponsors'] - teams[team2_name]['total_sponsors']
        teams['sponsors_leader'] = team1_name.upper()
    else:
        teams['sponsors_gap'] = teams[team2_name]['total_sponsors'] - teams[team1_name]['total_sponsors']
        teams['sponsors_leader'] = team2_name.upper()

    # School-wide sponsors total (for banner display)
    metrics['total_sponsors'] = teams[team1_name]['total_sponsors'] + teams[team2_name]['total_sponsors']
    metrics['sponsors_students'] = teams[team1_name]['sponsors_students'] + teams[team2_name]['sponsors_students']
    metrics['sponsors_pct'] = (metrics['sponsors_students'] / total_roster * 100) if total_roster > 0 else 0

    # === TOP PERFORMERS ===
    performers = {}

    # Fundraising leader(s)
    fundraising_leader_query = """
        SELECT
            rc.student_name,
            r.grade_level,
            rc.donation_amount
        FROM Reader_Cumulative rc
        JOIN Roster r ON rc.student_name = r.student_name
        WHERE rc.donation_amount = (SELECT MAX(donation_amount) FROM Reader_Cumulative)
        ORDER BY rc.student_name
    """
    fundraising_leaders = db.execute_query(fundraising_leader_query)
    if fundraising_leaders:
        if len(fundraising_leaders) <= 3:
            names = ", ".join([leader['student_name'] for leader in fundraising_leaders])
        else:
            names = ", ".join([leader['student_name'] for leader in fundraising_leaders[:3]]) + f" and {len(fundraising_leaders) - 3} others"

        grades = set([leader['grade_level'] for leader in fundraising_leaders])
        grade_text = f"Grade {fundraising_leaders[0]['grade_level']}" if len(grades) == 1 else "Various"

        performers['fundraising'] = {
            'names': names,
            'grade': grade_text,
            'amount': fundraising_leaders[0]['donation_amount'],
            'tie_count': len(fundraising_leaders)
        }
    else:
        performers['fundraising'] = {'names': 'N/A', 'grade': '', 'amount': 0, 'tie_count': 1}

    # Reading leader(s)
    reading_leader_query = f"""
        SELECT
            dl.student_name,
            r.grade_level,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        WHERE 1=1 {date_where}
        GROUP BY dl.student_name, r.grade_level
        HAVING total_minutes = (
            SELECT MAX(total_minutes) FROM (
                SELECT SUM(MIN(minutes_read, 120)) as total_minutes
                FROM Daily_Logs
                WHERE 1=1 {date_where_no_alias}
                GROUP BY student_name
            )
        )
        ORDER BY dl.student_name
    """
    reading_leaders = db.execute_query(reading_leader_query)
    if reading_leaders:
        if len(reading_leaders) <= 3:
            names = ", ".join([leader['student_name'] for leader in reading_leaders])
        else:
            names = ", ".join([leader['student_name'] for leader in reading_leaders[:3]]) + f" and {len(reading_leaders) - 3} others"

        grades = set([leader['grade_level'] for leader in reading_leaders])
        grade_text = f"Grade {reading_leaders[0]['grade_level']}" if len(grades) == 1 else "Various"

        performers['reading'] = {
            'names': names,
            'grade': grade_text,
            'minutes': int(reading_leaders[0]['total_minutes']),
            'tie_count': len(reading_leaders)
        }
    else:
        performers['reading'] = {'names': 'N/A', 'grade': '', 'minutes': 0, 'tie_count': 1}

    # Top class by fundraising
    class_fundraising_query = """
        SELECT
            r.teacher_name,
            r.grade_level,
            SUM(rc.donation_amount) as total_fundraising
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.teacher_name, r.grade_level
        ORDER BY total_fundraising DESC
        LIMIT 1
    """
    class_fundraising_result = db.execute_query(class_fundraising_query)
    if class_fundraising_result and class_fundraising_result[0]:
        performers['class_fundraising'] = {
            'teacher': class_fundraising_result[0]['teacher_name'],
            'grade': class_fundraising_result[0]['grade_level'],
            'amount': class_fundraising_result[0]['total_fundraising'] or 0
        }
    else:
        performers['class_fundraising'] = {'teacher': 'N/A', 'grade': '', 'amount': 0}

    # Top class by reading (cumulative through selected date)
    class_reading_where = f"WHERE dl.log_date <= '{date_filter}'" if date_filter != 'all' and date_filter in dates else ""
    class_reading_query = f"""
        SELECT
            r.teacher_name,
            r.grade_level,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        {class_reading_where}
        GROUP BY r.teacher_name, r.grade_level
        ORDER BY total_minutes DESC
        LIMIT 1
    """
    class_reading_result = db.execute_query(class_reading_query)
    if class_reading_result and class_reading_result[0]:
        performers['class_reading'] = {
            'teacher': class_reading_result[0]['teacher_name'],
            'grade': class_reading_result[0]['grade_level'],
            'minutes': int(class_reading_result[0]['total_minutes'] or 0)
        }
    else:
        performers['class_reading'] = {'teacher': 'N/A', 'grade': '', 'minutes': 0}

    # === PARTICIPATION (Cumulative through selected date) ===
    participation = {}
    participation['total_roster'] = total_roster

    # Determine dates to include (cumulative through selected date)
    if date_filter != 'all' and date_filter in dates:
        # Get all dates up through and including selected date
        dates_through_selected = [d for d in dates if d <= date_filter]
        participation_day_count = len(dates_through_selected)
        participation_date_label = f"through {date_filter}"
    else:
        # Full contest - all dates
        dates_through_selected = dates
        participation_day_count = len(dates)
        participation_date_label = "Full Contest"

    # Build WHERE clause for participation queries
    if date_filter != 'all' and date_filter in dates:
        participation_where = f"AND dl.log_date <= '{date_filter}'"
    else:
        participation_where = ""

    # Store for template
    participation['day_count'] = participation_day_count
    participation['date_label'] = participation_date_label

    # Total participating (cumulative through selected date)
    participation['total_participating'] = metrics['participating_students']
    participation['total_participating_pct'] = metrics['participation_pct']

    # All N days active (through selected date)
    all_days_query = f"""
        SELECT COUNT(DISTINCT student_name) as count
        FROM (
            SELECT student_name, COUNT(DISTINCT log_date) as days
            FROM Daily_Logs dl
            WHERE minutes_read > 0 {participation_where}
            GROUP BY student_name
            HAVING days = {participation_day_count}
        )
    """
    all_days_result = db.execute_query(all_days_query)
    participation['all_days_active'] = all_days_result[0]['count'] if all_days_result and all_days_result[0] else 0
    participation['all_days_active_pct'] = (participation['all_days_active'] / total_roster * 100) if total_roster > 0 else 0

    # Met goal at least once (through selected date)
    met_goal_once_query = f"""
        SELECT COUNT(DISTINCT dl.student_name) as count
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE dl.minutes_read >= gr.min_daily_minutes {participation_where}
    """
    met_goal_once_result = db.execute_query(met_goal_once_query)
    participation['met_goal_once'] = met_goal_once_result[0]['count'] if met_goal_once_result and met_goal_once_result[0] else 0
    participation['met_goal_once_pct'] = (participation['met_goal_once'] / total_roster * 100) if total_roster > 0 else 0

    # Met goal all days (through selected date)
    met_goal_all_query = f"""
        SELECT COUNT(*) as count
        FROM (
            SELECT dl.student_name, COUNT(DISTINCT dl.log_date) as days_met_goal
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE dl.minutes_read >= gr.min_daily_minutes {participation_where}
            GROUP BY dl.student_name
            HAVING days_met_goal = {participation_day_count}
        )
    """
    met_goal_all_result = db.execute_query(met_goal_all_query)
    participation['met_goal_all'] = met_goal_all_result[0]['count'] if met_goal_all_result and met_goal_all_result[0] else 0
    participation['met_goal_all_pct'] = (participation['met_goal_all'] / total_roster * 100) if total_roster > 0 else 0

    # === DATA INTEGRITY ===
    integrity = {'has_issues': False, 'issue_count': 0}

    # Run quick integrity checks
    q22_result = reports.q22_student_name_sync_check()
    q23_result = reports.q23_roster_integrity_check()

    if q22_result.get('has_issues') or q23_result.get('has_issues'):
        integrity['has_issues'] = True
        integrity['issue_count'] = len(q22_result.get('data', [])) + len(q23_result.get('data', []))

    # === METADATA (Last Updated) ===
    metadata = {}

    # Daily_Logs timestamp
    daily_logs_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'daily'
    """
    daily_logs_ts = db.execute_query(daily_logs_ts_query)
    if daily_logs_ts and daily_logs_ts[0] and daily_logs_ts[0]['last_updated']:
        metadata['daily_logs_updated'] = daily_logs_ts[0]['last_updated']
    else:
        metadata['daily_logs_updated'] = 'Never'

    # Reader_Cumulative timestamp
    reader_cumulative_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'cumulative'
    """
    reader_cumulative_ts = db.execute_query(reader_cumulative_ts_query)
    if reader_cumulative_ts and reader_cumulative_ts[0] and reader_cumulative_ts[0]['last_updated']:
        metadata['reader_cumulative_updated'] = reader_cumulative_ts[0]['last_updated']
    else:
        metadata['reader_cumulative_updated'] = 'Never'

    # Roster timestamp (static - set during init)
    metadata['roster_updated'] = '09/15/2025 8:00 AM'

    # Team_Color_Bonus timestamp (event date)
    team_color_bonus_query = """
        SELECT event_date, COUNT(*) as class_count
        FROM Team_Color_Bonus
        GROUP BY event_date
        ORDER BY event_date DESC
        LIMIT 1
    """
    team_color_bonus_ts = db.execute_query(team_color_bonus_query)
    if team_color_bonus_ts and team_color_bonus_ts[0] and team_color_bonus_ts[0]['event_date']:
        event_date = team_color_bonus_ts[0]['event_date']
        class_count = team_color_bonus_ts[0]['class_count']
        metadata['team_color_bonus_updated'] = f"{event_date} ({class_count} classes)"
    else:
        metadata['team_color_bonus_updated'] = 'No data'

    return render_template('school.html',
                         environment=env,
                         dates=dates,
                         full_contest_range=full_contest_range,
                         metrics=metrics,
                         teams=teams,
                         team1_name=team1_name,
                         team2_name=team2_name,
                         performers=performers,
                         participation=participation,
                         integrity=integrity,
                         metadata=metadata)


@app.route('/teams')
def teams_tab():
    """Teams head-to-head competition dashboard"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()

    # Get filter parameter (optional)
    date_filter = request.args.get('date', 'all')

    # Get all available dates
    dates = db.get_all_dates()

    # Build WHERE clause based on filter (cumulative through selected date)
    date_where = ""
    date_where_no_alias = ""
    if date_filter != 'all' and date_filter in dates:
        date_where = f"AND dl.log_date <= '{date_filter}'"
        date_where_no_alias = f"AND log_date <= '{date_filter}'"

    # Get team names (sorted alphabetically for consistency)
    team_names_query = "SELECT DISTINCT team_name FROM Roster ORDER BY team_name"
    team_names_result = db.execute_query(team_names_query)
    team_names = [row['team_name'] for row in team_names_result] if team_names_result else []

    # Ensure we have exactly 2 teams
    if len(team_names) != 2:
        return jsonify({'error': f'Expected 2 teams, found {len(team_names)}'}), 500

    team1_name = team_names[0]  # Kitsko (alphabetically first)
    team2_name = team_names[1]  # Staub (alphabetically second)

    # Calculate full contest date range
    sorted_dates = sorted(dates)
    total_days = len(sorted_dates)
    if sorted_dates:
        start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').strftime('%b %d')
        end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').strftime('%b %d, %Y')
        full_contest_range = f"{start_date}-{end_date}"
    else:
        full_contest_range = "Oct 10-15, 2025"  # Fallback if no dates

    # Campaign Day calculation - date-aware (for banner metric)
    if date_filter != 'all' and date_filter in dates:
        # Find position of selected date (1-based)
        current_day = sorted_dates.index(date_filter) + 1
        campaign_date = date_filter  # Store for subtitle display
    else:
        # Full contest - show total days
        current_day = total_days
        campaign_date = full_contest_range

    # === BANNER METRICS (6 metrics showing team winners + Campaign Day) ===
    banner = {}

    # Helper function to get team data
    def get_team_metrics(team_name):
        metrics = {}

        # 1. Fundraising
        fundraising_query = f"""
            SELECT COALESCE(SUM(rc.donation_amount), 0) as total_fundraising,
                   COUNT(DISTINCT CASE WHEN rc.donation_amount > 0 THEN rc.student_name END) as students_with_donations
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}')
        """
        fundraising_result = db.execute_query(fundraising_query)
        if fundraising_result and fundraising_result[0]:
            metrics['fundraising'] = fundraising_result[0]['total_fundraising'] or 0
            metrics['fundraising_students'] = fundraising_result[0]['students_with_donations'] or 0
        else:
            metrics['fundraising'] = 0
            metrics['fundraising_students'] = 0

        # 2. Minutes Read (with color bonus)
        minutes_query = f"""
            WITH TeamBonus AS (
                SELECT SUM(tcb.bonus_minutes) as total_bonus
                FROM Team_Color_Bonus tcb
                INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
                WHERE LOWER(ci.team_name) = LOWER('{team_name}')
            )
            SELECT
                COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base,
                COALESCE((SELECT total_bonus FROM TeamBonus), 0) as bonus_minutes
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}') {date_where}
        """
        minutes_result = db.execute_query(minutes_query)
        if minutes_result and minutes_result[0]:
            base = int(minutes_result[0]['total_minutes_base'] or 0)
            bonus = int(minutes_result[0]['bonus_minutes'] or 0)
            metrics['minutes_with_color'] = base + bonus
        else:
            metrics['minutes_with_color'] = 0

        # 3. Participation % (average daily with color bonus)
        # Get total days being measured
        total_days_query = f"""
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where_no_alias}
        """
        total_days_result = db.execute_query(total_days_query)
        days_count = total_days_result[0]['total_days'] if total_days_result and total_days_result[0] else 1

        # Get team size
        team_size_query = f"""
            SELECT COUNT(*) as team_size
            FROM Roster
            WHERE LOWER(team_name) = LOWER('{team_name}')
        """
        team_size_result = db.execute_query(team_size_query)
        team_size = team_size_result[0]['team_size'] if team_size_result and team_size_result[0] else 1

        # Calculate average daily participation
        participation_query = f"""
            SELECT AVG(daily_pct) as avg_participation
            FROM (
                SELECT
                    dl.log_date,
                    (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                     (SELECT COUNT(*) FROM Roster WHERE LOWER(team_name) = LOWER('{team_name}'))) as daily_pct
                FROM Daily_Logs dl
                JOIN Roster r ON dl.student_name = r.student_name
                WHERE LOWER(r.team_name) = LOWER('{team_name}') {date_where}
                GROUP BY dl.log_date
            )
        """
        participation_result = db.execute_query(participation_query)
        base_participation = participation_result[0]['avg_participation'] or 0 if participation_result and participation_result[0] else 0

        # Add color bonus to participation
        color_bonus_query = f"""
            SELECT SUM(tcb.bonus_participation_points) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            WHERE LOWER(ci.team_name) = LOWER('{team_name}')
        """
        color_bonus_result = db.execute_query(color_bonus_query)
        color_bonus_points = color_bonus_result[0]['total_bonus'] if color_bonus_result and color_bonus_result[0] and color_bonus_result[0]['total_bonus'] else 0

        metrics['participation_pct'] = base_participation + (color_bonus_points * 100.0 / (team_size * days_count)) if team_size > 0 and days_count > 0 else base_participation
        metrics['participation_students'] = team_size  # Total students on team

        # 4. Goal Met ≥1 Day (students who met their grade's goal at least once)
        goal_met_query = f"""
            SELECT COUNT(DISTINCT dl.student_name) as students_met_goal
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE LOWER(r.team_name) = LOWER('{team_name}')
              AND dl.minutes_read >= gr.min_daily_minutes {date_where}
        """
        goal_met_result = db.execute_query(goal_met_query)
        if goal_met_result and goal_met_result[0]:
            metrics['goal_met_students'] = goal_met_result[0]['students_met_goal'] or 0
        else:
            metrics['goal_met_students'] = 0
        # Calculate percentage
        metrics['goal_met_pct'] = (metrics['goal_met_students'] / team_size * 100) if team_size > 0 else 0

        # 5. Sponsors (total sponsors for team)
        sponsors_query = f"""
            SELECT
                COALESCE(SUM(rc.sponsors), 0) as total_sponsors,
                COUNT(DISTINCT CASE WHEN rc.sponsors > 0 THEN rc.student_name END) as students_with_sponsors
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}')
        """
        sponsors_result = db.execute_query(sponsors_query)
        if sponsors_result and sponsors_result[0]:
            metrics['sponsors'] = int(sponsors_result[0]['total_sponsors'] or 0)
            metrics['sponsors_students'] = int(sponsors_result[0]['students_with_sponsors'] or 0)
        else:
            metrics['sponsors'] = 0
            metrics['sponsors_students'] = 0

        return metrics

    # Get metrics for both teams
    team1_metrics = get_team_metrics(team1_name)
    team2_metrics = get_team_metrics(team2_name)

    # Determine winners for each banner metric
    banner_metrics = [
        {
            'name': 'Fundraising',
            'icon': '💰',
            'key': 'fundraising',
            'format': 'currency',
            'honors_filter': False
        },
        {
            'name': 'Minutes Read',
            'icon': '📚',
            'key': 'minutes_with_color',
            'format': 'number',
            'honors_filter': True
        },
        {
            'name': 'Sponsors',
            'icon': '🎁',
            'key': 'sponsors',
            'format': 'number',
            'honors_filter': False
        },
        {
            'name': 'Avg. Participation (With Color)',
            'icon': '👥',
            'key': 'participation_pct',
            'format': 'percentage',
            'honors_filter': True
        },
        {
            'name': 'Goal Met ≥1 Day',
            'icon': '🎯',
            'key': 'goal_met_pct',
            'format': 'percentage',
            'honors_filter': True
        }
    ]

    for metric in banner_metrics:
        key = metric['key']
        team1_value = team1_metrics[key]
        team2_value = team2_metrics[key]

        if team1_value > team2_value:
            metric['winner'] = team1_name
            metric['winner_value'] = team1_value
        elif team2_value > team1_value:
            metric['winner'] = team2_name
            metric['winner_value'] = team2_value
        else:
            metric['winner'] = 'TIE'
            metric['winner_value'] = team1_value

        # Store individual team values and student counts for all metrics
        metric['team1_value'] = team1_value
        metric['team2_value'] = team2_value
        metric['team1_students'] = team1_metrics['participation_students']
        metric['team2_students'] = team2_metrics['participation_students']

        # Store metric-specific counts for subtitle
        if key == 'fundraising':
            metric['team1_count'] = team1_metrics['fundraising_students']
            metric['team2_count'] = team2_metrics['fundraising_students']
        elif key == 'goal_met_pct':
            metric['team1_count'] = team1_metrics['goal_met_students']
            metric['team2_count'] = team2_metrics['goal_met_students']
        elif key == 'participation_pct':
            # Calculate participating count from percentage
            metric['team1_count'] = int(team1_metrics['participation_students'] * team1_metrics['participation_pct'] / 100)
            metric['team2_count'] = int(team2_metrics['participation_students'] * team2_metrics['participation_pct'] / 100)
        elif key == 'sponsors':
            metric['team1_count'] = team1_metrics['sponsors_students']
            metric['team2_count'] = team2_metrics['sponsors_students']

    banner['metrics'] = banner_metrics

    # === TOP PERFORMERS BY TEAM ===
    top_performers = {}

    # Helper function to get top performers for a team
    def get_top_performers_for_team(team_name):
        performers = {}

        # Fundraising Leader (student)
        fundraising_leader_query = f"""
            SELECT rc.student_name, r.grade_level, r.class_name, rc.donation_amount
            FROM Reader_Cumulative rc
            JOIN Roster r ON rc.student_name = r.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}')
            ORDER BY rc.donation_amount DESC
            LIMIT 1
        """
        fundraising_result = db.execute_query(fundraising_leader_query)
        if fundraising_result and fundraising_result[0]:
            performers['fundraising_leader'] = fundraising_result[0]
        else:
            performers['fundraising_leader'] = {'student_name': 'N/A', 'grade_level': '', 'class_name': '', 'donation_amount': 0}

        # Reading Leader (student)
        reading_leader_query = f"""
            SELECT dl.student_name, r.grade_level, r.class_name, SUM(MIN(dl.minutes_read, 120)) as total_minutes
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}') {date_where}
            GROUP BY dl.student_name, r.grade_level, r.class_name
            ORDER BY total_minutes DESC
            LIMIT 1
        """
        reading_result = db.execute_query(reading_leader_query)
        if reading_result and reading_result[0]:
            performers['reading_leader'] = reading_result[0]
        else:
            performers['reading_leader'] = {'student_name': 'N/A', 'grade_level': '', 'class_name': '', 'total_minutes': 0}

        # Top Class (Fundraising)
        class_fundraising_query = f"""
            SELECT r.teacher_name, r.class_name, r.grade_level, SUM(rc.donation_amount) as total_fundraising
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}')
            GROUP BY r.teacher_name, r.class_name, r.grade_level
            ORDER BY total_fundraising DESC
            LIMIT 1
        """
        class_fundraising_result = db.execute_query(class_fundraising_query)
        if class_fundraising_result and class_fundraising_result[0]:
            performers['top_class_fundraising'] = class_fundraising_result[0]
        else:
            performers['top_class_fundraising'] = {'teacher_name': 'N/A', 'class_name': '', 'grade_level': '', 'total_fundraising': 0}

        # Top Class (Reading)
        class_reading_query = f"""
            SELECT r.teacher_name, r.class_name, r.grade_level, SUM(MIN(dl.minutes_read, 120)) as total_minutes
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE LOWER(r.team_name) = LOWER('{team_name}') {date_where}
            GROUP BY r.teacher_name, r.class_name, r.grade_level
            ORDER BY total_minutes DESC
            LIMIT 1
        """
        class_reading_result = db.execute_query(class_reading_query)
        if class_reading_result and class_reading_result[0]:
            performers['top_class_reading'] = class_reading_result[0]
        else:
            performers['top_class_reading'] = {'teacher_name': 'N/A', 'class_name': '', 'grade_level': '', 'total_minutes': 0}

        return performers

    top_performers[team1_name] = get_top_performers_for_team(team1_name)
    top_performers[team2_name] = get_top_performers_for_team(team2_name)

    # === COMPARISON TABLE (10 metrics) ===
    comparison_table = []

    # Helper function to add table row
    def add_comparison_row(metric_name, metric_type, team1_value, team2_value, format_type='number'):
        leader = None
        gap = 0

        if team1_value > team2_value:
            leader = team1_name
            gap = team1_value - team2_value
        elif team2_value > team1_value:
            leader = team2_name
            gap = team2_value - team1_value
        else:
            leader = 'TIE'
            gap = 0

        comparison_table.append({
            'metric': metric_name,
            'type': metric_type,
            'team1_value': team1_value,
            'team2_value': team2_value,
            'leader': leader,
            'gap': gap,
            'format': format_type
        })

    # === FUNDRAISING METRICS ===
    add_comparison_row('Fundraising', 'Fundraising', team1_metrics['fundraising'], team2_metrics['fundraising'], 'currency')
    add_comparison_row('Sponsors', 'Fundraising', team1_metrics['sponsors'], team2_metrics['sponsors'], 'number')

    # === READING METRICS ===
    # 1. Minutes Read (in hours)
    team1_minutes_hours = team1_metrics['minutes_with_color'] / 60
    team2_minutes_hours = team2_metrics['minutes_with_color'] / 60
    add_comparison_row('Minutes Read', 'Reading', team1_minutes_hours, team2_minutes_hours, 'hours')

    # 2. Participation % (students who participated at least once / total students)
    team1_participated_query = f"""
        SELECT COUNT(DISTINCT dl.student_name) as participated_count
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        WHERE LOWER(r.team_name) = LOWER('{team1_name}')
          AND dl.minutes_read > 0 {date_where}
    """
    team1_participated_result = db.execute_query(team1_participated_query)
    team1_participated_count = team1_participated_result[0]['participated_count'] if team1_participated_result and team1_participated_result[0] else 0
    team1_participation_pct = (team1_participated_count / team1_metrics['participation_students'] * 100) if team1_metrics['participation_students'] > 0 else 0

    team2_participated_query = f"""
        SELECT COUNT(DISTINCT dl.student_name) as participated_count
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        WHERE LOWER(r.team_name) = LOWER('{team2_name}')
          AND dl.minutes_read > 0 {date_where}
    """
    team2_participated_result = db.execute_query(team2_participated_query)
    team2_participated_count = team2_participated_result[0]['participated_count'] if team2_participated_result and team2_participated_result[0] else 0
    team2_participation_pct = (team2_participated_count / team2_metrics['participation_students'] * 100) if team2_metrics['participation_students'] > 0 else 0

    add_comparison_row('Participation %', 'Reading', team1_participation_pct, team2_participation_pct, 'percentage')

    # 3. Avg. Participation (With Color) - average daily participation with color bonus
    add_comparison_row('Avg. Participation (With Color)', 'Reading', team1_metrics['participation_pct'], team2_metrics['participation_pct'], 'percentage')

    # 4. All 4 Days Active % (students who read all days / total students)
    # First, get count of days in filter period
    days_count_query = f"""
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
        WHERE 1=1 {date_where_no_alias}
    """
    days_count_result = db.execute_query(days_count_query)
    filter_days_count = days_count_result[0]['total_days'] if days_count_result and days_count_result[0] else 0

    team1_all_days_query = f"""
        SELECT COUNT(DISTINCT student_name) as all_days_count
        FROM (
            SELECT dl.student_name, COUNT(DISTINCT dl.log_date) as days_active
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = LOWER('{team1_name}')
              AND dl.minutes_read > 0 {date_where}
            GROUP BY dl.student_name
            HAVING COUNT(DISTINCT dl.log_date) = {filter_days_count}
        )
    """
    team1_all_days_result = db.execute_query(team1_all_days_query)
    team1_all_days_count = team1_all_days_result[0]['all_days_count'] if team1_all_days_result and team1_all_days_result[0] else 0
    team1_all_days_pct = (team1_all_days_count / team1_metrics['participation_students'] * 100) if team1_metrics['participation_students'] > 0 else 0

    team2_all_days_query = f"""
        SELECT COUNT(DISTINCT student_name) as all_days_count
        FROM (
            SELECT dl.student_name, COUNT(DISTINCT dl.log_date) as days_active
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = LOWER('{team2_name}')
              AND dl.minutes_read > 0 {date_where}
            GROUP BY dl.student_name
            HAVING COUNT(DISTINCT dl.log_date) = {filter_days_count}
        )
    """
    team2_all_days_result = db.execute_query(team2_all_days_query)
    team2_all_days_count = team2_all_days_result[0]['all_days_count'] if team2_all_days_result and team2_all_days_result[0] else 0
    team2_all_days_pct = (team2_all_days_count / team2_metrics['participation_students'] * 100) if team2_metrics['participation_students'] > 0 else 0

    add_comparison_row('All 4 Days Active %', 'Reading', team1_all_days_pct, team2_all_days_pct, 'percentage')

    # 4. Met Goal ≥1 Day % (already have count, just need percentage)
    team1_goal_met_pct = (team1_metrics['goal_met_students'] / team1_metrics['participation_students'] * 100) if team1_metrics['participation_students'] > 0 else 0
    team2_goal_met_pct = (team2_metrics['goal_met_students'] / team2_metrics['participation_students'] * 100) if team2_metrics['participation_students'] > 0 else 0
    add_comparison_row('Met Goal ≥1 Day %', 'Reading', team1_goal_met_pct, team2_goal_met_pct, 'percentage')

    # 5. Met Goal All Days % (students who met goal every day / total students)
    team1_goal_all_days_query = f"""
        SELECT COUNT(DISTINCT student_name) as goal_all_days_count
        FROM (
            SELECT dl.student_name,
                   COUNT(DISTINCT CASE
                       WHEN dl.minutes_read >= gr.min_daily_minutes THEN dl.log_date
                   END) as days_met_goal
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE LOWER(r.team_name) = LOWER('{team1_name}') {date_where}
            GROUP BY dl.student_name
            HAVING COUNT(DISTINCT CASE
                       WHEN dl.minutes_read >= gr.min_daily_minutes THEN dl.log_date
                   END) = {filter_days_count}
        )
    """
    team1_goal_all_days_result = db.execute_query(team1_goal_all_days_query)
    team1_goal_all_days_count = team1_goal_all_days_result[0]['goal_all_days_count'] if team1_goal_all_days_result and team1_goal_all_days_result[0] else 0
    team1_goal_all_days_pct = (team1_goal_all_days_count / team1_metrics['participation_students'] * 100) if team1_metrics['participation_students'] > 0 else 0

    team2_goal_all_days_query = f"""
        SELECT COUNT(DISTINCT student_name) as goal_all_days_count
        FROM (
            SELECT dl.student_name,
                   COUNT(DISTINCT CASE
                       WHEN dl.minutes_read >= gr.min_daily_minutes THEN dl.log_date
                   END) as days_met_goal
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE LOWER(r.team_name) = LOWER('{team2_name}') {date_where}
            GROUP BY dl.student_name
            HAVING COUNT(DISTINCT CASE
                       WHEN dl.minutes_read >= gr.min_daily_minutes THEN dl.log_date
                   END) = {filter_days_count}
        )
    """
    team2_goal_all_days_result = db.execute_query(team2_goal_all_days_query)
    team2_goal_all_days_count = team2_goal_all_days_result[0]['goal_all_days_count'] if team2_goal_all_days_result and team2_goal_all_days_result[0] else 0
    team2_goal_all_days_pct = (team2_goal_all_days_count / team2_metrics['participation_students'] * 100) if team2_metrics['participation_students'] > 0 else 0

    add_comparison_row('Met Goal All Days %', 'Reading', team1_goal_all_days_pct, team2_goal_all_days_pct, 'percentage')

    # === TEAM STATS ===
    # 1. Color War Points (bonus points from Team_Color_Bonus table)
    team1_color_points_query = f"""
        SELECT
            COALESCE(SUM(tcb.bonus_participation_points), 0) as total_points
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        WHERE LOWER(ci.team_name) = LOWER('{team1_name}')
    """
    team1_color_points_result = db.execute_query(team1_color_points_query)
    team1_color_points = team1_color_points_result[0]['total_points'] if team1_color_points_result and team1_color_points_result[0] else 0

    team2_color_points_query = f"""
        SELECT
            COALESCE(SUM(tcb.bonus_participation_points), 0) as total_points
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        WHERE LOWER(ci.team_name) = LOWER('{team2_name}')
    """
    team2_color_points_result = db.execute_query(team2_color_points_query)
    team2_color_points = team2_color_points_result[0]['total_points'] if team2_color_points_result and team2_color_points_result[0] else 0

    add_comparison_row('Color War Points', 'Team Stats', team1_color_points, team2_color_points, 'number')

    # 2. Students (Team Size)
    add_comparison_row('Students (Team Size)', 'Team Stats', team1_metrics['participation_students'], team2_metrics['participation_students'], 'number')

    # === FULL CONTEST RANGE ===
    sorted_dates = sorted(dates)
    if sorted_dates:
        start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').strftime('%b %d')
        end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').strftime('%b %d, %Y')
        full_contest_range = f"{start_date}-{end_date}"
    else:
        full_contest_range = "Oct 10-15, 2025"  # Fallback if no dates

    # === METADATA (Last Updated) ===
    metadata = {}

    # Daily_Logs timestamp
    daily_logs_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'daily'
    """
    daily_logs_ts = db.execute_query(daily_logs_ts_query)
    if daily_logs_ts and daily_logs_ts[0] and daily_logs_ts[0]['last_updated']:
        metadata['daily_logs_updated'] = daily_logs_ts[0]['last_updated']
    else:
        metadata['daily_logs_updated'] = 'Never'

    # Reader_Cumulative timestamp
    reader_cumulative_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'cumulative'
    """
    reader_cumulative_ts = db.execute_query(reader_cumulative_ts_query)
    if reader_cumulative_ts and reader_cumulative_ts[0] and reader_cumulative_ts[0]['last_updated']:
        metadata['reader_cumulative_updated'] = reader_cumulative_ts[0]['last_updated']
    else:
        metadata['reader_cumulative_updated'] = 'Never'

    # Roster timestamp (static - set during init)
    metadata['roster_updated'] = '09/15/2025 8:00 AM'

    # Team_Color_Bonus timestamp (event date)
    team_color_bonus_query = """
        SELECT event_date, COUNT(*) as class_count
        FROM Team_Color_Bonus
        GROUP BY event_date
        ORDER BY event_date DESC
        LIMIT 1
    """
    team_color_bonus_ts = db.execute_query(team_color_bonus_query)
    if team_color_bonus_ts and team_color_bonus_ts[0] and team_color_bonus_ts[0]['event_date']:
        event_date = team_color_bonus_ts[0]['event_date']
        class_count = team_color_bonus_ts[0]['class_count']
        metadata['team_color_bonus_updated'] = f"{event_date} ({class_count} classes)"
    else:
        metadata['team_color_bonus_updated'] = 'No data'

    return render_template('teams.html',
                         environment=env,
                         dates=dates,
                         date_filter=date_filter,
                         current_day=current_day,
                         campaign_date=campaign_date,
                         total_days=total_days,
                         full_contest_range=full_contest_range,
                         team1_name=team1_name,
                         team2_name=team2_name,
                         banner=banner,
                         top_performers=top_performers,
                         comparison_table=comparison_table,
                         metadata=metadata)


@app.route('/classes')
def grade_level_tab():
    """Grade Level dashboard - class and grade-level competition view"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()

    # Get filter parameters (optional)
    date_filter = request.args.get('date', 'all')
    grade_filter = request.args.get('grade', 'all')
    team_filter = request.args.get('team', 'all')

    # Get all available dates
    dates = db.get_all_dates()

    # Build WHERE clause based on filter (cumulative through selected date)
    date_where = ""
    if date_filter != 'all' and date_filter in dates:
        date_where = f" AND dl.log_date <= '{date_filter}'"

    # Build grade WHERE clause
    grade_where = ""
    if grade_filter != 'all':
        grade_where = f" AND ci.grade_level = '{grade_filter}'"

    # Build team WHERE clause
    team_where = ""
    if team_filter != 'all':
        team_where = f" AND ci.team_name = '{team_filter}'"

    # DEBUG: Log filter state
    print(f"\n=== GRADE LEVEL ROUTE DEBUG ===")
    print(f"  date_filter: {date_filter}")
    print(f"  grade_filter: {grade_filter}")
    print(f"  team_filter: {team_filter}")
    print(f"  date_where: {repr(date_where)}")
    print(f"  grade_where: {repr(grade_where)}")
    print(f"  team_where: {repr(team_where)}")

    # Calculate full contest date range
    sorted_dates = sorted(dates)
    total_days = len(sorted_dates)
    if sorted_dates:
        start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').strftime('%b %d')
        end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').strftime('%b %d, %Y')
        full_contest_range = f"{start_date}-{end_date}"
    else:
        full_contest_range = "Oct 10-15, 2025"  # Fallback if no dates

    # Campaign Day calculation - date-aware (for banner metric)
    if date_filter != 'all' and date_filter in dates:
        # Find position of selected date (1-based)
        current_day = sorted_dates.index(date_filter) + 1
        campaign_date = date_filter  # Store for subtitle display
    else:
        # Full contest - show total days
        current_day = total_days
        campaign_date = full_contest_range

    # === GET ALL CLASSES (unfiltered) TO CALCULATE TRUE SCHOOL-WIDE WINNERS ===
    # IMPORTANT: School-wide winners must be calculated across ALL grades/teams, not just filtered
    all_classes_query = get_grade_level_classes_query(date_where, "", "")  # No grade/team filter
    all_classes_result = db.execute_query(all_classes_query)
    all_classes = [dict(row) for row in all_classes_result] if all_classes_result else []

    # Find TRUE school-wide winners (gold highlights) across ALL grades
    # Matches metrics from Teams page for consistency
    if all_classes:
        school_winners = {
            'fundraising': max(all_classes, key=lambda x: x['total_fundraising'])['total_fundraising'],
            'minutes': max(all_classes, key=lambda x: x['total_minutes'])['total_minutes'],
            'participation': max(all_classes, key=lambda x: x['participation_pct'])['participation_pct'],
            'avg_participation_with_color': max(all_classes, key=lambda x: x['avg_participation_with_color_pct'])['avg_participation_with_color_pct'],
            'all_days_active': max(all_classes, key=lambda x: x['all_days_active_pct'])['all_days_active_pct'],
            'goal_met_once': max(all_classes, key=lambda x: x['goal_met_once_pct'])['goal_met_once_pct'],
            'goal_met_all_days': max(all_classes, key=lambda x: x['goal_met_all_days_pct'])['goal_met_all_days_pct'],
            'color_war_points': max(all_classes, key=lambda x: x['color_war_points'])['color_war_points'],
            'sponsors': max(all_classes, key=lambda x: x['total_sponsors'])['total_sponsors']
        }
    else:
        school_winners = {
            'fundraising': 0,
            'minutes': 0,
            'participation': 0,
            'avg_participation_with_color': 0,
            'all_days_active': 0,
            'goal_met_once': 0,
            'goal_met_all_days': 0,
            'color_war_points': 0,
            'sponsors': 0
        }

    # === GET FILTERED CLASSES FOR DISPLAY ===
    classes_query = get_grade_level_classes_query(date_where, grade_where, team_where)
    classes_result = db.execute_query(classes_query)

    # DEBUG: Log result count
    row_count = len(classes_result) if classes_result else 0
    print(f"  Query returned {row_count} classes")
    if row_count > 0 and classes_result:
        grades_in_results = set(row['grade_level'] for row in classes_result)
        print(f"  Grades in results: {grades_in_results}")
    print(f"=================================\n")

    # Find grade-level winners (silver highlights) for each metric - use ALL classes
    # Matches metrics from Teams page for consistency
    grade_winners = {}
    for grade in ['K', '1', '2', '3', '4', '5']:
        grade_classes = [c for c in all_classes if c['grade_level'] == grade]
        if grade_classes:
            grade_winners[grade] = {
                'fundraising': max(grade_classes, key=lambda x: x['total_fundraising'])['total_fundraising'],
                'minutes': max(grade_classes, key=lambda x: x['total_minutes'])['total_minutes'],
                'participation': max(grade_classes, key=lambda x: x['participation_pct'])['participation_pct'],
                'avg_participation_with_color': max(grade_classes, key=lambda x: x['avg_participation_with_color_pct'])['avg_participation_with_color_pct'],
                'all_days_active': max(grade_classes, key=lambda x: x['all_days_active_pct'])['all_days_active_pct'],
                'goal_met_once': max(grade_classes, key=lambda x: x['goal_met_once_pct'])['goal_met_once_pct'],
                'goal_met_all_days': max(grade_classes, key=lambda x: x['goal_met_all_days_pct'])['goal_met_all_days_pct'],
                'color_war_points': max(grade_classes, key=lambda x: x['color_war_points'])['color_war_points'],
                'sponsors': max(grade_classes, key=lambda x: x['total_sponsors'])['total_sponsors']
            }

    # Convert filtered results to list of dicts
    classes = []
    if classes_result:
        classes = [dict(row) for row in classes_result]

        # Add winner flags to each class
        for cls in classes:
            cls['is_school_winner'] = {}
            cls['is_grade_winner'] = {}

            # Check if this class is a school-wide winner (matches Teams metrics)
            cls['is_school_winner']['fundraising'] = (cls['total_fundraising'] == school_winners['fundraising'] and cls['total_fundraising'] > 0)
            cls['is_school_winner']['minutes'] = (cls['total_minutes'] == school_winners['minutes'] and cls['total_minutes'] > 0)
            cls['is_school_winner']['participation'] = (cls['participation_pct'] == school_winners['participation'] and cls['participation_pct'] > 0)
            cls['is_school_winner']['avg_participation_with_color'] = (cls['avg_participation_with_color_pct'] == school_winners['avg_participation_with_color'] and cls['avg_participation_with_color_pct'] > 0)
            cls['is_school_winner']['all_days_active'] = (cls['all_days_active_pct'] == school_winners['all_days_active'] and cls['all_days_active_pct'] > 0)
            cls['is_school_winner']['goal_met_once'] = (cls['goal_met_once_pct'] == school_winners['goal_met_once'] and cls['goal_met_once_pct'] > 0)
            cls['is_school_winner']['goal_met_all_days'] = (cls['goal_met_all_days_pct'] == school_winners['goal_met_all_days'] and cls['goal_met_all_days_pct'] > 0)
            cls['is_school_winner']['color_war_points'] = (cls['color_war_points'] == school_winners['color_war_points'] and cls['color_war_points'] > 0)
            cls['is_school_winner']['sponsors'] = (cls['total_sponsors'] == school_winners['sponsors'] and cls['total_sponsors'] > 0)

            # Check if this class is a grade-level winner (matches Teams metrics)
            if cls['grade_level'] in grade_winners:
                gw = grade_winners[cls['grade_level']]
                cls['is_grade_winner']['fundraising'] = (cls['total_fundraising'] == gw['fundraising'] and cls['total_fundraising'] > 0)
                cls['is_grade_winner']['minutes'] = (cls['total_minutes'] == gw['minutes'] and cls['total_minutes'] > 0)
                cls['is_grade_winner']['participation'] = (cls['participation_pct'] == gw['participation'] and cls['participation_pct'] > 0)
                cls['is_grade_winner']['avg_participation_with_color'] = (cls['avg_participation_with_color_pct'] == gw['avg_participation_with_color'] and cls['avg_participation_with_color_pct'] > 0)
                cls['is_grade_winner']['all_days_active'] = (cls['all_days_active_pct'] == gw['all_days_active'] and cls['all_days_active_pct'] > 0)
                cls['is_grade_winner']['goal_met_once'] = (cls['goal_met_once_pct'] == gw['goal_met_once'] and cls['goal_met_once_pct'] > 0)
                cls['is_grade_winner']['goal_met_all_days'] = (cls['goal_met_all_days_pct'] == gw['goal_met_all_days'] and cls['goal_met_all_days_pct'] > 0)
                cls['is_grade_winner']['color_war_points'] = (cls['color_war_points'] == gw['color_war_points'] and cls['color_war_points'] > 0)
                cls['is_grade_winner']['sponsors'] = (cls['total_sponsors'] == gw['sponsors'] and cls['total_sponsors'] > 0)

    # === GET GRADE AGGREGATIONS FOR CARDS ===
    grade_agg_query = get_grade_aggregations_query(date_where, grade_where, team_where)
    grade_summaries_result = db.execute_query(grade_agg_query)
    grade_summaries = [dict(row) for row in grade_summaries_result] if grade_summaries_result else []

    # Get team names dynamically from database
    team_names_query = "SELECT DISTINCT team_name FROM Roster ORDER BY team_name"
    team_names_result = db.execute_query(team_names_query)
    team_names = [row['team_name'] for row in team_names_result] if team_names_result else []

    # Enrich grade_summaries with properly named team attributes
    for grade in grade_summaries:
        if len(team_names) >= 2:
            grade['team1_name'] = team_names[0]
            grade['team2_name'] = team_names[1]
            # Rename the generic columns to use actual team names for the template
            grade[f'{team_names[0].lower()}_students'] = grade.get('team1_students', 0)
            grade[f'{team_names[1].lower()}_students'] = grade.get('team2_students', 0)

    # === GET LEADERS FOR HEADLINE BANNER (All grades + each individual grade) ===
    def parse_banner_leaders(leaders_result):
        """Helper to parse leader query results into dict"""
        leaders = {}
        if leaders_result:
            for row in leaders_result:
                leaders[row['metric']] = {
                    'class_name': row['class_name'],
                    'teacher': row['teacher_name'],
                    'grade': row['grade_level'],
                    'team': row['team_name'],
                    'value': row['value']
                }
        return leaders

    # Get school-wide leaders (all grades, optionally filtered by team)
    team_for_banner = team_filter if team_filter != 'all' else None
    leaders_query_all = get_school_wide_leaders_query(date_where, grade=None, team=team_for_banner)
    leaders_result_all = db.execute_query(leaders_query_all)
    banner_leaders_all = parse_banner_leaders(leaders_result_all)

    # Get grade-specific leaders (now using consistent format)
    banner_leaders_by_grade = {}
    grades = ['K', '1', '2', '3', '4', '5']

    for grade in grades:
        leaders_query_grade = get_school_wide_leaders_query(date_where, grade=grade, team=team_for_banner)
        leaders_result_grade = db.execute_query(leaders_query_grade)
        banner_leaders_by_grade[grade] = parse_banner_leaders(leaders_result_grade)

    # Set banner_leaders based on grade filter
    if grade_filter != 'all' and grade_filter in banner_leaders_by_grade:
        # Show filtered grade leaders in banner
        banner_leaders = banner_leaders_by_grade[grade_filter]
    else:
        # Show all grades (school-wide) leaders in banner
        banner_leaders = banner_leaders_all

    # === METADATA (Last Updated) ===
    metadata = {}

    # Daily_Logs timestamp
    daily_logs_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'daily'
    """
    daily_logs_ts = db.execute_query(daily_logs_ts_query)
    metadata['daily_logs_updated'] = daily_logs_ts[0]['last_updated'] if daily_logs_ts and daily_logs_ts[0] and daily_logs_ts[0]['last_updated'] else 'Never'

    # Reader_Cumulative timestamp
    reader_cumulative_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'cumulative'
    """
    reader_cumulative_ts = db.execute_query(reader_cumulative_ts_query)
    metadata['reader_cumulative_updated'] = reader_cumulative_ts[0]['last_updated'] if reader_cumulative_ts and reader_cumulative_ts[0] and reader_cumulative_ts[0]['last_updated'] else 'Never'

    # Roster timestamp
    roster_ts_query = "SELECT datetime('now', 'localtime') as last_updated"
    roster_ts = db.execute_query(roster_ts_query)
    metadata['roster_updated'] = roster_ts[0]['last_updated'] if roster_ts and roster_ts[0] else 'Never'

    # Team Color Bonus
    metadata['team_color_bonus_updated'] = '2025-10-13 (Spirit Day)'

    return render_template('grade_level.html',
                         environment=env,
                         date_filter=date_filter,
                         grade_filter=grade_filter,
                         team_filter=team_filter,
                         dates=dates,
                         current_day=current_day,
                         campaign_date=campaign_date,
                         total_days=total_days,
                         full_contest_range=full_contest_range,
                         classes=classes,
                         grade_summaries=grade_summaries,
                         banner_leaders=banner_leaders,
                         banner_leaders_by_grade=banner_leaders_by_grade,
                         school_winners=school_winners if classes else {},
                         grade_winners=grade_winners if classes else {},
                         metadata=metadata,
                         team_names=team_names)


@app.route('/students')
def students_tab():
    """Students master-detail dashboard"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()

    # Get filter parameters
    date_filter = request.args.get('date', 'all')
    grade_filter = request.args.get('grade', 'all')
    team_filter = request.args.get('team', 'all')

    # Get all available dates for filter dropdown
    dates = db.get_all_dates()

    # Get team names (sorted alphabetically for consistency)
    team_names_query = "SELECT DISTINCT team_name FROM Roster ORDER BY team_name"
    team_names_result = db.execute_query(team_names_query)
    team_names = [row['team_name'] for row in team_names_result] if team_names_result else []

    # Calculate full contest date range
    sorted_dates = sorted(dates)
    total_days = len(sorted_dates)
    if sorted_dates:
        start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').strftime('%b %d')
        end_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d').strftime('%b %d, %Y')
        full_contest_range = f"{start_date}-{end_date}"
    else:
        full_contest_range = "Oct 10-15, 2025"  # Fallback if no dates

    # === GET DATA FROM DATABASE ===

    # Get all students data with filters
    students = db.get_students_data(date_filter, grade_filter, team_filter)

    # Get banner metrics (6 metrics)
    banner_metrics = db.get_students_banner(date_filter, grade_filter, team_filter)

    # Get school-wide winners (gold highlights)
    school_winners = db.get_students_school_winners(date_filter)

    # Get filtered winners (silver highlights)
    filtered_winners = {}
    grade_winners = {}
    if grade_filter != 'all' or team_filter != 'all':
        # Specific filter applied - use filtered winners
        filtered_winners = db.get_students_filtered_winners(date_filter, grade_filter, team_filter)
    else:
        # All grades shown - get grade-level winners for silver highlighting
        grade_winners = db.get_students_grade_winners(date_filter)

    # === BANNER SETUP ===

    # Campaign Day calculation - date-aware
    if date_filter != 'all' and date_filter in dates:
        # Find position of selected date (1-based)
        current_day = sorted_dates.index(date_filter) + 1
        campaign_date = date_filter  # Store for subtitle display
    else:
        # Full contest - show total days
        current_day = total_days
        campaign_date = full_contest_range

    # Build banner dictionary with all 6 metrics
    banner = {
        'campaign_day': current_day,
        'campaign_date': campaign_date,
        'total_days': total_days,  # Total contest days (never changes with filters)
        'days_in_filter': current_day,  # Number of days included in current filter (for "X/Y" display)
        'total_fundraising': banner_metrics.get('total_fundraising', 0),
        'total_minutes': banner_metrics.get('total_minutes', 0),
        'total_hours': banner_metrics.get('total_minutes', 0) // 60,
        'total_sponsors': banner_metrics.get('total_sponsors', 0),
        'avg_participation_pct': banner_metrics.get('avg_participation_pct', 0),
        'goal_met_pct': banner_metrics.get('goal_met_pct', 0),
        'total_students': banner_metrics.get('total_students', 0)
    }

    # === HIGHLIGHTING SETUP ===

    # Determine which highlighting mode to use
    # - Gold: School-wide winners (all students)
    # - Silver: Filtered winners (grade/team subset)
    highlight_mode = 'gold' if (grade_filter == 'all' and team_filter == 'all') else 'silver'

    # Choose appropriate winners dict
    winners = school_winners if highlight_mode == 'gold' else filtered_winners

    # === BUILD TEAM INDEX MAPPING (alphabetical order determines color) ===
    # Team 1 (alphabetically first) = index 0 (blue)
    # Team 2 (alphabetically second) = index 1 (yellow)
    team_index_map = {}
    for idx, team_name in enumerate(team_names):
        team_index_map[team_name] = idx

    # === METADATA (Last Updated) ===
    metadata = {}

    # Daily_Logs timestamp
    daily_logs_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'daily'
    """
    daily_logs_ts = db.execute_query(daily_logs_ts_query)
    if daily_logs_ts and daily_logs_ts[0] and daily_logs_ts[0]['last_updated']:
        metadata['daily_logs_updated'] = daily_logs_ts[0]['last_updated']
    else:
        metadata['daily_logs_updated'] = 'Never'

    # Reader_Cumulative timestamp
    reader_cumulative_ts_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'cumulative'
    """
    reader_cumulative_ts = db.execute_query(reader_cumulative_ts_query)
    if reader_cumulative_ts and reader_cumulative_ts[0] and reader_cumulative_ts[0]['last_updated']:
        metadata['reader_cumulative_updated'] = reader_cumulative_ts[0]['last_updated']
    else:
        metadata['reader_cumulative_updated'] = 'Never'

    # Roster timestamp (static - set during init)
    metadata['roster_updated'] = '09/15/2025 8:00 AM'

    # Grade_Rules timestamp (static)
    metadata['grade_rules_updated'] = '09/15/2025 8:00 AM'

    # === RENDER TEMPLATE ===

    return render_template('students.html',
                         environment=env,
                         students=students,
                         banner=banner,
                         school_winners=school_winners,
                         filtered_winners=filtered_winners,
                         grade_winners=grade_winners,
                         highlight_mode=highlight_mode,
                         date_filter=date_filter,
                         grade_filter=grade_filter,
                         team_filter=team_filter,
                         dates=dates,
                         team_names=team_names,
                         team_index_map=team_index_map,
                         full_contest_range=full_contest_range,
                         metadata=metadata)


@app.route('/student/<student_name>')
def student_detail(student_name):
    """Student detail API endpoint (returns JSON for modal)"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()

    # Get filter parameter (should match main page filter)
    date_filter = request.args.get('date', 'all')

    # Get all dates for calculating days_in_filter
    dates = db.get_all_dates()
    sorted_dates = sorted(dates)

    # Calculate days in filter (for "X/Y" display)
    if date_filter != 'all' and date_filter in dates:
        days_in_filter = sorted_dates.index(date_filter) + 1
    else:
        days_in_filter = len(sorted_dates)

    # Get student detail from database
    detail = db.get_student_detail(student_name, date_filter)

    # Add days_in_filter to response
    detail['days_in_filter'] = days_in_filter

    # Return JSON
    return jsonify(detail)


# Keep old index route for backward compatibility during transition
@app.route('/index_old')
def index():
    """Main dashboard (old version - kept for reference)"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()
    reports = get_current_reports()

    counts = db.get_table_counts()
    dates = db.get_all_dates()

    # Get overall totals
    totals_query = """
        SELECT
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name || '-' || dl.log_date END) as total_participations,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes,
            COUNT(DISTINCT dl.log_date) as days_with_data,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) as unique_participants
        FROM Daily_Logs dl
    """
    totals_result = db.execute_query(totals_query)
    totals = totals_result[0] if totals_result else {}

    # Get total donations from Reader_Cumulative
    donations_query = "SELECT ROUND(SUM(donation_amount), 2) as total_donations FROM Reader_Cumulative"
    donations_result = db.execute_query(donations_query)
    if donations_result and donations_result[0]['total_donations']:
        totals['total_donations'] = donations_result[0]['total_donations']
    else:
        totals['total_donations'] = 0

    # Get verification statistics for comparison with online program
    verification_stats = {}

    # Get total students from roster
    roster_count_query = "SELECT COUNT(*) as total_students FROM Roster"
    roster_count = db.execute_query(roster_count_query)
    total_students = roster_count[0]['total_students'] if roster_count and roster_count[0] else 0

    # Get participating students count and days of data
    participation_query = """
        SELECT
            COUNT(DISTINCT CASE WHEN minutes_read > 0 THEN student_name END) as participating_students,
            COUNT(DISTINCT log_date) as days_of_data
        FROM Daily_Logs
    """
    participation_result = db.execute_query(participation_query)
    if participation_result and participation_result[0]:
        participating_students = participation_result[0]['participating_students'] or 0
        days_of_data = participation_result[0]['days_of_data'] or 0
    else:
        participating_students = 0
        days_of_data = 0

    # Calculate participation percentage
    if total_students > 0:
        participation_pct = round((participating_students / total_students) * 100, 1)
    else:
        participation_pct = 0

    verification_stats['total_students'] = total_students
    verification_stats['participating_students'] = participating_students
    verification_stats['participation_pct'] = participation_pct
    verification_stats['days_of_data'] = days_of_data

    # 1. Total Donations with donor count
    donations_detail_query = """
        SELECT
            ROUND(SUM(donation_amount), 2) as total_donations,
            COUNT(CASE WHEN donation_amount > 0 THEN 1 END) as donor_count
        FROM Reader_Cumulative
    """
    donations_detail = db.execute_query(donations_detail_query)
    if donations_detail and donations_detail[0]:
        verification_stats['total_donations'] = donations_detail[0]['total_donations'] or 0
        verification_stats['donor_count'] = donations_detail[0]['donor_count'] or 0
    else:
        verification_stats['total_donations'] = 0
        verification_stats['donor_count'] = 0

    # 2. Total Minutes Read (CAPPED at 120 min/day for official counting) and reader count
    # Note: We use capped minutes here because this is the "official" total that matches school counting rules
    # Reader_Cumulative stores UNCAPPED minutes, so we're comparing capped vs uncapped (apples-to-oranges)
    # This shows the real reconciliation difference that matters for data verification
    minutes_detail_query = """
        SELECT
            SUM(MIN(minutes_read, 120)) as total_minutes_capped,
            COUNT(DISTINCT CASE WHEN minutes_read > 0 THEN student_name END) as reader_count
        FROM Daily_Logs
    """
    minutes_detail = db.execute_query(minutes_detail_query)
    if minutes_detail and minutes_detail[0]:
        verification_stats['total_minutes'] = int(minutes_detail[0]['total_minutes_capped'] or 0)
        verification_stats['reader_count'] = minutes_detail[0]['reader_count'] or 0
    else:
        verification_stats['total_minutes'] = 0
        verification_stats['reader_count'] = 0

    # Also get minutes from Reader_Cumulative for comparison (uncapped)
    cumulative_minutes_query = """
        SELECT
            SUM(cumulative_minutes) as total_cumulative_minutes
        FROM Reader_Cumulative
    """
    cumulative_minutes_detail = db.execute_query(cumulative_minutes_query)
    if cumulative_minutes_detail and cumulative_minutes_detail[0]:
        verification_stats['total_minutes_cumulative'] = int(cumulative_minutes_detail[0]['total_cumulative_minutes'] or 0)
    else:
        verification_stats['total_minutes_cumulative'] = 0

    # Calculate difference: Reader_Cumulative (uncapped) - Daily_Logs (capped)
    # This is the reconciliation difference that includes both capping effect and data sync issues
    verification_stats['total_minutes_difference'] = verification_stats['total_minutes_cumulative'] - verification_stats['total_minutes']

    # 3. Top Readers (by donations and by minutes)
    top_fundraiser_query = """
        SELECT student_name, donation_amount
        FROM Reader_Cumulative
        WHERE donation_amount > 0
        ORDER BY donation_amount DESC
        LIMIT 1
    """
    top_fundraiser = db.execute_query(top_fundraiser_query)
    if top_fundraiser and top_fundraiser[0]:
        verification_stats['top_fundraiser_name'] = top_fundraiser[0]['student_name']
        verification_stats['top_fundraiser_amount'] = top_fundraiser[0]['donation_amount']
    else:
        verification_stats['top_fundraiser_name'] = 'N/A'
        verification_stats['top_fundraiser_amount'] = 0

    top_reader_query = """
        SELECT
            student_name,
            SUM(MIN(minutes_read, 120)) as total_minutes_credited
        FROM Daily_Logs
        WHERE minutes_read > 0
        GROUP BY student_name
        ORDER BY total_minutes_credited DESC
        LIMIT 1
    """
    top_reader = db.execute_query(top_reader_query)
    if top_reader and top_reader[0]:
        verification_stats['top_reader_name'] = top_reader[0]['student_name']
        verification_stats['top_reader_minutes'] = int(top_reader[0]['total_minutes_credited'])
    else:
        verification_stats['top_reader_name'] = 'N/A'
        verification_stats['top_reader_minutes'] = 0

    # 4. Top Classes (by donations and by minutes)
    top_fundraising_class_query = """
        SELECT
            r.teacher_name,
            r.class_name,
            SUM(rc.donation_amount) as total_donations
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.teacher_name, r.class_name
        HAVING total_donations > 0
        ORDER BY total_donations DESC
        LIMIT 1
    """
    top_fundraising_class = db.execute_query(top_fundraising_class_query)
    if top_fundraising_class and top_fundraising_class[0]:
        verification_stats['top_fundraising_class'] = top_fundraising_class[0]['teacher_name']
        verification_stats['top_fundraising_class_amount'] = top_fundraising_class[0]['total_donations']
    else:
        verification_stats['top_fundraising_class'] = 'N/A'
        verification_stats['top_fundraising_class_amount'] = 0

    top_reading_class_query = """
        SELECT
            r.teacher_name,
            r.class_name,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes_credited
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE dl.minutes_read > 0
        GROUP BY r.teacher_name, r.class_name
        ORDER BY total_minutes_credited DESC
        LIMIT 1
    """
    top_reading_class = db.execute_query(top_reading_class_query)
    if top_reading_class and top_reading_class[0]:
        verification_stats['top_reading_class'] = top_reading_class[0]['teacher_name']
        verification_stats['top_reading_class_minutes'] = int(top_reading_class[0]['total_minutes_credited'])
    else:
        verification_stats['top_reading_class'] = 'N/A'
        verification_stats['top_reading_class_minutes'] = 0

    # 5. Integrity Checks - Run all integrity reports
    # 5a. Minutes Integrity Check - Compare Daily_Logs total vs Reader_Cumulative total
    integrity_check_query = """
        SELECT
            COALESCE(SUM(dl.minutes_read), 0) as daily_total,
            COALESCE(SUM(rc.cumulative_minutes), 0) as cumulative_total,
            COALESCE(SUM(rc.cumulative_minutes), 0) - COALESCE(SUM(dl.minutes_read), 0) as difference
        FROM (SELECT SUM(minutes_read) as minutes_read FROM Daily_Logs) dl,
             (SELECT SUM(cumulative_minutes) as cumulative_minutes FROM Reader_Cumulative) rc
    """
    integrity_result = db.execute_query(integrity_check_query)
    if integrity_result and integrity_result[0]:
        daily_total = int(integrity_result[0]['daily_total'] or 0)
        cumulative_total = int(integrity_result[0]['cumulative_total'] or 0)
        difference = int(integrity_result[0]['difference'] or 0)

        verification_stats['integrity_daily_total'] = daily_total
        verification_stats['integrity_cumulative_total'] = cumulative_total
        verification_stats['integrity_difference'] = difference
        verification_stats['integrity_match'] = (difference == 0)
    else:
        verification_stats['integrity_daily_total'] = 0
        verification_stats['integrity_cumulative_total'] = 0
        verification_stats['integrity_difference'] = 0
        verification_stats['integrity_match'] = True

    # 5b. Student Name Sync Check (Q22)
    q22_result = reports.q22_student_name_sync_check()
    verification_stats['name_sync_pass'] = not q22_result.get('has_issues', False)
    verification_stats['name_sync_note'] = q22_result.get('note', '')

    # 5c. Roster Integrity Check (Q23)
    q23_result = reports.q23_roster_integrity_check()
    verification_stats['roster_integrity_pass'] = not q23_result.get('has_issues', False)
    verification_stats['roster_integrity_note'] = q23_result.get('note', '')

    # Overall integrity status
    verification_stats['all_integrity_checks_pass'] = (
        verification_stats['integrity_match'] and
        verification_stats['name_sync_pass'] and
        verification_stats['roster_integrity_pass']
    )

    # Timestamp for when integrity checks were run
    verification_stats['integrity_check_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get timestamps for "Last Updated" display
    # For donations data (from Reader_Cumulative)
    donations_timestamp_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'cumulative'
    """
    donations_ts_result = db.execute_query(donations_timestamp_query)
    if donations_ts_result and donations_ts_result[0] and donations_ts_result[0]['last_updated']:
        verification_stats['donations_last_updated'] = donations_ts_result[0]['last_updated']
    else:
        verification_stats['donations_last_updated'] = None

    # For minutes data (from Daily_Logs)
    minutes_timestamp_query = """
        SELECT MAX(upload_timestamp) as last_updated
        FROM Upload_History
        WHERE file_type = 'daily'
    """
    minutes_ts_result = db.execute_query(minutes_timestamp_query)
    if minutes_ts_result and minutes_ts_result[0] and minutes_ts_result[0]['last_updated']:
        verification_stats['minutes_last_updated'] = minutes_ts_result[0]['last_updated']
    else:
        verification_stats['minutes_last_updated'] = None

    # Get today's summary (most recent date)
    today_summary = None
    if dates:
        latest_date = dates[0]
        today_summary = reports.q2_daily_summary(latest_date, 'team')

    return render_template('index.html',
                         counts=counts,
                         dates=dates,
                         environment=env,
                         totals=totals,
                         today_summary=today_summary,
                         latest_date=dates[0] if dates else None,
                         verification_stats=verification_stats)


@app.route('/upload')
def upload_page():
    """Data upload page"""
    env = session.get('environment', DEFAULT_DATABASE)
    return render_template('upload.html', environment=env)


@app.route('/api/set_environment', methods=['POST'])
def set_environment():
    """Set the current environment (sample or prod)"""
    env = request.json.get('environment', DEFAULT_DATABASE)
    if env in ['sample', 'prod']:
        session['environment'] = env
        # Save preference to config file for next startup
        write_config(env)
        return jsonify({'success': True, 'environment': env})
    return jsonify({'success': False, 'error': 'Invalid environment'}), 400


@app.route('/api/upload_history')
def get_upload_history():
    """Get upload history for current environment"""
    try:
        db = get_current_db()
        history = db.get_upload_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete_day/<log_date>', methods=['DELETE'])
def delete_day(log_date):
    """Delete all data for a specific date"""
    try:
        db = get_current_db()
        env = session.get('environment', DEFAULT_DATABASE)

        # Delete from Daily_Logs
        result = db.delete_day_data(log_date)
        result['environment'] = env

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete_cumulative', methods=['DELETE'])
def delete_cumulative():
    """Delete all cumulative data (donations, sponsors, cumulative minutes)"""
    try:
        db = get_current_db()
        env = session.get('environment', DEFAULT_DATABASE)

        # Delete from Reader_Cumulative
        result = db.delete_cumulative_data()
        result['environment'] = env

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload_daily', methods=['POST'])
def upload_daily():
    """Handle daily minutes data upload"""
    try:
        log_date = request.form.get('log_date')
        if not log_date:
            return jsonify({'success': False, 'error': 'Date is required'}), 400

        minutes_file = request.files.get('minutes_file')

        if not minutes_file:
            return jsonify({'success': False, 'error': 'Minutes file is required'}), 400

        # Get confirmation flag
        confirmed = request.form.get('confirmed', 'false').lower() == 'true'

        # Get current environment
        env = session.get('environment', DEFAULT_DATABASE)

        # Safeguard: Check if sample data is being uploaded to production
        if env == 'prod' and not confirmed:
            # Check filename for "sample" keyword
            minutes_name = minutes_file.filename.lower()

            if 'sample' in minutes_name:
                return jsonify({
                    'success': False,
                    'needs_sample_confirmation': True,
                    'error': f'WARNING: You are uploading file with "sample" in the name to PRODUCTION environment. File: {minutes_file.filename}. Please confirm this is intentional.',
                    'filename': minutes_file.filename
                }), 400

        db = get_current_db()
        result = db.upload_daily_data(log_date, minutes_file, confirmed)

        # Add environment info to result
        result['environment'] = env

        # If upload failed, return error with appropriate status code
        if not result.get('success', True):
            error_msg = result.get('error') or (result['errors'][0] if result.get('errors') else 'Unknown error occurred')
            return jsonify({'success': False, 'error': error_msg, 'errors': result.get('errors', [])}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload_cumulative', methods=['POST'])
def upload_cumulative():
    """Handle cumulative stats upload"""
    try:
        cumulative_file = request.files.get('cumulative_file')

        if not cumulative_file:
            return jsonify({'success': False, 'error': 'Cumulative stats file is required'}), 400

        # Get confirmation flag
        confirmed = request.form.get('confirmed', 'false').lower() == 'true'

        # Get current environment
        env = session.get('environment', DEFAULT_DATABASE)

        # Safeguard: Check if sample data is being uploaded to production
        if env == 'prod' and not confirmed:
            # Check filename for "sample" keyword
            cumulative_name = cumulative_file.filename.lower()

            if 'sample' in cumulative_name:
                return jsonify({
                    'success': False,
                    'needs_sample_confirmation': True,
                    'error': f'WARNING: You are uploading file with "sample" in the name to PRODUCTION environment. File: {cumulative_file.filename}. Please confirm this is intentional.',
                    'filename': cumulative_file.filename
                }), 400

        db = get_current_db()
        result = db.upload_cumulative_stats(cumulative_file, confirmed)

        # Add environment info to result
        result['environment'] = env

        # If upload failed, return error with appropriate status code
        if not result.get('success', True):
            error_msg = result.get('error') or (result['errors'][0] if result.get('errors') else 'Unknown error occurred')
            return jsonify({'success': False, 'error': error_msg, 'errors': result.get('errors', [])}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload_team_color_bonus', methods=['POST'])
def upload_team_color_bonus():
    """Handle Team Color Bonus data upload"""
    try:
        event_date = request.form.get('event_date')
        if not event_date:
            return jsonify({'success': False, 'error': 'Event date is required'}), 400

        bonus_file = request.files.get('bonus_file')

        if not bonus_file:
            return jsonify({'success': False, 'error': 'Team Color Bonus file is required'}), 400

        # Get confirmation flag
        confirmed = request.form.get('confirmed', 'false').lower() == 'true'

        # Get current environment
        env = session.get('environment', DEFAULT_DATABASE)

        # Safeguard: Check if sample data is being uploaded to production
        if env == 'prod' and not confirmed:
            # Check filename for "sample" keyword
            bonus_name = bonus_file.filename.lower()

            if 'sample' in bonus_name:
                return jsonify({
                    'success': False,
                    'needs_sample_confirmation': True,
                    'error': f'WARNING: You are uploading file with "sample" in the name to PRODUCTION environment. File: {bonus_file.filename}. Please confirm this is intentional.',
                    'filename': bonus_file.filename
                }), 400

        # Read CSV data
        csv_data = bonus_file.read().decode('utf-8')

        db = get_current_db()
        result = db.load_team_color_bonus_data(csv_data, event_date)

        # Add environment info to result
        result['environment'] = env

        # If upload failed, return error with appropriate status code
        if not result.get('success', True):
            error_msg = result.get('error') or (result['errors'][0] if result.get('errors') else 'Unknown error occurred')
            return jsonify({'success': False, 'error': error_msg, 'errors': result.get('errors', [])}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete_upload_history_batch', methods=['DELETE'])
def delete_upload_history_batch():
    """Delete multiple upload history records"""
    try:
        data = request.json
        upload_ids = data.get('upload_ids', [])

        if not upload_ids:
            return jsonify({
                'success': False,
                'error': 'No upload IDs provided'
            }), 400

        # Get current environment
        env = session.get('environment', DEFAULT_DATABASE)

        db = get_current_db()
        result = db.delete_upload_history_batch(upload_ids)

        # Add environment info to result
        result['environment'] = env

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/reports')
def reports_page():
    """Reports listing page"""
    env = session.get('environment', DEFAULT_DATABASE)
    report_list = [
        {'id': 'q2', 'name': 'Q2: Daily Summary Report', 'description': 'Daily summary by class or team with participation rates', 'group': 'update', 'type': 'daily'},
        {'id': 'q3', 'name': 'Q3: Reader Cumulative Enhanced', 'description': 'Complete cumulative stats with class, teacher, team, and participation metrics', 'group': 'export', 'type': 'cumulative'},
        {'id': 'q4', 'name': 'Q4/Slide 4: Prize Drawing', 'description': 'Random prize drawing - one winner per grade from students who met their goal', 'group': 'prize', 'type': 'daily'},
        {'id': 'q5', 'name': 'Q5: Student Cumulative Report', 'description': 'Student cumulative stats - Top Readers, Goal Getters, Top Fundraisers', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q6', 'name': 'Q6: Class Participation Winner', 'description': 'Class participation winner ranked by average daily participation rate', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q7', 'name': 'Q7: Complete Log', 'description': 'Complete denormalized log for export to Excel/CSV', 'group': 'export', 'type': 'export'},
        {'id': 'q8', 'name': 'Q8: Student Reading Details', 'description': 'Individual student reading details - minutes read and days met goal', 'group': 'export', 'type': 'cumulative'},
        {'id': 'q9', 'name': 'Q9: Most Donations Per Grade', 'description': 'Student with highest donation amount in each grade', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q10', 'name': 'Q10: Most Minutes Per Grade', 'description': 'Student with most minutes read in each grade', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q11', 'name': 'Q11: Most Sponsors Per Grade', 'description': 'Student with most sponsors in each grade', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q12', 'name': 'Q12: Best Class Per Grade', 'description': 'Leading class in each grade by participation rate', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q13', 'name': 'Q13: Best Class in School', 'description': 'Overall best classroom by participation rate', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q14', 'name': 'Q14/Slide 3: Team Participation', 'description': 'Team participation winner by average participation rate', 'group': 'update', 'type': 'cumulative'},
        {'id': 'q15', 'name': 'Q15: Goal Getters', 'description': 'Students who met their reading goal every day', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q16', 'name': 'Q16: Top Earner Per Team', 'description': 'Student with highest donation on each team', 'group': 'prize', 'type': 'cumulative'},
        {'id': 'q18', 'name': 'Q18/Slide 2: Lead Class by Grade', 'description': 'Leading class in each grade by average daily participation rate', 'group': 'update', 'type': 'cumulative'},
        {'id': 'q19', 'name': 'Q19/Slide 5: Team Minutes', 'description': 'Total minutes read by each team', 'group': 'update', 'type': 'cumulative'},
        {'id': 'q20', 'name': 'Q20/Slide 6: Team Donations', 'description': 'Total donations raised by each team', 'group': 'update', 'type': 'cumulative'},
    ]
    db = get_current_db()
    dates = db.get_all_dates()
    return render_template('reports.html', reports=report_list, dates=dates, environment=env)


@app.route('/admin')
def admin_page():
    """Administration page"""
    env = session.get('environment', DEFAULT_DATABASE)
    admin_report_list = [
        {'id': 'q1', 'name': 'Q1: Table Row Counts', 'description': 'Database table row counts (utility report)', 'type': 'utility'},
        {'id': 'q21', 'name': 'Q21: Data Sync & Minutes Integrity Check', 'description': 'Verify students are synced between tables and daily minutes match cumulative', 'type': 'utility'},
        {'id': 'q22', 'name': 'Q22: Student Name Sync Check', 'description': 'Verify students in Daily_Logs match Reader_Cumulative', 'type': 'utility'},
        {'id': 'q23', 'name': 'Q23: Roster Integrity Check', 'description': 'Verify all students exist in Roster table', 'type': 'utility'},
    ]
    return render_template('admin.html', reports=admin_report_list, environment=env)


@app.route('/api/report/<report_id>')
def run_report(report_id):
    """Run a specific report"""
    try:
        # Get optional parameters
        log_date = request.args.get('date')
        group_by = request.args.get('group_by', 'class')
        sort_by = request.args.get('sort_by', 'minutes')
        limit = request.args.get('limit', type=int)

        # Get current environment's report generator
        reports = get_current_reports()
        db = get_current_db()

        # Route to appropriate report
        if report_id == 'q1':
            result = reports.q1_table_counts()
        elif report_id == 'q2':
            result = reports.q2_daily_summary(log_date, group_by)
        elif report_id == 'q3':
            result = reports.q3_reader_cumulative_enhanced()
        elif report_id == 'q4':
            if not log_date:
                dates = db.get_all_dates()
                log_date = dates[0] if dates else None
            if not log_date:
                return jsonify({'error': 'No data available'}), 400
            result = reports.q4_prize_drawing(log_date)
        elif report_id == 'q5':
            result = reports.q5_student_cumulative(sort_by, limit)
        elif report_id == 'q6':
            result = reports.q6_class_participation()
        elif report_id == 'q7':
            result = reports.q7_complete_log(log_date)
        elif report_id == 'q14':
            result = reports.q14_team_participation()
        elif report_id == 'q18':
            result = reports.q18_lead_class_by_grade()
        elif report_id == 'q19':
            result = reports.q19_team_minutes()
        elif report_id == 'q20':
            result = reports.q20_team_donations()
        elif report_id == 'q21':
            result = reports.q21_minutes_integrity_check()
        elif report_id == 'q8':
            result = reports.q8_student_reading_details()
        elif report_id == 'q22':
            result = reports.q22_student_name_sync_check()
        elif report_id == 'q23':
            result = reports.q23_roster_integrity_check()
        elif report_id == 'q9':
            result = reports.q9_most_donations_by_grade()
        elif report_id == 'q10':
            result = reports.q10_most_minutes_by_grade()
        elif report_id == 'q11':
            result = reports.q11_most_sponsors_by_grade()
        elif report_id == 'q12':
            result = reports.q12_best_class_by_grade_simplified()
        elif report_id == 'q13':
            result = reports.q13_overall_best_class_simplified()
        elif report_id == 'q15':
            result = reports.q15_goal_getters()
        elif report_id == 'q16':
            result = reports.q16_top_earner_per_team()
        else:
            return jsonify({'error': 'Unknown report'}), 404

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/<report_id>')
def export_report(report_id):
    """Export report as CSV"""
    try:
        # Get the report data
        log_date = request.args.get('date')
        group_by = request.args.get('group_by', 'class')
        sort_by = request.args.get('sort_by', 'minutes')

        # Get current environment's report generator
        reports = get_current_reports()
        db = get_current_db()

        # Get report data (same logic as run_report)
        if report_id == 'q1':
            result = reports.q1_table_counts()
        elif report_id == 'q2':
            result = reports.q2_daily_summary(log_date, group_by)
        elif report_id == 'q3':
            result = reports.q3_reader_cumulative_enhanced()
        elif report_id == 'q4':
            if not log_date:
                dates = db.get_all_dates()
                log_date = dates[0] if dates else None
            result = reports.q4_prize_drawing(log_date)
        elif report_id == 'q5':
            result = reports.q5_student_cumulative(sort_by)
        elif report_id == 'q6':
            result = reports.q6_class_participation()
        elif report_id == 'q7':
            result = reports.q7_complete_log(log_date)
        elif report_id == 'q14':
            result = reports.q14_team_participation()
        elif report_id == 'q18':
            result = reports.q18_lead_class_by_grade()
        elif report_id == 'q19':
            result = reports.q19_team_minutes()
        elif report_id == 'q20':
            result = reports.q20_team_donations()
        elif report_id == 'q21':
            result = reports.q21_minutes_integrity_check()
        elif report_id == 'q8':
            result = reports.q8_student_reading_details()
        elif report_id == 'q22':
            result = reports.q22_student_name_sync_check()
        elif report_id == 'q23':
            result = reports.q23_roster_integrity_check()
        elif report_id == 'q9':
            result = reports.q9_most_donations_by_grade()
        elif report_id == 'q10':
            result = reports.q10_most_minutes_by_grade()
        elif report_id == 'q11':
            result = reports.q11_most_sponsors_by_grade()
        elif report_id == 'q12':
            result = reports.q12_best_class_by_grade_simplified()
        elif report_id == 'q13':
            result = reports.q13_overall_best_class_simplified()
        elif report_id == 'q15':
            result = reports.q15_goal_getters()
        elif report_id == 'q16':
            result = reports.q16_top_earner_per_team()
        else:
            return jsonify({'error': 'Unknown report'}), 404

        # Convert to CSV
        output = io.StringIO()
        if result['data']:
            writer = csv.DictWriter(output, fieldnames=result['columns'])
            writer.writeheader()
            writer.writerows(result['data'])

        # Create response
        csv_data = output.getvalue()
        response = Response(csv_data, mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename={report_id}_{datetime.now().strftime("%Y%m%d")}.csv'

        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export_all')
def export_all():
    """Export all data as ZIP - Placeholder for now"""
    try:
        # TODO: Implement full ZIP export in Phase 3
        return jsonify({'error': 'Feature coming soon - Export All Data (ZIP)'}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== Database Management Endpoints (Phase 2: Multi-Database) ==========

@app.route('/api/databases', methods=['GET'])
def list_databases():
    """List all registered year databases"""
    try:
        db = get_current_db()
        databases = db.list_databases()
        return jsonify({
            'success': True,
            'databases': databases
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/databases/register', methods=['POST'])
def register_database():
    """Register a new year database"""
    try:
        data = request.json
        year = data.get('year')
        db_filename = data.get('db_filename')
        description = data.get('description', '')

        if not year or not db_filename:
            return jsonify({
                'success': False,
                'error': 'Year and database filename are required'
            }), 400

        db = get_current_db()
        result = db.register_database(int(year), db_filename, description)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/databases/<int:year>', methods=['GET'])
def get_database_info(year):
    """Get information about a specific year database"""
    try:
        db = get_current_db()
        info = db.get_database_info(year)

        if info:
            return jsonify({
                'success': True,
                'database': info
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Database for year {year} not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/databases/<int:year>/stats', methods=['PUT'])
def update_database_stats(year):
    """Update statistics for a year database"""
    try:
        db = get_current_db()
        result = db.update_database_stats(year)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/databases/<int:year>/activate', methods=['PUT'])
def activate_database(year):
    """Set a database as active"""
    try:
        db = get_current_db()
        result = db.set_active_database(year)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/databases/active', methods=['GET'])
def get_active_database():
    """Get the currently active database"""
    try:
        db = get_current_db()
        active = db.get_active_database()

        if active:
            return jsonify({
                'success': True,
                'database': active
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No active database set'
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/databases/<int:year>', methods=['DELETE'])
def delete_database_registration(year):
    """Delete a database registration"""
    try:
        db = get_current_db()
        result = db.delete_database_registration(year)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== Clear Data Tables Endpoints (Feature 29) ==========

@app.route('/api/table_counts', methods=['GET'])
def get_table_counts():
    """Get record counts for clearable tables"""
    try:
        db = get_current_db()
        conn = db.get_connection()
        cursor = conn.cursor()

        counts = {}
        tables = ['Upload_History', 'Reader_Cumulative', 'Daily_Logs']

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            counts[table] = result[0] if result else 0

        return jsonify({
            'success': True,
            'counts': counts
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear_tables', methods=['DELETE'])
def clear_tables():
    """Clear selected data tables"""
    try:
        data = request.json
        tables = data.get('tables', [])

        # Validate table names
        valid_tables = ['Upload_History', 'Reader_Cumulative', 'Daily_Logs']
        for table in tables:
            if table not in valid_tables:
                return jsonify({
                    'success': False,
                    'error': f'Invalid table name: {table}'
                }), 400

        if not tables:
            return jsonify({
                'success': False,
                'error': 'No tables specified'
            }), 400

        db = get_current_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        env = session.get('environment', DEFAULT_DATABASE)

        deleted = {}

        try:
            # Begin transaction
            cursor.execute('BEGIN')

            # Clear each table and track deleted counts
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count_before = cursor.fetchone()[0]

                cursor.execute(f"DELETE FROM {table}")
                deleted[table] = count_before

            # Commit transaction
            conn.commit()

            # Log the operation
            print(f"[{datetime.now()}] Cleared {len(tables)} tables in {env} environment:")
            for table, count in deleted.items():
                print(f"  - {table}: {count} records deleted")

            return jsonify({
                'success': True,
                'deleted': deleted,
                'environment': env
            })

        except Exception as e:
            # Rollback on error
            conn.rollback()
            return jsonify({
                'success': False,
                'error': f'Transaction failed: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/workflows')
def workflows_page():
    """Workflow execution page"""
    env = session.get('environment', DEFAULT_DATABASE)
    db = get_current_db()
    dates = db.get_all_dates()
    return render_template('workflows.html', dates=dates, environment=env)


@app.route('/tables')
def tables_page():
    """Database tables viewer page"""
    env = session.get('environment', DEFAULT_DATABASE)
    table_list = [
        {'id': 'roster', 'name': 'Roster', 'description': 'All students with their class assignments, teachers, grades, and teams'},
        {'id': 'class_info', 'name': 'Class Info', 'description': 'Summary of each class including home room, teacher, grade, team, and total students'},
        {'id': 'grade_rules', 'name': 'Grade Rules', 'description': 'Minimum and maximum daily reading minutes by grade level'},
        {'id': 'daily_logs', 'name': 'Daily Logs', 'description': 'Daily reading minutes for each student by date (participation tracking)'},
        {'id': 'reader_cumulative', 'name': 'Reader Cumulative', 'description': 'Cumulative fundraising stats (donations, sponsors) and total minutes for each student'},
        {'id': 'team_color_bonus', 'name': 'Team Color Bonus', 'description': 'Special event bonus data: students wearing team colors earn extra participation points and minutes'},
        {'id': 'upload_history', 'name': 'Upload History', 'description': 'Complete history of all data uploads with timestamps, file details, and status'},
        {'id': 'complete_log', 'name': 'Q7: Complete Log (Query)', 'description': 'Complete denormalized log combining all data - perfect for export to Excel/CSV'},
    ]
    return render_template('tables.html', tables=table_list, environment=env)


@app.route('/api/table/<table_id>')
def view_table(table_id):
    """View contents of a database table"""
    try:
        db = get_current_db()
        reports = get_current_reports()

        # Handle Q7 Complete Log (query, not a table)
        if table_id == 'complete_log':
            report_result = reports.q7_complete_log()
            return jsonify({
                'title': 'Q7: Complete Log (Query)',
                'description': 'Complete denormalized log combining all data from Daily_Logs and Roster',
                'columns': report_result['columns'],
                'data': report_result['data'],
                'row_count': len(report_result['data'])
            })

        # Map table IDs to actual table names
        table_map = {
            'roster': 'Roster',
            'class_info': 'Class_Info',
            'grade_rules': 'Grade_Rules',
            'daily_logs': 'Daily_Logs',
            'reader_cumulative': 'Reader_Cumulative',
            'team_color_bonus': 'Team_Color_Bonus',
            'upload_history': 'Upload_History'
        }

        if table_id not in table_map:
            return jsonify({'error': 'Unknown table'}), 404

        table_name = table_map[table_id]

        # Get table data
        query = f"SELECT * FROM {table_name}"
        if table_id == 'daily_logs':
            query += " ORDER BY log_date DESC, student_name ASC"
        elif table_id == 'reader_cumulative':
            query += " ORDER BY team_name ASC, student_name ASC"
        elif table_id == 'team_color_bonus':
            query += " ORDER BY event_date DESC, class_name ASC"
        elif table_id == 'upload_history':
            query += " ORDER BY upload_timestamp DESC"
        elif table_id == 'roster':
            query += " ORDER BY team_name ASC, grade_level ASC, class_name ASC, student_name ASC"
        elif table_id == 'class_info':
            query += " ORDER BY team_name ASC, grade_level ASC, class_name ASC"

        data = db.execute_query(query)

        return jsonify({
            'title': f'{table_name} Table',
            'description': f'Complete contents of the {table_name} table',
            'columns': list(data[0].keys()) if data else [],
            'data': data,
            'row_count': len(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/help')
def help_page():
    """User manual / help page"""
    env = session.get('environment', DEFAULT_DATABASE)
    return render_template('help.html', environment=env)

@app.route('/help/claude')
def help_claude():
    """Claude Code development documentation"""
    env = session.get('environment', DEFAULT_DATABASE)
    return render_template('claude_development.html', environment=env)

@app.route('/help/requirements')
def help_requirements():
    """Application requirements document (IMPLEMENTATION_PROMPT.md)"""
    env = session.get('environment', DEFAULT_DATABASE)
    # Read IMPLEMENTATION_PROMPT.md
    requirements_content = ""
    try:
        with open('IMPLEMENTATION_PROMPT.md', 'r', encoding='utf-8') as f:
            requirements_content = f.read()
    except FileNotFoundError:
        requirements_content = "# Error\n\nIMPLEMENTATION_PROMPT.md not found."

    return render_template('requirements.html',
                         environment=env,
                         requirements_content=requirements_content)

@app.route('/help/requirements/download')
def download_requirements():
    """Download IMPLEMENTATION_PROMPT.md file"""
    try:
        return send_file('IMPLEMENTATION_PROMPT.md',
                        as_attachment=True,
                        download_name='IMPLEMENTATION_PROMPT.md',
                        mimetype='text/markdown')
    except FileNotFoundError:
        return "File not found", 404

@app.route('/prototypes/<path:filename>')
def serve_prototype(filename):
    """Serve HTML prototype files"""
    try:
        # Remove .html extension if not present, then add it back
        if not filename.endswith('.html'):
            filename = filename + '.html'
        return send_file(f'prototypes/{filename}', mimetype='text/html')
    except FileNotFoundError:
        return "Prototype not found", 404


@app.route('/api/workflow/<workflow_id>')
def run_workflow(workflow_id):
    """Run a workflow (sequence of reports)"""
    try:
        log_date = request.args.get('date')

        # Get current environment's report generator
        reports = get_current_reports()
        db = get_current_db()

        if workflow_id == 'qd':  # Daily Slide Update
            report_ids = ['q18', 'q14', 'q4', 'q19', 'q20']
            workflow_name = 'Daily Slide Update (Slides 2-6)'
        elif workflow_id == 'qc':  # Cumulative
            report_ids = ['q5', 'q6', 'q14', 'q18', 'q19', 'q20']
            workflow_name = 'Cumulative Prize Reports'
        elif workflow_id == 'qf':  # Final Prizes
            report_ids = ['q9', 'q10', 'q11', 'q12', 'q13', 'q16', 'q4', 'q14', 'q19', 'q15']
            workflow_name = 'Final Prize Winners'
        elif workflow_id == 'qa':  # All Reports
            # Updated to include new prize reports Q9-Q13, Q15-Q16, and Q3
            report_ids = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q18', 'q19', 'q20', 'q21', 'q22', 'q23']
            workflow_name = 'All Main Reports (22 Reports)'
        else:
            return jsonify({'error': 'Unknown workflow'}), 404

        # Run all reports
        results = []
        for rid in report_ids:
            if rid == 'q1':
                results.append(reports.q1_table_counts())
            elif rid == 'q2':
                results.append(reports.q2_daily_summary(log_date, 'class'))
            elif rid == 'q3':
                results.append(reports.q3_reader_cumulative_enhanced())
            elif rid == 'q4':  # Prize drawing needs a date
                if not log_date:
                    dates = db.get_all_dates()
                    log_date = dates[0] if dates else None
                if log_date:
                    results.append(reports.q4_prize_drawing(log_date))
                else:
                    # Add error message if no data available
                    results.append({
                        'title': 'Q4/Slide 4: Prize Drawing - No Data',
                        'description': 'No daily data available for prize drawing',
                        'columns': [],
                        'data': [],
                        'error': 'No daily data uploaded yet'
                    })
            elif rid == 'q5':
                results.append(reports.q5_student_cumulative('minutes'))
            elif rid == 'q6':
                results.append(reports.q6_class_participation())
            elif rid == 'q7':
                results.append(reports.q7_complete_log(log_date))
            elif rid == 'q8':
                results.append(reports.q8_student_reading_details())
            elif rid == 'q14':
                results.append(reports.q14_team_participation())
            elif rid == 'q18':
                results.append(reports.q18_lead_class_by_grade())
            elif rid == 'q19':
                results.append(reports.q19_team_minutes())
            elif rid == 'q20':
                results.append(reports.q20_team_donations())
            elif rid == 'q21':
                results.append(reports.q21_minutes_integrity_check())
            elif rid == 'q22':
                results.append(reports.q22_student_name_sync_check())
            elif rid == 'q23':
                results.append(reports.q23_roster_integrity_check())
            elif rid == 'q9':
                results.append(reports.q9_most_donations_by_grade())
            elif rid == 'q10':
                results.append(reports.q10_most_minutes_by_grade())
            elif rid == 'q11':
                results.append(reports.q11_most_sponsors_by_grade())
            elif rid == 'q12':
                results.append(reports.q12_best_class_by_grade_simplified())
            elif rid == 'q13':
                results.append(reports.q13_overall_best_class_simplified())
            elif rid == 'q15':
                results.append(reports.q15_goal_getters())
            elif rid == 'q16':
                results.append(reports.q16_top_earner_per_team())

        return jsonify({
            'workflow_name': workflow_name,
            'reports': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("READ-A-THON REPORTING SYSTEM")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://127.0.0.1:5001")
    print("\nPress CTRL+C to stop the server\n")
    app.run(debug=True, host='127.0.0.1', port=5001)
