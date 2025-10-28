"""
SQL Queries Module for Read-a-Thon Database
Contains all SQL queries extracted from database.py, organized as constants and template functions.
"""

# ============================================================================
# CREATE TABLE STATEMENTS
# ============================================================================

CREATE_TABLE_ROSTER = """
    CREATE TABLE IF NOT EXISTS Roster (
        student_name TEXT PRIMARY KEY,
        class_name TEXT NOT NULL,
        home_room TEXT NOT NULL,
        teacher_name TEXT NOT NULL,
        grade_level TEXT NOT NULL,
        team_name TEXT NOT NULL
    )
"""

CREATE_TABLE_CLASS_INFO = """
    CREATE TABLE IF NOT EXISTS Class_Info (
        class_name TEXT PRIMARY KEY,
        home_room TEXT NOT NULL,
        teacher_name TEXT NOT NULL,
        grade_level TEXT NOT NULL,
        team_name TEXT NOT NULL,
        total_students INTEGER NOT NULL
    )
"""

CREATE_TABLE_GRADE_RULES = """
    CREATE TABLE IF NOT EXISTS Grade_Rules (
        grade_level TEXT PRIMARY KEY,
        min_daily_minutes INTEGER NOT NULL,
        max_daily_minutes_credit INTEGER NOT NULL
    )
"""

CREATE_TABLE_DAILY_LOGS = """
    CREATE TABLE IF NOT EXISTS Daily_Logs (
        log_date TEXT NOT NULL,
        student_name TEXT NOT NULL,
        minutes_read INTEGER DEFAULT 0,
        PRIMARY KEY (log_date, student_name),
        FOREIGN KEY (student_name) REFERENCES Roster(student_name)
    )
"""

CREATE_TABLE_READER_CUMULATIVE = """
    CREATE TABLE IF NOT EXISTS Reader_Cumulative (
        student_name TEXT PRIMARY KEY,
        teacher_name TEXT,
        team_name TEXT,
        donation_amount REAL DEFAULT 0.0,
        sponsors INTEGER DEFAULT 0,
        cumulative_minutes INTEGER DEFAULT 0,
        upload_timestamp TEXT NOT NULL,
        FOREIGN KEY (student_name) REFERENCES Roster(student_name)
    )
"""

CREATE_TABLE_UPLOAD_HISTORY = """
    CREATE TABLE IF NOT EXISTS Upload_History (
        upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT,
        upload_timestamp TEXT NOT NULL,
        filename TEXT,
        row_count INTEGER,
        total_students_affected INTEGER,
        upload_type TEXT DEFAULT 'new',
        status TEXT DEFAULT 'success',
        action_taken TEXT DEFAULT 'inserted',
        records_replaced INTEGER DEFAULT 0,
        audit_details TEXT
    )
"""

CREATE_TABLE_DATABASE_METADATA = """
    CREATE TABLE IF NOT EXISTS Database_Metadata (
        db_id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL UNIQUE,
        db_filename TEXT NOT NULL,
        description TEXT,
        created_timestamp TEXT NOT NULL,
        is_active INTEGER DEFAULT 0,
        student_count INTEGER DEFAULT 0,
        total_days INTEGER DEFAULT 0,
        total_donations REAL DEFAULT 0.0
    )
"""

CREATE_TABLE_TEAM_COLOR_BONUS = """
    CREATE TABLE IF NOT EXISTS Team_Color_Bonus (
        event_date TEXT NOT NULL,
        class_name TEXT NOT NULL,
        students_wearing_colors INTEGER NOT NULL,
        bonus_minutes INTEGER NOT NULL,
        bonus_participation_points INTEGER NOT NULL,
        PRIMARY KEY (event_date, class_name),
        FOREIGN KEY (class_name) REFERENCES Class_Info(class_name)
    )
"""

# ============================================================================
# ALTER TABLE STATEMENTS
# ============================================================================

ALTER_ADD_ACTION_TAKEN = "ALTER TABLE Upload_History ADD COLUMN action_taken TEXT DEFAULT 'inserted'"
ALTER_ADD_RECORDS_REPLACED = "ALTER TABLE Upload_History ADD COLUMN records_replaced INTEGER DEFAULT 0"
ALTER_ADD_AUDIT_DETAILS = "ALTER TABLE Upload_History ADD COLUMN audit_details TEXT"

# ============================================================================
# DELETE STATEMENTS
# ============================================================================

DELETE_ALL_ROSTER = "DELETE FROM Roster"
DELETE_ALL_CLASS_INFO = "DELETE FROM Class_Info"
DELETE_ALL_GRADE_RULES = "DELETE FROM Grade_Rules"
DELETE_ALL_READER_CUMULATIVE = "DELETE FROM Reader_Cumulative"
DELETE_DAY_DATA = "DELETE FROM Daily_Logs WHERE log_date = ?"
DELETE_UPLOAD_HISTORY_BY_DATE = "DELETE FROM Upload_History WHERE log_date = ?"
DELETE_UPLOAD_HISTORY_CUMULATIVE = "DELETE FROM Upload_History WHERE log_date IS NULL"

def get_delete_upload_history_batch_query(upload_ids):
    """Generate DELETE query for multiple upload history records"""
    placeholders = ','.join('?' * len(upload_ids))
    return f"DELETE FROM Upload_History WHERE upload_id IN ({placeholders})"

DELETE_DATABASE_METADATA = "DELETE FROM Database_Metadata WHERE year = ?"

# ============================================================================
# INSERT STATEMENTS
# ============================================================================

INSERT_ROSTER = """
    INSERT INTO Roster (student_name, class_name, home_room, teacher_name, grade_level, team_name)
    VALUES (?, ?, ?, ?, ?, ?)
"""

INSERT_CLASS_INFO = """
    INSERT INTO Class_Info (class_name, home_room, teacher_name, grade_level, team_name, total_students)
    VALUES (?, ?, ?, ?, ?, ?)
"""

INSERT_GRADE_RULES = """
    INSERT INTO Grade_Rules (grade_level, min_daily_minutes, max_daily_minutes_credit)
    VALUES (?, ?, ?)
"""

INSERT_TEAM_COLOR_BONUS = """
    INSERT OR REPLACE INTO Team_Color_Bonus
    (event_date, class_name, students_wearing_colors, bonus_minutes, bonus_participation_points)
    VALUES (?, ?, ?, ?, ?)
"""

