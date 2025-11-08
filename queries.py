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

def get_grade_level_classes_query(date_where="", grade_where="", team_where=""):
    """
    Get all classes with their metrics for the Grade Level tab.
    Metrics match the Teams page calculations exactly for consistency.

    Args:
        date_where: SQL WHERE clause for date filtering (e.g., "AND dl.log_date <= '2025-10-15'")
                    Empty string = full contest
        grade_where: SQL WHERE clause for grade filtering (e.g., "AND ci.grade_level = '2'")
                     Empty string = all grades
        team_where: SQL WHERE clause for team filtering (e.g., "AND ci.team_name = 'Team 1'")
                    Empty string = all teams

    Returns metrics (matching Teams table rows):
    - Fundraising (NEVER filtered)
    - Sponsors (NEVER filtered)
    - Minutes read with color bonus (FILTERED by date)
    - Participation % - students who participated at least once (FILTERED by date)
    - All Days Active % - students who read all days (FILTERED by date)
    - Met Goal ≥1 Day % (FILTERED by date)
    - Met Goal All Days % (FILTERED by date)
    - Color War Points (bonus_participation_points)
    - Students (Team Size) - total students
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
            WHERE 1=1{grade_where}{team_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students
        ),
        MinutesMetrics AS (
            SELECT
                ci.class_name,

                -- Minutes read base (FILTERED by date) - cap at 120 per day per student
                COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes_base

            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE 1=1{date_where}{grade_where}{team_where}
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
        FilterDaysCount AS (
            SELECT COUNT(DISTINCT dl.log_date) as total_days
            FROM Daily_Logs dl
            WHERE 1=1 {date_where}
        ),
        Participation AS (
            SELECT
                ci.class_name,
                COUNT(DISTINCT dl.student_name) as participated_count
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            {grade_where}{team_where}
            GROUP BY ci.class_name
        ),
        AllDaysActive AS (
            SELECT
                class_name,
                COUNT(DISTINCT student_name) as all_days_count
            FROM (
                SELECT
                    ci.class_name,
                    dl.student_name,
                    COUNT(DISTINCT dl.log_date) as days_active,
                    (SELECT total_days FROM FilterDaysCount) as filter_days
                FROM Class_Info ci
                JOIN Roster r ON ci.class_name = r.class_name
                JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE dl.minutes_read > 0 {date_where}
                {grade_where}{team_where}
                GROUP BY ci.class_name, dl.student_name
                HAVING COUNT(DISTINCT dl.log_date) = (SELECT total_days FROM FilterDaysCount)
            )
            GROUP BY class_name
        ),
        GoalMetOnce AS (
            SELECT
                ci.class_name,
                COUNT(DISTINCT dl.student_name) as students_met_goal
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Daily_Logs dl ON r.student_name = dl.student_name
            JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE dl.minutes_read >= gr.min_daily_minutes {date_where}
            {grade_where}{team_where}
            GROUP BY ci.class_name
        ),
        GoalMetAllDays AS (
            SELECT
                class_name,
                COUNT(DISTINCT student_name) as goal_all_days_count
            FROM (
                SELECT
                    ci.class_name,
                    dl.student_name,
                    COUNT(DISTINCT CASE
                        WHEN dl.minutes_read >= gr.min_daily_minutes THEN dl.log_date
                    END) as days_met_goal,
                    (SELECT total_days FROM FilterDaysCount) as filter_days
                FROM Class_Info ci
                JOIN Roster r ON ci.class_name = r.class_name
                JOIN Daily_Logs dl ON r.student_name = dl.student_name
                JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
                WHERE 1=1 {date_where}
                {grade_where}{team_where}
                GROUP BY ci.class_name, dl.student_name
                HAVING COUNT(DISTINCT CASE
                    WHEN dl.minutes_read >= gr.min_daily_minutes THEN dl.log_date
                END) = (SELECT total_days FROM FilterDaysCount)
            )
            GROUP BY class_name
        ),
        AvgDailyParticipation AS (
            SELECT
                class_name,
                AVG(daily_pct) as avg_daily_pct
            FROM (
                SELECT
                    ci.class_name,
                    ci.total_students,
                    dl.log_date,
                    (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / ci.total_students) as daily_pct
                FROM Class_Info ci
                JOIN Roster r ON ci.class_name = r.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE 1=1 {date_where}
                {grade_where}{team_where}
                GROUP BY ci.class_name, ci.total_students, dl.log_date
            )
            GROUP BY class_name
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

            -- Participation % - matches Teams page calculation (students who participated at least once / total)
            CASE WHEN cm.total_students > 0
                THEN ROUND(COALESCE(p.participated_count, 0) * 100.0 / cm.total_students, 1)
                ELSE 0
            END as participation_pct,

            -- Avg. Participation (With Color) - average daily participation + color bonus
            CASE WHEN cm.total_students > 0 AND (SELECT total_days FROM FilterDaysCount) > 0
                THEN ROUND(
                    COALESCE(adp.avg_daily_pct, 0) +
                    (COALESCE(cb.bonus_participation_points, 0) * 100.0 / (cm.total_students * (SELECT total_days FROM FilterDaysCount))),
                    1
                )
                ELSE COALESCE(adp.avg_daily_pct, 0)
            END as avg_participation_with_color_pct,

            -- All Days Active % (students who read all days / total)
            CASE WHEN cm.total_students > 0
                THEN ROUND(COALESCE(ada.all_days_count, 0) * 100.0 / cm.total_students, 1)
                ELSE 0
            END as all_days_active_pct,

            -- Met Goal ≥1 Day % (students who met goal at least once / total)
            CASE WHEN cm.total_students > 0
                THEN ROUND(COALESCE(gmo.students_met_goal, 0) * 100.0 / cm.total_students, 1)
                ELSE 0
            END as goal_met_once_pct,

            -- Met Goal All Days % (students who met goal every day / total)
            CASE WHEN cm.total_students > 0
                THEN ROUND(COALESCE(gma.goal_all_days_count, 0) * 100.0 / cm.total_students, 1)
                ELSE 0
            END as goal_met_all_days_pct,

            -- Color War Points
            COALESCE(cb.bonus_participation_points, 0) as color_war_points

        FROM ClassMetrics cm
        LEFT JOIN ColorBonus cb ON cm.class_name = cb.class_name
        LEFT JOIN Participation p ON cm.class_name = p.class_name
        LEFT JOIN AvgDailyParticipation adp ON cm.class_name = adp.class_name
        LEFT JOIN AllDaysActive ada ON cm.class_name = ada.class_name
        LEFT JOIN GoalMetOnce gmo ON cm.class_name = gmo.class_name
        LEFT JOIN GoalMetAllDays gma ON cm.class_name = gma.class_name
        ORDER BY cm.grade_level, cm.teacher_name
    """

