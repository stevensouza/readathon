"""
Read-a-Thon Web Application
Flask-based browser interface for managing and reporting on read-a-thon data
"""

from flask import Flask, render_template, request, jsonify, send_file, Response, session
from database import ReadathonDB, ReportGenerator
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
    teams = {}

    # Team Staub (cumulative through selected date)
    staub_where = f"AND dl.log_date <= '{date_filter}'" if date_filter != 'all' and date_filter in dates else ""
    staub_query = f"""
        WITH TeamBonus AS (
            SELECT SUM(tcb.bonus_minutes) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            WHERE LOWER(ci.team_name) = 'staub'
        )
        SELECT
            COUNT(DISTINCT r.class_name) as classes,
            COALESCE(SUM(rc.donation_amount), 0) as fundraising,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base,
            COALESCE((SELECT total_bonus FROM TeamBonus), 0) as bonus_minutes,
            COUNT(DISTINCT r.student_name) as students
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE LOWER(r.team_name) = 'staub' {staub_where}
    """
    staub_result = db.execute_query(staub_query)
    if staub_result and staub_result[0]:
        minutes_base = int(staub_result[0]['total_minutes_base'] or 0)
        bonus_min = int(staub_result[0]['bonus_minutes'] or 0)
        minutes_with_color = minutes_base + bonus_min
        teams['staub'] = {
            'classes': staub_result[0]['classes'] or 0,
            'fundraising': staub_result[0]['fundraising'] or 0,
            'minutes_base': minutes_base,
            'bonus_minutes': bonus_min,
            'minutes_with_color': minutes_with_color,
            'hours_base': minutes_base // 60,
            'hours_with_color': minutes_with_color // 60,
            'students': staub_result[0]['students'] or 0
        }
    else:
        teams['staub'] = {'classes': 0, 'fundraising': 0, 'minutes_base': 0, 'bonus_minutes': 0, 'minutes_with_color': 0, 'hours_base': 0, 'hours_with_color': 0, 'students': 0}

    # Team Kitsko
    kitsko_query = f"""
        WITH TeamBonus AS (
            SELECT SUM(tcb.bonus_minutes) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            WHERE LOWER(ci.team_name) = 'kitsko'
        )
        SELECT
            COUNT(DISTINCT r.class_name) as classes,
            COALESCE(SUM(rc.donation_amount), 0) as fundraising,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base,
            COALESCE((SELECT total_bonus FROM TeamBonus), 0) as bonus_minutes,
            COUNT(DISTINCT r.student_name) as students
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE LOWER(r.team_name) = 'kitsko' {staub_where}
    """
    kitsko_result = db.execute_query(kitsko_query)
    if kitsko_result and kitsko_result[0]:
        minutes_base = int(kitsko_result[0]['total_minutes_base'] or 0)
        bonus_min = int(kitsko_result[0]['bonus_minutes'] or 0)
        minutes_with_color = minutes_base + bonus_min
        teams['kitsko'] = {
            'classes': kitsko_result[0]['classes'] or 0,
            'fundraising': kitsko_result[0]['fundraising'] or 0,
            'minutes_base': minutes_base,
            'bonus_minutes': bonus_min,
            'minutes_with_color': minutes_with_color,
            'hours_base': minutes_base // 60,
            'hours_with_color': minutes_with_color // 60,
            'students': kitsko_result[0]['students'] or 0
        }
    else:
        teams['kitsko'] = {'classes': 0, 'fundraising': 0, 'minutes_base': 0, 'bonus_minutes': 0, 'minutes_with_color': 0, 'hours_base': 0, 'hours_with_color': 0, 'students': 0}

    # Team Staub - Average Daily Participation Percentage (with and without color bonus)
    # Get total days and team size for calculations
    total_days_query = f"""
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
        WHERE 1=1 {staub_where.replace('dl.', '')}
    """
    total_days_result = db.execute_query(total_days_query)
    total_days = total_days_result[0]['total_days'] if total_days_result and total_days_result[0] else 1

    staub_size = teams['staub']['students']
    staub_participation_query = f"""
        SELECT
            AVG(daily_pct) as avg_participation
        FROM (
            SELECT
                dl.log_date,
                (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                 (SELECT COUNT(*) FROM Roster WHERE LOWER(team_name) = 'staub')) as daily_pct
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = 'staub' {staub_where}
            GROUP BY dl.log_date
        )
    """
    staub_participation_result = db.execute_query(staub_participation_query)
    teams['staub']['participation_pct'] = staub_participation_result[0]['avg_participation'] or 0 if staub_participation_result and staub_participation_result[0] else 0

    # Calculate participation with color bonus for Staub
    staub_bonus_query = """
        SELECT SUM(tcb.bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        WHERE LOWER(ci.team_name) = 'staub'
    """
    staub_bonus_result = db.execute_query(staub_bonus_query)
    staub_color_bonus = staub_bonus_result[0]['total_bonus'] if staub_bonus_result and staub_bonus_result[0] and staub_bonus_result[0]['total_bonus'] else 0
    teams['staub']['color_bonus_points'] = staub_color_bonus
    teams['staub']['participation_pct_with_color'] = teams['staub']['participation_pct'] + (staub_color_bonus * 100.0 / (staub_size * total_days)) if staub_size > 0 and total_days > 0 else teams['staub']['participation_pct']

    # Team Kitsko - Average Daily Participation Percentage (with and without color bonus)
    kitsko_size = teams['kitsko']['students']
    kitsko_participation_query = f"""
        SELECT
            AVG(daily_pct) as avg_participation
        FROM (
            SELECT
                dl.log_date,
                (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                 (SELECT COUNT(*) FROM Roster WHERE LOWER(team_name) = 'kitsko')) as daily_pct
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name
            WHERE LOWER(r.team_name) = 'kitsko' {staub_where}
            GROUP BY dl.log_date
        )
    """
    kitsko_participation_result = db.execute_query(kitsko_participation_query)
    teams['kitsko']['participation_pct'] = kitsko_participation_result[0]['avg_participation'] or 0 if kitsko_participation_result and kitsko_participation_result[0] else 0

    # Calculate participation with color bonus for Kitsko
    kitsko_bonus_query = """
        SELECT SUM(tcb.bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        WHERE LOWER(ci.team_name) = 'kitsko'
    """
    kitsko_bonus_result = db.execute_query(kitsko_bonus_query)
    kitsko_color_bonus = kitsko_bonus_result[0]['total_bonus'] if kitsko_bonus_result and kitsko_bonus_result[0] and kitsko_bonus_result[0]['total_bonus'] else 0
    teams['kitsko']['color_bonus_points'] = kitsko_color_bonus
    teams['kitsko']['participation_pct_with_color'] = teams['kitsko']['participation_pct'] + (kitsko_color_bonus * 100.0 / (kitsko_size * total_days)) if kitsko_size > 0 and total_days > 0 else teams['kitsko']['participation_pct']

    # Determine leader and calculate gaps for each metric
    # Note: Different teams may lead different metrics - gaps show which team is ahead in each category
    if teams['staub']['fundraising'] > teams['kitsko']['fundraising']:
        teams['leader'] = 'STAUB'
        teams['fundraising_gap'] = teams['staub']['fundraising'] - teams['kitsko']['fundraising']
        teams['fundraising_leader'] = 'STAUB'
    else:
        teams['leader'] = 'KITSKO'
        teams['fundraising_gap'] = teams['kitsko']['fundraising'] - teams['staub']['fundraising']
        teams['fundraising_leader'] = 'KITSKO'

    # Reading gap - base version
    if teams['staub']['hours_base'] > teams['kitsko']['hours_base']:
        teams['reading_gap'] = teams['staub']['hours_base'] - teams['kitsko']['hours_base']
        teams['reading_leader'] = 'STAUB'
    else:
        teams['reading_gap'] = teams['kitsko']['hours_base'] - teams['staub']['hours_base']
        teams['reading_leader'] = 'KITSKO'

    # Reading gap - with color version
    if teams['staub']['hours_with_color'] > teams['kitsko']['hours_with_color']:
        teams['reading_gap_with_color'] = teams['staub']['hours_with_color'] - teams['kitsko']['hours_with_color']
        teams['reading_leader_with_color'] = 'STAUB'
    else:
        teams['reading_gap_with_color'] = teams['kitsko']['hours_with_color'] - teams['staub']['hours_with_color']
        teams['reading_leader_with_color'] = 'KITSKO'

    # Participation gap - base version
    if teams['staub']['participation_pct'] > teams['kitsko']['participation_pct']:
        teams['participation_gap'] = teams['staub']['participation_pct'] - teams['kitsko']['participation_pct']
        teams['participation_leader'] = 'STAUB'
    else:
        teams['participation_gap'] = teams['kitsko']['participation_pct'] - teams['staub']['participation_pct']
        teams['participation_leader'] = 'KITSKO'

    # Participation gap - with color version
    if teams['staub']['participation_pct_with_color'] > teams['kitsko']['participation_pct_with_color']:
        teams['participation_gap_with_color'] = teams['staub']['participation_pct_with_color'] - teams['kitsko']['participation_pct_with_color']
        teams['participation_leader_with_color'] = 'STAUB'
    else:
        teams['participation_gap_with_color'] = teams['kitsko']['participation_pct_with_color'] - teams['staub']['participation_pct_with_color']
        teams['participation_leader_with_color'] = 'KITSKO'

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
                         performers=performers,
                         participation=participation,
                         integrity=integrity,
                         metadata=metadata)


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