INSERT_READER_CUMULATIVE = """
    INSERT INTO Reader_Cumulative
    (student_name, teacher_name, team_name, donation_amount, sponsors, cumulative_minutes, upload_timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

INSERT_DAILY_LOGS_UPSERT = """
    INSERT INTO Daily_Logs (log_date, student_name, minutes_read)
    VALUES (?, ?, ?)
    ON CONFLICT(log_date, student_name)
    DO UPDATE SET minutes_read = ?
"""

INSERT_UPLOAD_HISTORY_CUMULATIVE = """
    INSERT INTO Upload_History
    (log_date, upload_timestamp, filename, row_count, total_students_affected, upload_type, status, action_taken, records_replaced, audit_details, file_type)
    VALUES (NULL, datetime('now'), ?, ?, ?, 'cumulative_stats', ?, ?, ?, ?, 'cumulative')
"""

INSERT_UPLOAD_HISTORY_DAILY = """
    INSERT INTO Upload_History
    (log_date, upload_timestamp, filename, row_count, total_students_affected, upload_type, status, action_taken, records_replaced, audit_details, file_type)
    VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, 'daily')
"""

INSERT_DATABASE_METADATA = """
    INSERT INTO Database_Metadata
    (year, db_filename, description, created_timestamp, is_active, student_count, total_days, total_donations)
    VALUES (?, ?, ?, ?, 0, 0, 0, 0.0)
"""

# ============================================================================
# UPDATE STATEMENTS
# ============================================================================

UPDATE_DATABASE_METADATA_INACTIVE_ALL = "UPDATE Database_Metadata SET is_active = 0"
UPDATE_DATABASE_METADATA_ACTIVE = "UPDATE Database_Metadata SET is_active = 1 WHERE year = ?"

UPDATE_DATABASE_METADATA_STATS = """
    UPDATE Database_Metadata
    SET student_count = ?,
        total_days = ?,
        total_donations = ?
    WHERE year = ?
"""

# ============================================================================
# SELECT STATEMENTS - SIMPLE QUERIES
# ============================================================================

SELECT_TABLE_INFO = "PRAGMA table_info(Upload_History)"

SELECT_COUNT_ROSTER = "SELECT COUNT(*) FROM Roster"
SELECT_COUNT_CLASS_INFO = "SELECT COUNT(*) FROM Class_Info"
SELECT_COUNT_GRADE_RULES = "SELECT COUNT(*) FROM Grade_Rules"
SELECT_COUNT_DAILY_LOGS = "SELECT COUNT(*) FROM Daily_Logs"
SELECT_COUNT_READER_CUMULATIVE = "SELECT COUNT(*) FROM Reader_Cumulative"
SELECT_COUNT_TEAM_COLOR_BONUS = "SELECT COUNT(*) FROM Team_Color_Bonus"

SELECT_ALL_DATES = "SELECT DISTINCT log_date FROM Daily_Logs ORDER BY log_date DESC"

SELECT_TEAM_NAME_FROM_ROSTER = "SELECT team_name FROM Roster WHERE student_name = ?"

SELECT_STUDENT_EXISTS_IN_ROSTER = "SELECT student_name FROM Roster WHERE student_name = ?"

SELECT_COUNT_DAILY_LOGS_BY_DATE = "SELECT COUNT(*) FROM Daily_Logs WHERE log_date = ?"

SELECT_DISTINCT_STUDENTS_BY_DATE = "SELECT DISTINCT student_name FROM Daily_Logs WHERE log_date = ? ORDER BY student_name"

SELECT_STUDENT_COUNT_DAILY_LOGS_BY_DATE = "SELECT COUNT(*), GROUP_CONCAT(student_name) FROM Daily_Logs WHERE log_date = ?"

SELECT_ALL_STUDENTS_READER_CUMULATIVE = "SELECT student_name FROM Reader_Cumulative ORDER BY student_name"

SELECT_ALL_STUDENTS_READER_CUMULATIVE_SET = "SELECT student_name FROM Reader_Cumulative ORDER BY student_name"

SELECT_TOTAL_DAYS_DAILY_LOGS = "SELECT COUNT(DISTINCT log_date) FROM Daily_Logs"

SELECT_TOTAL_DAYS_FOR_QUERY = "SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs"

SELECT_STUDENT_COUNT_ROSTER = "SELECT COUNT(*) FROM Roster"

SELECT_TOTAL_DAYS_DAILY_LOGS_COUNT = "SELECT COUNT(DISTINCT log_date) FROM Daily_Logs"

SELECT_TOTAL_DONATIONS_READER_CUMULATIVE = "SELECT COALESCE(SUM(donation_amount), 0.0) FROM Reader_Cumulative"

def get_table_count_query(table_name):
    """Generate SELECT COUNT query for a specific table"""
    return f"SELECT COUNT(*) FROM {table_name}"

# ============================================================================
# SELECT STATEMENTS - VALIDATION & LOOKUP
# ============================================================================

SELECT_CLASS_INFO_BY_NAME = """
    SELECT class_name, team_name
    FROM Class_Info
    WHERE UPPER(class_name) = UPPER(?)
"""

SELECT_EXISTING_UPLOAD = """
    SELECT upload_timestamp, filename, total_students_affected
    FROM Upload_History
    WHERE log_date = ?
    ORDER BY upload_timestamp DESC
    LIMIT 1
"""

SELECT_UPLOAD_HISTORY = """
    SELECT
        upload_id,
        log_date,
        upload_timestamp,
        filename,
        row_count,
        total_students_affected,
        upload_type,
        status,
        action_taken,
        records_replaced,
        audit_details
    FROM Upload_History
    ORDER BY upload_timestamp DESC
    LIMIT ?
"""

SELECT_DB_METADATA_BY_YEAR = """
    SELECT
        db_id,
        year,
        db_filename,
        description,
        created_timestamp,
        is_active,
        student_count,
        total_days,
        total_donations
    FROM Database_Metadata
    WHERE year = ?
"""

SELECT_DB_METADATA_ACTIVE = """
    SELECT
        db_id,
        year,
        db_filename,
        description,
        created_timestamp,
        is_active,
        student_count,
        total_days,
        total_donations
    FROM Database_Metadata
    WHERE is_active = 1
    LIMIT 1
"""

SELECT_DB_METADATA_ALL = """
    SELECT
        db_id,
        year,
        db_filename,
        description,
        created_timestamp,
        is_active,
        student_count,
        total_days,
        total_donations
    FROM Database_Metadata
    ORDER BY year DESC