def get_grade_aggregations_query(date_where="", grade_where="", team_where=""):
    """
    Get grade-level aggregations for grade summary cards.
    Shows top class and top student per grade for each metric.

    Args:
        date_where: SQL WHERE clause for date filtering (uses dl. prefix)
        grade_where: SQL WHERE clause for grade filtering (uses ci. or r. prefix)
        team_where: SQL WHERE clause for team filtering (uses ci. or r. prefix)
    """
    # Build WHERE clauses for Roster table (using r. prefix)
    grade_where_r = grade_where.replace('ci.grade_level', 'r.grade_level') if grade_where else ""
    team_where_r = team_where.replace('ci.team_name', 'r.team_name') if team_where else ""

    return f"""
        WITH TeamNames AS (
            SELECT DISTINCT team_name
            FROM Roster
            ORDER BY team_name
        ),
        GradeStats AS (
            SELECT
                ci.grade_level,
                COUNT(DISTINCT ci.class_name) as num_classes,
                COUNT(DISTINCT r.student_name) as num_students,
                SUM(CASE WHEN r.team_name = (SELECT team_name FROM TeamNames LIMIT 1) THEN 1 ELSE 0 END) as team1_students,
                SUM(CASE WHEN r.team_name = (SELECT team_name FROM TeamNames LIMIT 1 OFFSET 1) THEN 1 ELSE 0 END) as team2_students
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            WHERE 1=1 {grade_where} {team_where}
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
            WHERE 1=1 {grade_where_r} {team_where_r}
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
            WHERE 1=1 {grade_where_r} {team_where_r}
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
            WHERE 1=1 {grade_where} {team_where}
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
            WHERE 1=1 {grade_where_r} {team_where_r}
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
            WHERE 1=1 {grade_where_r} {team_where_r}
            GROUP BY r.grade_level, dl.student_name, r.team_name
        )
        SELECT
            gs.grade_level,
            gs.num_classes,
            gs.num_students,
            gs.team1_students,
            gs.team2_students,

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

# ============================================================================
# STUDENTS PAGE QUERIES
# ============================================================================

def get_students_master_query(date_where="", date_where_no_alias="", grade_where="", team_where=""):
    """
    Get all students with their aggregate data for the Students page master table.

    Returns 13 columns per student:
    - student_name, grade_level, team_name, class_name, teacher_name
    - fundraising (donation_amount), sponsors
    - minutes_capped (max 120/day), minutes_uncapped (actual)
    - days_participated, participation_pct
    - days_met_goal, goal_met_pct

    Args:
        date_where: SQL WHERE clause for date filtering with alias (e.g., "AND dl.log_date <= '2025-10-15'")
        date_where_no_alias: SQL WHERE clause for date filtering without alias (e.g., "AND log_date <= '2025-10-15'")
        grade_where: SQL WHERE clause for grade filtering (e.g., "AND r.grade_level = '2'")
        team_where: SQL WHERE clause for team filtering (e.g., "AND r.team_name = 'Phoenix'")
    """
    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where_no_alias}
        ),
        StudentMetrics AS (
            SELECT
                r.student_name,
                r.grade_level,
                r.team_name,
                r.class_name,
                r.teacher_name,
                COALESCE(rc.donation_amount, 0) as fundraising,
                COALESCE(rc.sponsors, 0) as sponsors,
                COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as minutes_capped,
                COALESCE(SUM(dl.minutes_read), 0) as minutes_uncapped,
                COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY r.student_name, r.grade_level, r.team_name, r.class_name, r.teacher_name,
                     rc.donation_amount, rc.sponsors
        )
        SELECT
            sm.student_name,
            sm.grade_level,
            sm.team_name,
            sm.class_name,
            sm.teacher_name,
            sm.fundraising,
            sm.sponsors,
            sm.minutes_capped,
            sm.minutes_uncapped,
            sm.days_participated,
            CASE WHEN (SELECT total_days FROM TotalDays) > 0
                THEN ROUND(100.0 * sm.days_participated / (SELECT total_days FROM TotalDays), 1)
                ELSE 0
            END as participation_pct,
            sm.days_met_goal,
            CASE WHEN sm.days_participated > 0
                THEN ROUND(100.0 * sm.days_met_goal / sm.days_participated, 1)
                ELSE 0
            END as goal_met_pct
        FROM StudentMetrics sm
        ORDER BY sm.student_name
    """

def get_student_detail_query(date_where=""):
    """
    Get individual student detail with summary metrics and daily breakdown.

    Returns two result sets:
    1. Student summary (1 row)
    2. Daily log entries (multiple rows)

    This query is designed to be executed twice:
    - First without the daily breakdown (just summary)
    - Second with daily breakdown (for modal)

    Args:
        date_where: SQL WHERE clause for date filtering
    """
    summary_query = f"""
        SELECT
            r.student_name,
            r.grade_level,
            r.team_name,
            r.class_name,
            r.teacher_name,
            COALESCE(rc.donation_amount, 0) as fundraising,
            COALESCE(rc.sponsors, 0) as sponsors,
            COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_capped,
            COALESCE(SUM(dl.minutes_read), 0) as total_uncapped,
            COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated,
            COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal,
            gr.min_daily_minutes as grade_goal
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
        LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE r.student_name = ?
        GROUP BY r.student_name, r.grade_level, r.team_name, r.class_name, r.teacher_name,
                 rc.donation_amount, rc.sponsors, gr.min_daily_minutes
    """

    daily_query = f"""
        SELECT
            dl.log_date,
            dl.minutes_read as actual_minutes,
            CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END as capped_minutes,
            CASE WHEN dl.minutes_read > 120 THEN 1 ELSE 0 END as exceeded_cap,
            CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END as met_goal,
            gr.min_daily_minutes as grade_goal
        FROM Daily_Logs dl
        JOIN Roster r ON dl.student_name = r.student_name
        JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE dl.student_name = ? {date_where}
        ORDER BY dl.log_date
    """

    return summary_query, daily_query

def get_students_school_winners_query(date_where=""):
    """
    Get school-wide winners (gold highlights) for all metrics.

    Returns one row per metric with the max value across ALL students.
    Used to identify which students get gold oval highlights.

    Args:
        date_where: SQL WHERE clause for date filtering

    Returns columns: metric_name, max_value
    """
    return f"""
        SELECT 'fundraising' as metric, MAX(COALESCE(rc.donation_amount, 0)) as max_value
        FROM Reader_Cumulative rc

        UNION ALL

        SELECT 'sponsors' as metric, MAX(COALESCE(rc.sponsors, 0)) as max_value
        FROM Reader_Cumulative rc

        UNION ALL

        SELECT 'minutes_capped' as metric, MAX(total_capped) as max_value
        FROM (
            SELECT SUM(MIN(dl.minutes_read, 120)) as total_capped
            FROM Daily_Logs dl
            WHERE 1=1 {date_where}
            GROUP BY dl.student_name
        )

        UNION ALL

        SELECT 'minutes_uncapped' as metric, MAX(total_uncapped) as max_value
        FROM (
            SELECT SUM(dl.minutes_read) as total_uncapped
            FROM Daily_Logs dl
            WHERE 1=1 {date_where}
            GROUP BY dl.student_name
        )

        UNION ALL

        SELECT 'days_participated' as metric, MAX(days_participated) as max_value
        FROM (
            SELECT COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated
            FROM Daily_Logs dl
            WHERE 1=1 {date_where}
            GROUP BY dl.student_name
        )

        UNION ALL

        SELECT 'days_met_goal' as metric, MAX(days_met_goal) as max_value
        FROM (
            SELECT COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name
        )

        UNION ALL

        SELECT 'participation_pct' as metric, MAX(participation_pct) as max_value
        FROM (
            SELECT CASE
                WHEN (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE 1=1 {date_where}) > 0
                THEN ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) / (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE 1=1 {date_where}), 1)
                ELSE 0
            END as participation_pct
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY r.student_name
        )

        UNION ALL

        SELECT 'goal_met_pct' as metric, MAX(goal_met_pct) as max_value
        FROM (
            SELECT CASE
                WHEN COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) > 0
                THEN ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) / COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END), 1)
                ELSE 0
            END as goal_met_pct
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name
        )
    """