"""

SELECT_DB_ID_BY_YEAR = "SELECT db_id FROM Database_Metadata WHERE year = ?"

SELECT_DB_ID_AND_ACTIVE_BY_YEAR = "SELECT db_id, is_active FROM Database_Metadata WHERE year = ?"

# ============================================================================
# SELECT STATEMENTS - REPORT METADATA
# ============================================================================

SELECT_LAST_DAILY_UPLOAD = """
    SELECT MAX(upload_timestamp), log_date
    FROM Upload_History
    WHERE log_date IS NOT NULL
    ORDER BY upload_timestamp DESC
    LIMIT 1
"""

SELECT_LAST_CUMULATIVE_UPLOAD = """
    SELECT MAX(upload_timestamp)
    FROM Upload_History
    WHERE log_date IS NULL
    ORDER BY upload_timestamp DESC
    LIMIT 1
"""

SELECT_DATE_RANGE_DAILY_LOGS = """
    SELECT
        MIN(log_date) as min_date,
        MAX(log_date) as max_date
    FROM Daily_Logs
"""

# ============================================================================
# REPORT QUERIES - Q2 Daily Summary
# ============================================================================

def get_q2_daily_summary_by_class_query(date_filter, days_subquery):
    """Q2: Daily Summary Report grouped by class"""
    return f"""
        WITH TotalDays AS ({days_subquery}),
        StudentGoalCounts AS (
            SELECT
                r.student_name,
                r.class_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal,
                COUNT(DISTINCT dl.log_date) as student_days
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_filter}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name, r.class_name
        )
        SELECT
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            ci.total_students,
            td.total_days as days_with_data,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
                  (ci.total_students * td.total_days), 1) as participation_rate,
            COUNT(DISTINCT CASE WHEN sgc.days_met_goal > 0 THEN sgc.student_name END) as student_count_met_goal_any_day,
            COUNT(DISTINCT CASE WHEN sgc.days_met_goal = td.total_days AND sgc.student_days = td.total_days THEN sgc.student_name END) as student_count_met_goal_all_days,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes
        FROM Roster r
        INNER JOIN Class_Info ci ON r.class_name = ci.class_name
        CROSS JOIN TotalDays td
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_filter}
        LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        LEFT JOIN StudentGoalCounts sgc ON r.student_name = sgc.student_name AND r.class_name = sgc.class_name
        GROUP BY r.class_name, r.teacher_name, r.grade_level, r.team_name, ci.total_students, td.total_days
        HAVING td.total_days > 0
        ORDER BY r.team_name ASC, r.grade_level ASC, r.class_name ASC
    """

def get_q2_daily_summary_by_team_query(date_filter, days_subquery):
    """Q2: Daily Summary Report grouped by team"""
    return f"""
        WITH TotalDays AS ({days_subquery}),
        StudentGoalCounts AS (
            SELECT
                r.student_name,
                r.team_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal,
                COUNT(DISTINCT dl.log_date) as student_days
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_filter}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name, r.team_name
        )
        SELECT
            r.team_name,
            COUNT(DISTINCT r.student_name) as total_students,
            td.total_days as days_with_data,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
                  (COUNT(DISTINCT r.student_name) * td.total_days), 1) as participation_rate,
            COUNT(DISTINCT CASE WHEN sgc.days_met_goal > 0 THEN sgc.student_name END) as student_count_met_goal_any_day,
            COUNT(DISTINCT CASE WHEN sgc.days_met_goal = td.total_days AND sgc.student_days = td.total_days THEN sgc.student_name END) as student_count_met_goal_all_days,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes
        FROM Roster r
        CROSS JOIN TotalDays td
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_filter}
        LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        LEFT JOIN StudentGoalCounts sgc ON r.student_name = sgc.student_name AND r.team_name = sgc.team_name
        GROUP BY r.team_name, td.total_days
        HAVING td.total_days > 0
        ORDER BY r.team_name ASC
    """

# ============================================================================
# REPORT QUERIES - Q3 Reader Cumulative Enhanced
# ============================================================================

QUERY_Q3_READER_CUMULATIVE = """
    SELECT
        rc.student_name,
        r.class_name,
        r.grade_level,
        rc.teacher_name,
        rc.team_name,
        COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated,
        SUM(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as days_met_goal,
        rc.cumulative_minutes,
        rc.donation_amount,
        rc.sponsors
    FROM Reader_Cumulative rc
    LEFT JOIN Roster r ON rc.student_name = r.student_name
    LEFT JOIN Daily_Logs dl ON rc.student_name = dl.student_name
    LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
    GROUP BY rc.student_name, r.class_name, r.grade_level, rc.teacher_name, rc.team_name,
             rc.cumulative_minutes, rc.donation_amount, rc.sponsors
    ORDER BY rc.cumulative_minutes DESC, rc.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q4 Prize Drawing
# ============================================================================

QUERY_Q4_PRIZE_DRAWING = """
    SELECT DISTINCT
        r.student_name,
        r.grade_level,
        r.class_name,
        r.teacher_name,
        dl.minutes_read,
        gr.min_daily_minutes
    FROM Roster r
    INNER JOIN Daily_Logs dl ON r.student_name = dl.student_name
    INNER JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
    WHERE dl.log_date = ? AND dl.minutes_read >= gr.min_daily_minutes
    ORDER BY r.grade_level, r.student_name
"""

# ============================================================================
# REPORT QUERIES - Q5 Student Cumulative
# ============================================================================

def get_q5_student_cumulative_query(sort_by='minutes', limit=None):
    """Q5: Student Cumulative Report with dynamic sorting"""
    query = """
        SELECT
            r.student_name,
            r.class_name,
            r.grade_level,
            r.team_name,
            COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes_credited,
            SUM(dl.minutes_read) as total_minutes_actual,
            SUM(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as days_met_goal,
            COALESCE(rc.donation_amount, 0.0) as total_donations,
            COALESCE(rc.sponsors, 0) as total_sponsors
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.student_name, r.class_name, r.grade_level, r.team_name, rc.donation_amount, rc.sponsors
    """

    # Add ordering based on sort_by parameter
    if sort_by.lower() in ['minutes', 'top readers']:
        query += " ORDER BY total_minutes_credited DESC, r.student_name ASC"
    elif sort_by.lower() in ['goal', 'goals', 'goal getters']:
        query += " ORDER BY days_met_goal DESC, total_minutes_credited DESC, r.student_name ASC"
    elif sort_by.lower() in ['donations', 'fundraisers']:
        query += " ORDER BY total_donations DESC, r.student_name ASC"
    else:
        query += " ORDER BY total_minutes_credited DESC, r.student_name ASC"

    if limit:
        query += f" LIMIT {limit}"

    return query

# ============================================================================
# REPORT QUERIES - Q6 Class Participation
# ============================================================================

QUERY_Q6_CLASS_PARTICIPATION = """
    WITH TotalDays AS (
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
    ),
    BonusData AS (
        SELECT
            class_name,
            SUM(bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus
        GROUP BY class_name
    )
    SELECT
        r.class_name,
        r.teacher_name,
        r.grade_level,
        r.team_name,
        ci.total_students,
        td.total_days as days_with_data,
        COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations_base,
        COALESCE(bd.total_bonus, 0) as color_bonus_points,
        COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(bd.total_bonus, 0) as total_participations_with_color,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
              (ci.total_students * td.total_days), 2) as avg_participation_rate,
        ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(bd.total_bonus, 0)) /
              (ci.total_students * td.total_days), 2) as avg_participation_rate_with_color
    FROM Roster r
    INNER JOIN Class_Info ci ON r.class_name = ci.class_name
    CROSS JOIN TotalDays td
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    LEFT JOIN BonusData bd ON r.class_name = bd.class_name
    GROUP BY r.class_name, r.teacher_name, r.grade_level, r.team_name, ci.total_students, td.total_days, bd.total_bonus
    HAVING td.total_days > 0
    ORDER BY avg_participation_rate_with_color DESC, r.class_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q7 Complete Log
# ============================================================================

def get_q7_complete_log_query(date_filter):
    """Q7: Complete Log - Denormalized export"""
    return f"""
        SELECT
            dl.log_date,
            dl.student_name,
            dl.minutes_read,
            r.class_name,
            r.home_room,
            r.teacher_name,
            r.grade_level,
            r.team_name
        FROM Daily_Logs dl
        INNER JOIN Roster r ON dl.student_name = r.student_name
        {date_filter}
        ORDER BY dl.log_date DESC, r.team_name ASC, r.class_name ASC, dl.student_name ASC
    """

# ============================================================================
# REPORT QUERIES - Q8 Student Reading Details
# ============================================================================

QUERY_Q8_STUDENT_READING_DETAILS = """
    SELECT
        r.student_name,
        r.class_name,
        r.teacher_name,
        r.grade_level,
        r.team_name,
        SUM(dl.minutes_read) as total_minutes_read,
        SUM(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as days_met_goal,
        COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated
    FROM Roster r
    INNER JOIN Daily_Logs dl ON r.student_name = dl.student_name
    LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
    WHERE dl.minutes_read > 0
    GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name
    ORDER BY total_minutes_read DESC, r.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q9 Most Donations by Grade
# ============================================================================

QUERY_Q9_MOST_DONATIONS_BY_GRADE = """
    WITH MaxByGrade AS (
        SELECT
            r.grade_level,
            MAX(COALESCE(rc.donation_amount, 0)) as max_donation
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.grade_level
    )
    SELECT
        r.grade_level,
        r.student_name,
        COALESCE(rc.donation_amount, 0) as donation_amount,
        COALESCE(rc.sponsors, 0) as sponsors,
        r.team_name,
        r.class_name
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    INNER JOIN MaxByGrade mbg ON r.grade_level = mbg.grade_level
        AND COALESCE(rc.donation_amount, 0) = mbg.max_donation
    WHERE mbg.max_donation > 0
    ORDER BY r.grade_level ASC, r.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q10 Most Minutes by Grade
# ============================================================================

QUERY_Q10_MOST_MINUTES_BY_GRADE = """
    WITH StudentMinutes AS (
        SELECT
            r.student_name,
            r.grade_level,
            r.team_name,
            r.class_name,
            SUM(MIN(dl.minutes_read, 120)) as total_minutes_capped,
            COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        GROUP BY r.student_name, r.grade_level, r.team_name, r.class_name
    ),
    MaxByGrade AS (
        SELECT
            grade_level,
            MAX(total_minutes_capped) as max_minutes
        FROM StudentMinutes
        GROUP BY grade_level
    )
    SELECT
        sm.grade_level,
        sm.student_name,
        sm.total_minutes_capped,
        sm.days_participated,
        sm.team_name,
        sm.class_name
    FROM StudentMinutes sm
    INNER JOIN MaxByGrade mbg ON sm.grade_level = mbg.grade_level
        AND sm.total_minutes_capped = mbg.max_minutes
    WHERE sm.total_minutes_capped > 0
    ORDER BY sm.grade_level ASC, sm.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q11 Most Sponsors by Grade
# ============================================================================

QUERY_Q11_MOST_SPONSORS_BY_GRADE = """
    WITH MaxByGrade AS (
        SELECT
            r.grade_level,
            MAX(COALESCE(rc.sponsors, 0)) as max_sponsors
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.grade_level
    )
    SELECT
        r.grade_level,
        r.student_name,
        COALESCE(rc.sponsors, 0) as sponsor_count,
        COALESCE(rc.donation_amount, 0) as donation_amount,
        r.team_name,
        r.class_name
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    INNER JOIN MaxByGrade mbg ON r.grade_level = mbg.grade_level
        AND COALESCE(rc.sponsors, 0) = mbg.max_sponsors
    WHERE mbg.max_sponsors > 0
    ORDER BY r.grade_level ASC, r.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q12 Best Class by Grade (Simplified)
# ============================================================================

QUERY_Q12_BEST_CLASS_BY_GRADE = """
    WITH TotalDays AS (
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
    ),
    BonusData AS (
        SELECT
            class_name,
            SUM(bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus
        GROUP BY class_name
    ),
    ClassStats AS (
        SELECT
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            ci.total_students,
            td.total_days as days_with_data,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations_base,
            COALESCE(bd.total_bonus, 0) as color_bonus_points,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
                  (ci.total_students * td.total_days), 2) as avg_participation_rate,
            ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(bd.total_bonus, 0)) /
                  (ci.total_students * td.total_days), 2) as avg_participation_rate_with_color
        FROM Roster r
        INNER JOIN Class_Info ci ON r.class_name = ci.class_name
        CROSS JOIN TotalDays td
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        LEFT JOIN BonusData bd ON r.class_name = bd.class_name
        GROUP BY r.class_name, r.teacher_name, r.grade_level, r.team_name, ci.total_students, td.total_days, bd.total_bonus
        HAVING td.total_days > 0
    ),
    MaxByGrade AS (
        SELECT grade_level, MAX(avg_participation_rate_with_color) as max_rate
        FROM ClassStats
        GROUP BY grade_level
    )
    SELECT
        cs.grade_level,
        cs.class_name,
        cs.teacher_name,
        cs.team_name,
        cs.total_participations_base,
        cs.color_bonus_points,
        cs.avg_participation_rate,
        cs.avg_participation_rate_with_color
    FROM ClassStats cs
    INNER JOIN MaxByGrade mbg ON cs.grade_level = mbg.grade_level AND cs.avg_participation_rate_with_color = mbg.max_rate
    ORDER BY cs.grade_level ASC, cs.class_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q13 Overall Best Class (Simplified)
# ============================================================================

QUERY_Q13_OVERALL_BEST_CLASS = """
    WITH TotalDays AS (
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
    ),
    BonusData AS (
        SELECT
            class_name,
            SUM(bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus
        GROUP BY class_name
    )
    SELECT
        r.class_name,
        r.teacher_name,
        r.grade_level,
        r.team_name,
        COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations_base,
        COALESCE(bd.total_bonus, 0) as color_bonus_points,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
              (ci.total_students * td.total_days), 2) as avg_participation_rate,
        ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(bd.total_bonus, 0)) /
              (ci.total_students * td.total_days), 2) as avg_participation_rate_with_color
    FROM Roster r
    INNER JOIN Class_Info ci ON r.class_name = ci.class_name
    CROSS JOIN TotalDays td
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    LEFT JOIN BonusData bd ON r.class_name = bd.class_name
    GROUP BY r.class_name, r.teacher_name, r.grade_level, r.team_name, ci.total_students, td.total_days, bd.total_bonus
    HAVING td.total_days > 0
    ORDER BY avg_participation_rate_with_color DESC, r.class_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q14 Team Participation
# ============================================================================

QUERY_Q14_TEAM_PARTICIPATION = """
    WITH TotalDays AS (
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
    ),
    TeamBonusData AS (
        SELECT
            ci.team_name,
            SUM(tcb.bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        GROUP BY ci.team_name
    )
    SELECT
        r.team_name,
        COUNT(DISTINCT r.student_name) as total_students,
        td.total_days as days_with_data,
        COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations_base,
        COALESCE(tbd.total_bonus, 0) as color_bonus_points,
        COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(tbd.total_bonus, 0) as total_participations_with_color,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
              (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_rate,
        ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(tbd.total_bonus, 0)) /
              (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_rate_with_color
    FROM Roster r
    CROSS JOIN TotalDays td
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    LEFT JOIN TeamBonusData tbd ON r.team_name = tbd.team_name
    GROUP BY r.team_name, td.total_days, tbd.total_bonus
    HAVING td.total_days > 0
    ORDER BY avg_participation_rate_with_color DESC
"""

# ============================================================================
# REPORT QUERIES - Q15 Goal Getters
# ============================================================================

QUERY_Q15_GOAL_GETTERS = """
    WITH TotalDays AS (
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
    ),
    StudentGoalDays AS (
        SELECT
            r.student_name,
            r.grade_level,
            r.team_name,
            r.class_name,
            COUNT(DISTINCT dl.log_date) as days_with_data,
            SUM(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as days_met_goal,
            td.total_days
        FROM Roster r
        CROSS JOIN TotalDays td
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        GROUP BY r.student_name, r.grade_level, r.team_name, r.class_name, td.total_days
        HAVING days_met_goal = td.total_days AND days_with_data = td.total_days
    )
    SELECT
        student_name,
        grade_level,
        days_met_goal,
        total_days,
        team_name,
        class_name
    FROM StudentGoalDays
    ORDER BY grade_level ASC, student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q16 Top Earner Per Team
# ============================================================================

QUERY_Q16_TOP_EARNER_PER_TEAM = """
    WITH MaxByTeam AS (
        SELECT
            r.team_name,
            MAX(COALESCE(rc.donation_amount, 0)) as max_donation
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.team_name
    )
    SELECT
        r.team_name,
        r.student_name,
        COALESCE(rc.donation_amount, 0) as donation_amount,
        COALESCE(rc.sponsors, 0) as sponsors,
        r.grade_level,
        r.class_name
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    INNER JOIN MaxByTeam mbt ON r.team_name = mbt.team_name
        AND COALESCE(rc.donation_amount, 0) = mbt.max_donation
    WHERE mbt.max_donation > 0
    ORDER BY r.team_name ASC, r.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q18 Lead Class by Grade
# ============================================================================

QUERY_Q18_LEAD_CLASS_BY_GRADE = """
    WITH TotalDays AS (
        SELECT COUNT(DISTINCT log_date) as total_days
        FROM Daily_Logs
    ),
    BonusData AS (
        SELECT
            class_name,
            SUM(bonus_participation_points) as total_bonus
        FROM Team_Color_Bonus
        GROUP BY class_name
    ),
    ClassStats AS (
        SELECT
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            ci.total_students,
            td.total_days as days_with_data,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations_base,
            COALESCE(bd.total_bonus, 0) as color_bonus_points,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(bd.total_bonus, 0) as total_participations_with_color,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) /
                  (ci.total_students * td.total_days), 2) as avg_participation_rate,
            ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(bd.total_bonus, 0)) /
                  (ci.total_students * td.total_days), 2) as avg_participation_rate_with_color
        FROM Roster r
        INNER JOIN Class_Info ci ON r.class_name = ci.class_name
        CROSS JOIN TotalDays td
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        LEFT JOIN BonusData bd ON r.class_name = bd.class_name
        GROUP BY r.class_name, r.teacher_name, r.grade_level, r.team_name, ci.total_students, td.total_days, bd.total_bonus
        HAVING td.total_days > 0
    ),
    MaxByGrade AS (
        SELECT grade_level, MAX(avg_participation_rate_with_color) as max_rate
        FROM ClassStats
        GROUP BY grade_level
    )
    SELECT
        cs.grade_level,
        cs.class_name,
        cs.teacher_name,
        cs.team_name,
        cs.total_students,
        cs.days_with_data,
        cs.total_participations_base,
        cs.color_bonus_points,
        cs.total_participations_with_color,
        cs.avg_participation_rate,
        cs.avg_participation_rate_with_color
    FROM ClassStats cs
    INNER JOIN MaxByGrade mbg ON cs.grade_level = mbg.grade_level AND cs.avg_participation_rate_with_color = mbg.max_rate
    ORDER BY cs.grade_level ASC, cs.class_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q19 Team Minutes