def get_students_banner_query(date_where="", date_where_no_alias="", grade_where="", team_where=""):
    """
    Get banner metrics for Students page (6 metrics matching School/Teams/Grade pages).

    Metrics (in order):
    1. Campaign Day - Full contest status (no filter)
    2. Fundraising - Total for filtered students (no date filter)
    3. Minutes Read - Total capped minutes for filtered students (honors date filter)
    4. Sponsors - Total sponsors for filtered students (no date filter)
    5. Avg. Participation - Average of (days_participated / total_days * 100) across filtered students (honors date filter)
    6. Goal Met (≥1 Day) - Filtered students who met goal ≥1 day (honors date filter)

    Args:
        date_where: SQL WHERE clause for date filtering with alias
        date_where_no_alias: SQL WHERE clause for date filtering without alias
        grade_where: SQL WHERE clause for grade filtering
        team_where: SQL WHERE clause for team filtering
    """
    return f"""
        WITH FilteredStudents AS (
            SELECT COUNT(DISTINCT r.student_name) as total_students
            FROM Roster r
            WHERE 1=1 {grade_where} {team_where}
        ),
        TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where_no_alias}
        ),
        AllDays AS (
            SELECT COUNT(DISTINCT log_date) as all_days
            FROM Daily_Logs
        ),
        Fundraising AS (
            SELECT
                COALESCE(SUM(rc.donation_amount), 0) as total_fundraising,
                MAX(rc.donation_amount) as max_fundraising
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE 1=1 {grade_where} {team_where}
        ),
        Minutes AS (
            SELECT
                COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_minutes
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            WHERE 1=1 {grade_where} {team_where}
        ),
        Sponsors AS (
            SELECT
                COALESCE(SUM(rc.sponsors), 0) as total_sponsors
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE 1=1 {grade_where} {team_where}
        ),
        Participation AS (
            SELECT
                CASE WHEN (SELECT total_students FROM FilteredStudents) > 0 AND (SELECT total_days FROM TotalDays) > 0
                    THEN ROUND(100.0 * COUNT(*) / ((SELECT total_students FROM FilteredStudents) * (SELECT total_days FROM TotalDays)), 1)
                    ELSE 0
                END as avg_participation_pct
            FROM Roster r
            INNER JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            WHERE dl.minutes_read > 0 {grade_where} {team_where}
        ),
        GoalMet AS (
            SELECT
                COUNT(DISTINCT r.student_name) as goal_met_count
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE dl.minutes_read >= gr.min_daily_minutes {grade_where} {team_where}
        )
        SELECT
            (SELECT total_days FROM TotalDays) as campaign_days,
            (SELECT all_days FROM AllDays) as total_contest_days,
            (SELECT total_fundraising FROM Fundraising) as total_fundraising,
            (SELECT total_minutes FROM Minutes) as total_minutes,
            (SELECT total_sponsors FROM Sponsors) as total_sponsors,
            ROUND(COALESCE((SELECT avg_participation_pct FROM Participation), 0), 1) as avg_participation_pct,
            CASE WHEN (SELECT total_students FROM FilteredStudents) > 0
                THEN ROUND(100.0 * (SELECT goal_met_count FROM GoalMet) / (SELECT total_students FROM FilteredStudents), 1)
                ELSE 0
            END as goal_met_pct,
            (SELECT total_students FROM FilteredStudents) as total_students
    """

def get_students_filtered_winners_query(date_where="", grade_where="", team_where=""):
    """
    Get winners within the current filter group (silver highlights).

    Only used when grade_filter != 'all' OR team_filter != 'all'
    Returns max values for each metric within the filtered group.

    Args:
        date_where: SQL WHERE clause for date filtering
        grade_where: SQL WHERE clause for grade filtering
        team_where: SQL WHERE clause for team filtering

    Returns columns: metric_name, max_value
    """
    return f"""
        SELECT 'fundraising' as metric, MAX(COALESCE(rc.donation_amount, 0)) as max_value
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        WHERE 1=1 {grade_where} {team_where}

        UNION ALL

        SELECT 'sponsors' as metric, MAX(COALESCE(rc.sponsors, 0)) as max_value
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        WHERE 1=1 {grade_where} {team_where}

        UNION ALL

        SELECT 'minutes_capped' as metric, MAX(total_capped) as max_value
        FROM (
            SELECT SUM(MIN(dl.minutes_read, 120)) as total_capped
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY dl.student_name
        )

        UNION ALL

        SELECT 'minutes_uncapped' as metric, MAX(total_uncapped) as max_value
        FROM (
            SELECT SUM(dl.minutes_read) as total_uncapped
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY dl.student_name
        )

        UNION ALL

        SELECT 'days_participated' as metric, MAX(days_participated) as max_value
        FROM (
            SELECT COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY dl.student_name
        )

        UNION ALL

        SELECT 'days_met_goal' as metric, MAX(days_met_goal) as max_value
        FROM (
            SELECT COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY r.student_name
        )

        UNION ALL

        SELECT 'participation_pct' as metric, MAX(participation_pct) as max_value
        FROM (
            SELECT CASE
                WHEN (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE 1=1 {date_where}) > 0
                THEN ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) / (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE 1=1 {date_where}), 1)
                ELSE 0
            END as participation_pct
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY r.student_name
        )

        UNION ALL

        SELECT 'goal_met_pct' as metric, MAX(goal_met_pct) as max_value
        FROM (
            SELECT CASE
                WHEN COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) > 0
                THEN ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) / COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END), 1)
                ELSE 0
            END as goal_met_pct
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            WHERE 1=1 {grade_where} {team_where}
            GROUP BY r.student_name
        )
    """