# ============================================================================

QUERY_Q19_TEAM_MINUTES = """
    WITH TeamBonusMinutes AS (
        SELECT
            ci.team_name,
            SUM(tcb.bonus_minutes) as total_bonus
        FROM Team_Color_Bonus tcb
        INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
        GROUP BY ci.team_name
    ),
    TeamTotals AS (
        SELECT
            r.team_name,
            COUNT(DISTINCT r.student_name) as total_students,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) / 60 as total_hours_base,
            COALESCE(tbm.total_bonus, 0) as bonus_minutes,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) + COALESCE(tbm.total_bonus, 0) as total_minutes_with_color,
            (COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) + COALESCE(tbm.total_bonus, 0)) / 60 as total_hours_with_color,
            ROUND(1.0 * COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) / COUNT(DISTINCT r.student_name), 1) as avg_minutes_per_student,
            ROUND(1.0 * (COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) + COALESCE(tbm.total_bonus, 0)) / COUNT(DISTINCT r.student_name), 1) as avg_minutes_per_student_with_color
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        LEFT JOIN TeamBonusMinutes tbm ON r.team_name = tbm.team_name
        GROUP BY r.team_name, tbm.total_bonus
    ),
    CombinedResults AS (
        SELECT
            team_name,
            total_students,
            total_minutes_base,
            total_hours_base,
            bonus_minutes,
            total_minutes_with_color,
            total_hours_with_color,
            avg_minutes_per_student,
            avg_minutes_per_student_with_color
        FROM TeamTotals
        UNION ALL
        SELECT
            'TOTAL' as team_name,
            SUM(total_students) as total_students,
            SUM(total_minutes_base) as total_minutes_base,
            SUM(total_hours_base) as total_hours_base,
            SUM(bonus_minutes) as bonus_minutes,
            SUM(total_minutes_with_color) as total_minutes_with_color,
            SUM(total_hours_with_color) as total_hours_with_color,
            ROUND(1.0 * SUM(total_minutes_base) / SUM(total_students), 1) as avg_minutes_per_student,
            ROUND(1.0 * SUM(total_minutes_with_color) / SUM(total_students), 1) as avg_minutes_per_student_with_color
        FROM TeamTotals
    )
    SELECT * FROM CombinedResults
    ORDER BY
        CASE WHEN team_name = 'TOTAL' THEN 2 ELSE 1 END,
        total_minutes_with_color DESC
"""