def get_school_wide_leaders_query(date_where="", grade=None, team=None):
    """
    Get leaders for the headline banner.
    If grade is None: Returns top class across ALL grades (school-wide)
    If grade is specified: Returns top class within that grade only
    If team is specified: Returns top class within that team only

    IMPORTANT: Groups by CLASS_NAME (not teacher_name) to handle teachers with multiple classes
    IMPORTANT: Includes color bonus in minutes to match table calculations
    """
    grade_where = f" AND ci.grade_level = '{grade}'" if grade else ""
    team_where = f" AND ci.team_name = '{team}'" if team else ""

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
            WHERE 1=1 {grade_where} {team_where}
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
                WHERE 1=1 {grade_where} {team_where}
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
            WHERE 1=1 {grade_where} {team_where}
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
                    ci.total_students,
                    dl.log_date,
                    (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / ci.total_students) as daily_pct
                FROM Class_Info ci
                JOIN Roster r ON ci.class_name = r.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE 1=1 {grade_where} {team_where} {date_where}
                GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students, dl.log_date
            ),
            ClassAvgParticipation AS (
                SELECT
                    class_name,
                    teacher_name,
                    grade_level,
                    team_name,
                    total_students,
                    AVG(daily_pct) as avg_participation
                FROM ClassDailyParticipation
                GROUP BY class_name, teacher_name, grade_level, team_name, total_students
            ),
            ColorBonus AS (
                SELECT
                    class_name,
                    SUM(bonus_participation_points) as bonus_points
                FROM Team_Color_Bonus
                GROUP BY class_name
            ),
            DaysCount AS (
                SELECT COUNT(DISTINCT dl.log_date) as total_days
                FROM Daily_Logs dl
                WHERE 1=1 {date_where}
            )
            SELECT
                'participation' as metric,
                cap.class_name,
                cap.teacher_name,
                cap.grade_level,
                cap.team_name,
                (cap.avg_participation + (COALESCE(cb.bonus_points, 0) * 100.0 / (cap.total_students * (SELECT total_days FROM DaysCount)))) as value
            FROM ClassAvgParticipation cap
            LEFT JOIN ColorBonus cb ON cap.class_name = cb.class_name
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
                CASE WHEN ci.total_students > 0
                    THEN ROUND(COUNT(DISTINCT dl.student_name) * 100.0 / ci.total_students, 1)
                    ELSE 0
                END as value
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            JOIN Grade_Rules gr ON ci.grade_level = gr.grade_level
            WHERE dl.minutes_read >= gr.min_daily_minutes {grade_where} {date_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students
            ORDER BY value DESC
            LIMIT 1
        )
    """

# Q24 - Database_Metadata (Multi-Year Database Registry)
QUERY_Q24_DATABASE_METADATA = """
    SELECT
        db_id,
        year,
        db_filename,
        description,
        created_timestamp,
        CASE WHEN is_active = 1 THEN 'ACTIVE' ELSE 'INACTIVE' END as status,
        student_count,
        total_days,
        total_donations
    FROM Database_Metadata
    ORDER BY year DESC
"""

# ============================================================================
# DATABASE COMPARISON QUERIES
# ============================================================================

# Get available databases from registry
QUERY_DB_REGISTRY_LIST = """
    SELECT
        database_id,
        display_name,
        year,
        filename,
        description,
        is_active,
        student_count,
        total_days,
        total_donations
    FROM Database_Registry
    ORDER BY year DESC