# ============================================================================
# REPORT QUERIES - Q20 Team Donations
# ============================================================================

QUERY_Q20_TEAM_DONATIONS = """
    SELECT
        r.team_name,
        ROUND(SUM(COALESCE(rc.donation_amount, 0)), 2) as total_donations,
        SUM(COALESCE(rc.sponsors, 0)) as total_sponsors,
        COUNT(DISTINCT r.student_name) as total_students,
        ROUND(SUM(COALESCE(rc.donation_amount, 0)) / COUNT(DISTINCT r.student_name), 2) as avg_donation_per_student
    FROM Roster r
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    GROUP BY r.team_name
    ORDER BY total_donations DESC
"""

# ============================================================================
# REPORT QUERIES - Q21 Minutes Integrity Check
# ============================================================================

QUERY_Q21_MINUTES_INTEGRITY = """
    SELECT
        r.student_name,
        r.team_name,
        r.class_name,
        COALESCE(SUM(dl.minutes_read), 0) as daily_minutes_sum,
        COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as daily_minutes_capped,
        COALESCE(rc.cumulative_minutes, 0) as cumulative_minutes,
        COALESCE(rc.cumulative_minutes, 0) - COALESCE(SUM(dl.minutes_read), 0) as difference,
        CASE
            WHEN COALESCE(rc.cumulative_minutes, 0) = COALESCE(SUM(dl.minutes_read), 0) THEN 'OK'
            WHEN rc.cumulative_minutes IS NULL AND SUM(dl.minutes_read) > 0 THEN 'MISSING_CUMULATIVE'
            WHEN rc.cumulative_minutes > 0 AND SUM(dl.minutes_read) IS NULL THEN 'MISSING_DAILY'
            WHEN COALESCE(rc.cumulative_minutes, 0) != COALESCE(SUM(dl.minutes_read), 0) THEN 'MINUTES_MISMATCH'
            ELSE 'NO_DATA'
        END as status
    FROM Roster r
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
    LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
    GROUP BY r.student_name, r.team_name, r.class_name, rc.cumulative_minutes
    HAVING status != 'NO_DATA'
    ORDER BY
        CASE status
            WHEN 'MINUTES_MISMATCH' THEN 1
            WHEN 'MISSING_CUMULATIVE' THEN 2
            WHEN 'MISSING_DAILY' THEN 3
            WHEN 'OK' THEN 4
        END,
        ABS(difference) DESC,
        r.student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q22 Student Name Sync Check
# ============================================================================

QUERY_Q22_STUDENT_NAME_SYNC = """
    SELECT
        COALESCE(dl.student_name, rc.student_name) as student_name,
        CASE
            WHEN dl.student_name IS NOT NULL AND rc.student_name IS NOT NULL THEN 'OK'
            WHEN dl.student_name IS NOT NULL AND rc.student_name IS NULL THEN 'IN_DAILY_ONLY'
            WHEN dl.student_name IS NULL AND rc.student_name IS NOT NULL THEN 'IN_CUMULATIVE_ONLY'
        END as status,
        CASE WHEN dl.student_name IS NOT NULL THEN 'Yes' ELSE 'No' END as in_daily_logs,
        CASE WHEN rc.student_name IS NOT NULL THEN 'Yes' ELSE 'No' END as in_reader_cumulative
    FROM (
        SELECT DISTINCT student_name FROM Daily_Logs WHERE minutes_read > 0
    ) dl
    FULL OUTER JOIN (
        SELECT DISTINCT student_name FROM Reader_Cumulative WHERE cumulative_minutes > 0
    ) rc ON dl.student_name = rc.student_name
    WHERE dl.student_name IS NULL OR rc.student_name IS NULL
    ORDER BY
        CASE status
            WHEN 'IN_DAILY_ONLY' THEN 1
            WHEN 'IN_CUMULATIVE_ONLY' THEN 2
            ELSE 3
        END,
        student_name ASC
"""

# ============================================================================
# REPORT QUERIES - Q23 Roster Integrity Check
# ============================================================================

QUERY_Q23_ROSTER_INTEGRITY = """
    SELECT
        student_name,
        found_in_table,
        CASE
            WHEN in_roster = 1 THEN 'OK'
            ELSE 'MISSING_FROM_ROSTER'
        END as status
    FROM (
        SELECT
            student_name,
            'Daily_Logs' as found_in_table,
            (SELECT COUNT(*) FROM Roster WHERE Roster.student_name = dl.student_name) as in_roster
        FROM (SELECT DISTINCT student_name FROM Daily_Logs WHERE minutes_read > 0) dl

        UNION

        SELECT
            student_name,
            'Reader_Cumulative' as found_in_table,
            (SELECT COUNT(*) FROM Roster WHERE Roster.student_name = rc.student_name) as in_roster
        FROM (SELECT DISTINCT student_name FROM Reader_Cumulative) rc
    )
    WHERE in_roster = 0
    ORDER BY student_name ASC, found_in_table ASC