"""

def get_db_comparison_school_fundraising(date_filter=None):
    """Get school-wide fundraising total and top class"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH SchoolTotal AS (
            SELECT COALESCE(SUM(donation_amount), 0) as total_fundraising
            FROM Reader_Cumulative
        ),
        TopClass AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COALESCE(SUM(rc.donation_amount), 0) as class_fundraising
            FROM Class_Info ci
            LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY class_fundraising DESC
            LIMIT 1
        )
        SELECT
            st.total_fundraising,
            tc.class_name,
            tc.teacher_name,
            tc.grade_level,
            tc.team_name,
            tc.class_fundraising
        FROM SchoolTotal st, TopClass tc
    """

def get_db_comparison_school_minutes(date_filter=None):
    """Get school-wide capped minutes total and top class"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH SchoolTotal AS (
            SELECT COALESCE(SUM(CASE WHEN minutes_read > 120 THEN 120 ELSE minutes_read END), 0) as total_minutes
            FROM Daily_Logs
            WHERE minutes_read > 0 {date_where}
        ),
        TopClass AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as class_minutes
            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY class_minutes DESC
            LIMIT 1
        )
        SELECT
            st.total_minutes,
            tc.class_name,
            tc.teacher_name,
            tc.grade_level,
            tc.team_name,
            tc.class_minutes
        FROM SchoolTotal st, TopClass tc
    """

def get_db_comparison_school_sponsors(date_filter=None):
    """Get school-wide sponsor count and top class"""
    return """
        WITH SchoolTotal AS (
            SELECT COALESCE(SUM(sponsors), 0) as total_sponsors
            FROM Reader_Cumulative
        ),
        TopClass AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COALESCE(SUM(rc.sponsors), 0) as class_sponsors
            FROM Class_Info ci
            LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY class_sponsors DESC
            LIMIT 1
        )
        SELECT
            st.total_sponsors,
            tc.class_name,
            tc.teacher_name,
            tc.grade_level,
            tc.team_name,
            tc.class_sponsors
        FROM SchoolTotal st, TopClass tc
    """

def get_db_comparison_school_participation(date_filter=None):
    """Get school-wide participation percentage and top class"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH SchoolParticipation AS (
            SELECT
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) as participating_count,
                COUNT(DISTINCT r.student_name) as total_count
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE 1=1 {date_where}
        ),
        TopClass AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 / NULLIF(ci.total_students, 0) as class_participation
            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE 1=1 {date_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students
            ORDER BY class_participation DESC
            LIMIT 1
        )
        SELECT
            sp.participation_pct,
            sp.participating_count,
            sp.total_count,
            tc.class_name,
            tc.teacher_name,
            tc.grade_level,
            tc.team_name,
            tc.class_participation
        FROM SchoolParticipation sp, TopClass tc
    """

def get_db_comparison_school_size():
    """Get school size (student count)"""
    return """
        SELECT
            COUNT(DISTINCT student_name) as student_count,
            COUNT(DISTINCT class_name) as class_count
        FROM Roster
    """

def get_db_comparison_student_top_fundraiser():
    """Get top student fundraiser"""
    return """
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            COALESCE(rc.donation_amount, 0) as fundraising
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        ORDER BY fundraising DESC
        LIMIT 1
    """

def get_db_comparison_student_top_reader(date_filter=None):
    """Get top student reader (capped minutes)"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE dl.minutes_read > 0 {date_where}
        GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name
        ORDER BY total_minutes DESC
        LIMIT 1
    """

def get_db_comparison_student_top_sponsors():
    """Get student with most sponsors"""
    return """
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            COALESCE(rc.sponsors, 0) as sponsor_count
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        ORDER BY sponsor_count DESC
        LIMIT 1
    """

def get_db_comparison_team_top(metric, date_filter=None):
    """Get top team for a given metric

    Args:
        metric: 'fundraising', 'minutes', 'sponsors', 'participation', 'size'
        date_filter: Optional date filter for time-based metrics
    """
    date_where = ""
    if date_filter and date_filter != 'all' and metric in ['minutes', 'participation']:
        date_where = f"AND dl.log_date <= '{date_filter}'"

    if metric == 'fundraising':
        return f"""
            WITH TeamTotals AS (
                SELECT
                    r.team_name,
                    COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
                FROM Roster r
                LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
                GROUP BY r.team_name
                ORDER BY total_fundraising DESC
                LIMIT 1
            ),
            TopClass AS (
                SELECT
                    ci.class_name,
                    ci.teacher_name,
                    ci.grade_level,
                    ci.team_name,
                    COALESCE(SUM(rc.donation_amount), 0) as class_fundraising
                FROM Class_Info ci
                LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
                WHERE ci.team_name = (SELECT team_name FROM TeamTotals)
                GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
                ORDER BY class_fundraising DESC
                LIMIT 1
            )
            SELECT
                tt.team_name,
                tt.total_fundraising,
                tc.class_name,
                tc.teacher_name,
                tc.grade_level
            FROM TeamTotals tt, TopClass tc
        """
    elif metric == 'minutes':
        return f"""
            WITH TeamTotals AS (
                SELECT
                    r.team_name,
                    COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
                FROM Roster r
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE dl.minutes_read > 0 {date_where}
                GROUP BY r.team_name
                ORDER BY total_minutes DESC
                LIMIT 1
            ),
            TopClass AS (
                SELECT
                    ci.class_name,
                    ci.teacher_name,
                    ci.grade_level,
                    ci.team_name,
                    COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as class_minutes
                FROM Class_Info ci
                LEFT JOIN Roster r ON ci.class_name = r.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE dl.minutes_read > 0 {date_where}
                    AND ci.team_name = (SELECT team_name FROM TeamTotals)
                GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
                ORDER BY class_minutes DESC
                LIMIT 1
            )
            SELECT
                tt.team_name,
                tt.total_minutes,
                tc.class_name,
                tc.teacher_name,
                tc.grade_level
            FROM TeamTotals tt, TopClass tc
        """
    elif metric == 'size':
        return """
            WITH TeamSizes AS (
                SELECT
                    team_name,
                    COUNT(DISTINCT student_name) as student_count,
                    COUNT(DISTINCT class_name) as class_count
                FROM Roster
                GROUP BY team_name
                ORDER BY student_count DESC
                LIMIT 1
            )
            SELECT
                team_name,
                student_count,
                class_count
            FROM TeamSizes
        """
    # Add more metrics as needed
    else:
        return "SELECT NULL"

def get_db_comparison_grade_top(metric, date_filter=None):
    """Get top grade for a given metric

    Args:
        metric: 'fundraising', 'minutes', 'sponsors', 'participation', 'size'
        date_filter: Optional date filter for time-based metrics
    """
    date_where = ""
    if date_filter and date_filter != 'all' and metric in ['minutes', 'participation']:
        date_where = f"AND dl.log_date <= '{date_filter}'"

    if metric == 'fundraising':
        return f"""
            WITH GradeTotals AS (
                SELECT
                    r.grade_level,
                    COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
                FROM Roster r
                LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
                GROUP BY r.grade_level
                ORDER BY total_fundraising DESC
                LIMIT 1
            ),
            TopClass AS (
                SELECT
                    ci.class_name,
                    ci.teacher_name,
                    ci.team_name,
                    ci.grade_level,
                    COALESCE(SUM(rc.donation_amount), 0) as class_fundraising
                FROM Class_Info ci
                LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
                WHERE ci.grade_level = (SELECT grade_level FROM GradeTotals)
                GROUP BY ci.class_name, ci.teacher_name, ci.team_name, ci.grade_level
                ORDER BY class_fundraising DESC
                LIMIT 1
            )
            SELECT
                gt.grade_level,
                gt.total_fundraising,
                tc.class_name,
                tc.teacher_name,
                tc.team_name
            FROM GradeTotals gt, TopClass tc
        """
    elif metric == 'minutes':
        return f"""
            WITH GradeTotals AS (
                SELECT
                    r.grade_level,
                    COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
                FROM Roster r
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE dl.minutes_read > 0 {date_where}
                GROUP BY r.grade_level
                ORDER BY total_minutes DESC
                LIMIT 1
            ),
            TopClass AS (
                SELECT
                    ci.class_name,
                    ci.teacher_name,
                    ci.team_name,
                    ci.grade_level,
                    COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as class_minutes
                FROM Class_Info ci
                LEFT JOIN Roster r ON ci.class_name = r.class_name
                LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
                WHERE dl.minutes_read > 0 {date_where}
                    AND ci.grade_level = (SELECT grade_level FROM GradeTotals)
                GROUP BY ci.class_name, ci.teacher_name, ci.team_name, ci.grade_level
                ORDER BY class_minutes DESC
                LIMIT 1
            )
            SELECT
                gt.grade_level,
                gt.total_minutes,
                tc.class_name,
                tc.teacher_name,
                tc.team_name
            FROM GradeTotals gt, TopClass tc
        """
    elif metric == 'size':
        return """
            WITH GradeSizes AS (
                SELECT
                    grade_level,
                    COUNT(DISTINCT student_name) as student_count,
                    COUNT(DISTINCT class_name) as class_count
                FROM Roster
                GROUP BY grade_level
                ORDER BY student_count DESC
                LIMIT 1
            )
            SELECT
                grade_level,
                student_count,
                class_count
            FROM GradeSizes
        """
    else:
        return "SELECT NULL"

def get_db_comparison_class_top(metric, date_filter=None):
    """Get top class for a given metric

    Args:
        metric: 'fundraising', 'minutes', 'sponsors', 'participation', 'size'
        date_filter: Optional date filter for time-based metrics
    """
    date_where = ""
    if date_filter and date_filter != 'all' and metric in ['minutes', 'participation']:
        date_where = f"AND dl.log_date <= '{date_filter}'"

    if metric == 'fundraising':
        return """
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COALESCE(SUM(rc.donation_amount), 0) as total_fundraising
            FROM Class_Info ci
            LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY total_fundraising DESC
            LIMIT 1
        """
    elif metric == 'minutes':
        return f"""
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                COALESCE(SUM(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 0) as total_minutes
            FROM Class_Info ci
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY total_minutes DESC
            LIMIT 1
        """
    elif metric == 'size':
        return """
            SELECT
                class_name,
                teacher_name,
                grade_level,
                team_name,
                total_students
            FROM Class_Info
            ORDER BY total_students DESC
            LIMIT 1
        """
    else:
        return "SELECT NULL"

# Additional School-Level Comparison Queries

def get_db_comparison_school_avg_participation(date_filter=None):
    """Get school-wide average participation % with color bonus"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        ColorBonus AS (
            SELECT COALESCE(SUM(bonus_participation_points), 0) as total_bonus
            FROM Team_Color_Bonus
        )
        SELECT
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) /
                  (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_pct_base,
            ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) + cb.total_bonus) /
                  (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_pct_with_color,
            COUNT(DISTINCT r.student_name) as total_students,
            td.total_days,
            cb.total_bonus
        FROM Roster r
        CROSS JOIN TotalDays td
        CROSS JOIN ColorBonus cb
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE td.total_days > 0 {date_where}
    """

def get_db_comparison_school_goal_met():
    """Get school-wide % who met goal at least 1 day"""
    return """
        WITH StudentGoals AS (
            SELECT
                r.student_name,
                MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name
        )
        SELECT
            ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct,
            SUM(met_goal) as students_who_met_goal,
            COUNT(*) as total_students
        FROM StudentGoals
    """

def get_db_comparison_school_all_days_active(date_filter=None):
    """Get school-wide % who logged reading every day"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        StudentDaysActive AS (
            SELECT
                r.student_name,
                COUNT(DISTINCT dl.log_date) as days_active
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY r.student_name
        )
        SELECT
            ROUND(100.0 * SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) /
                  NULLIF(COUNT(DISTINCT r.student_name), 0), 2) as all_days_active_pct,
            SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) as students_all_days,
            COUNT(DISTINCT r.student_name) as total_students,
            td.total_days
        FROM Roster r
        CROSS JOIN TotalDays td
        LEFT JOIN StudentDaysActive sda ON r.student_name = sda.student_name
    """

def get_db_comparison_school_goal_met_all_days():
    """Get school-wide % who met goal every day"""
    return """
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
        ),
        StudentGoalDays AS (
            SELECT
                r.student_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name
        )
        SELECT
            ROUND(100.0 * SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) /
                  NULLIF(COUNT(DISTINCT r.student_name), 0), 2) as goal_met_all_days_pct,
            SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) as students_goal_all_days,
            COUNT(DISTINCT r.student_name) as total_students,
            td.total_days
        FROM Roster r
        CROSS JOIN TotalDays td
        LEFT JOIN StudentGoalDays sgd ON r.student_name = sgd.student_name
    """

def get_db_comparison_school_color_war_points():
    """Get school-wide color war points total"""
    return """
        WITH ParticipationPoints AS (
            SELECT COUNT(DISTINCT CASE WHEN minutes_read > 0 THEN log_date || '-' || student_name END) as base_points
            FROM Daily_Logs
        ),
        BonusPoints AS (
            SELECT COALESCE(SUM(bonus_participation_points), 0) as bonus_points
            FROM Team_Color_Bonus
        )
        SELECT
            pp.base_points + bp.bonus_points as total_points,
            pp.base_points,
            bp.bonus_points
        FROM ParticipationPoints pp, BonusPoints bp
    """

# Additional Team-Level Comparison Queries

def get_db_comparison_team_sponsors():
    """Get team with most sponsors"""
    return """
        WITH TeamSponsors AS (
            SELECT
                r.team_name,
                COALESCE(SUM(rc.sponsors), 0) as total_sponsors
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY total_sponsors DESC
            LIMIT 1
        ),
        TopClass AS (
            SELECT
                ci.class_name,
                ci.grade_level,
                COALESCE(SUM(rc.sponsors), 0) as class_sponsors
            FROM Class_Info ci
            LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
            WHERE ci.team_name = (SELECT team_name FROM TeamSponsors)
            GROUP BY ci.class_name, ci.grade_level
            ORDER BY class_sponsors DESC
            LIMIT 1
        )
        SELECT
            ts.team_name,
            ts.total_sponsors,
            tc.class_name,
            tc.grade_level
        FROM TeamSponsors ts, TopClass tc
    """

def get_db_comparison_team_participation(date_filter=None):
    """Get team with highest participation (≥1 day)"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH TeamParticipation AS (
            SELECT
                r.team_name,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                    NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) as participating_count,
                COUNT(DISTINCT r.student_name) as total_count
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE 1=1 {date_where}
            GROUP BY r.team_name
            ORDER BY participation_pct DESC
            LIMIT 1
        )
        SELECT
            team_name,
            participation_pct,
            participating_count,
            total_count
        FROM TeamParticipation
    """

def get_db_comparison_team_avg_participation(date_filter=None):
    """Get team with highest average participation % with color bonus"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        TeamBonusData AS (
            SELECT
                ci.team_name,
                SUM(tcb.bonus_participation_points) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            GROUP BY ci.team_name
        ),
        TeamStats AS (
            SELECT
                r.team_name,
                COUNT(DISTINCT r.student_name) as total_students,
                td.total_days,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations,
                COALESCE(tbd.total_bonus, 0) as color_bonus,
                ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(tbd.total_bonus, 0)) /
                      (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_with_color
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN TeamBonusData tbd ON r.team_name = tbd.team_name
            WHERE td.total_days > 0 {date_where}
            GROUP BY r.team_name, td.total_days, tbd.total_bonus
            ORDER BY avg_participation_with_color DESC
            LIMIT 1
        )
        SELECT * FROM TeamStats
    """

def get_db_comparison_team_goal_met():
    """Get team with highest % who met goal at least 1 day"""
    return """
        WITH StudentGoals AS (
            SELECT
                r.team_name,
                r.student_name,
                MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.team_name, r.student_name
        ),
        TeamGoals AS (
            SELECT
                team_name,
                ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct,
                SUM(met_goal) as students_who_met_goal,
                COUNT(*) as total_students
            FROM StudentGoals
            GROUP BY team_name
            ORDER BY goal_met_pct DESC
            LIMIT 1
        )
        SELECT * FROM TeamGoals
    """

def get_db_comparison_team_all_days_active(date_filter=None):
    """Get team with highest % who logged every day"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        StudentDaysActive AS (
            SELECT
                r.team_name,
                r.student_name,
                COUNT(DISTINCT dl.log_date) as days_active
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY r.team_name, r.student_name
        ),
        TeamStats AS (
            SELECT
                r.team_name,
                ROUND(100.0 * SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) /
                      NULLIF(COUNT(DISTINCT r.student_name), 0), 2) as all_days_active_pct,
                SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) as students_all_days,
                COUNT(DISTINCT r.student_name) as total_students,
                td.total_days
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN StudentDaysActive sda ON r.student_name = sda.student_name AND r.team_name = sda.team_name
            GROUP BY r.team_name, td.total_days
            ORDER BY all_days_active_pct DESC
            LIMIT 1
        )
        SELECT * FROM TeamStats
    """

def get_db_comparison_team_goal_met_all_days():
    """Get team with highest % who met goal every day"""
    return """
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
        ),
        StudentGoalDays AS (
            SELECT
                r.team_name,
                r.student_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.team_name, r.student_name
        ),
        TeamStats AS (
            SELECT
                r.team_name,
                ROUND(100.0 * SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) /
                      NULLIF(COUNT(DISTINCT r.student_name), 0), 2) as goal_met_all_days_pct,
                SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) as students_goal_all_days,
                COUNT(DISTINCT r.student_name) as total_students,
                td.total_days
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN StudentGoalDays sgd ON r.student_name = sgd.student_name AND r.team_name = sgd.team_name
            GROUP BY r.team_name, td.total_days
            ORDER BY goal_met_all_days_pct DESC
            LIMIT 1
        )
        SELECT * FROM TeamStats
    """

def get_db_comparison_team_color_war_points():
    """Get team with most color war points"""
    return """
        WITH TeamParticipationPoints AS (
            SELECT
                r.team_name,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            GROUP BY r.team_name
        ),
        TeamBonusPoints AS (
            SELECT
                ci.team_name,
                COALESCE(SUM(tcb.bonus_participation_points), 0) as bonus_points
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            GROUP BY ci.team_name
        ),
        TeamTotalPoints AS (
            SELECT
                tpp.team_name,
                tpp.base_points + COALESCE(tbp.bonus_points, 0) as total_points,
                tpp.base_points,
                COALESCE(tbp.bonus_points, 0) as bonus_points
            FROM TeamParticipationPoints tpp
            LEFT JOIN TeamBonusPoints tbp ON tpp.team_name = tbp.team_name
            ORDER BY total_points DESC
            LIMIT 1
        )
        SELECT * FROM TeamTotalPoints
    """

# Additional Grade-Level Comparison Queries

def get_db_comparison_grade_sponsors():
    """Get grade with most sponsors"""
    return """
        WITH GradeSponsors AS (
            SELECT
                r.grade_level,
                COALESCE(SUM(rc.sponsors), 0) as total_sponsors
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.grade_level
            ORDER BY total_sponsors DESC
            LIMIT 1
        ),
        TopClass AS (
            SELECT
                ci.class_name,
                ci.team_name,
                COALESCE(SUM(rc.sponsors), 0) as class_sponsors
            FROM Class_Info ci
            LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
            WHERE ci.grade_level = (SELECT grade_level FROM GradeSponsors)
            GROUP BY ci.class_name, ci.team_name
            ORDER BY class_sponsors DESC
            LIMIT 1
        )
        SELECT
            gs.grade_level,
            gs.total_sponsors,
            tc.class_name,
            tc.team_name
        FROM GradeSponsors gs, TopClass tc
    """

def get_db_comparison_grade_participation(date_filter=None):
    """Get grade with highest participation (≥1 day)"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH GradeParticipation AS (
            SELECT
                r.grade_level,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                    NULLIF(COUNT(DISTINCT r.student_name), 0) as participation_pct,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) as participating_count,
                COUNT(DISTINCT r.student_name) as total_count
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE 1=1 {date_where}
            GROUP BY r.grade_level
            ORDER BY participation_pct DESC
            LIMIT 1
        )
        SELECT
            grade_level,
            participation_pct,
            participating_count,
            total_count
        FROM GradeParticipation
    """

def get_db_comparison_grade_avg_participation(date_filter=None):
    """Get grade with highest average participation % with color bonus"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        GradeBonusData AS (
            SELECT
                ci.grade_level,
                SUM(tcb.bonus_participation_points) as total_bonus
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            GROUP BY ci.grade_level
        ),
        GradeStats AS (
            SELECT
                r.grade_level,
                COUNT(DISTINCT r.student_name) as total_students,
                td.total_days,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations,
                COALESCE(gbd.total_bonus, 0) as color_bonus,
                ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(gbd.total_bonus, 0)) /
                      (COUNT(DISTINCT r.student_name) * td.total_days), 2) as avg_participation_with_color
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN GradeBonusData gbd ON r.grade_level = gbd.grade_level
            WHERE td.total_days > 0 {date_where}
            GROUP BY r.grade_level, td.total_days, gbd.total_bonus
            ORDER BY avg_participation_with_color DESC
            LIMIT 1
        )
        SELECT * FROM GradeStats
    """

def get_db_comparison_grade_goal_met():
    """Get grade with highest % who met goal at least 1 day"""
    return """
        WITH StudentGoals AS (
            SELECT
                r.grade_level,
                r.student_name,
                MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.grade_level, r.student_name
        ),
        GradeGoals AS (
            SELECT
                grade_level,
                ROUND(100.0 * SUM(met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct,
                SUM(met_goal) as students_who_met_goal,
                COUNT(*) as total_students
            FROM StudentGoals
            GROUP BY grade_level
            ORDER BY goal_met_pct DESC
            LIMIT 1
        )
        SELECT * FROM GradeGoals
    """

def get_db_comparison_grade_all_days_active(date_filter=None):
    """Get grade with highest % who logged every day"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        StudentDaysActive AS (
            SELECT
                r.grade_level,
                r.student_name,
                COUNT(DISTINCT dl.log_date) as days_active
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY r.grade_level, r.student_name
        ),
        GradeStats AS (
            SELECT
                r.grade_level,
                ROUND(100.0 * SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) /
                      NULLIF(COUNT(DISTINCT r.student_name), 0), 2) as all_days_active_pct,
                SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) as students_all_days,
                COUNT(DISTINCT r.student_name) as total_students,
                td.total_days
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN StudentDaysActive sda ON r.student_name = sda.student_name AND r.grade_level = sda.grade_level
            GROUP BY r.grade_level, td.total_days
            ORDER BY all_days_active_pct DESC
            LIMIT 1
        )
        SELECT * FROM GradeStats
    """

def get_db_comparison_grade_goal_met_all_days():
    """Get grade with highest % who met goal every day"""
    return """
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
        ),
        StudentGoalDays AS (
            SELECT
                r.grade_level,
                r.student_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.grade_level, r.student_name
        ),
        GradeStats AS (
            SELECT
                r.grade_level,
                ROUND(100.0 * SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) /
                      NULLIF(COUNT(DISTINCT r.student_name), 0), 2) as goal_met_all_days_pct,
                SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) as students_goal_all_days,
                COUNT(DISTINCT r.student_name) as total_students,
                td.total_days
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN StudentGoalDays sgd ON r.student_name = sgd.student_name AND r.grade_level = sgd.grade_level
            GROUP BY r.grade_level, td.total_days
            ORDER BY goal_met_all_days_pct DESC
            LIMIT 1
        )
        SELECT * FROM GradeStats
    """

def get_db_comparison_grade_color_war_points():
    """Get grade with most color war points"""
    return """
        WITH GradeParticipationPoints AS (
            SELECT
                r.grade_level,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            GROUP BY r.grade_level
        ),
        GradeBonusPoints AS (
            SELECT
                ci.grade_level,
                COALESCE(SUM(tcb.bonus_participation_points), 0) as bonus_points
            FROM Team_Color_Bonus tcb
            INNER JOIN Class_Info ci ON tcb.class_name = ci.class_name
            GROUP BY ci.grade_level
        ),
        GradeTotalPoints AS (
            SELECT
                gpp.grade_level,
                gpp.base_points + COALESCE(gbp.bonus_points, 0) as total_points,
                gpp.base_points,
                COALESCE(gbp.bonus_points, 0) as bonus_points
            FROM GradeParticipationPoints gpp
            LEFT JOIN GradeBonusPoints gbp ON gpp.grade_level = gbp.grade_level
            ORDER BY total_points DESC
            LIMIT 1
        )
        SELECT * FROM GradeTotalPoints
    """

# Additional Class-Level Comparison Queries

def get_db_comparison_class_sponsors():
    """Get class with most sponsors"""
    return """
        SELECT
            ci.class_name,
            ci.teacher_name,
            ci.grade_level,
            ci.team_name,
            COALESCE(SUM(rc.sponsors), 0) as total_sponsors
        FROM Class_Info ci
        LEFT JOIN Reader_Cumulative rc ON ci.teacher_name = rc.teacher_name
        GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name
        ORDER BY total_sponsors DESC
        LIMIT 1
    """

def get_db_comparison_class_participation(date_filter=None):
    """Get class with highest participation (≥1 day)"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        SELECT
            ci.class_name,
            ci.teacher_name,
            ci.grade_level,
            ci.team_name,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) * 100.0 /
                NULLIF(ci.total_students, 0) as participation_pct,
            COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.student_name END) as participating_count,
            ci.total_students as total_count
        FROM Class_Info ci
        LEFT JOIN Roster r ON ci.class_name = r.class_name
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE 1=1 {date_where}
        GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students
        ORDER BY participation_pct DESC
        LIMIT 1
    """

def get_db_comparison_class_avg_participation(date_filter=None):
    """Get class with highest average participation % with color bonus"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND dl.log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        ClassBonusData AS (
            SELECT
                class_name,
                SUM(bonus_participation_points) as total_bonus
            FROM Team_Color_Bonus
            GROUP BY class_name
        ),
        ClassStats AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                ci.total_students,
                td.total_days,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) as total_participations,
                COALESCE(cbd.total_bonus, 0) as color_bonus,
                ROUND(100.0 * (COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || r.student_name END) + COALESCE(cbd.total_bonus, 0)) /
                      (ci.total_students * td.total_days), 2) as avg_participation_with_color
            FROM Class_Info ci
            CROSS JOIN TotalDays td
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN ClassBonusData cbd ON ci.class_name = cbd.class_name
            WHERE td.total_days > 0 {date_where}
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students, td.total_days, cbd.total_bonus
            ORDER BY avg_participation_with_color DESC
            LIMIT 1
        )
        SELECT * FROM ClassStats
    """

def get_db_comparison_class_goal_met():
    """Get class with highest % who met goal at least 1 day"""
    return """
        WITH StudentGoals AS (
            SELECT
                r.class_name,
                r.student_name,
                MAX(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 ELSE 0 END) as met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.class_name, r.student_name
        ),
        ClassGoals AS (
            SELECT
                sg.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                ROUND(100.0 * SUM(sg.met_goal) / NULLIF(COUNT(*), 0), 2) as goal_met_pct,
                SUM(sg.met_goal) as students_who_met_goal,
                COUNT(*) as total_students
            FROM StudentGoals sg
            INNER JOIN Class_Info ci ON sg.class_name = ci.class_name
            GROUP BY sg.class_name, ci.teacher_name, ci.grade_level, ci.team_name
            ORDER BY goal_met_pct DESC
            LIMIT 1
        )
        SELECT * FROM ClassGoals
    """

def get_db_comparison_class_all_days_active(date_filter=None):
    """Get class with highest % who logged every day"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        StudentDaysActive AS (
            SELECT
                r.class_name,
                r.student_name,
                COUNT(DISTINCT dl.log_date) as days_active
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY r.class_name, r.student_name
        ),
        ClassStats AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                ROUND(100.0 * SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) /
                      NULLIF(ci.total_students, 0), 2) as all_days_active_pct,
                SUM(CASE WHEN sda.days_active = td.total_days THEN 1 ELSE 0 END) as students_all_days,
                ci.total_students,
                td.total_days
            FROM Class_Info ci
            CROSS JOIN TotalDays td
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN StudentDaysActive sda ON r.student_name = sda.student_name AND r.class_name = sda.class_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students, td.total_days
            ORDER BY all_days_active_pct DESC
            LIMIT 1
        )
        SELECT * FROM ClassStats
    """

def get_db_comparison_class_goal_met_all_days():
    """Get class with highest % who met goal every day"""
    return """
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
        ),
        StudentGoalDays AS (
            SELECT
                r.class_name,
                r.student_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.class_name, r.student_name
        ),
        ClassStats AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                ROUND(100.0 * SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) /
                      NULLIF(ci.total_students, 0), 2) as goal_met_all_days_pct,
                SUM(CASE WHEN sgd.days_met_goal = td.total_days THEN 1 ELSE 0 END) as students_goal_all_days,
                ci.total_students,
                td.total_days
            FROM Class_Info ci
            CROSS JOIN TotalDays td
            LEFT JOIN Roster r ON ci.class_name = r.class_name
            LEFT JOIN StudentGoalDays sgd ON r.student_name = sgd.student_name AND r.class_name = sgd.class_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level, ci.team_name, ci.total_students, td.total_days
            ORDER BY goal_met_all_days_pct DESC
            LIMIT 1
        )
        SELECT * FROM ClassStats
    """

def get_db_comparison_class_color_war_points():
    """Get class with most color war points"""
    return """
        WITH ClassParticipationPoints AS (
            SELECT
                r.class_name,
                COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END) as base_points
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            GROUP BY r.class_name
        ),
        ClassBonusPoints AS (
            SELECT
                class_name,
                COALESCE(SUM(bonus_participation_points), 0) as bonus_points
            FROM Team_Color_Bonus
            GROUP BY class_name
        ),
        ClassTotalPoints AS (
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                ci.team_name,
                cpp.base_points + COALESCE(cbp.bonus_points, 0) as total_points,
                cpp.base_points,
                COALESCE(cbp.bonus_points, 0) as bonus_points
            FROM Class_Info ci
            INNER JOIN ClassParticipationPoints cpp ON ci.class_name = cpp.class_name
            LEFT JOIN ClassBonusPoints cbp ON ci.class_name = cbp.class_name
            ORDER BY total_points DESC
            LIMIT 1
        )
        SELECT * FROM ClassTotalPoints
    """

# Additional Student-Level Comparison Queries

def get_db_comparison_student_top_participation(date_filter=None):
    """Get student with highest participation rate"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        StudentParticipation AS (
            SELECT
                r.student_name,
                r.class_name,
                r.teacher_name,
                r.grade_level,
                r.team_name,
                COUNT(DISTINCT dl.log_date) as days_active,
                ROUND(100.0 * COUNT(DISTINCT dl.log_date) / td.total_days, 2) as participation_pct
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name, td.total_days
            ORDER BY participation_pct DESC, days_active DESC
            LIMIT 1
        )
        SELECT * FROM StudentParticipation
    """

def get_db_comparison_student_goal_met():
    """Get student who met goal most days"""
    return """
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal,
            ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) /
                  NULLIF(COUNT(DISTINCT dl.log_date), 0), 2) as goal_met_pct
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
        WHERE dl.minutes_read > 0
        GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name, gr.min_daily_minutes
        ORDER BY days_met_goal DESC, goal_met_pct DESC
        LIMIT 1
    """

def get_db_comparison_student_all_days_active(date_filter=None):
    """Get students who logged every day (100% participation)"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
            WHERE 1=1 {date_where}
        ),
        StudentDaysActive AS (
            SELECT
                r.student_name,
                r.class_name,
                r.teacher_name,
                r.grade_level,
                r.team_name,
                COUNT(DISTINCT dl.log_date) as days_active,
                td.total_days
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            WHERE dl.minutes_read > 0 {date_where}
            GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name, td.total_days
            HAVING COUNT(DISTINCT dl.log_date) = td.total_days
            ORDER BY r.student_name
            LIMIT 1
        )
        SELECT * FROM StudentDaysActive
    """

def get_db_comparison_student_goal_met_all_days():
    """Get students who met goal every day"""
    return """
        WITH TotalDays AS (
            SELECT COUNT(DISTINCT log_date) as total_days
            FROM Daily_Logs
        ),
        StudentGoalDays AS (
            SELECT
                r.student_name,
                r.class_name,
                r.teacher_name,
                r.grade_level,
                r.team_name,
                COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal,
                td.total_days
            FROM Roster r
            CROSS JOIN TotalDays td
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name, td.total_days
            HAVING COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) = td.total_days
            ORDER BY r.student_name
            LIMIT 1
        )
        SELECT * FROM StudentGoalDays
    """

def get_db_comparison_student_color_war_points():
    """Get student with most color war points (participation days)"""
    return """
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            COUNT(DISTINCT dl.log_date) as total_points
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE dl.minutes_read > 0
        GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name
        ORDER BY total_points DESC
        LIMIT 1
    """

def get_db_comparison_student_avg_minutes_per_day(date_filter=None):
    """Get student with highest average minutes per day"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            ROUND(AVG(CASE WHEN dl.minutes_read > 120 THEN 120 ELSE dl.minutes_read END), 1) as avg_minutes_per_day,
            COUNT(DISTINCT dl.log_date) as days_active
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE dl.minutes_read > 0 {date_where}
        GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name
        HAVING COUNT(DISTINCT dl.log_date) >= 3
        ORDER BY avg_minutes_per_day DESC
        LIMIT 1
    """

def get_db_comparison_student_total_days(date_filter=None):
    """Get student with most days active"""
    date_where = ""
    if date_filter and date_filter != 'all':
        date_where = f"AND log_date <= '{date_filter}'"

    return f"""
        SELECT
            r.student_name,
            r.class_name,
            r.teacher_name,
            r.grade_level,
            r.team_name,
            COUNT(DISTINCT dl.log_date) as total_days
        FROM Roster r
        LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name
        WHERE dl.minutes_read > 0 {date_where}
        GROUP BY r.student_name, r.class_name, r.teacher_name, r.grade_level, r.team_name
        ORDER BY total_days DESC
        LIMIT 1
    """