"""

# ============================================================================
# GRADE LEVEL TAB QUERIES
# ============================================================================

def get_grade_level_classes_query(date_where="", grade_where=""):
    """
    Get all classes with their metrics for the Grade Level tab.

    Args:
        date_where: SQL WHERE clause for date filtering (e.g., "AND dl.log_date <= '2025-10-15'")
                    Empty string = full contest
        grade_where: SQL WHERE clause for grade filtering (e.g., "WHERE ci.grade_level = '2'")
                     Empty string = all grades

    Returns metrics:
    - Fundraising (NEVER filtered)
    - Sponsors (NEVER filtered)
    - Minutes read with color bonus (FILTERED by date and grade)
    - Avg per student (FILTERED by date and grade)
    - Participation % (FILTERED by date and grade)
    - Goal met ≥1 day (FILTERED by date and grade)
    """
    return f"""
        -- Separate Reader_Cumulative metrics (fundraising, sponsors) from Daily_Logs metrics (minutes)
        -- This prevents the Daily_Logs JOIN from multiplying Reader_Cumulative data
        WITH FundraisingMetrics AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                ci.total_students,

                -- Fundraising (NEVER filtered by date)
                COALESCE(SUM(rc.donation_amount), 0) as total_fundraising,

                -- Sponsors (NEVER filtered by date)
                COALESCE(SUM(rc.sponsors), 0) as total_sponsors

            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            {grade_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students
        ),
        MinutesMetrics AS (
            SELECT
                ci.class_name,

                -- Minutes read base (FILTERED by date) - cap at 120 per day per student
                COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base

            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            {grade_where}
            GROUP BY ci.class_name
        ),
        ClassMetrics AS (
            SELECT
                fm.class_name,
                fm.teacher_name,
                fm.grade_level,
                fm.team_name,
                fm.total_students,
                fm.total_fundraising,
                fm.total_sponsors,
                COALESCE(mm.total_minutes_base, 0) as total_minutes_base
            FROM FundraisingMetrics fm
            LEFT JOIN MinutesMetrics mm ON fm.class_name = mm.class_name
        ),
        ColorBonus AS (
            SELECT
                tcb.class_name,
                COALESCE(SUM(tcb.bonus_minutes), 0) as bonus_minutes,
                COALESCE(SUM(tcb.bonus_participation_points), 0) as bonus_participation_points
            FROM Team_Color_Bonus tcb
            GROUP BY tcb.class_name
        ),
        Participation AS (
            SELECT
                class_name,
                AVG(daily_pct) as avg_participation_pct
            FROM (
                SELECT
                    r.class_name as class_name,
                    dl.log_date,
                    (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / ci.total_students) as daily_pct
                FROM Roster r
                JOIN Class_Info ci ON r.class_name = ci.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
                GROUP BY r.class_name, dl.log_date, ci.total_students
            ) AS daily_participation
            GROUP BY class_name
        ),
        GoalMet AS (
            SELECT
                r.class_name,
                COUNT(DISTINCT dl.student_name) as students_met_goal
            FROM Roster r
            JOIN Daily_Logs dl ON r.student_name = dl.student_name
            JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE dl.minutes_read >= gr.min_daily_minutes {date_where}
            GROUP BY r.class_name
        )
        SELECT
            cm.class_name,
            cm.teacher_name,
            cm.grade_level,
            cm.team_name,
            cm.total_students,

            -- Fundraising (no filter indicator needed)
            cm.total_fundraising,

            -- Sponsors (no filter indicator needed)
            cm.total_sponsors,

            -- Minutes with color bonus (honors date filter)
            (cm.total_minutes_base + COALESCE(cb.bonus_minutes, 0)) as total_minutes,

            -- Avg per student (honors date filter)
            CASE WHEN cm.total_students > 0
                THEN ROUND((cm.total_minutes_base + COALESCE(cb.bonus_minutes, 0)) * 1.0 / cm.total_students, 1)
                ELSE 0
            END as avg_minutes_per_student,

            -- Participation % with color bonus (honors date filter)
            COALESCE(p.avg_participation_pct, 0) as participation_pct,

            -- Goal met ≥1 day (honors date filter)
            COALESCE(gm.students_met_goal, 0) as students_met_goal

        FROM ClassMetrics cm
        LEFT JOIN ColorBonus cb ON cm.class_name = cb.class_name
        LEFT JOIN Participation p ON cm.class_name = p.class_name
        LEFT JOIN GoalMet gm ON cm.class_name = gm.class_name
        ORDER BY cm.grade_level, cm.teacher_name
    """

def get_grade_aggregations_query(date_where=""):
    """
    Get grade-level aggregations for grade summary cards.
    Shows top class and top student per grade for each metric.
    """
    return f"""
        WITH GradeStats AS (
            SELECT
                ci.grade_level,
                COUNT(DISTINCT ci.class_name) as num_classes,
                SUM(ci.total_students) as num_students,
                SUM(CASE WHEN ci.team_name = 'Kitsko' THEN ci.total_students ELSE 0 END) as kitsko_students,
                SUM(CASE WHEN ci.team_name = 'Staub' THEN ci.total_students ELSE 0 END) as staub_students
            FROM Class_Info ci
            GROUP BY ci.grade_level
        ),
        GradeTopFundraising AS (
            SELECT
                r.grade_level,
                r.teacher_name,
                r.team_name,
                SUM(rc.donation_amount) as total_fundraising,
                ROW_NUMBER() OVER (PARTITION BY r.grade_level ORDER BY SUM(rc.donation_amount) DESC) as rn
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.grade_level, r.teacher_name, r.team_name
        ),
        GradeTopReading AS (
            SELECT
                r.grade_level,
                r.teacher_name,
                r.team_name,
                SUM(MIN(dl.minutes_read, 120)) as total_minutes,
                ROW_NUMBER() OVER (PARTITION BY r.grade_level ORDER BY SUM(MIN(dl.minutes_read, 120)) DESC) as rn
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY r.grade_level, r.teacher_name, r.team_name
        ),
        ClassDailyParticipation AS (
            SELECT
                ci.grade_level,
                ci.teacher_name,
                ci.team_name,
                dl.log_date,
                (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / ci.total_students) as daily_pct
            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY ci.grade_level, ci.teacher_name, ci.team_name, dl.log_date, ci.total_students
        ),
        GradeTopParticipation AS (
            SELECT
                grade_level,
                teacher_name,
                team_name,
                AVG(daily_pct) as avg_participation_pct,
                ROW_NUMBER() OVER (PARTITION BY grade_level ORDER BY AVG(daily_pct) DESC) as rn
            FROM ClassDailyParticipation
            GROUP BY grade_level, teacher_name, team_name
        ),
        StudentTopFundraising AS (
            SELECT
                r.grade_level,
                rc.student_name,
                r.team_name,
                rc.donation_amount,
                ROW_NUMBER() OVER (PARTITION BY r.grade_level ORDER BY rc.donation_amount DESC) as rn
            FROM Reader_Cumulative rc
            JOIN Roster r ON rc.student_name = r.student_name
        ),
        StudentTopReading AS (
            SELECT
                r.grade_level,
                dl.student_name,
                r.team_name,
                SUM(MIN(dl.minutes_read, 120)) as total_minutes,
                ROW_NUMBER() OVER (PARTITION BY r.grade_level ORDER BY SUM(MIN(dl.minutes_read, 120)) DESC) as rn
            FROM Daily_Logs dl
            JOIN Roster r ON dl.student_name = r.student_name {date_where}
            GROUP BY r.grade_level, dl.student_name, r.team_name
        )
        SELECT
            gs.grade_level,
            gs.num_classes,
            gs.num_students,
            gs.kitsko_students,
            gs.staub_students,

            -- Top class fundraising
            gtf.teacher_name as top_fundraising_teacher,
            gtf.team_name as top_fundraising_team,
            gtf.total_fundraising as top_fundraising_amount,

            -- Top class reading
            gtr.teacher_name as top_reading_teacher,
            gtr.team_name as top_reading_team,
            gtr.total_minutes as top_reading_minutes,

            -- Top class participation
            gtp.teacher_name as top_participation_teacher,
            gtp.team_name as top_participation_team,
            gtp.avg_participation_pct as top_participation_pct,

            -- Top student fundraising
            stf.student_name as top_student_fundraiser,
            stf.team_name as top_student_fundraiser_team,
            stf.donation_amount as top_student_fundraising_amount,

            -- Top student reading
            str.student_name as top_student_reader,
            str.team_name as top_student_reader_team,
            str.total_minutes as top_student_reading_minutes

        FROM GradeStats gs
        LEFT JOIN GradeTopFundraising gtf ON gs.grade_level = gtf.grade_level AND gtf.rn = 1
        LEFT JOIN GradeTopReading gtr ON gs.grade_level = gtr.grade_level AND gtr.rn = 1
        LEFT JOIN GradeTopParticipation gtp ON gs.grade_level = gtp.grade_level AND gtp.rn = 1
        LEFT JOIN StudentTopFundraising stf ON gs.grade_level = stf.grade_level AND stf.rn = 1
        LEFT JOIN StudentTopReading str ON gs.grade_level = str.grade_level AND str.rn = 1
        ORDER BY
            CASE gs.grade_level
                WHEN 'K' THEN 0
                WHEN '1st' THEN 1
                WHEN '2nd' THEN 2
                WHEN '3rd' THEN 3
                WHEN '4th' THEN 4
                WHEN '5th' THEN 5
                ELSE 99
            END
    """

def get_school_wide_leaders_query(date_where="", grade=None):
    """
    Get leaders for the headline banner.
    If grade is None: Returns top class across ALL grades (school-wide)
    If grade is specified: Returns top class within that grade only

    IMPORTANT: Groups by CLASS_NAME (not teacher_name) to handle teachers with multiple classes
    IMPORTANT: Includes color bonus in minutes to match table calculations
    """
    grade_where = f" AND ci.grade_level = '{grade}'" if grade else ""

    return f"""
        SELECT * FROM (
            SELECT
                'fundraising' as metric,
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                SUM(rc.donation_amount) as value
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE 1=1 {grade_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY value DESC
            LIMIT 1
        )

        UNION ALL

        SELECT * FROM (
            -- Minutes with color bonus (matches table calculation)
            WITH ClassMinutes AS (
                SELECT
                    ci.class_name,
                    ci.teacher_name,
                    ci.grade_level,
                    ci.team_name,
                    SUM(MIN(dl.minutes_read, 120)) as base_minutes
                FROM Class_Info ci
                JOIN Roster r ON ci.class_name = r.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
                WHERE 1=1 {grade_where}
                GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ),
            ColorBonus AS (
                SELECT
                    class_name,
                    SUM(bonus_minutes) as bonus_minutes
                FROM Team_Color_Bonus
                GROUP BY class_name
            )
            SELECT
                'minutes' as metric,
                cm.class_name,
                cm.teacher_name,
                cm.grade_level,
                cm.team_name,
                (cm.base_minutes + COALESCE(cb.bonus_minutes, 0)) as value
            FROM ClassMinutes cm
            LEFT JOIN ColorBonus cb ON cm.class_name = cb.class_name
            ORDER BY value DESC
            LIMIT 1
        )

        UNION ALL

        SELECT * FROM (
            SELECT
                'sponsors' as metric,
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                SUM(rc.sponsors) as value
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE 1=1 {grade_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY value DESC
            LIMIT 1
        )

        UNION ALL

        SELECT * FROM (
            WITH ClassDailyParticipation AS (
                SELECT
                    ci.class_name,
                    ci.teacher_name,
                    ci.grade_level,
                    ci.team_name,
                    dl.log_date,
                    (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / ci.total_students) as daily_pct
                FROM Class_Info ci
                JOIN Roster r ON ci.class_name = r.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE 1=1 {grade_where} {date_where}
                GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students, dl.log_date
            )
            SELECT
                'participation' as metric,
                class_name,
                teacher_name,
                grade_level,
                team_name,
                AVG(daily_pct) as value
            FROM ClassDailyParticipation
            GROUP BY class_name, teacher_name, grade_level, team_name
            ORDER BY value DESC
            LIMIT 1
        )

        UNION ALL

        SELECT * FROM (
            SELECT
                'goals_met' as metric,
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COUNT(DISTINCT dl.student_name) as value
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            JOIN Grade_Rules gr ON ci.grade_level = gr.grade_level
            WHERE dl.minutes_read >= gr.min_daily_minutes {grade_where} {date_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY value DESC
            LIMIT 1
        )
    """
