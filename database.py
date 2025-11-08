"""
Read-a-Thon Database Module
Handles SQLite database creation, initialization, and all data operations
"""

import sqlite3
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import random
from report_metadata import (
    COLUMN_METADATA,
    get_report_terms,
    generate_q21_analysis,
    generate_q22_analysis,
    generate_q23_analysis
)
from queries import *


class DatabaseRegistry:
    """
    Central registry for managing multiple read-a-thon databases.

    The registry database (readathon_registry.db) tracks all available databases,
    which one is active, and maintains summary statistics for each.
    """

    def __init__(self, registry_path: str = "db/readathon_registry.db"):
        """Initialize registry database connection"""
        self.registry_path = registry_path
        self.conn = sqlite3.connect(registry_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close registry database connection"""
        if self.conn:
            self.conn.close()

    def list_databases(self) -> List[Dict[str, Any]]:
        """
        Get all registered databases.

        Returns:
            List of database dictionaries with all fields
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT db_id, db_filename, display_name, year, description,
                   is_active, created_timestamp, student_count,
                   total_days, total_donations
            FROM Database_Registry
            ORDER BY year DESC, display_name ASC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'db_id': row['db_id'],
                'db_filename': row['db_filename'],
                'display_name': row['display_name'],
                'year': row['year'],
                'description': row['description'],
                'is_active': row['is_active'],
                'created_timestamp': row['created_timestamp'],
                'student_count': row['student_count'],
                'total_days': row['total_days'],
                'total_donations': row['total_donations']
            })

        return results

    def get_database(self, db_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single database by ID.

        Args:
            db_id: Database ID

        Returns:
            Database dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT db_id, db_filename, display_name, year, description,
                   is_active, created_timestamp, student_count,
                   total_days, total_donations
            FROM Database_Registry
            WHERE db_id = ?
        ''', (db_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'db_id': row['db_id'],
            'db_filename': row['db_filename'],
            'display_name': row['display_name'],
            'year': row['year'],
            'description': row['description'],
            'is_active': row['is_active'],
            'created_timestamp': row['created_timestamp'],
            'student_count': row['student_count'],
            'total_days': row['total_days'],
            'total_donations': row['total_donations']
        }

    def get_database_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get database by display_name or filename (case-insensitive).

        Args:
            name: Display name, filename, or special alias ("sample")

        Returns:
            Database dictionary or None if not found
        """
        cursor = self.conn.cursor()

        # Try exact match on display_name or filename (case-insensitive)
        cursor.execute('''
            SELECT db_id, db_filename, display_name, year, description,
                   is_active, created_timestamp, student_count,
                   total_days, total_donations
            FROM Database_Registry
            WHERE LOWER(display_name) = LOWER(?)
               OR db_filename = ?
        ''', (name, name))

        row = cursor.fetchone()
        if row:
            return {
                'db_id': row['db_id'],
                'db_filename': row['db_filename'],
                'display_name': row['display_name'],
                'year': row['year'],
                'description': row['description'],
                'is_active': row['is_active'],
                'created_timestamp': row['created_timestamp'],
                'student_count': row['student_count'],
                'total_days': row['total_days'],
                'total_donations': row['total_donations']
            }

        # Special case: "sample" alias matches any database with "sample" in display_name
        if name.lower() == 'sample':
            cursor.execute('''
                SELECT db_id, db_filename, display_name, year, description,
                       is_active, created_timestamp, student_count,
                       total_days, total_donations
                FROM Database_Registry
                WHERE LOWER(display_name) LIKE '%sample%'
                LIMIT 1
            ''')

            row = cursor.fetchone()
            if row:
                return {
                    'db_id': row['db_id'],
                    'db_filename': row['db_filename'],
                    'display_name': row['display_name'],
                    'year': row['year'],
                    'description': row['description'],
                    'is_active': row['is_active'],
                    'created_timestamp': row['created_timestamp'],
                    'student_count': row['student_count'],
                    'total_days': row['total_days'],
                    'total_donations': row['total_donations']
                }

        return None

    def get_active_database(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active database.

        Returns:
            Active database dictionary or None if no active database
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT db_id, db_filename, display_name, year, description,
                   is_active, created_timestamp, student_count,
                   total_days, total_donations
            FROM Database_Registry
            WHERE is_active = 1
            LIMIT 1
        ''')

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'db_id': row['db_id'],
            'db_filename': row['db_filename'],
            'display_name': row['display_name'],
            'year': row['year'],
            'description': row['description'],
            'is_active': row['is_active'],
            'created_timestamp': row['created_timestamp'],
            'student_count': row['student_count'],
            'total_days': row['total_days'],
            'total_donations': row['total_donations']
        }

    def set_active_database(self, db_id: int) -> Dict[str, Any]:
        """
        Set a database as active (deactivates all others).

        Args:
            db_id: Database ID to activate

        Returns:
            Result dictionary with success status
        """
        cursor = self.conn.cursor()

        # Check if database exists
        db = self.get_database(db_id)
        if not db:
            return {'success': False, 'error': f'Database ID {db_id} not found'}

        # Deactivate all databases
        cursor.execute('UPDATE Database_Registry SET is_active = 0')

        # Activate the specified database
        cursor.execute('UPDATE Database_Registry SET is_active = 1 WHERE db_id = ?', (db_id,))

        self.conn.commit()

        return {
            'success': True,
            'message': f'Activated database: {db["display_name"]}',
            'database': db
        }

    def register_database(self, filename: str, name: str, year: Optional[int],
                         description: str = '') -> int:
        """
        Register a new database in the registry.

        Args:
            filename: Database filename (e.g., "readathon_2026.db")
            name: Display name (e.g., "2026 Read-a-Thon")
            year: School year or None for non-year databases
            description: Optional description

        Returns:
            New database ID
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO Database_Registry
            (db_filename, display_name, year, description, is_active, created_timestamp,
             student_count, total_days, total_donations)
            VALUES (?, ?, ?, ?, 0, ?, 0, 0, 0.0)
        ''', (filename, name, year, description, datetime.now().isoformat()))

        self.conn.commit()

        return cursor.lastrowid

    def update_stats(self, db_id: int, student_count: int = None,
                    total_days: int = None, total_donations: float = None) -> Dict[str, Any]:
        """
        Update statistics for a database.

        Args:
            db_id: Database ID
            student_count: Number of students (optional)
            total_days: Number of contest days (optional)
            total_donations: Total fundraising amount (optional)

        Returns:
            Result dictionary with success status
        """
        cursor = self.conn.cursor()

        # Check if database exists
        db = self.get_database(db_id)
        if not db:
            return {'success': False, 'error': f'Database ID {db_id} not found'}

        # Build update query dynamically based on provided values
        updates = []
        values = []

        if student_count is not None:
            updates.append('student_count = ?')
            values.append(student_count)

        if total_days is not None:
            updates.append('total_days = ?')
            values.append(total_days)

        if total_donations is not None:
            updates.append('total_donations = ?')
            values.append(total_donations)

        if not updates:
            return {'success': True, 'message': 'No updates provided'}

        values.append(db_id)
        query = f"UPDATE Database_Registry SET {', '.join(updates)} WHERE db_id = ?"

        cursor.execute(query, values)
        self.conn.commit()

        return {'success': True, 'message': 'Statistics updated'}

    def recalculate_stats_from_file(self, db_id: int) -> Dict[str, Any]:
        """
        Recalculate statistics by querying the actual contest database file.

        This opens the contest database, queries Roster, Daily_Logs, and Reader_Cumulative,
        then updates the registry with the calculated values.

        Args:
            db_id: Database ID

        Returns:
            Result dictionary with success status and calculated values
        """
        # Get database info from registry
        db = self.get_database(db_id)
        if not db:
            return {'success': False, 'error': f'Database ID {db_id} not found'}

        db_path = f"db/{db['db_filename']}"

        try:
            # Open the contest database file
            contest_conn = sqlite3.connect(db_path)
            cursor = contest_conn.cursor()

            # Get student count from Roster
            cursor.execute("SELECT COUNT(*) FROM Roster")
            student_count = cursor.fetchone()[0]

            # Get total days from Daily_Logs
            cursor.execute("SELECT COUNT(DISTINCT log_date) FROM Daily_Logs")
            total_days = cursor.fetchone()[0]

            # Get total donations from Reader_Cumulative
            cursor.execute("SELECT COALESCE(SUM(donation_amount), 0.0) FROM Reader_Cumulative")
            total_donations = cursor.fetchone()[0]

            contest_conn.close()

            # Update registry with calculated values
            result = self.update_stats(db_id, student_count, total_days, total_donations)

            if result['success']:
                return {
                    'success': True,
                    'message': f'Statistics recalculated for {db["display_name"]}',
                    'student_count': student_count,
                    'total_days': total_days,
                    'total_donations': total_donations,
                    'display_name': db['display_name']
                }
            else:
                return result

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to recalculate stats: {str(e)}'
            }

    def delete_database(self, db_id: int) -> Dict[str, Any]:
        """
        Delete a database registration (does NOT delete the actual .db file).

        Args:
            db_id: Database ID

        Returns:
            Result dictionary with success status
        """
        cursor = self.conn.cursor()

        # Check if database exists
        db = self.get_database(db_id)
        if not db:
            return {'success': False, 'error': f'Database ID {db_id} not found'}

        # Don't allow deleting the active database
        if db['is_active']:
            return {'success': False, 'error': 'Cannot delete active database. Activate another database first.'}

        cursor.execute('DELETE FROM Database_Registry WHERE db_id = ?', (db_id,))
        self.conn.commit()

        return {
            'success': True,
            'message': f'Unregistered database: {db["display_name"]} (file not deleted)'
        }


class ReadathonDB:
    """Main database class for Read-a-Thon system"""

    def __init__(self, db_path: str = "readathon.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()

    def get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_database(self):
        """Create all tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Roster table
        cursor.execute(CREATE_TABLE_ROSTER)

        # Class_Info table
        cursor.execute(CREATE_TABLE_CLASS_INFO)

        # Grade_Rules table
        cursor.execute(CREATE_TABLE_GRADE_RULES)

        # Daily_Logs table (simplified - minutes only)
        cursor.execute(CREATE_TABLE_DAILY_LOGS)

        # Reader_Cumulative table - cumulative stats per student
        cursor.execute(CREATE_TABLE_READER_CUMULATIVE)

        # Upload_History table - tracks all uploads with audit trail
        cursor.execute(CREATE_TABLE_UPLOAD_HISTORY)

        # Add audit columns to existing Upload_History table if they don't exist
        cursor.execute(SELECT_TABLE_INFO)
        columns = [row[1] for row in cursor.fetchall()]

        if 'action_taken' not in columns:
            cursor.execute(ALTER_ADD_ACTION_TAKEN)

        if 'records_replaced' not in columns:
            cursor.execute(ALTER_ADD_RECORDS_REPLACED)

        if 'audit_details' not in columns:
            cursor.execute(ALTER_ADD_AUDIT_DETAILS)

        # Database_Metadata table - tracks year databases for multi-year support
        cursor.execute(CREATE_TABLE_DATABASE_METADATA)

        # Team_Color_Bonus table - tracks special team color day bonuses
        cursor.execute(CREATE_TABLE_TEAM_COLOR_BONUS)

        conn.commit()

    def load_roster_data(self, csv_data: str) -> int:
        """Load roster data from CSV string"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute(DELETE_ALL_ROSTER)

        reader = csv.DictReader(io.StringIO(csv_data))
        count = 0
        for row in reader:
            cursor.execute(INSERT_ROSTER,
                          (row['student_name'], row['class_name'], row['home_room'],
                           row['teacher_name'], row['grade_level'], row['team_name']))
            count += 1

        conn.commit()
        return count

    def load_class_info_data(self, csv_data: str) -> int:
        """Load class info data from CSV string"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute(DELETE_ALL_CLASS_INFO)

        reader = csv.DictReader(io.StringIO(csv_data))
        count = 0
        for row in reader:
            cursor.execute(INSERT_CLASS_INFO,
                          (row['class_name'], row['home_room'], row['teacher_name'],
                           row['grade_level'], row['team_name'], int(row['total_students'])))
            count += 1

        conn.commit()
        return count

    def load_grade_rules_data(self, csv_data: str) -> int:
        """Load grade rules data from CSV string"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute(DELETE_ALL_GRADE_RULES)

        reader = csv.DictReader(io.StringIO(csv_data))
        count = 0
        for row in reader:
            cursor.execute(INSERT_GRADE_RULES,
                          (row['grade_level'], int(row['min_daily_minutes']),
                           int(row['max_daily_minutes_credit'])))
            count += 1

        conn.commit()
        return count

    def load_team_color_bonus_data(self, csv_data: str, event_date: str) -> Dict[str, Any]:
        """Load Team Color Bonus data from CSV string

        CSV format: timestamp, class_name, team_name, grade_level, students_count
        Example: 10/16/2025 8:46:06, teacher1, team1, 1, 14

        Validation:
        - class_name must exist in Class_Info (case-insensitive, use lowercase teacher name)
        - team_name must match the team for that class (case-insensitive)
        - timestamp and grade_level are informational only
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Parse CSV (case-insensitive column matching)
        reader = csv.DictReader(io.StringIO(csv_data))

        # Normalize column names to lowercase for case-insensitive matching
        normalized_rows = []
        for row in reader:
            normalized_row = {k.strip().lower(): v for k, v in row.items()}
            normalized_rows.append(normalized_row)

        count = 0
        errors = []

        for row in normalized_rows:
            try:
                # Extract data from CSV (columns are now lowercase)
                csv_class_name = row.get('class_name', '').strip()
                csv_team_name = row.get('team_name', '').strip()
                students_count = int(row.get('students_count', 0))

                if not csv_class_name:
                    errors.append(f"Missing class_name in row: {row}")
                    continue

                if not csv_team_name:
                    errors.append(f"Missing team_name in row: {row}")
                    continue

                # Validate class_name exists in Class_Info (case-insensitive)
                cursor.execute(SELECT_CLASS_INFO_BY_NAME, (csv_class_name,))

                result = cursor.fetchone()
                if not result:
                    errors.append(f"Class not found: '{csv_class_name}'")
                    continue

                db_class_name = result[0]  # Use actual database case
                db_team_name = result[1]

                # Validate team_name matches (case-insensitive)
                if db_team_name.upper() != csv_team_name.upper():
                    errors.append(f"Team mismatch for '{csv_class_name}': CSV has '{csv_team_name}', database has '{db_team_name}'")
                    continue

                # Calculate bonus values
                bonus_minutes = students_count * 10
                bonus_participation = students_count * 1

                # Insert or replace the bonus data
                cursor.execute(INSERT_TEAM_COLOR_BONUS,
                              (event_date, db_class_name, students_count, bonus_minutes, bonus_participation))

                count += 1
            except ValueError as e:
                errors.append(f"Invalid students_count in row {row}: {str(e)}")
            except KeyError as e:
                errors.append(f"Missing required column {str(e)} in row: {row}")
            except Exception as e:
                errors.append(f"Error processing row {row}: {str(e)}")

        conn.commit()

        return {
            'success': len(errors) == 0,
            'count': count,
            'errors': errors
        }

    def check_existing_upload(self, log_date: str) -> Optional[Dict[str, Any]]:
        """Check if data already exists for this date"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(SELECT_EXISTING_UPLOAD, (log_date,))

        row = cursor.fetchone()
        if row:
            return {
                'timestamp': row[0],
                'filename': row[1],
                'students_affected': row[2]
            }
        return None

    def get_upload_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get upload history ordered by most recent first"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(SELECT_UPLOAD_HISTORY, (limit,))

        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def delete_day_data(self, log_date: str) -> Dict[str, Any]:
        """Delete all data for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if data exists
            cursor.execute(SELECT_COUNT_DAILY_LOGS_BY_DATE, (log_date,))
            count = cursor.fetchone()[0]

            if count == 0:
                return {
                    'success': False,
                    'error': f'No data found for date {log_date}'
                }

            # Get affected student names for audit trail
            cursor.execute(SELECT_DISTINCT_STUDENTS_BY_DATE, (log_date,))
            affected_students = [row[0] for row in cursor.fetchall()]

            # Delete from Daily_Logs
            cursor.execute(DELETE_DAY_DATA, (log_date,))

            # Delete from Upload_History
            cursor.execute(DELETE_UPLOAD_HISTORY_BY_DATE, (log_date,))

            conn.commit()

            return {
                'success': True,
                'deleted_records': count,
                'log_date': log_date,
                'affected_students': affected_students
            }
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def delete_cumulative_data(self) -> Dict[str, Any]:
        """Delete all cumulative data (donations, sponsors, cumulative minutes)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if data exists
            cursor.execute(SELECT_COUNT_READER_CUMULATIVE)
            count = cursor.fetchone()[0]

            if count == 0:
                return {
                    'success': False,
                    'error': 'No cumulative data found'
                }

            # Get affected student names for audit trail
            cursor.execute(SELECT_ALL_STUDENTS_READER_CUMULATIVE)
            affected_students = [row[0] for row in cursor.fetchall()]

            # Delete all cumulative data
            cursor.execute(DELETE_ALL_READER_CUMULATIVE)

            # Delete cumulative upload history
            cursor.execute(DELETE_UPLOAD_HISTORY_CUMULATIVE)

            conn.commit()

            return {
                'success': True,
                'deleted_records': count,
                'affected_students': affected_students
            }
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def delete_upload_history_batch(self, upload_ids: List[int]) -> Dict[str, Any]:
        """Delete multiple upload history records by their IDs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if not upload_ids:
                return {
                    'success': False,
                    'error': 'No upload IDs provided'
                }

            # Delete all specified upload history records
            delete_query = get_delete_upload_history_batch_query(upload_ids)
            cursor.execute(delete_query, tuple(upload_ids))

            deleted_count = cursor.rowcount

            conn.commit()

            return {
                'success': True,
                'deleted_count': deleted_count
            }
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def _detect_columns(self, csv_headers: List[str]) -> Dict[str, bool]:
        """
        Detect which columns are present in CSV (case-insensitive)
        Returns dict with boolean flags for each column type
        """
        headers_lower = [h.lower().strip() for h in csv_headers]

        return {
            'student_name': any(h in headers_lower for h in ['reader name', 'readername', 'student name', 'student_name', 'name']),
            'minutes': any(h in headers_lower for h in ['minutes', 'minutes read', 'minutes_read', 'cumulative minutes', 'cumulative_minutes']),
            'teacher': any(h in headers_lower for h in ['teacher', 'teacher name', 'teacher_name']),
            'raised': any(h in headers_lower for h in ['raised', 'donation amount', 'donation_amount', 'donations']),
            'sponsors': any(h in headers_lower for h in ['sponsors', 'sponsor count', 'sponsor_count'])
        }

    def upload_cumulative_stats(self, cumulative_file, confirmed: bool = False) -> Dict[str, Any]:
        """
        Upload cumulative stats from CSV file
        CSV columns: Reader Name, Teacher, Email (ignore), Raised, Sponsors, Sessions (ignore), PageCreated (ignore), Minutes
        Returns dict with success status, counts, and any errors
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        result = {
            'success': True,
            'rows_processed': 0,
            'students_matched': 0,
            'students_unmatched': 0,
            'errors': [],
            'warnings': [],
            'unmatched_names': []
        }

        try:
            # Read CSV file
            content = cumulative_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))

            # Validate columns before processing
            if not reader.fieldnames:
                result['success'] = False
                result['errors'].append('ERROR: CSV file is empty or has no headers')
                return result

            detected = self._detect_columns(reader.fieldnames)

            # Check for ALL mandatory cumulative columns
            missing = []
            if not detected['student_name']:
                missing.append('Reader Name (or Student Name/Name)')
            if not detected['teacher']:
                missing.append('Teacher')
            if not detected['raised']:
                missing.append('Raised (or Donation Amount/Donations)')
            if not detected['sponsors']:
                missing.append('Sponsors (or Sponsor Count)')
            if not detected['minutes']:
                missing.append('Minutes (or Cumulative Minutes)')

            if missing:
                result['success'] = False
                # Check if this is a daily file (has name + minutes, but missing Raised and Sponsors which are cumulative-only)
                if detected['student_name'] and detected['minutes'] and not detected['raised'] and not detected['sponsors']:
                    result['errors'].append(
                        'ERROR: This appears to be a daily minutes file (has Reader Name and Minutes, but missing Raised and Sponsors columns). '
                        'Please use the "Daily Minutes Upload" section instead.'
                    )
                else:
                    result['errors'].append(
                        f'ERROR: Missing required columns: {", ".join(missing)}'
                    )
                return result

            # Collect all data first - use dict to handle duplicates
            cumulative_data = {}
            duplicate_tracker = {}  # Track duplicates for warnings
            roster_checked = set()  # Track which students we've checked

            for row in reader:
                # Extract data from CSV (case-insensitive column matching)
                student_name = None
                teacher_name = None
                donation_amount = 0.0
                sponsors = 0
                cumulative_minutes = 0

                for key in row.keys():
                    if key.lower() in ['reader name', 'student_name', 'name']:
                        student_name = row[key].strip()
                    elif key.lower() in ['teacher', 'teacher_name']:
                        teacher_name = row[key].strip()
                    elif key.lower() in ['raised', 'donation_amount', 'donations']:
                        try:
                            donation_amount = float(row[key]) if row[key] else 0.0
                        except (ValueError, TypeError):
                            donation_amount = 0.0
                    elif key.lower() in ['sponsors', 'sponsor_count']:
                        try:
                            sponsors = int(row[key]) if row[key] else 0
                        except (ValueError, TypeError):
                            sponsors = 0
                    elif key.lower() in ['minutes', 'cumulative_minutes']:
                        try:
                            cumulative_minutes = int(row[key]) if row[key] else 0
                        except (ValueError, TypeError):
                            cumulative_minutes = 0

                if student_name:
                    result['rows_processed'] += 1

                    # Check for duplicates
                    if student_name in cumulative_data:
                        # Duplicate found - track it
                        if student_name not in duplicate_tracker:
                            # First duplicate - record original values
                            orig = cumulative_data[student_name]
                            duplicate_tracker[student_name] = [{
                                'donation': orig['donation_amount'],
                                'sponsors': orig['sponsors'],
                                'minutes': orig['cumulative_minutes']
                            }]
                        # Add current row's values
                        duplicate_tracker[student_name].append({
                            'donation': donation_amount,
                            'sponsors': sponsors,
                            'minutes': cumulative_minutes
                        })
                        # SUM the values (Option A - like daily upload)
                        cumulative_data[student_name]['donation_amount'] += donation_amount
                        cumulative_data[student_name]['sponsors'] += sponsors
                        cumulative_data[student_name]['cumulative_minutes'] += cumulative_minutes
                        # Keep the last teacher_name
                        cumulative_data[student_name]['teacher_name'] = teacher_name
                    else:
                        # First occurrence
                        cumulative_data[student_name] = {
                            'teacher_name': teacher_name,
                            'donation_amount': donation_amount,
                            'sponsors': sponsors,
                            'cumulative_minutes': cumulative_minutes,
                            'team_name': None  # Will be set below
                        }

                    # Lookup team_name from Roster (only once per student)
                    if student_name not in roster_checked:
                        roster_checked.add(student_name)
                        cursor.execute(SELECT_TEAM_NAME_FROM_ROSTER, (student_name,))
                        roster_row = cursor.fetchone()

                        if roster_row:
                            cumulative_data[student_name]['team_name'] = roster_row[0]
                            result['students_matched'] += 1
                        else:
                            cumulative_data[student_name]['team_name'] = "ERROR: NO ROSTER MATCH"
                            result['students_unmatched'] += 1
                            result['unmatched_names'].append(student_name)
                            result['warnings'].append(f"Student not found in roster (imported anyway): {student_name}")

            # Add warnings for duplicate students
            for student_name, occurrences in duplicate_tracker.items():
                # Calculate totals
                total_donation = sum(o['donation'] for o in occurrences)
                total_sponsors = sum(o['sponsors'] for o in occurrences)
                total_minutes = sum(o['minutes'] for o in occurrences)

                # Format lists for display
                donations_list = [f"${o['donation']:.2f}" for o in occurrences]
                sponsors_list = [o['sponsors'] for o in occurrences]
                minutes_list = [o['minutes'] for o in occurrences]

                result['warnings'].append(
                    f"Duplicate rows for {student_name}: found {len(occurrences)} rows with "
                    f"donations {donations_list}, sponsors {sponsors_list}, minutes {minutes_list}, "
                    f"summed to ${total_donation:.2f} donations, {total_sponsors} sponsors, {total_minutes} minutes"
                )

            # Get existing data before deletion for audit trail
            cursor.execute(SELECT_COUNT_READER_CUMULATIVE)
            existing_count = cursor.fetchone()[0]

            cursor.execute(SELECT_ALL_STUDENTS_READER_CUMULATIVE_SET)
            existing_students = set([row[0] for row in cursor.fetchall()])

            # Delete all existing data
            cursor.execute(DELETE_ALL_READER_CUMULATIVE)

            # Insert all new data
            upload_timestamp = datetime.now().isoformat()
            for student_name, data in cumulative_data.items():
                cursor.execute(INSERT_READER_CUMULATIVE,
                              (student_name, data['teacher_name'], data['team_name'],
                               data['donation_amount'], data['sponsors'], data['cumulative_minutes'], upload_timestamp))

            conn.commit()

            # Build audit details
            import json
            new_students = set(cumulative_data.keys())
            students_removed = existing_students - new_students
            students_added = new_students - existing_students
            students_updated = existing_students & new_students

            audit_details = {
                'previous_total': existing_count,
                'new_total': len(cumulative_data),
                'students_removed': len(students_removed),
                'students_added': len(students_added),
                'students_updated': len(students_updated)
            }

            # Add errors/warnings to audit
            if result['errors']:
                audit_details['errors'] = result['errors']
            if result['warnings']:
                audit_details['warnings'] = result['warnings']
            if result['unmatched_names']:
                audit_details['unmatched_count'] = len(result['unmatched_names'])

            # Determine status
            if result['students_unmatched'] > 0:
                status = 'warning'
            else:
                status = 'success'

            # Record upload in history
            cumulative_filename = cumulative_file.filename if cumulative_file else None
            action_taken = 'replaced' if existing_count > 0 else 'inserted'

            cursor.execute(INSERT_UPLOAD_HISTORY_CUMULATIVE,
                          (cumulative_filename, result['rows_processed'], result['students_matched'], status,
                           action_taken, existing_count, json.dumps(audit_details)))

            conn.commit()

        except Exception as e:
            result['success'] = False
            result['errors'].append(str(e))
            conn.rollback()

        return result

    def upload_daily_data(self, log_date: str, minutes_file, confirmed: bool = False) -> Dict[str, Any]:
        """
        Upload daily minutes data only - Always replaces existing data for the date
        Returns dict with success status, counts, and any errors
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        result = {
            'success': True,
            'minutes_processed': 0,
            'errors': [],
            'warnings': [],
            'info': [],
            'replaced_data': False,
            'records_replaced': 0,
            'audit_info': {}
        }

        try:
            # Check for existing data to track what will be replaced
            cursor.execute(SELECT_STUDENT_COUNT_DAILY_LOGS_BY_DATE, (log_date,))
            existing_row = cursor.fetchone()
            existing_count = existing_row[0] if existing_row else 0
            existing_students = existing_row[1].split(',') if existing_row and existing_row[1] else []

            if existing_count > 0:
                result['replaced_data'] = True
                result['records_replaced'] = existing_count
                result['audit_info']['replaced_students'] = existing_students
                result['info'].append(f"Replaced {existing_count} existing records for date {log_date}")

            # Continue with upload (no confirmation needed)
            # Process minutes file
            minutes_data = {}
            duplicate_tracker = {}  # Track duplicates: {student_name: [minutes1, minutes2, ...]}
            roster_checked = set()  # Track which students we've already checked against roster

            if minutes_file:
                content = minutes_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(content))

                # Validate columns before processing
                if not reader.fieldnames:
                    result['success'] = False
                    result['errors'].append('ERROR: CSV file is empty or has no headers')
                    return result

                detected = self._detect_columns(reader.fieldnames)

                # Check if this appears to be a cumulative file (has Raised AND Sponsors - the cumulative-only columns)
                if detected['raised'] and detected['sponsors']:
                    result['success'] = False
                    result['errors'].append(
                        'ERROR: This appears to be a cumulative stats file (contains Raised and Sponsors columns). '
                        'Please use the "Cumulative Stats Upload" section instead.'
                    )
                    return result

                # Check for mandatory daily columns
                if not detected['student_name']:
                    result['success'] = False
                    result['errors'].append('ERROR: Missing required column: Reader Name (or Student Name/Name)')
                    return result

                if not detected['minutes']:
                    result['success'] = False
                    result['errors'].append('ERROR: Missing required column: Minutes (or Minutes Read)')
                    return result

                for row in reader:
                    # Look for columns (case-insensitive)
                    student_name = None
                    minutes = None
                    teacher_name = None

                    for key in row.keys():
                        if key.lower() in ['reader name', 'readername', 'student name', 'student_name', 'name']:
                            student_name = row[key].strip() if row[key] else None
                        elif key.lower() in ['minutes', 'minutes_read']:
                            try:
                                minutes = int(row[key]) if row[key] else 0
                            except (ValueError, TypeError):
                                minutes = 0
                        elif key.lower() in ['teacher', 'teacher name', 'teacher_name']:
                            teacher_name = row[key].strip() if row[key] else None

                    # Detect empty rows (teacher present but no student data)
                    if teacher_name and not student_name:
                        result['warnings'].append(f"Empty record found for teacher {teacher_name} (no student or minutes data)")
                        continue

                    if student_name:
                        result['minutes_processed'] += 1

                        # Track if this is a duplicate
                        if student_name in minutes_data:
                            # Duplicate found - add to tracker
                            if student_name not in duplicate_tracker:
                                duplicate_tracker[student_name] = [minutes_data[student_name]]
                            duplicate_tracker[student_name].append(minutes)
                            # Sum the minutes (Option A)
                            minutes_data[student_name] = minutes_data[student_name] + minutes
                        else:
                            # First occurrence
                            minutes_data[student_name] = minutes

                        # Check if student exists in roster (only check once per student)
                        if student_name not in roster_checked:
                            roster_checked.add(student_name)
                            cursor.execute(SELECT_STUDENT_EXISTS_IN_ROSTER, (student_name,))
                            if not cursor.fetchone():
                                result['warnings'].append(f"Student not found in roster (imported anyway): {student_name}")

            # Add warnings for duplicate students
            for student_name, minutes_list in duplicate_tracker.items():
                total = sum(minutes_list)
                result['warnings'].append(f"Duplicate rows for {student_name}: found {len(minutes_list)} rows with minutes {minutes_list}, summed to {total}")

            # Insert data
            for student_name, minutes in minutes_data.items():
                # Insert or update
                cursor.execute(INSERT_DAILY_LOGS_UPSERT,
                              (log_date, student_name, minutes, minutes))

            conn.commit()

            # Determine status (info messages don't affect status)
            if len(result['warnings']) > 0:
                status = 'warning'
            else:
                status = 'success'

            # Build audit details
            import json
            audit_details = {}

            # Add errors/warnings/info to audit
            if result['errors']:
                audit_details['errors'] = result['errors']
            if result['warnings']:
                audit_details['warnings'] = result['warnings']
            if result['info']:
                audit_details['info'] = result['info']

            # Add replacement info to audit (no student names - only counts/statistics)
            if result['replaced_data']:
                audit_details['records_replaced'] = result['records_replaced']

            # Record upload in history
            upload_type = 'update' if confirmed else 'new'
            minutes_filename = minutes_file.filename if minutes_file else None
            total_students = len(minutes_data)
            action_taken = 'replaced' if existing_count > 0 else 'inserted'

            cursor.execute(INSERT_UPLOAD_HISTORY_DAILY,
                          (log_date, minutes_filename, result['minutes_processed'], total_students, upload_type, status, action_taken, existing_count, json.dumps(audit_details)))

            conn.commit()

        except Exception as e:
            result['success'] = False
            result['errors'].append(str(e))
            conn.rollback()

        return result

    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        counts = {}
        for table in ['Roster', 'Class_Info', 'Grade_Rules', 'Daily_Logs', 'Reader_Cumulative', 'Team_Color_Bonus']:
            cursor.execute(get_table_count_query(table))
            counts[table] = cursor.fetchone()[0]

        return counts

    def get_table_metadata(self, table_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific table.
        Returns table structure, column info, row count, relationships, etc.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table metadata definitions
        table_metadata = {
            'roster': {
                'table_name': 'Roster',
                'primary_key': 'student_name',
                'description': 'Student roster with class, teacher, grade, and team assignments for all participants.',
                'referenced_by': ['Daily_Logs', 'Reader_Cumulative'],
                'references': ['Class_Info'],
                'columns': [
                    {'name': 'student_name', 'description': 'Student full name (primary key)'},
                    {'name': 'class_name', 'description': 'Homeroom class ID'},
                    {'name': 'home_room', 'description': 'Home room identifier'},
                    {'name': 'teacher_name', 'description': 'Teacher name'},
                    {'name': 'grade_level', 'description': 'Grade level (K, 1, 2, 3, 4, 5)'},
                    {'name': 'team_name', 'description': 'Competition team assignment'},
                ]
            },
            'class_info': {
                'table_name': 'Class_Info',
                'primary_key': 'class_name',
                'description': 'Summary of each class including home room, teacher, grade, team, and total students.',
                'referenced_by': ['Roster'],
                'references': [],
                'columns': [
                    {'name': 'class_name', 'description': 'Homeroom class ID (primary key)'},
                    {'name': 'home_room', 'description': 'Home room identifier'},
                    {'name': 'teacher_name', 'description': 'Teacher name'},
                    {'name': 'grade_level', 'description': 'Grade level (K, 1, 2, 3, 4, 5)'},
                    {'name': 'team_name', 'description': 'Competition team assignment'},
                    {'name': 'total_students', 'description': 'Number of students in class'},
                ]
            },
            'grade_rules': {
                'table_name': 'Grade_Rules',
                'primary_key': 'grade_level',
                'description': 'Minimum and maximum daily reading minutes by grade level for goal calculations.',
                'referenced_by': [],
                'references': [],
                'columns': [
                    {'name': 'grade_level', 'description': 'Grade level (K, 1, 2, 3, 4, 5) (primary key)'},
                    {'name': 'min_minutes', 'description': 'Minimum daily reading goal in minutes'},
                    {'name': 'max_minutes', 'description': 'Maximum daily reading goal in minutes'},
                ]
            },
            'daily_logs': {
                'table_name': 'Daily_Logs',
                'primary_key': 'student_name, log_date',
                'description': 'Daily reading minutes for each student by date - tracks participation and goal achievement.',
                'referenced_by': [],
                'references': ['Roster'],
                'columns': [
                    {'name': 'student_name', 'description': 'Student full name (foreign key to Roster)'},
                    {'name': 'log_date', 'description': 'Date of reading log (YYYY-MM-DD format)'},
                    {'name': 'minutes_read', 'description': 'Minutes read on this date (uncapped)'},
                    {'name': 'capped_minutes', 'description': 'Minutes read (capped at 120 per day for official totals)'},
                    {'name': 'met_goal', 'description': 'Whether student met their daily reading goal (0 or 1)'},
                ]
            },
            'reader_cumulative': {
                'table_name': 'Reader_Cumulative',
                'primary_key': 'student_name',
                'description': 'Cumulative fundraising stats (donations, sponsors) and total minutes for each student.',
                'referenced_by': [],
                'references': ['Roster'],
                'columns': [
                    {'name': 'student_name', 'description': 'Student full name (foreign key to Roster)'},
                    {'name': 'total_donations', 'description': 'Total fundraising amount raised'},
                    {'name': 'num_sponsors', 'description': 'Number of sponsors supporting this student'},
                    {'name': 'total_minutes', 'description': 'Cumulative reading minutes (from Daily_Logs)'},
                ]
            },
            'team_color_bonus': {
                'table_name': 'Team_Color_Bonus',
                'primary_key': 'student_name, log_date',
                'description': 'Special event bonus: students wearing team colors earn extra participation points and bonus minutes.',
                'referenced_by': [],
                'references': ['Roster'],
                'columns': [
                    {'name': 'student_name', 'description': 'Student full name (foreign key to Roster)'},
                    {'name': 'log_date', 'description': 'Date of bonus event'},
                    {'name': 'wore_team_color', 'description': 'Whether student wore team colors (0 or 1)'},
                    {'name': 'bonus_minutes', 'description': 'Bonus minutes awarded (typically 10)'},
                    {'name': 'bonus_points', 'description': 'Bonus participation points awarded'},
                ]
            },
            'upload_history': {
                'table_name': 'Upload_History',
                'primary_key': 'upload_id',
                'description': 'Complete audit trail of all data uploads with timestamps, file details, and action history.',
                'referenced_by': [],
                'references': [],
                'columns': [
                    {'name': 'upload_id', 'description': 'Unique upload identifier (auto-increment)'},
                    {'name': 'upload_date', 'description': 'Timestamp of upload'},
                    {'name': 'file_name', 'description': 'Original CSV file name'},
                    {'name': 'file_type', 'description': 'Type of data (daily_reading, cumulative, etc.)'},
                    {'name': 'rows_processed', 'description': 'Number of rows processed from CSV'},
                    {'name': 'status', 'description': 'Upload status (success, error, etc.)'},
                    {'name': 'action_taken', 'description': 'Action performed (replace, update, skip)'},
                    {'name': 'records_replaced', 'description': 'Number of records replaced/updated'},
                    {'name': 'audit_details', 'description': 'Detailed audit information (JSON format)'},
                ]
            },
            'complete_log': {
                'table_name': 'Q7: Complete Log (Query)',
                'primary_key': 'N/A (Generated Query)',
                'description': 'Complete denormalized log combining Daily_Logs, Roster, and Reader_Cumulative - perfect for export to Excel/CSV.',
                'referenced_by': [],
                'references': ['Daily_Logs', 'Roster', 'Reader_Cumulative'],
                'columns': [
                    {'name': 'Various', 'description': 'Dynamic columns from joined tables - see Q7 report for full column list'},
                ]
            },
        }

        if table_id not in table_metadata:
            return {'error': f'Unknown table: {table_id}'}

        metadata = table_metadata[table_id].copy()

        # Get row count
        if table_id == 'complete_log':
            # Complete log is a query, not a table - get count from Daily_Logs
            cursor.execute("SELECT COUNT(*) FROM Daily_Logs")
        else:
            table_name_sql = metadata['table_name']
            cursor.execute(f"SELECT COUNT(*) FROM {table_name_sql}")
        metadata['row_count'] = cursor.fetchone()[0]

        # Get last updated timestamp (if applicable)
        last_updated = None
        if table_id == 'daily_logs':
            cursor.execute("SELECT MAX(log_date) FROM Daily_Logs")
            result = cursor.fetchone()[0]
            if result:
                last_updated = result
        elif table_id == 'upload_history':
            cursor.execute("SELECT MAX(upload_date) FROM Upload_History")
            result = cursor.fetchone()[0]
            if result:
                last_updated = result

        metadata['last_updated'] = last_updated

        return metadata

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)

        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_all_dates(self) -> List[str]:
        """Get all unique dates from Daily_Logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(SELECT_ALL_DATES)
        return [row[0] for row in cursor.fetchall()]

    # ========== Database Metadata Management (Phase 2: Multi-Database) ==========

    def list_databases(self) -> List[Dict[str, Any]]:
        """List all registered year databases"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(SELECT_DB_METADATA_ALL)

        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def register_database(self, year: int, db_filename: str, description: str = None) -> Dict[str, Any]:
        """Register a new year database in metadata table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if year already exists
            cursor.execute("SELECT db_id FROM Database_Metadata WHERE year = ?", (year,))
            if cursor.fetchone():
                return {
                    'success': False,
                    'error': f'Database for year {year} already registered'
                }

            # Insert new database record
            created_timestamp = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO Database_Metadata
                (year, db_filename, description, created_timestamp, is_active, student_count, total_days, total_donations)
                VALUES (?, ?, ?, ?, 0, 0, 0, 0.0)
            """, (year, db_filename, description, created_timestamp))

            conn.commit()

            db_id = cursor.lastrowid

            return {
                'success': True,
                'db_id': db_id,
                'year': year,
                'db_filename': db_filename
            }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def get_database_info(self, year: int) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific year database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
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
        """, (year,))

        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))

        return None

    def update_database_stats(self, year: int) -> Dict[str, Any]:
        """Update student_count, total_days, total_donations for a year database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get student count from Roster
            cursor.execute("SELECT COUNT(*) FROM Roster")
            student_count = cursor.fetchone()[0]

            # Get total days from Daily_Logs
            cursor.execute("SELECT COUNT(DISTINCT log_date) FROM Daily_Logs")
            total_days = cursor.fetchone()[0]

            # Get total donations from Reader_Cumulative
            cursor.execute("SELECT COALESCE(SUM(donation_amount), 0.0) FROM Reader_Cumulative")
            total_donations = cursor.fetchone()[0]

            # Update Database_Metadata
            cursor.execute("""
                UPDATE Database_Metadata
                SET student_count = ?,
                    total_days = ?,
                    total_donations = ?
                WHERE year = ?
            """, (student_count, total_days, total_donations, year))

            if cursor.rowcount == 0:
                return {
                    'success': False,
                    'error': f'Database for year {year} not found'
                }

            conn.commit()

            return {
                'success': True,
                'year': year,
                'student_count': student_count,
                'total_days': total_days,
                'total_donations': total_donations
            }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def set_active_database(self, year: int) -> Dict[str, Any]:
        """Mark a database as active (unmarks all others)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if year exists
            cursor.execute("SELECT db_id FROM Database_Metadata WHERE year = ?", (year,))
            if not cursor.fetchone():
                return {
                    'success': False,
                    'error': f'Database for year {year} not found'
                }

            # Unmark all databases
            cursor.execute("UPDATE Database_Metadata SET is_active = 0")

            # Mark the selected year as active
            cursor.execute("UPDATE Database_Metadata SET is_active = 1 WHERE year = ?", (year,))

            conn.commit()

            return {
                'success': True,
                'year': year,
                'message': f'Database for year {year} is now active'
            }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def get_active_database(self) -> Optional[Dict[str, Any]]:
        """Get the currently active database metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
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
        """)

        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))

        return None

    def delete_database_registration(self, year: int) -> Dict[str, Any]:
        """Delete database registration from metadata (does not delete actual .db file)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if year exists
            cursor.execute("SELECT db_id, is_active FROM Database_Metadata WHERE year = ?", (year,))
            row = cursor.fetchone()

            if not row:
                return {
                    'success': False,
                    'error': f'Database for year {year} not found'
                }

            if row[1] == 1:  # is_active
                return {
                    'success': False,
                    'error': f'Cannot delete active database. Switch to another year first.'
                }

            # Delete the registration
            cursor.execute("DELETE FROM Database_Metadata WHERE year = ?", (year,))

            conn.commit()

            return {
                'success': True,
                'year': year,
                'message': f'Database registration for year {year} deleted'
            }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    # ========== Students Page Methods ==========

    def get_students_data(self, date_filter: str = 'all', grade_filter: str = 'all',
                          team_filter: str = 'all') -> List[Dict[str, Any]]:
        """
        Get all students with their aggregate data for the Students page table.

        Args:
            date_filter: 'all' or specific date (cumulative through date)
            grade_filter: 'all' or grade level ('K', '1st', '2nd', '3rd', '4th', '5th')
            team_filter: 'all' or team name

        Returns:
            List of dicts with 13 columns per student:
            - student_name, grade_level, team_name, class_name, teacher_name
            - fundraising, sponsors
            - minutes_capped, minutes_uncapped
            - days_participated, participation_pct
            - days_met_goal, goal_met_pct
        """
        # Build WHERE clauses
        date_where = ""
        date_where_no_alias = ""
        grade_where = ""
        team_where = ""

        if date_filter != 'all':
            date_where = f"AND dl.log_date <= '{date_filter}'"
            date_where_no_alias = f"AND log_date <= '{date_filter}'"

        if grade_filter != 'all':
            grade_where = f"AND r.grade_level = '{grade_filter}'"

        if team_filter != 'all':
            team_where = f"AND r.team_name = '{team_filter}'"

        # Get query from queries.py
        query = get_students_master_query(date_where, date_where_no_alias, grade_where, team_where)

        # Execute and return results
        return self.execute_query(query)

    def get_student_detail(self, student_name: str, date_filter: str = 'all') -> Dict[str, Any]:
        """
        Get individual student detail with summary metrics and daily breakdown.

        Args:
            student_name: Name of student
            date_filter: 'all' or specific date (cumulative through date)

        Returns:
            Dict with:
            - summary: Student summary metrics (fundraising, minutes, sponsors, etc.)
            - daily: List of daily log entries
        """
        # Build WHERE clause for date filter
        date_where = ""
        if date_filter != 'all':
            date_where = f"AND dl.log_date <= '{date_filter}'"

        # Get queries from queries.py
        summary_query, daily_query = get_student_detail_query(date_where)

        # Execute summary query
        summary_results = self.execute_query(summary_query, (student_name,))
        summary = summary_results[0] if summary_results else None

        # Execute daily query
        daily_results = self.execute_query(daily_query, (student_name,))

        return {
            'summary': summary,
            'daily': daily_results
        }

    def get_students_school_winners(self, date_filter: str = 'all') -> Dict[str, float]:
        """
        Get school-wide max values for each metric (gold highlights).

        Args:
            date_filter: 'all' or specific date (cumulative through date)

        Returns:
            Dict mapping metric name to max value:
            {
                'fundraising': 1250.0,
                'sponsors': 15,
                'minutes_capped': 720,
                'minutes_uncapped': 850,
                'days_participated': 6,
                'days_met_goal': 6
            }
        """
        # Build WHERE clause for date filter
        date_where = ""
        if date_filter != 'all':
            date_where = f"AND dl.log_date <= '{date_filter}'"

        # Get query from queries.py
        query = get_students_school_winners_query(date_where)

        # Execute query
        results = self.execute_query(query)

        # Convert to dict
        winners = {}
        for row in results:
            winners[row['metric']] = row['max_value']

        return winners

    def get_students_banner(self, date_filter: str = 'all', grade_filter: str = 'all',
                           team_filter: str = 'all') -> Dict[str, Any]:
        """
        Get banner metrics for Students page (6 metrics matching School/Teams/Grade pages).

        Args:
            date_filter: 'all' or specific date (cumulative through date)
            grade_filter: 'all' or grade level
            team_filter: 'all' or team name

        Returns:
            Dict with:
            - campaign_days: Current day number (date-aware)
            - total_contest_days: Total days in contest
            - total_fundraising: Sum of fundraising for filtered students
            - total_minutes: Sum of capped minutes for filtered students
            - total_sponsors: Sum of sponsors for filtered students
            - avg_participation_pct: Avg. participation % (can exceed 100% with color)
            - goal_met_pct: % of students who met goal ≥1 day
            - total_students: Number of students in filtered group
        """
        # Build WHERE clauses
        date_where = ""
        date_where_no_alias = ""
        grade_where = ""
        team_where = ""

        if date_filter != 'all':
            date_where = f"AND dl.log_date <= '{date_filter}'"
            date_where_no_alias = f"AND log_date <= '{date_filter}'"

        if grade_filter != 'all':
            grade_where = f"AND r.grade_level = '{grade_filter}'"

        if team_filter != 'all':
            team_where = f"AND r.team_name = '{team_filter}'"

        # Get query from queries.py
        query = get_students_banner_query(date_where, date_where_no_alias, grade_where, team_where)

        # Execute query
        results = self.execute_query(query)

        return results[0] if results else {}

    def get_students_grade_winners(self, date_filter: str = 'all') -> Dict[str, Dict[str, float]]:
        """
        Get grade-level winners for all grades (silver highlights when viewing all grades).

        Used when grade_filter == 'all' AND team_filter == 'all' to show grade-level leaders.

        Args:
            date_filter: 'all' or specific date (cumulative through date)

        Returns:
            Dict mapping grade_level -> Dict[metric_name -> max_value]
            Example: {'K': {'fundraising': 100, 'minutes_capped': 500, ...}, '1': {...}, ...}
        """
        date_where = f"AND dl.log_date <= '{date_filter}'" if date_filter != 'all' else ""

        query = f"""
        -- Get max values for each metric within each grade
        SELECT
            r.grade_level,
            'fundraising' as metric,
            MAX(COALESCE(rc.donation_amount, 0)) as max_value
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.grade_level

        UNION ALL

        SELECT
            r.grade_level,
            'sponsors' as metric,
            MAX(COALESCE(rc.sponsors, 0)) as max_value
        FROM Roster r
        LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        GROUP BY r.grade_level

        UNION ALL

        SELECT grade_level, 'minutes_capped' as metric, MAX(total_capped) as max_value
        FROM (
            SELECT r.grade_level, COALESCE(SUM(MIN(dl.minutes_read, 120)), 0) as total_capped
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY r.grade_level, r.student_name
        )
        GROUP BY grade_level

        UNION ALL

        SELECT grade_level, 'minutes_uncapped' as metric, MAX(total_uncapped) as max_value
        FROM (
            SELECT r.grade_level, COALESCE(SUM(dl.minutes_read), 0) as total_uncapped
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY r.grade_level, r.student_name
        )
        GROUP BY grade_level

        UNION ALL

        SELECT grade_level, 'days_participated' as metric, MAX(days_participated) as max_value
        FROM (
            SELECT r.grade_level, COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) as days_participated
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY r.grade_level, r.student_name
        )
        GROUP BY grade_level

        UNION ALL

        SELECT grade_level, 'participation_pct' as metric, MAX(participation_pct) as max_value
        FROM (
            SELECT
                r.grade_level,
                CASE
                    WHEN (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE 1=1 {date_where}) > 0
                    THEN ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) / (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE 1=1 {date_where}), 1)
                    ELSE 0
                END as participation_pct
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            GROUP BY r.grade_level, r.student_name
        )
        GROUP BY grade_level

        UNION ALL

        SELECT grade_level, 'days_met_goal' as metric, MAX(days_met_goal) as max_value
        FROM (
            SELECT r.grade_level, COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) as days_met_goal
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.grade_level, r.student_name
        )
        GROUP BY grade_level

        UNION ALL

        SELECT grade_level, 'goal_met_pct' as metric, MAX(goal_met_pct) as max_value
        FROM (
            SELECT
                r.grade_level,
                CASE
                    WHEN COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END) > 0
                    THEN ROUND(100.0 * COUNT(CASE WHEN dl.minutes_read >= gr.min_daily_minutes THEN 1 END) / COUNT(CASE WHEN dl.minutes_read > 0 THEN 1 END), 1)
                    ELSE 0
                END as goal_met_pct
            FROM Roster r
            LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name {date_where}
            LEFT JOIN Grade_Rules gr ON r.grade_level = gr.grade_level
            GROUP BY r.grade_level, r.student_name
        )
        GROUP BY grade_level
        """

        results = self.execute_query(query)

        # Organize by grade -> metric -> value
        grade_winners = {}
        for row in results:
            grade = row['grade_level']
            metric = row['metric']
            value = row['max_value']

            if grade not in grade_winners:
                grade_winners[grade] = {}
            grade_winners[grade][metric] = value

        return grade_winners

    def get_students_filtered_winners(self, date_filter: str = 'all', grade_filter: str = 'all',
                                     team_filter: str = 'all') -> Dict[str, float]:
        """
        Get winners within the current filter group (silver highlights).

        Only used when grade_filter != 'all' OR team_filter != 'all'.
        Returns max values for each metric within the filtered group.

        Args:
            date_filter: 'all' or specific date (cumulative through date)
            grade_filter: 'all' or grade level
            team_filter: 'all' or team name

        Returns:
            Dict mapping metric name to max value (same format as get_students_school_winners)
        """
        # Build WHERE clauses
        date_where = ""
        grade_where = ""
        team_where = ""

        if date_filter != 'all':
            date_where = f"AND dl.log_date <= '{date_filter}'"

        if grade_filter != 'all':
            grade_where = f"AND r.grade_level = '{grade_filter}'"

        if team_filter != 'all':
            team_where = f"AND r.team_name = '{team_filter}'"

        # Get query from queries.py
        query = get_students_filtered_winners_query(date_where, grade_where, team_where)

        # Execute query
        results = self.execute_query(query)

        # Convert to dict
        winners = {}
        for row in results:
            winners[row['metric']] = row['max_value']

        return winners

    def export_all_tables(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Export all database tables for ZIP backup.
        Returns a dictionary with table names as keys and lists of row dicts as values.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # All 7 tables to export (Database_Registry excluded - separate database file)
        tables = [
            'Roster',
            'Class_Info',
            'Grade_Rules',
            'Daily_Logs',
            'Reader_Cumulative',
            'Upload_History',
            'Team_Color_Bonus'
        ]

        export_data = {}

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            # Convert sqlite3.Row objects to dictionaries
            export_data[table] = [dict(row) for row in rows]

        return export_data

    def get_export_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current database for export README.
        Returns counts, timestamps, and other useful context.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get table counts
        counts = {}
        for table in ['Roster', 'Class_Info', 'Grade_Rules', 'Daily_Logs',
                      'Reader_Cumulative', 'Upload_History', 'Team_Color_Bonus']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]

        # Get date range from Daily_Logs
        cursor.execute("SELECT MIN(log_date), MAX(log_date) FROM Daily_Logs")
        date_row = cursor.fetchone()
        date_range = {
            'min_date': date_row[0] if date_row[0] else 'N/A',
            'max_date': date_row[1] if date_row[1] else 'N/A'
        }

        # Get last upload timestamp
        cursor.execute("SELECT MAX(upload_timestamp) FROM Upload_History")
        last_upload = cursor.fetchone()[0] or 'N/A'

        # Get totals
        cursor.execute("SELECT SUM(donation_amount), SUM(sponsors) FROM Reader_Cumulative")
        totals_row = cursor.fetchone()
        totals = {
            'total_donations': totals_row[0] if totals_row[0] else 0.0,
            'total_sponsors': totals_row[1] if totals_row[1] else 0
        }

        # Get total minutes (capped)
        cursor.execute("""
            SELECT SUM(CASE
                WHEN minutes_read > 120 THEN 120
                ELSE minutes_read
            END) as total_capped_minutes
            FROM Daily_Logs
        """)
        total_minutes = cursor.fetchone()[0] or 0

        return {
            'counts': counts,
            'date_range': date_range,
            'last_upload': last_upload,
            'totals': totals,
            'total_minutes': total_minutes,
            'export_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database_path': self.db_path
        }


# Report generation functions
class ReportGenerator:
    """Generates all Read-a-Thon reports"""

    def __init__(self, db: ReadathonDB):
        self.db = db

    def _get_last_upload_timestamps(self) -> str:
        """Get formatted last upload timestamps for metadata"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get latest daily upload
        cursor.execute("""
            SELECT MAX(upload_timestamp), log_date
            FROM Upload_History
            WHERE log_date IS NOT NULL
            ORDER BY upload_timestamp DESC
            LIMIT 1
        """)
        daily_row = cursor.fetchone()

        # Get latest cumulative upload
        cursor.execute("""
            SELECT MAX(upload_timestamp)
            FROM Upload_History
            WHERE log_date IS NULL
            ORDER BY upload_timestamp DESC
            LIMIT 1
        """)
        cumulative_row = cursor.fetchone()

        parts = []
        if daily_row and daily_row[0]:
            parts.append(f"Daily Logs ({daily_row[1]}: {daily_row[0][:16]})")
        if cumulative_row and cumulative_row[0]:
            parts.append(f"Reader Cumulative ({cumulative_row[0][:16]})")

        return ', '.join(parts) if parts else 'Not available'

    def _get_report_timestamp(self) -> str:
        """Get current timestamp for report generation"""
        return f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    def q1_table_counts(self) -> Dict[str, Any]:
        """Q1: Total Row Count - utility report"""
        counts = self.db.get_table_counts()

        results = []
        for table, count in counts.items():
            results.append({'table_name': table, 'row_count': count})

        return {
            'title': 'Q1: Table Row Counts',
            'description': 'Utility report showing row counts in each table',
            'columns': ['table_name', 'row_count'],
            'data': results,
            'sort': 'table_name (asc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'All database tables (system query)',
                'columns': COLUMN_METADATA['q1'],
                'terms': get_report_terms('q1')
            }
        }

    def q2_daily_summary(self, log_date: Optional[str] = None, group_by: str = 'class') -> Dict[str, Any]:
        """Q2: Daily Summary Report"""

        date_filter = ""
        params = []
        if log_date:
            date_filter = "AND dl.log_date = ?"
            # Date filter is used twice in the query (StudentGoalCounts CTE and main SELECT)
            params.append(log_date)
            params.append(log_date)

        # Get total days for the filtered date range
        if log_date:
            # For single date, days is always 1
            days_subquery = "SELECT 1 as total_days"
        else:
            # For all dates, count distinct dates
            days_subquery = "SELECT COUNT(DISTINCT log_date) as total_days FROM Daily_Logs"

        if group_by.lower() == 'class':
            query = f"""
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
        else:  # by team
            query = f"""
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

        results = self.db.execute_query(query, tuple(params))

        date_display = log_date if log_date else "All Dates"

        return {
            'title': f'Q2: Daily Summary Report - {date_display}',
            'description': f'Comprehensive daily summary grouped by {group_by}',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'sort': f'{group_by}_name (asc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Class_Info, Grade_Rules',
                'columns': COLUMN_METADATA['q2'],
                'terms': get_report_terms('q2')
            }
        }

    def q3_reader_cumulative_enhanced(self) -> Dict[str, Any]:
        """Q3: Reader Cumulative - Enhanced with class, grade, and participation details"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q3: Reader Cumulative - Enhanced Student Details',
            'description': 'Complete cumulative stats with class, teacher, team, grade, and participation metrics',
            'columns': ['student_name', 'class_name', 'grade_level', 'teacher_name', 'team_name',
                       'days_participated', 'days_met_goal', 'cumulative_minutes', 'donation_amount', 'sponsors'],
            'data': results,
            'sort': 'cumulative_minutes (desc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Reader_Cumulative, Roster, Daily_Logs, Grade_Rules',
                'columns': COLUMN_METADATA['q3'],
                'terms': get_report_terms('q3')
            }
        }

    def q4_prize_drawing(self, log_date: str) -> Dict[str, Any]:
        """Q4/Slide 4: Prize Drawing Entrants - Daily random selection"""

        # Get all students who met their daily reading goal on this date
        query = """
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

        participants = self.db.execute_query(query, (log_date,))

        # Group by grade
        by_grade = {}
        for p in participants:
            grade = p['grade_level']
            if grade not in by_grade:
                by_grade[grade] = []
            by_grade[grade].append(p)

        # Select one winner per grade
        winners = []
        for grade in sorted(by_grade.keys()):
            if by_grade[grade]:
                winner = random.choice(by_grade[grade])
                winner['total_eligible'] = len(by_grade[grade])
                winners.append(winner)

        return {
            'title': f'Q4/Slide 4: Prize Drawing Winners - {log_date}',
            'description': 'Random selection of one winner per grade from students who met their daily reading goal',
            'columns': ['grade_level', 'student_name', 'class_name', 'teacher_name', 'minutes_read', 'min_daily_minutes', 'total_eligible'],
            'data': winners,
            'sort': 'grade_level (asc)',
            'note': 'Winners are randomly selected each time this report runs',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Grade_Rules',
                'columns': COLUMN_METADATA['q4'],
                'terms': get_report_terms('q4')
            }
        }

    def q5_student_cumulative(self, sort_by: str = 'minutes', limit: int = None) -> Dict[str, Any]:
        """Q5: Student Cumulative Report (Top Readers, Goal Getters, Top Fundraisers)"""

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
            title_suffix = "Top Readers"
        elif sort_by.lower() in ['goal', 'goals', 'goal getters']:
            query += " ORDER BY days_met_goal DESC, total_minutes_credited DESC, r.student_name ASC"
            title_suffix = "Goal Getters"
        elif sort_by.lower() in ['donations', 'fundraisers']:
            query += " ORDER BY total_donations DESC, r.student_name ASC"
            title_suffix = "Top Fundraisers"
        else:
            query += " ORDER BY total_minutes_credited DESC, r.student_name ASC"
            title_suffix = "All Students"

        if limit:
            query += f" LIMIT {limit}"

        results = self.db.execute_query(query)

        return {
            'title': f'Q5: Student Cumulative Report - {title_suffix}',
            'description': 'Cumulative student performance - participation from Daily_Logs, fundraising from Reader_Cumulative',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'sort': f'{sort_by} (desc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Grade_Rules, Reader_Cumulative',
                'columns': COLUMN_METADATA['q5'],
                'terms': get_report_terms('q5')
            }
        }

    def q6_class_participation(self) -> Dict[str, Any]:
        """Q6: Class Participation Winner - Cumulative"""

        query = """
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

        results = self.db.execute_query(query)

        # Find winners (handle ties) - use WITH COLOR version
        winners = []
        if results:
            max_rate = results[0]['avg_participation_rate_with_color']
            for row in results:
                if row['avg_participation_rate_with_color'] == max_rate:
                    winners.append(row)
                else:
                    break

        return {
            'title': 'Q6: Class Participation Winner (Cumulative)',
            'description': 'Classes ranked by average daily participation rate WITH team color bonus. Winner determined by avg_participation_rate_with_color.',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'winners': winners,
            'sort': 'avg_participation_rate_with_color (desc)',
            'note': 'Tie-breaking: All classes with the highest rate (with color bonus) are listed as winners',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Class_Info, Daily_Logs, Team_Color_Bonus',
                'columns': COLUMN_METADATA['q6'],
                'terms': get_report_terms('q6')
            }
        }

    def q7_complete_log(self, log_date: Optional[str] = None) -> Dict[str, Any]:
        """Q7: Complete Log - Denormalized export table (daily minutes only)"""

        date_filter = ""
        params = []
        if log_date:
            date_filter = "WHERE dl.log_date = ?"
            params.append(log_date)

        query = f"""
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

        results = self.db.execute_query(query, tuple(params))

        date_display = log_date if log_date else "All Dates"

        return {
            'title': f'Q7: Complete Log - {date_display}',
            'description': 'Fully denormalized daily minutes log for export (donations available in Reader_Cumulative table)',
            'columns': ['log_date', 'student_name', 'minutes_read', 'class_name', 'home_room', 'teacher_name', 'grade_level', 'team_name'],
            'data': results,
            'sort': 'log_date (desc), team_name (asc), class_name (asc), student_name (asc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Daily_Logs, Roster',
                'columns': COLUMN_METADATA['q7'],
                'terms': get_report_terms('q7')
            }
        }

    def q14_team_participation(self) -> Dict[str, Any]:
        """Q14/Slide 3: Team Participation Winner - Cumulative"""

        query = """
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

        results = self.db.execute_query(query)

        # Find winners (handle ties) - use WITH COLOR version
        winners = []
        if results:
            max_rate = results[0]['avg_participation_rate_with_color']
            for row in results:
                if row['avg_participation_rate_with_color'] == max_rate:
                    winners.append(row)

        return {
            'title': 'Q14/Slide 3: Team Participation Winner (Cumulative)',
            'description': 'Teams ranked by average daily participation rate WITH team color bonus. Winner (losing captain dresses in costume) determined by avg_participation_rate_with_color.',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'winners': winners,
            'sort': 'avg_participation_rate_with_color (desc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Class_Info, Team_Color_Bonus',
                'columns': COLUMN_METADATA['q14'],
                'terms': get_report_terms('q14')
            }
        }

    def q18_lead_class_by_grade(self) -> Dict[str, Any]:
        """Q18/Slide 2: Lead Class by Grade - Cumulative"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q18/Slide 2: Leading Class by Grade (Cumulative)',
            'description': 'Leading class in each grade by average daily participation rate WITH team color bonus. Winner per grade determined by avg_participation_rate_with_color.',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'sort': 'grade_level (asc)',
            'note': 'Ties are shown when multiple classes have the same max participation rate (with color bonus)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Class_Info, Daily_Logs, Team_Color_Bonus',
                'columns': COLUMN_METADATA['q18'],
                'terms': get_report_terms('q18')
            }
        }

    def q19_team_minutes(self) -> Dict[str, Any]:
        """Q19/Slide 5: Cumulative Team Minutes"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q19/Slide 5: Cumulative Team Minutes',
            'description': '''Total cumulative minutes read by each team with and without Team Color Bonus.

Calculation Rules:<br>
• Data Source: Daily_Logs table (contains only valid contest period data)<br>
• Daily Cap: 120 minutes per student per day (all grade levels)<br>
• Formula: SUM(MIN(dl.minutes_read, 120)) per team<br>
• Team Color Bonus: +10 minutes per participating student from color day event<br>
• Note: Using Daily_Logs ensures grade-based caps are respected and data is limited to the contest period (Reader_Cumulative table includes all data)''',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'sort': 'total_minutes_with_color (desc), with TOTAL row at bottom',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Team_Color_Bonus, Class_Info',
                'columns': COLUMN_METADATA['q19'],
                'terms': get_report_terms('q19')
            }
        }

    def q20_team_donations(self) -> Dict[str, Any]:
        """Q20/Slide 6: Cumulative Team Donations"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q20/Slide 6: Cumulative Team Donations',
            'description': 'Total donations and sponsors by each team (from Reader_Cumulative)',
            'columns': ['team_name', 'total_donations', 'total_sponsors', 'total_students', 'avg_donation_per_student'],
            'data': results,
            'sort': 'total_donations (desc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Reader_Cumulative',
                'columns': COLUMN_METADATA['q20'],
                'terms': get_report_terms('q20')
            }
        }

    def q21_minutes_integrity_check(self) -> Dict[str, Any]:
        """Q21: Data Sync & Minutes Integrity Check - Verify students are synced and daily minutes match cumulative"""

        # Get actual date range from Daily_Logs for dynamic display
        date_range_query = """
            SELECT
                MIN(log_date) as min_date,
                MAX(log_date) as max_date
            FROM Daily_Logs
        """
        date_result = self.db.execute_query(date_range_query)

        # Format dates as MM/DD
        date_range = None
        if date_result and date_result[0]['min_date'] and date_result[0]['max_date']:
            from datetime import datetime
            min_date = datetime.strptime(date_result[0]['min_date'], '%Y-%m-%d')
            max_date = datetime.strptime(date_result[0]['max_date'], '%Y-%m-%d')
            date_range = f"{min_date.month}/{min_date.day}-{max_date.month}/{max_date.day}"

        query = """
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

        results = self.db.execute_query(query)

        # Count issues
        issues = [r for r in results if r['status'] != 'OK']
        ok_count = len([r for r in results if r['status'] == 'OK'])

        note = f"Found {len(issues)} discrepancies and {ok_count} matching records"

        return {
            'title': 'Q21: Data Sync & Minutes Integrity Check',
            'description': 'Verify students are synced between Daily_Logs and Reader_Cumulative, and that daily minutes totals match cumulative minutes',
            'columns': ['student_name', 'team_name', 'class_name', 'daily_minutes_sum', 'cumulative_minutes', 'difference', 'status'],
            'data': results,
            'sort': 'status (priority), difference (desc)',
            'note': note,

            # Enhanced metadata
            'last_updated': self._get_last_upload_timestamps(),
            'metadata': {
                'source_tables': 'Daily_Logs, Reader_Cumulative (primary) • Roster (reference)',
                'columns': COLUMN_METADATA['q21'],
                'terms': get_report_terms('q21')
            },
            'analysis': generate_q21_analysis(results, date_range=date_range)
        }

    def q8_student_reading_details(self) -> Dict[str, Any]:
        """Q8: Individual Student Reading Details - Students with any reading activity"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q8: Individual Student Reading Details',
            'description': 'All students who have done any reading, with total minutes and days met goal',
            'columns': ['student_name', 'class_name', 'teacher_name', 'grade_level', 'team_name', 'total_minutes_read', 'days_met_goal', 'days_participated'],
            'data': results,
            'sort': 'total_minutes_read (desc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Grade_Rules',
                'columns': COLUMN_METADATA['q8'],
                'terms': get_report_terms('q8')
            }
        }

    def q22_student_name_sync_check(self) -> Dict[str, Any]:
        """Q22: Student Name Sync Check - Verify students with reading minutes are synced between Daily_Logs and Reader_Cumulative"""

        query = """
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

        results = self.db.execute_query(query)

        # Count issues
        issues_count = len(results)
        in_daily_only = len([r for r in results if r['status'] == 'IN_DAILY_ONLY'])
        in_cumulative_only = len([r for r in results if r['status'] == 'IN_CUMULATIVE_ONLY'])

        if issues_count == 0:
            note = "All students with reading minutes are properly synced between Daily_Logs and Reader_Cumulative"
        else:
            note = f"Found {issues_count} reading sync issues: {in_daily_only} in Daily_Logs only, {in_cumulative_only} in Reader_Cumulative only (Note: Students with donations but no reading minutes are excluded from this check)"

        return {
            'title': 'Q22: Student Name Sync Check (Reading Minutes)',
            'description': 'Verify students with reading minutes are synced between Daily_Logs and Reader_Cumulative (excludes donation-only students)',
            'columns': ['student_name', 'status', 'in_daily_logs', 'in_reader_cumulative'],
            'data': results,
            'sort': 'status (priority)',
            'note': note,
            'has_issues': issues_count > 0,

            # Enhanced metadata
            'last_updated': self._get_last_upload_timestamps(),
            'metadata': {
                'source_tables': 'Daily_Logs, Reader_Cumulative (primary)',
                'columns': COLUMN_METADATA['q22'],
                'terms': get_report_terms('q22')
            },
            'analysis': generate_q22_analysis(results)
        }

    def q23_roster_integrity_check(self) -> Dict[str, Any]:
        """Q23: Roster Integrity Check - Verify all students in Daily_Logs and Reader_Cumulative exist in Roster"""

        query = """
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

        results = self.db.execute_query(query)

        # Count issues
        issues_count = len(results)

        if issues_count == 0:
            note = "All students in Daily_Logs and Reader_Cumulative exist in Roster"
        else:
            note = f"Found {issues_count} students in Daily_Logs or Reader_Cumulative who are missing from Roster"

        return {
            'title': 'Q23: Roster Integrity Check',
            'description': 'Verify all students in Daily_Logs and Reader_Cumulative exist in Roster',
            'columns': ['student_name', 'found_in_table', 'status'],
            'data': results,
            'sort': 'student_name (asc)',
            'note': note,
            'has_issues': issues_count > 0,

            # Enhanced metadata
            'last_updated': self._get_last_upload_timestamps(),
            'metadata': {
                'source_tables': 'Daily_Logs, Reader_Cumulative, Roster',
                'columns': COLUMN_METADATA['q23'],
                'terms': get_report_terms('q23')
            },
            'analysis': generate_q23_analysis(results)
        }

    def q24_database_metadata(self) -> Dict[str, Any]:
        """Q24: Database_Registry - Multi-Year Database Registry"""
        # Query the central registry database (separate from contest databases)
        registry = DatabaseRegistry()
        databases = registry.list_databases()

        # Format results for report display
        results = []
        for db in databases:
            results.append([
                db['db_id'],
                db['year'],
                db['db_filename'],
                db['description'],
                db['created_timestamp'],
                'ACTIVE' if db['is_active'] else 'INACTIVE',
                db['student_count'],
                db['total_days'],
                db['total_donations']
            ])

        return {
            'title': 'Q24: Database_Registry - Multi-Year Database Registry',
            'description': 'All registered databases with year, filename, active status, and summary statistics (from central registry database)',
            'columns': ['db_id', 'year', 'db_filename', 'description', 'created_timestamp', 'status',
                       'student_count', 'total_days', 'total_donations'],
            'data': results,
            'sort': 'year (desc)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Database_Registry (db/readathon_registry.db - separate database file)',
                'columns': {
                    'db_id': 'Unique database identifier (auto-increment)',
                    'year': 'School year for this database',
                    'db_filename': 'Database filename (e.g., readathon_2026.db)',
                    'description': 'Optional description of database',
                    'created_timestamp': 'When database was registered',
                    'status': 'ACTIVE or INACTIVE',
                    'student_count': 'Number of students in Roster',
                    'total_days': 'Number of reading days recorded',
                    'total_donations': 'Total fundraising dollars'
                },
                'terms': {
                    'Active Database': 'The currently selected database in use',
                    'Registry': 'Central table in separate database tracking all year databases',
                    'Multi-Year': 'System supports managing multiple school years'
                }
            }
        }

    def q9_most_donations_by_grade(self) -> Dict[str, Any]:
        """Q9: Most Donations by Grade - Per Grade Level (1 winner per grade)"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q9: Most Donations Per Grade Level',
            'description': 'Student with highest donation amount in each grade (1 winner per grade, ties shown)',
            'columns': ['grade_level', 'student_name', 'donation_amount', 'sponsors', 'team_name', 'class_name'],
            'data': results,
            'sort': 'grade_level (asc)',
            'note': 'Prize: Book Store $25 Gift Card per grade level',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Reader_Cumulative',
                'columns': COLUMN_METADATA['q9'],
                'terms': get_report_terms('q9')
            }
        }

    def q10_most_minutes_by_grade(self) -> Dict[str, Any]:
        """Q10: Most Minutes Read by Grade - Per Grade Level (1 winner per grade)"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q10: Most Minutes Read Per Grade Level',
            'description': 'Student with most capped minutes in each grade (1 winner per grade, ties shown)',
            'columns': ['grade_level', 'student_name', 'total_minutes_capped', 'days_participated', 'team_name', 'class_name'],
            'data': results,
            'sort': 'grade_level (asc)',
            'note': 'Prize: Grandpa Joe\'s $25 Gift Card per grade level. Uses 120-minute daily cap.',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs',
                'columns': COLUMN_METADATA['q10'],
                'terms': get_report_terms('q10')
            }
        }

    def q11_most_sponsors_by_grade(self) -> Dict[str, Any]:
        """Q11: Most Sponsors by Grade - Per Grade Level (1 winner per grade)"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q11: Most Sponsors Per Grade Level',
            'description': 'Student with most sponsors in each grade (1 winner per grade, ties shown)',
            'columns': ['grade_level', 'student_name', 'sponsor_count', 'donation_amount', 'team_name', 'class_name'],
            'data': results,
            'sort': 'grade_level (asc)',
            'note': 'Prize: Learning Express $25 Gift Card per grade level',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Reader_Cumulative',
                'columns': COLUMN_METADATA['q11'],
                'terms': get_report_terms('q11')
            }
        }

    def q12_best_class_by_grade_simplified(self) -> Dict[str, Any]:
        """Q12: Best Class Per Grade - Simplified (1 winner per grade)"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q12: Best Class Per Grade (Simplified)',
            'description': 'Leading class in each grade by participation rate WITH team color bonus (1 winner per grade, ties shown). Winner determined by avg_participation_rate_with_color.',
            'columns': list(results[0].keys()) if results else [],
            'data': results,
            'sort': 'grade_level (asc)',
            'note': 'Prize: Classroom party/activity per grade level',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Class_Info, Daily_Logs, Team_Color_Bonus',
                'columns': COLUMN_METADATA['q12'],
                'terms': get_report_terms('q12')
            }
        }

    def q13_overall_best_class_simplified(self) -> Dict[str, Any]:
        """Q13: Overall Best Class in School - Simplified (1 winner school-wide)"""

        query = """
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

        results = self.db.execute_query(query)

        # Get only the winner(s) - handle ties - use WITH COLOR version
        winners = []
        if results:
            max_rate = results[0]['avg_participation_rate_with_color']
            for row in results:
                if row['avg_participation_rate_with_color'] == max_rate:
                    winners.append(row)
                else:
                    break

        return {
            'title': 'Q13: Best Class in School (Simplified)',
            'description': 'Overall best classroom by participation rate WITH team color bonus (1 winner school-wide, ties shown). Winner determined by avg_participation_rate_with_color.',
            'columns': list(winners[0].keys()) if winners else [],
            'data': winners,
            'sort': 'avg_participation_rate_with_color (desc)',
            'note': 'Prize: $100 for the teacher',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Class_Info, Daily_Logs, Team_Color_Bonus',
                'columns': COLUMN_METADATA['q13'],
                'terms': get_report_terms('q13')
            }
        }

    def q15_goal_getters(self) -> Dict[str, Any]:
        """Q15: Goal Getters - All Students Who Met Goal Every Day (All qualifying students)"""

        query = """
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

        results = self.db.execute_query(query)

        # Get total days for note
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT log_date) FROM Daily_Logs")
        total_days = cursor.fetchone()[0]

        return {
            'title': 'Q15: Goal Getters - All Qualifying Students',
            'description': f'Students who met their grade\'s daily reading goal for ALL {total_days} days of the contest',
            'columns': ['student_name', 'grade_level', 'days_met_goal', 'total_days', 'team_name', 'class_name'],
            'data': results,
            'sort': 'grade_level (asc), student_name (asc)',
            'note': 'Prize: Books (varies by grade level)',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Daily_Logs, Grade_Rules',
                'columns': COLUMN_METADATA['q15'],
                'terms': get_report_terms('q15')
            }
        }

    def q16_top_earner_per_team(self) -> Dict[str, Any]:
        """Q16: Top Earner Per Team (1 winner per team, 2 total)"""

        query = """
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

        results = self.db.execute_query(query)

        return {
            'title': 'Q16: Top Earner Per Team',
            'description': 'Student with highest donation amount on each team (1 winner per team, ties shown)',
            'columns': ['team_name', 'student_name', 'donation_amount', 'sponsors', 'grade_level', 'class_name'],
            'data': results,
            'sort': 'team_name (asc)',
            'note': 'Prize: Principal for a day / Librarian for a day',
            'last_updated': self._get_report_timestamp(),
            'metadata': {
                'source_tables': 'Roster, Reader_Cumulative',
                'columns': COLUMN_METADATA['q16'],
                'terms': get_report_terms('q16')
            }
        }

    def _format_tied_winners(self, winners: List[Dict], name_field: str = 'student_name') -> Dict[str, Any]:
        """
        Format a list of tied winners into a display string and metadata.

        Args:
            winners: List of winner dicts from query results
            name_field: Field name containing the winner's name (default: 'student_name')

        Returns:
            Dict with:
            - names: Formatted string like "Alice, Bob, Charlie and 10 others"
            - tie_count: Number of tied winners
            - grade_context: "Grade X" or "Various" if multiple grades
        """
        if not winners:
            return {
                'names': 'N/A',
                'tie_count': 0,
                'grade_context': ''
            }

        # Format names (show first 3, then "and X others")
        if len(winners) <= 3:
            names = ", ".join([w[name_field] for w in winners])
        else:
            names = ", ".join([w[name_field] for w in winners[:3]]) + f" and {len(winners) - 3} others"

        # Determine grade context
        grades = set([w.get('grade_level', '') for w in winners if w.get('grade_level')])
        if len(grades) == 1:
            grade_context = f"Grade {winners[0].get('grade_level', '')}"
        else:
            grade_context = "Various"

        return {
            'names': names,
            'tie_count': len(winners),
            'grade_context': grade_context
        }

    def get_database_comparison(self, db1_filename: str, db2_filename: str, filter_period: str = 'all') -> Dict[str, Any]:
        """
        Compare two databases and return comparison data for all metrics and entity levels.

        Args:
            db1_filename: Filename of first database (e.g., 'readathon_2025.db')
            db2_filename: Filename of second database (e.g., 'readathon_2024.db')
            filter_period: Date filter ('all' or specific date like '2025-10-15')

        Returns:
            Dict containing comparison results with structure:
            {
                'db1_info': {...},
                'db2_info': {...},
                'comparisons': [
                    {
                        'entity_level': 'School',
                        'metric': 'Fundraising',
                        'db1_value': {...},
                        'db2_value': {...},
                        'change': {...},
                        'winner': 'db1' or 'db2' or 'tie'
                    },
                    ...
                ]
            }
        """
        from queries import (
            QUERY_DB_REGISTRY_LIST,
            get_db_comparison_school_fundraising,
            get_db_comparison_school_minutes,
            get_db_comparison_school_sponsors,
            get_db_comparison_school_participation,
            get_db_comparison_school_size,
            get_db_comparison_school_avg_participation,
            get_db_comparison_school_goal_met,
            get_db_comparison_school_all_days_active,
            get_db_comparison_school_goal_met_all_days,
            get_db_comparison_school_color_war_points,
            get_db_comparison_student_top_fundraiser,
            get_db_comparison_student_top_reader,
            get_db_comparison_student_top_sponsors,
            get_db_comparison_student_top_participation,
            get_db_comparison_student_goal_met,
            get_db_comparison_student_all_days_active,
            get_db_comparison_student_goal_met_all_days,
            get_db_comparison_student_avg_minutes_per_day,
            get_db_comparison_student_total_days,
            get_db_comparison_team_top,
            get_db_comparison_team_sponsors,
            get_db_comparison_team_participation,
            get_db_comparison_team_avg_participation,
            get_db_comparison_team_goal_met,
            get_db_comparison_team_all_days_active,
            get_db_comparison_team_goal_met_all_days,
            get_db_comparison_team_color_war_points,
            get_db_comparison_grade_top,
            get_db_comparison_grade_sponsors,
            get_db_comparison_grade_participation,
            get_db_comparison_grade_avg_participation,
            get_db_comparison_grade_goal_met,
            get_db_comparison_grade_all_days_active,
            get_db_comparison_grade_goal_met_all_days,
            get_db_comparison_grade_color_war_points,
            get_db_comparison_class_top,
            get_db_comparison_class_sponsors,
            get_db_comparison_class_participation,
            get_db_comparison_class_avg_participation,
            get_db_comparison_class_goal_met,
            get_db_comparison_class_all_days_active,
            get_db_comparison_class_goal_met_all_days,
            get_db_comparison_class_color_war_points
        )

        # Get database registry for metadata
        registry = DatabaseRegistry()
        db1_info = registry.get_database_by_name(db1_filename)
        db2_info = registry.get_database_by_name(db2_filename)

        # Connect to both databases
        db1 = ReadathonDB(f'db/{db1_filename}')
        db2 = ReadathonDB(f'db/{db2_filename}')

        comparisons = []

        # Helper function to calculate change
        def calc_change(val1, val2):
            if val2 == 0:
                if val1 > 0:
                    return {'absolute': val1, 'percent': None, 'direction': 'up'}
                return {'absolute': 0, 'percent': 0, 'direction': 'neutral'}

            absolute_change = val1 - val2
            percent_change = (absolute_change / val2) * 100
            direction = 'up' if absolute_change > 0 else ('down' if absolute_change < 0 else 'neutral')

            return {
                'absolute': absolute_change,
                'percent': percent_change,
                'direction': direction
            }

        # School-level comparisons
        # School - Fundraising
        db1_school_fundraising = db1.execute_query(get_db_comparison_school_fundraising(filter_period))[0]
        db2_school_fundraising = db2.execute_query(get_db_comparison_school_fundraising(filter_period))[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Fundraising',
            'honors_filter': False,
            'db1_value': {
                'value': db1_school_fundraising['total_fundraising'],
                'context': f"Top class: {db1_school_fundraising['class_name']} (Grade {db1_school_fundraising['grade_level']}, {db1_school_fundraising['team_name']})"
            },
            'db2_value': {
                'value': db2_school_fundraising['total_fundraising'],
                'context': f"Top class: {db2_school_fundraising['class_name']} (Grade {db2_school_fundraising['grade_level']}, {db2_school_fundraising['team_name']})"
            },
            'change': calc_change(db1_school_fundraising['total_fundraising'], db2_school_fundraising['total_fundraising']),
            'winner': 'db1' if db1_school_fundraising['total_fundraising'] > db2_school_fundraising['total_fundraising'] else ('db2' if db1_school_fundraising['total_fundraising'] < db2_school_fundraising['total_fundraising'] else 'tie'),
            'format': 'currency'
        })

        # School - Minutes
        db1_school_minutes = db1.execute_query(get_db_comparison_school_minutes(filter_period))[0]
        db2_school_minutes = db2.execute_query(get_db_comparison_school_minutes(filter_period))[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Minutes Read',
            'honors_filter': True,
            'db1_value': {
                'value': db1_school_minutes['total_minutes'],
                'context': f"Top class: {db1_school_minutes['class_name']} (Grade {db1_school_minutes['grade_level']}, {db1_school_minutes['team_name']})"
            },
            'db2_value': {
                'value': db2_school_minutes['total_minutes'],
                'context': f"Top class: {db2_school_minutes['class_name']} (Grade {db2_school_minutes['grade_level']}, {db2_school_minutes['team_name']})"
            },
            'change': calc_change(db1_school_minutes['total_minutes'], db2_school_minutes['total_minutes']),
            'winner': 'db1' if db1_school_minutes['total_minutes'] > db2_school_minutes['total_minutes'] else ('db2' if db1_school_minutes['total_minutes'] < db2_school_minutes['total_minutes'] else 'tie'),
            'format': 'minutes'
        })

        # School - Sponsors
        db1_school_sponsors = db1.execute_query(get_db_comparison_school_sponsors())[0]
        db2_school_sponsors = db2.execute_query(get_db_comparison_school_sponsors())[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Sponsors',
            'honors_filter': False,
            'db1_value': {
                'value': db1_school_sponsors['total_sponsors'],
                'context': f"Top class: {db1_school_sponsors['class_name']} (Grade {db1_school_sponsors['grade_level']}, {db1_school_sponsors['team_name']})"
            },
            'db2_value': {
                'value': db2_school_sponsors['total_sponsors'],
                'context': f"Top class: {db2_school_sponsors['class_name']} (Grade {db2_school_sponsors['grade_level']}, {db2_school_sponsors['team_name']})"
            },
            'change': calc_change(db1_school_sponsors['total_sponsors'], db2_school_sponsors['total_sponsors']),
            'winner': 'db1' if db1_school_sponsors['total_sponsors'] > db2_school_sponsors['total_sponsors'] else ('db2' if db1_school_sponsors['total_sponsors'] < db2_school_sponsors['total_sponsors'] else 'tie'),
            'format': 'number'
        })

        # School - Participation
        db1_school_participation = db1.execute_query(get_db_comparison_school_participation(filter_period))[0]
        db2_school_participation = db2.execute_query(get_db_comparison_school_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Total Participating (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_school_participation['participation_pct'],
                'context': f"{db1_school_participation['participating_count']}/{db1_school_participation['total_count']} students"
            },
            'db2_value': {
                'value': db2_school_participation['participation_pct'],
                'context': f"{db2_school_participation['participating_count']}/{db2_school_participation['total_count']} students"
            },
            'change': calc_change(db1_school_participation['participation_pct'], db2_school_participation['participation_pct']),
            'winner': 'db1' if db1_school_participation['participation_pct'] > db2_school_participation['participation_pct'] else ('db2' if db1_school_participation['participation_pct'] < db2_school_participation['participation_pct'] else 'tie'),
            'format': 'percentage'
        })

        # School - Size
        db1_school_size = db1.execute_query(get_db_comparison_school_size())[0]
        db2_school_size = db2.execute_query(get_db_comparison_school_size())[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'School Size',
            'honors_filter': False,
            'db1_value': {
                'value': db1_school_size['student_count'],
                'context': f"({db1_school_size['class_count']} classes)"
            },
            'db2_value': {
                'value': db2_school_size['student_count'],
                'context': f"({db2_school_size['class_count']} classes)"
            },
            'change': calc_change(db1_school_size['student_count'], db2_school_size['student_count']),
            'winner': 'db1' if db1_school_size['student_count'] > db2_school_size['student_count'] else ('db2' if db1_school_size['student_count'] < db2_school_size['student_count'] else 'tie'),
            'format': 'number'
        })

        # Student-level comparisons
        # Student - Fundraising
        db1_student_fundraising_list = db1.execute_query(get_db_comparison_student_top_fundraiser())
        db2_student_fundraising_list = db2.execute_query(get_db_comparison_student_top_fundraiser())

        db1_fundraising_fmt = self._format_tied_winners(db1_student_fundraising_list)
        db2_fundraising_fmt = self._format_tied_winners(db2_student_fundraising_list)

        db1_fundraising_value = db1_student_fundraising_list[0]['fundraising'] if db1_student_fundraising_list else 0
        db2_fundraising_value = db2_student_fundraising_list[0]['fundraising'] if db2_student_fundraising_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Fundraising',
            'honors_filter': False,
            'db1_value': {
                'value': db1_fundraising_value,
                'winner_name': db1_fundraising_fmt['names'],
                'tie_count': db1_fundraising_fmt['tie_count'],
                'context': db1_fundraising_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_fundraising_value,
                'winner_name': db2_fundraising_fmt['names'],
                'tie_count': db2_fundraising_fmt['tie_count'],
                'context': db2_fundraising_fmt['grade_context']
            },
            'change': calc_change(db1_fundraising_value, db2_fundraising_value),
            'winner': 'db1' if db1_fundraising_value > db2_fundraising_value else ('db2' if db1_fundraising_value < db2_fundraising_value else 'tie'),
            'format': 'currency'
        })

        # Student - Minutes
        db1_student_minutes_list = db1.execute_query(get_db_comparison_student_top_reader(filter_period))
        db2_student_minutes_list = db2.execute_query(get_db_comparison_student_top_reader(filter_period))

        db1_minutes_fmt = self._format_tied_winners(db1_student_minutes_list)
        db2_minutes_fmt = self._format_tied_winners(db2_student_minutes_list)

        db1_minutes_value = db1_student_minutes_list[0]['total_minutes'] if db1_student_minutes_list else 0
        db2_minutes_value = db2_student_minutes_list[0]['total_minutes'] if db2_student_minutes_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Minutes Read',
            'honors_filter': True,
            'db1_value': {
                'value': db1_minutes_value,
                'winner_name': db1_minutes_fmt['names'],
                'tie_count': db1_minutes_fmt['tie_count'],
                'context': db1_minutes_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_minutes_value,
                'winner_name': db2_minutes_fmt['names'],
                'tie_count': db2_minutes_fmt['tie_count'],
                'context': db2_minutes_fmt['grade_context']
            },
            'change': calc_change(db1_minutes_value, db2_minutes_value),
            'winner': 'db1' if db1_minutes_value > db2_minutes_value else ('db2' if db1_minutes_value < db2_minutes_value else 'tie'),
            'format': 'minutes'
        })

        # Student - Sponsors
        db1_student_sponsors_list = db1.execute_query(get_db_comparison_student_top_sponsors())
        db2_student_sponsors_list = db2.execute_query(get_db_comparison_student_top_sponsors())

        db1_sponsors_fmt = self._format_tied_winners(db1_student_sponsors_list)
        db2_sponsors_fmt = self._format_tied_winners(db2_student_sponsors_list)

        db1_sponsors_value = db1_student_sponsors_list[0]['sponsor_count'] if db1_student_sponsors_list else 0
        db2_sponsors_value = db2_student_sponsors_list[0]['sponsor_count'] if db2_student_sponsors_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Sponsors',
            'honors_filter': False,
            'db1_value': {
                'value': db1_sponsors_value,
                'winner_name': db1_sponsors_fmt['names'],
                'tie_count': db1_sponsors_fmt['tie_count'],
                'context': db1_sponsors_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_sponsors_value,
                'winner_name': db2_sponsors_fmt['names'],
                'tie_count': db2_sponsors_fmt['tie_count'],
                'context': db2_sponsors_fmt['grade_context']
            },
            'change': calc_change(db1_sponsors_value, db2_sponsors_value),
            'winner': 'db1' if db1_sponsors_value > db2_sponsors_value else ('db2' if db1_sponsors_value < db2_sponsors_value else 'tie'),
            'format': 'number'
        })

        # Team-level comparisons
        # Note: Only fundraising, minutes, and size are implemented in queries.py
        team_metrics = [
            ('fundraising', 'Fundraising', False, 'currency'),
            ('minutes', 'Minutes Read', True, 'minutes'),
            ('size', 'Team Size', False, 'number')
        ]

        for metric_key, metric_name, honors_filter, format_type in team_metrics:
            # Get all tied winners for tie counting
            db1_team_list = db1.execute_query(get_db_comparison_team_top(metric_key, filter_period if honors_filter else None))
            db2_team_list = db2.execute_query(get_db_comparison_team_top(metric_key, filter_period if honors_filter else None))

            # Count ties and pick first winner
            db1_tie_count = len(db1_team_list)
            db2_tie_count = len(db2_team_list)
            db1_team = db1_team_list[0] if db1_team_list else {}
            db2_team = db2_team_list[0] if db2_team_list else {}

            # Determine the value field name based on metric
            value_field = f'total_{metric_key}' if metric_key != 'size' else 'student_count'

            # For size metric, context is different (no class_name returned)
            if metric_key == 'size':
                db1_context = f"({db1_team['class_count']} classes)" if db1_team else "N/A"
                db2_context = f"({db2_team['class_count']} classes)" if db2_team else "N/A"
            else:
                db1_context = f"Top class: {db1_team['class_name']} (Grade {db1_team['grade_level']})" if db1_team else "N/A"
                db2_context = f"Top class: {db2_team['class_name']} (Grade {db2_team['grade_level']})" if db2_team else "N/A"

            comparisons.append({
                'entity_level': 'Team',
                'metric': metric_name,
                'honors_filter': honors_filter,
                'db1_value': {
                    'value': db1_team.get(value_field, 0),
                    'winner_name': db1_team.get('team_name', 'N/A'),
                    'tie_count': db1_tie_count,
                    'context': db1_context
                },
                'db2_value': {
                    'value': db2_team.get(value_field, 0),
                    'winner_name': db2_team.get('team_name', 'N/A'),
                    'tie_count': db2_tie_count,
                    'context': db2_context
                },
                'change': calc_change(db1_team.get(value_field, 0), db2_team.get(value_field, 0)),
                'winner': 'db1' if db1_team.get(value_field, 0) > db2_team.get(value_field, 0) else ('db2' if db1_team.get(value_field, 0) < db2_team.get(value_field, 0) else 'tie'),
                'format': format_type
            })

        # Grade-level comparisons
        # Note: Only fundraising, minutes, and size are implemented in queries.py
        grade_metrics = [
            ('fundraising', 'Fundraising', False, 'currency'),
            ('minutes', 'Minutes Read', True, 'minutes'),
            ('size', 'Grade Size', False, 'number')
        ]

        for metric_key, metric_name, honors_filter, format_type in grade_metrics:
            # Get all tied winners for tie counting
            db1_grade_list = db1.execute_query(get_db_comparison_grade_top(metric_key, filter_period if honors_filter else None))
            db2_grade_list = db2.execute_query(get_db_comparison_grade_top(metric_key, filter_period if honors_filter else None))

            # Count ties and pick first winner
            db1_tie_count = len(db1_grade_list)
            db2_tie_count = len(db2_grade_list)
            db1_grade = db1_grade_list[0] if db1_grade_list else {}
            db2_grade = db2_grade_list[0] if db2_grade_list else {}

            # Determine the value field name based on metric
            value_field = f'total_{metric_key}' if metric_key != 'size' else 'student_count'

            # For size metric, context is different (no class_name returned)
            if metric_key == 'size':
                db1_context = f"({db1_grade['class_count']} classes)" if db1_grade else "N/A"
                db2_context = f"({db2_grade['class_count']} classes)" if db2_grade else "N/A"
            else:
                db1_context = f"Top class: {db1_grade['class_name']} ({db1_grade['team_name']})" if db1_grade else "N/A"
                db2_context = f"Top class: {db2_grade['class_name']} ({db2_grade['team_name']})" if db2_grade else "N/A"

            comparisons.append({
                'entity_level': 'Grade',
                'metric': metric_name,
                'honors_filter': honors_filter,
                'db1_value': {
                    'value': db1_grade.get(value_field, 0),
                    'winner_name': f"Grade {db1_grade.get('grade_level', 'N/A')}",
                    'tie_count': db1_tie_count,
                    'context': db1_context
                },
                'db2_value': {
                    'value': db2_grade.get(value_field, 0),
                    'winner_name': f"Grade {db2_grade.get('grade_level', 'N/A')}",
                    'tie_count': db2_tie_count,
                    'context': db2_context
                },
                'change': calc_change(db1_grade.get(value_field, 0), db2_grade.get(value_field, 0)),
                'winner': 'db1' if db1_grade.get(value_field, 0) > db2_grade.get(value_field, 0) else ('db2' if db1_grade.get(value_field, 0) < db2_grade.get(value_field, 0) else 'tie'),
                'format': format_type
            })

        # Class-level comparisons
        # Note: Only fundraising, minutes, and size are implemented in queries.py
        class_metrics = [
            ('fundraising', 'Fundraising', False, 'currency'),
            ('minutes', 'Minutes Read', True, 'minutes'),
            ('size', 'Class Size', False, 'number')
        ]

        for metric_key, metric_name, honors_filter, format_type in class_metrics:
            # Get all tied winners for tie counting
            db1_class_list = db1.execute_query(get_db_comparison_class_top(metric_key, filter_period if honors_filter else None))
            db2_class_list = db2.execute_query(get_db_comparison_class_top(metric_key, filter_period if honors_filter else None))

            # Count ties and pick first winner
            db1_tie_count = len(db1_class_list)
            db2_tie_count = len(db2_class_list)
            db1_class = db1_class_list[0] if db1_class_list else {}
            db2_class = db2_class_list[0] if db2_class_list else {}

            # Determine the value field name based on metric
            value_field = f'total_{metric_key}' if metric_key != 'size' else 'total_students'

            # For size metric, context is different
            if metric_key == 'size':
                db1_winner_name = db1_class.get('class_name', 'N/A')
                db2_winner_name = db2_class.get('class_name', 'N/A')
                db1_context = f"Grade {db1_class.get('grade_level', 'N/A')}, {db1_class.get('team_name', 'N/A')}" if db1_class else "N/A"
                db2_context = f"Grade {db2_class.get('grade_level', 'N/A')}, {db2_class.get('team_name', 'N/A')}" if db2_class else "N/A"
            else:
                db1_winner_name = db1_class.get('class_name', 'N/A')
                db2_winner_name = db2_class.get('class_name', 'N/A')
                db1_context = f"Grade {db1_class.get('grade_level', 'N/A')}, {db1_class.get('team_name', 'N/A')}" if db1_class else "N/A"
                db2_context = f"Grade {db2_class.get('grade_level', 'N/A')}, {db2_class.get('team_name', 'N/A')}" if db2_class else "N/A"

            comparisons.append({
                'entity_level': 'Class',
                'metric': metric_name,
                'honors_filter': honors_filter,
                'db1_value': {
                    'value': db1_class.get(value_field, 0),
                    'winner_name': db1_winner_name,
                    'tie_count': db1_tie_count,
                    'context': db1_context
                },
                'db2_value': {
                    'value': db2_class.get(value_field, 0),
                    'winner_name': db2_winner_name,
                    'tie_count': db2_tie_count,
                    'context': db2_context
                },
                'change': calc_change(db1_class.get(value_field, 0), db2_class.get(value_field, 0)),
                'winner': 'db1' if db1_class.get(value_field, 0) > db2_class.get(value_field, 0) else ('db2' if db1_class.get(value_field, 0) < db2_class.get(value_field, 0) else 'tie'),
                'format': format_type
            })

        # Additional School-level comparisons
        # School - Avg Participation % (With Color)
        db1_school_avg_part = db1.execute_query(get_db_comparison_school_avg_participation(filter_period))[0]
        db2_school_avg_part = db2.execute_query(get_db_comparison_school_avg_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Avg Participation % (With Color)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_school_avg_part['avg_participation_pct_with_color'],
                'context': f"({db1_school_avg_part['total_students']} students, {db1_school_avg_part['total_days']} days)"
            },
            'db2_value': {
                'value': db2_school_avg_part['avg_participation_pct_with_color'],
                'context': f"({db2_school_avg_part['total_students']} students, {db2_school_avg_part['total_days']} days)"
            },
            'change': calc_change(db1_school_avg_part['avg_participation_pct_with_color'], db2_school_avg_part['avg_participation_pct_with_color']),
            'winner': 'db1' if db1_school_avg_part['avg_participation_pct_with_color'] > db2_school_avg_part['avg_participation_pct_with_color'] else ('db2' if db1_school_avg_part['avg_participation_pct_with_color'] < db2_school_avg_part['avg_participation_pct_with_color'] else 'tie'),
            'format': 'percentage'
        })

        # School - Goal Met (≥1 Day)
        db1_school_goal = db1.execute_query(get_db_comparison_school_goal_met(filter_period))[0]
        db2_school_goal = db2.execute_query(get_db_comparison_school_goal_met(filter_period))[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Goal Met (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_school_goal['goal_met_pct'],
                'context': f"{db1_school_goal['students_who_met_goal']}/{db1_school_goal['total_students']} students"
            },
            'db2_value': {
                'value': db2_school_goal['goal_met_pct'],
                'context': f"{db2_school_goal['students_who_met_goal']}/{db2_school_goal['total_students']} students"
            },
            'change': calc_change(db1_school_goal['goal_met_pct'], db2_school_goal['goal_met_pct']),
            'winner': 'db1' if db1_school_goal['goal_met_pct'] > db2_school_goal['goal_met_pct'] else ('db2' if db1_school_goal['goal_met_pct'] < db2_school_goal['goal_met_pct'] else 'tie'),
            'format': 'percentage'
        })

        # School - All N Days Active %
        db1_school_all_days_result = db1.execute_query(get_db_comparison_school_all_days_active(filter_period))
        db2_school_all_days_result = db2.execute_query(get_db_comparison_school_all_days_active(filter_period))

        # Handle case where no students logged every day
        db1_school_all_days = db1_school_all_days_result[0] if db1_school_all_days_result else {
            'all_days_active_pct': 0, 'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_school_all_days = db2_school_all_days_result[0] if db2_school_all_days_result else {
            'all_days_active_pct': 0, 'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'School',
            'metric': 'All N Days Active %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_school_all_days['all_days_active_pct'],
                'context': f"{db1_school_all_days['students_all_days']}/{db1_school_all_days['total_students']} students ({db1_school_all_days['total_days']} days)"
            },
            'db2_value': {
                'value': db2_school_all_days['all_days_active_pct'],
                'context': f"{db2_school_all_days['students_all_days']}/{db2_school_all_days['total_students']} students ({db2_school_all_days['total_days']} days)"
            },
            'change': calc_change(db1_school_all_days['all_days_active_pct'], db2_school_all_days['all_days_active_pct']),
            'winner': 'db1' if db1_school_all_days['all_days_active_pct'] > db2_school_all_days['all_days_active_pct'] else ('db2' if db1_school_all_days['all_days_active_pct'] < db2_school_all_days['all_days_active_pct'] else 'tie'),
            'format': 'percentage'
        })

        # School - Goal Met All Days %
        db1_school_goal_all_result = db1.execute_query(get_db_comparison_school_goal_met_all_days(filter_period))
        db2_school_goal_all_result = db2.execute_query(get_db_comparison_school_goal_met_all_days(filter_period))

        # Handle case where no students met goal every day
        db1_school_goal_all = db1_school_goal_all_result[0] if db1_school_goal_all_result else {
            'goal_met_all_days_pct': 0, 'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_school_goal_all = db2_school_goal_all_result[0] if db2_school_goal_all_result else {
            'goal_met_all_days_pct': 0, 'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Goal Met All Days %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_school_goal_all['goal_met_all_days_pct'],
                'context': f"{db1_school_goal_all['students_goal_all_days']}/{db1_school_goal_all['total_students']} students ({db1_school_goal_all['total_days']} days)"
            },
            'db2_value': {
                'value': db2_school_goal_all['goal_met_all_days_pct'],
                'context': f"{db2_school_goal_all['students_goal_all_days']}/{db2_school_goal_all['total_students']} students ({db2_school_goal_all['total_days']} days)"
            },
            'change': calc_change(db1_school_goal_all['goal_met_all_days_pct'], db2_school_goal_all['goal_met_all_days_pct']),
            'winner': 'db1' if db1_school_goal_all['goal_met_all_days_pct'] > db2_school_goal_all['goal_met_all_days_pct'] else ('db2' if db1_school_goal_all['goal_met_all_days_pct'] < db2_school_goal_all['goal_met_all_days_pct'] else 'tie'),
            'format': 'percentage'
        })

        # School - Color War Points
        db1_school_points = db1.execute_query(get_db_comparison_school_color_war_points())[0]
        db2_school_points = db2.execute_query(get_db_comparison_school_color_war_points())[0]

        comparisons.append({
            'entity_level': 'School',
            'metric': 'Color War Points',
            'honors_filter': False,
            'db1_value': {
                'value': db1_school_points['total_points'],
                'context': f"({db1_school_points['base_points']} base + {db1_school_points['bonus_points']} bonus)"
            },
            'db2_value': {
                'value': db2_school_points['total_points'],
                'context': f"({db2_school_points['base_points']} base + {db2_school_points['bonus_points']} bonus)"
            },
            'change': calc_change(db1_school_points['total_points'], db2_school_points['total_points']),
            'winner': 'db1' if db1_school_points['total_points'] > db2_school_points['total_points'] else ('db2' if db1_school_points['total_points'] < db2_school_points['total_points'] else 'tie'),
            'format': 'number'
        })

        # Additional Team-level comparisons
        # Team - Sponsors
        db1_team_sponsors = db1.execute_query(get_db_comparison_team_sponsors())[0]
        db2_team_sponsors = db2.execute_query(get_db_comparison_team_sponsors())[0]

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'Sponsors',
            'honors_filter': False,
            'db1_value': {
                'value': db1_team_sponsors['total_sponsors'],
                'winner_name': db1_team_sponsors['team_name'],
                'context': f"Top class: {db1_team_sponsors['class_name']} (Grade {db1_team_sponsors['grade_level']})"
            },
            'db2_value': {
                'value': db2_team_sponsors['total_sponsors'],
                'winner_name': db2_team_sponsors['team_name'],
                'context': f"Top class: {db2_team_sponsors['class_name']} (Grade {db2_team_sponsors['grade_level']})"
            },
            'change': calc_change(db1_team_sponsors['total_sponsors'], db2_team_sponsors['total_sponsors']),
            'winner': 'db1' if db1_team_sponsors['total_sponsors'] > db2_team_sponsors['total_sponsors'] else ('db2' if db1_team_sponsors['total_sponsors'] < db2_team_sponsors['total_sponsors'] else 'tie'),
            'format': 'number'
        })

        # Team - Total Participating (≥1 Day)
        db1_team_part = db1.execute_query(get_db_comparison_team_participation(filter_period))[0]
        db2_team_part = db2.execute_query(get_db_comparison_team_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'Total Participating (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_team_part['participation_pct'],
                'winner_name': db1_team_part['team_name'],
                'context': f"{db1_team_part['participating_count']}/{db1_team_part['total_count']} students"
            },
            'db2_value': {
                'value': db2_team_part['participation_pct'],
                'winner_name': db2_team_part['team_name'],
                'context': f"{db2_team_part['participating_count']}/{db2_team_part['total_count']} students"
            },
            'change': calc_change(db1_team_part['participation_pct'], db2_team_part['participation_pct']),
            'winner': 'db1' if db1_team_part['participation_pct'] > db2_team_part['participation_pct'] else ('db2' if db1_team_part['participation_pct'] < db2_team_part['participation_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Team - Avg Participation % (With Color)
        db1_team_avg = db1.execute_query(get_db_comparison_team_avg_participation(filter_period))[0]
        db2_team_avg = db2.execute_query(get_db_comparison_team_avg_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'Avg Participation % (With Color)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_team_avg['avg_participation_with_color'],
                'winner_name': db1_team_avg['team_name'],
                'context': f"({db1_team_avg['total_students']} students, {db1_team_avg['total_days']} days)"
            },
            'db2_value': {
                'value': db2_team_avg['avg_participation_with_color'],
                'winner_name': db2_team_avg['team_name'],
                'context': f"({db2_team_avg['total_students']} students, {db2_team_avg['total_days']} days)"
            },
            'change': calc_change(db1_team_avg['avg_participation_with_color'], db2_team_avg['avg_participation_with_color']),
            'winner': 'db1' if db1_team_avg['avg_participation_with_color'] > db2_team_avg['avg_participation_with_color'] else ('db2' if db1_team_avg['avg_participation_with_color'] < db2_team_avg['avg_participation_with_color'] else 'tie'),
            'format': 'percentage'
        })

        # Team - Goal Met (≥1 Day)
        db1_team_goal = db1.execute_query(get_db_comparison_team_goal_met(filter_period))[0]
        db2_team_goal = db2.execute_query(get_db_comparison_team_goal_met(filter_period))[0]

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'Goal Met (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_team_goal['goal_met_pct'],
                'winner_name': db1_team_goal['team_name'],
                'context': f"{db1_team_goal['students_who_met_goal']}/{db1_team_goal['total_students']} students"
            },
            'db2_value': {
                'value': db2_team_goal['goal_met_pct'],
                'winner_name': db2_team_goal['team_name'],
                'context': f"{db2_team_goal['students_who_met_goal']}/{db2_team_goal['total_students']} students"
            },
            'change': calc_change(db1_team_goal['goal_met_pct'], db2_team_goal['goal_met_pct']),
            'winner': 'db1' if db1_team_goal['goal_met_pct'] > db2_team_goal['goal_met_pct'] else ('db2' if db1_team_goal['goal_met_pct'] < db2_team_goal['goal_met_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Team - All N Days Active %
        db1_team_all_days_result = db1.execute_query(get_db_comparison_team_all_days_active(filter_period))
        db2_team_all_days_result = db2.execute_query(get_db_comparison_team_all_days_active(filter_period))

        # Handle case where no team has all students active every day
        db1_team_all_days = db1_team_all_days_result[0] if db1_team_all_days_result else {
            'team_name': 'None', 'all_days_active_pct': 0, 'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_team_all_days = db2_team_all_days_result[0] if db2_team_all_days_result else {
            'team_name': 'None', 'all_days_active_pct': 0, 'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'All N Days Active %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_team_all_days['all_days_active_pct'],
                'winner_name': db1_team_all_days['team_name'],
                'context': f"{db1_team_all_days['students_all_days']}/{db1_team_all_days['total_students']} students ({db1_team_all_days['total_days']} days)"
            },
            'db2_value': {
                'value': db2_team_all_days['all_days_active_pct'],
                'winner_name': db2_team_all_days['team_name'],
                'context': f"{db2_team_all_days['students_all_days']}/{db2_team_all_days['total_students']} students ({db2_team_all_days['total_days']} days)"
            },
            'change': calc_change(db1_team_all_days['all_days_active_pct'], db2_team_all_days['all_days_active_pct']),
            'winner': 'db1' if db1_team_all_days['all_days_active_pct'] > db2_team_all_days['all_days_active_pct'] else ('db2' if db1_team_all_days['all_days_active_pct'] < db2_team_all_days['all_days_active_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Team - Goal Met All Days %
        db1_team_goal_all_result = db1.execute_query(get_db_comparison_team_goal_met_all_days(filter_period))
        db2_team_goal_all_result = db2.execute_query(get_db_comparison_team_goal_met_all_days(filter_period))

        # Handle case where no team has students who met goal every day
        db1_team_goal_all = db1_team_goal_all_result[0] if db1_team_goal_all_result else {
            'team_name': 'None', 'goal_met_all_days_pct': 0, 'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_team_goal_all = db2_team_goal_all_result[0] if db2_team_goal_all_result else {
            'team_name': 'None', 'goal_met_all_days_pct': 0, 'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'Goal Met All Days %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_team_goal_all['goal_met_all_days_pct'],
                'winner_name': db1_team_goal_all['team_name'],
                'context': f"{db1_team_goal_all['students_goal_all_days']}/{db1_team_goal_all['total_students']} students ({db1_team_goal_all['total_days']} days)"
            },
            'db2_value': {
                'value': db2_team_goal_all['goal_met_all_days_pct'],
                'winner_name': db2_team_goal_all['team_name'],
                'context': f"{db2_team_goal_all['students_goal_all_days']}/{db2_team_goal_all['total_students']} students ({db2_team_goal_all['total_days']} days)"
            },
            'change': calc_change(db1_team_goal_all['goal_met_all_days_pct'], db2_team_goal_all['goal_met_all_days_pct']),
            'winner': 'db1' if db1_team_goal_all['goal_met_all_days_pct'] > db2_team_goal_all['goal_met_all_days_pct'] else ('db2' if db1_team_goal_all['goal_met_all_days_pct'] < db2_team_goal_all['goal_met_all_days_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Team - Color War Points
        db1_team_points = db1.execute_query(get_db_comparison_team_color_war_points())[0]
        db2_team_points = db2.execute_query(get_db_comparison_team_color_war_points())[0]

        comparisons.append({
            'entity_level': 'Team',
            'metric': 'Color War Points',
            'honors_filter': False,
            'db1_value': {
                'value': db1_team_points['total_points'],
                'winner_name': db1_team_points['team_name'],
                'context': f"({db1_team_points['base_points']} base + {db1_team_points['bonus_points']} bonus)"
            },
            'db2_value': {
                'value': db2_team_points['total_points'],
                'winner_name': db2_team_points['team_name'],
                'context': f"({db2_team_points['base_points']} base + {db2_team_points['bonus_points']} bonus)"
            },
            'change': calc_change(db1_team_points['total_points'], db2_team_points['total_points']),
            'winner': 'db1' if db1_team_points['total_points'] > db2_team_points['total_points'] else ('db2' if db1_team_points['total_points'] < db2_team_points['total_points'] else 'tie'),
            'format': 'number'
        })

        # Additional Grade-level comparisons
        # Grade - Sponsors
        db1_grade_sponsors = db1.execute_query(get_db_comparison_grade_sponsors())[0]
        db2_grade_sponsors = db2.execute_query(get_db_comparison_grade_sponsors())[0]

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'Sponsors',
            'honors_filter': False,
            'db1_value': {
                'value': db1_grade_sponsors['total_sponsors'],
                'winner_name': f"Grade {db1_grade_sponsors['grade_level']}",
                'context': f"Top class: {db1_grade_sponsors['class_name']} ({db1_grade_sponsors['team_name']})"
            },
            'db2_value': {
                'value': db2_grade_sponsors['total_sponsors'],
                'winner_name': f"Grade {db2_grade_sponsors['grade_level']}",
                'context': f"Top class: {db2_grade_sponsors['class_name']} ({db2_grade_sponsors['team_name']})"
            },
            'change': calc_change(db1_grade_sponsors['total_sponsors'], db2_grade_sponsors['total_sponsors']),
            'winner': 'db1' if db1_grade_sponsors['total_sponsors'] > db2_grade_sponsors['total_sponsors'] else ('db2' if db1_grade_sponsors['total_sponsors'] < db2_grade_sponsors['total_sponsors'] else 'tie'),
            'format': 'number'
        })

        # Grade - Total Participating (≥1 Day)
        db1_grade_part = db1.execute_query(get_db_comparison_grade_participation(filter_period))[0]
        db2_grade_part = db2.execute_query(get_db_comparison_grade_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'Total Participating (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_grade_part['participation_pct'],
                'winner_name': f"Grade {db1_grade_part['grade_level']}",
                'context': f"{db1_grade_part['participating_count']}/{db1_grade_part['total_count']} students"
            },
            'db2_value': {
                'value': db2_grade_part['participation_pct'],
                'winner_name': f"Grade {db2_grade_part['grade_level']}",
                'context': f"{db2_grade_part['participating_count']}/{db2_grade_part['total_count']} students"
            },
            'change': calc_change(db1_grade_part['participation_pct'], db2_grade_part['participation_pct']),
            'winner': 'db1' if db1_grade_part['participation_pct'] > db2_grade_part['participation_pct'] else ('db2' if db1_grade_part['participation_pct'] < db2_grade_part['participation_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Grade - Avg Participation % (With Color)
        db1_grade_avg = db1.execute_query(get_db_comparison_grade_avg_participation(filter_period))[0]
        db2_grade_avg = db2.execute_query(get_db_comparison_grade_avg_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'Avg Participation % (With Color)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_grade_avg['avg_participation_with_color'],
                'winner_name': f"Grade {db1_grade_avg['grade_level']}",
                'context': f"({db1_grade_avg['total_students']} students, {db1_grade_avg['total_days']} days)"
            },
            'db2_value': {
                'value': db2_grade_avg['avg_participation_with_color'],
                'winner_name': f"Grade {db2_grade_avg['grade_level']}",
                'context': f"({db2_grade_avg['total_students']} students, {db2_grade_avg['total_days']} days)"
            },
            'change': calc_change(db1_grade_avg['avg_participation_with_color'], db2_grade_avg['avg_participation_with_color']),
            'winner': 'db1' if db1_grade_avg['avg_participation_with_color'] > db2_grade_avg['avg_participation_with_color'] else ('db2' if db1_grade_avg['avg_participation_with_color'] < db2_grade_avg['avg_participation_with_color'] else 'tie'),
            'format': 'percentage'
        })

        # Grade - Goal Met (≥1 Day)
        db1_grade_goal = db1.execute_query(get_db_comparison_grade_goal_met(filter_period))[0]
        db2_grade_goal = db2.execute_query(get_db_comparison_grade_goal_met(filter_period))[0]

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'Goal Met (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_grade_goal['goal_met_pct'],
                'winner_name': f"Grade {db1_grade_goal['grade_level']}",
                'context': f"{db1_grade_goal['students_who_met_goal']}/{db1_grade_goal['total_students']} students"
            },
            'db2_value': {
                'value': db2_grade_goal['goal_met_pct'],
                'winner_name': f"Grade {db2_grade_goal['grade_level']}",
                'context': f"{db2_grade_goal['students_who_met_goal']}/{db2_grade_goal['total_students']} students"
            },
            'change': calc_change(db1_grade_goal['goal_met_pct'], db2_grade_goal['goal_met_pct']),
            'winner': 'db1' if db1_grade_goal['goal_met_pct'] > db2_grade_goal['goal_met_pct'] else ('db2' if db1_grade_goal['goal_met_pct'] < db2_grade_goal['goal_met_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Grade - All N Days Active %
        db1_grade_all_days_result = db1.execute_query(get_db_comparison_grade_all_days_active(filter_period))
        db2_grade_all_days_result = db2.execute_query(get_db_comparison_grade_all_days_active(filter_period))

        # Handle case where no grade has all students active every day
        db1_grade_all_days = db1_grade_all_days_result[0] if db1_grade_all_days_result else {
            'grade_level': 'None', 'all_days_active_pct': 0, 'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_grade_all_days = db2_grade_all_days_result[0] if db2_grade_all_days_result else {
            'grade_level': 'None', 'all_days_active_pct': 0, 'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'All N Days Active %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_grade_all_days['all_days_active_pct'],
                'winner_name': f"Grade {db1_grade_all_days['grade_level']}",
                'context': f"{db1_grade_all_days['students_all_days']}/{db1_grade_all_days['total_students']} students ({db1_grade_all_days['total_days']} days)"
            },
            'db2_value': {
                'value': db2_grade_all_days['all_days_active_pct'],
                'winner_name': f"Grade {db2_grade_all_days['grade_level']}",
                'context': f"{db2_grade_all_days['students_all_days']}/{db2_grade_all_days['total_students']} students ({db2_grade_all_days['total_days']} days)"
            },
            'change': calc_change(db1_grade_all_days['all_days_active_pct'], db2_grade_all_days['all_days_active_pct']),
            'winner': 'db1' if db1_grade_all_days['all_days_active_pct'] > db2_grade_all_days['all_days_active_pct'] else ('db2' if db1_grade_all_days['all_days_active_pct'] < db2_grade_all_days['all_days_active_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Grade - Goal Met All Days %
        db1_grade_goal_all_result = db1.execute_query(get_db_comparison_grade_goal_met_all_days(filter_period))
        db2_grade_goal_all_result = db2.execute_query(get_db_comparison_grade_goal_met_all_days(filter_period))

        # Handle case where no grade has students who met goal every day
        db1_grade_goal_all = db1_grade_goal_all_result[0] if db1_grade_goal_all_result else {
            'grade_level': 'None', 'goal_met_all_days_pct': 0, 'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_grade_goal_all = db2_grade_goal_all_result[0] if db2_grade_goal_all_result else {
            'grade_level': 'None', 'goal_met_all_days_pct': 0, 'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'Goal Met All Days %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_grade_goal_all['goal_met_all_days_pct'],
                'winner_name': f"Grade {db1_grade_goal_all['grade_level']}",
                'context': f"{db1_grade_goal_all['students_goal_all_days']}/{db1_grade_goal_all['total_students']} students ({db1_grade_goal_all['total_days']} days)"
            },
            'db2_value': {
                'value': db2_grade_goal_all['goal_met_all_days_pct'],
                'winner_name': f"Grade {db2_grade_goal_all['grade_level']}",
                'context': f"{db2_grade_goal_all['students_goal_all_days']}/{db2_grade_goal_all['total_students']} students ({db2_grade_goal_all['total_days']} days)"
            },
            'change': calc_change(db1_grade_goal_all['goal_met_all_days_pct'], db2_grade_goal_all['goal_met_all_days_pct']),
            'winner': 'db1' if db1_grade_goal_all['goal_met_all_days_pct'] > db2_grade_goal_all['goal_met_all_days_pct'] else ('db2' if db1_grade_goal_all['goal_met_all_days_pct'] < db2_grade_goal_all['goal_met_all_days_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Grade - Color War Points
        db1_grade_points = db1.execute_query(get_db_comparison_grade_color_war_points())[0]
        db2_grade_points = db2.execute_query(get_db_comparison_grade_color_war_points())[0]

        comparisons.append({
            'entity_level': 'Grade',
            'metric': 'Color War Points',
            'honors_filter': False,
            'db1_value': {
                'value': db1_grade_points['total_points'],
                'winner_name': f"Grade {db1_grade_points['grade_level']}",
                'context': f"({db1_grade_points['base_points']} base + {db1_grade_points['bonus_points']} bonus)"
            },
            'db2_value': {
                'value': db2_grade_points['total_points'],
                'winner_name': f"Grade {db2_grade_points['grade_level']}",
                'context': f"({db2_grade_points['base_points']} base + {db2_grade_points['bonus_points']} bonus)"
            },
            'change': calc_change(db1_grade_points['total_points'], db2_grade_points['total_points']),
            'winner': 'db1' if db1_grade_points['total_points'] > db2_grade_points['total_points'] else ('db2' if db1_grade_points['total_points'] < db2_grade_points['total_points'] else 'tie'),
            'format': 'number'
        })

        # Additional Class-level comparisons
        # Class - Sponsors
        db1_class_sponsors = db1.execute_query(get_db_comparison_class_sponsors())[0]
        db2_class_sponsors = db2.execute_query(get_db_comparison_class_sponsors())[0]

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'Sponsors',
            'honors_filter': False,
            'db1_value': {
                'value': db1_class_sponsors['total_sponsors'],
                'winner_name': db1_class_sponsors['class_name'],
                'context': f"Grade {db1_class_sponsors['grade_level']}, {db1_class_sponsors['team_name']}"
            },
            'db2_value': {
                'value': db2_class_sponsors['total_sponsors'],
                'winner_name': db2_class_sponsors['class_name'],
                'context': f"Grade {db2_class_sponsors['grade_level']}, {db2_class_sponsors['team_name']}"
            },
            'change': calc_change(db1_class_sponsors['total_sponsors'], db2_class_sponsors['total_sponsors']),
            'winner': 'db1' if db1_class_sponsors['total_sponsors'] > db2_class_sponsors['total_sponsors'] else ('db2' if db1_class_sponsors['total_sponsors'] < db2_class_sponsors['total_sponsors'] else 'tie'),
            'format': 'number'
        })

        # Class - Total Participating (≥1 Day)
        db1_class_part = db1.execute_query(get_db_comparison_class_participation(filter_period))[0]
        db2_class_part = db2.execute_query(get_db_comparison_class_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'Total Participating (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_class_part['participation_pct'],
                'winner_name': db1_class_part['class_name'],
                'context': f"{db1_class_part['participating_count']}/{db1_class_part['total_count']} students, Grade {db1_class_part['grade_level']}, {db1_class_part['team_name']}"
            },
            'db2_value': {
                'value': db2_class_part['participation_pct'],
                'winner_name': db2_class_part['class_name'],
                'context': f"{db2_class_part['participating_count']}/{db2_class_part['total_count']} students, Grade {db2_class_part['grade_level']}, {db2_class_part['team_name']}"
            },
            'change': calc_change(db1_class_part['participation_pct'], db2_class_part['participation_pct']),
            'winner': 'db1' if db1_class_part['participation_pct'] > db2_class_part['participation_pct'] else ('db2' if db1_class_part['participation_pct'] < db2_class_part['participation_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Class - Avg Participation % (With Color)
        db1_class_avg = db1.execute_query(get_db_comparison_class_avg_participation(filter_period))[0]
        db2_class_avg = db2.execute_query(get_db_comparison_class_avg_participation(filter_period))[0]

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'Avg Participation % (With Color)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_class_avg['avg_participation_with_color'],
                'winner_name': db1_class_avg['class_name'],
                'context': f"Grade {db1_class_avg['grade_level']}, {db1_class_avg['team_name']} ({db1_class_avg['total_students']} students, {db1_class_avg['total_days']} days)"
            },
            'db2_value': {
                'value': db2_class_avg['avg_participation_with_color'],
                'winner_name': db2_class_avg['class_name'],
                'context': f"Grade {db2_class_avg['grade_level']}, {db2_class_avg['team_name']} ({db2_class_avg['total_students']} students, {db2_class_avg['total_days']} days)"
            },
            'change': calc_change(db1_class_avg['avg_participation_with_color'], db2_class_avg['avg_participation_with_color']),
            'winner': 'db1' if db1_class_avg['avg_participation_with_color'] > db2_class_avg['avg_participation_with_color'] else ('db2' if db1_class_avg['avg_participation_with_color'] < db2_class_avg['avg_participation_with_color'] else 'tie'),
            'format': 'percentage'
        })

        # Class - Goal Met (≥1 Day)
        db1_class_goal = db1.execute_query(get_db_comparison_class_goal_met(filter_period))[0]
        db2_class_goal = db2.execute_query(get_db_comparison_class_goal_met(filter_period))[0]

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'Goal Met (≥1 Day)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_class_goal['goal_met_pct'],
                'winner_name': db1_class_goal['class_name'],
                'context': f"Grade {db1_class_goal['grade_level']}, {db1_class_goal['team_name']} ({db1_class_goal['students_who_met_goal']}/{db1_class_goal['total_students']} students)"
            },
            'db2_value': {
                'value': db2_class_goal['goal_met_pct'],
                'winner_name': db2_class_goal['class_name'],
                'context': f"Grade {db2_class_goal['grade_level']}, {db2_class_goal['team_name']} ({db2_class_goal['students_who_met_goal']}/{db2_class_goal['total_students']} students)"
            },
            'change': calc_change(db1_class_goal['goal_met_pct'], db2_class_goal['goal_met_pct']),
            'winner': 'db1' if db1_class_goal['goal_met_pct'] > db2_class_goal['goal_met_pct'] else ('db2' if db1_class_goal['goal_met_pct'] < db2_class_goal['goal_met_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Class - All N Days Active %
        db1_class_all_days_result = db1.execute_query(get_db_comparison_class_all_days_active(filter_period))
        db2_class_all_days_result = db2.execute_query(get_db_comparison_class_all_days_active(filter_period))

        # Handle case where no class has all students active every day
        db1_class_all_days = db1_class_all_days_result[0] if db1_class_all_days_result else {
            'class_name': 'None', 'grade_level': 'N/A', 'team_name': 'N/A', 'all_days_active_pct': 0,
            'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_class_all_days = db2_class_all_days_result[0] if db2_class_all_days_result else {
            'class_name': 'None', 'grade_level': 'N/A', 'team_name': 'N/A', 'all_days_active_pct': 0,
            'students_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'All N Days Active %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_class_all_days['all_days_active_pct'],
                'winner_name': db1_class_all_days['class_name'],
                'context': f"Grade {db1_class_all_days['grade_level']}, {db1_class_all_days['team_name']} ({db1_class_all_days['students_all_days']}/{db1_class_all_days['total_students']} students, {db1_class_all_days['total_days']} days)"
            },
            'db2_value': {
                'value': db2_class_all_days['all_days_active_pct'],
                'winner_name': db2_class_all_days['class_name'],
                'context': f"Grade {db2_class_all_days['grade_level']}, {db2_class_all_days['team_name']} ({db2_class_all_days['students_all_days']}/{db2_class_all_days['total_students']} students, {db2_class_all_days['total_days']} days)"
            },
            'change': calc_change(db1_class_all_days['all_days_active_pct'], db2_class_all_days['all_days_active_pct']),
            'winner': 'db1' if db1_class_all_days['all_days_active_pct'] > db2_class_all_days['all_days_active_pct'] else ('db2' if db1_class_all_days['all_days_active_pct'] < db2_class_all_days['all_days_active_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Class - Goal Met All Days %
        db1_class_goal_all_result = db1.execute_query(get_db_comparison_class_goal_met_all_days(filter_period))
        db2_class_goal_all_result = db2.execute_query(get_db_comparison_class_goal_met_all_days(filter_period))

        # Handle case where no class has students who met goal every day
        db1_class_goal_all = db1_class_goal_all_result[0] if db1_class_goal_all_result else {
            'class_name': 'None', 'grade_level': 'N/A', 'team_name': 'N/A', 'goal_met_all_days_pct': 0,
            'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }
        db2_class_goal_all = db2_class_goal_all_result[0] if db2_class_goal_all_result else {
            'class_name': 'None', 'grade_level': 'N/A', 'team_name': 'N/A', 'goal_met_all_days_pct': 0,
            'students_goal_all_days': 0, 'total_students': 0, 'total_days': 0
        }

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'Goal Met All Days %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_class_goal_all['goal_met_all_days_pct'],
                'winner_name': db1_class_goal_all['class_name'],
                'context': f"Grade {db1_class_goal_all['grade_level']}, {db1_class_goal_all['team_name']} ({db1_class_goal_all['students_goal_all_days']}/{db1_class_goal_all['total_students']} students, {db1_class_goal_all['total_days']} days)"
            },
            'db2_value': {
                'value': db2_class_goal_all['goal_met_all_days_pct'],
                'winner_name': db2_class_goal_all['class_name'],
                'context': f"Grade {db2_class_goal_all['grade_level']}, {db2_class_goal_all['team_name']} ({db2_class_goal_all['students_goal_all_days']}/{db2_class_goal_all['total_students']} students, {db2_class_goal_all['total_days']} days)"
            },
            'change': calc_change(db1_class_goal_all['goal_met_all_days_pct'], db2_class_goal_all['goal_met_all_days_pct']),
            'winner': 'db1' if db1_class_goal_all['goal_met_all_days_pct'] > db2_class_goal_all['goal_met_all_days_pct'] else ('db2' if db1_class_goal_all['goal_met_all_days_pct'] < db2_class_goal_all['goal_met_all_days_pct'] else 'tie'),
            'format': 'percentage'
        })

        # Class - Color War Points
        db1_class_points = db1.execute_query(get_db_comparison_class_color_war_points())[0]
        db2_class_points = db2.execute_query(get_db_comparison_class_color_war_points())[0]

        comparisons.append({
            'entity_level': 'Class',
            'metric': 'Color War Points',
            'honors_filter': False,
            'db1_value': {
                'value': db1_class_points['total_points'],
                'winner_name': db1_class_points['class_name'],
                'context': f"Grade {db1_class_points['grade_level']}, {db1_class_points['team_name']} ({db1_class_points['base_points']} base + {db1_class_points['bonus_points']} bonus)"
            },
            'db2_value': {
                'value': db2_class_points['total_points'],
                'winner_name': db2_class_points['class_name'],
                'context': f"Grade {db2_class_points['grade_level']}, {db2_class_points['team_name']} ({db2_class_points['base_points']} base + {db2_class_points['bonus_points']} bonus)"
            },
            'change': calc_change(db1_class_points['total_points'], db2_class_points['total_points']),
            'winner': 'db1' if db1_class_points['total_points'] > db2_class_points['total_points'] else ('db2' if db1_class_points['total_points'] < db2_class_points['total_points'] else 'tie'),
            'format': 'number'
        })

        # Additional Student-level comparisons
        # Student - Participation %
        db1_student_part_list = db1.execute_query(get_db_comparison_student_top_participation(filter_period))
        db2_student_part_list = db2.execute_query(get_db_comparison_student_top_participation(filter_period))

        db1_part_fmt = self._format_tied_winners(db1_student_part_list)
        db2_part_fmt = self._format_tied_winners(db2_student_part_list)

        db1_part_value = db1_student_part_list[0]['participation_pct'] if db1_student_part_list else 0
        db2_part_value = db2_student_part_list[0]['participation_pct'] if db2_student_part_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Participation %',
            'honors_filter': True,
            'db1_value': {
                'value': db1_part_value,
                'winner_name': db1_part_fmt['names'],
                'tie_count': db1_part_fmt['tie_count'],
                'context': db1_part_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_part_value,
                'winner_name': db2_part_fmt['names'],
                'tie_count': db2_part_fmt['tie_count'],
                'context': db2_part_fmt['grade_context']
            },
            'change': calc_change(db1_part_value, db2_part_value),
            'winner': 'db1' if db1_part_value > db2_part_value else ('db2' if db1_part_value < db2_part_value else 'tie'),
            'format': 'percentage'
        })

        # Student - Goal Met (Days)
        db1_student_goal_list = db1.execute_query(get_db_comparison_student_goal_met(filter_period))
        db2_student_goal_list = db2.execute_query(get_db_comparison_student_goal_met(filter_period))

        db1_goal_fmt = self._format_tied_winners(db1_student_goal_list)
        db2_goal_fmt = self._format_tied_winners(db2_student_goal_list)

        db1_goal_value = db1_student_goal_list[0]['days_met_goal'] if db1_student_goal_list else 0
        db2_goal_value = db2_student_goal_list[0]['days_met_goal'] if db2_student_goal_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Goal Met (Days)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_goal_value,
                'winner_name': db1_goal_fmt['names'],
                'tie_count': db1_goal_fmt['tie_count'],
                'context': db1_goal_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_goal_value,
                'winner_name': db2_goal_fmt['names'],
                'tie_count': db2_goal_fmt['tie_count'],
                'context': db2_goal_fmt['grade_context']
            },
            'change': calc_change(db1_goal_value, db2_goal_value),
            'winner': 'db1' if db1_goal_value > db2_goal_value else ('db2' if db1_goal_value < db2_goal_value else 'tie'),
            'format': 'number'
        })

        # Student - All Days Active (100%)
        db1_student_all_list = db1.execute_query(get_db_comparison_student_all_days_active(filter_period))
        db2_student_all_list = db2.execute_query(get_db_comparison_student_all_days_active(filter_period))

        db1_all_fmt = self._format_tied_winners(db1_student_all_list)
        db2_all_fmt = self._format_tied_winners(db2_student_all_list)

        db1_all_value = db1_student_all_list[0]['days_active'] if db1_student_all_list else 0
        db2_all_value = db2_student_all_list[0]['days_active'] if db2_student_all_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'All Days Active (100%)',
            'honors_filter': True,
            'db1_value': {
                'value': db1_all_value,
                'winner_name': db1_all_fmt['names'],
                'tie_count': db1_all_fmt['tie_count'],
                'context': db1_all_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_all_value,
                'winner_name': db2_all_fmt['names'],
                'tie_count': db2_all_fmt['tie_count'],
                'context': db2_all_fmt['grade_context']
            },
            'change': calc_change(db1_all_value, db2_all_value),
            'winner': 'db1' if db1_all_value > db2_all_value else ('db2' if db1_all_value < db2_all_value else 'tie'),
            'format': 'number'
        })

        # Student - Goal Met All Days
        db1_student_goal_all_list = db1.execute_query(get_db_comparison_student_goal_met_all_days(filter_period))
        db2_student_goal_all_list = db2.execute_query(get_db_comparison_student_goal_met_all_days(filter_period))

        db1_goal_all_fmt = self._format_tied_winners(db1_student_goal_all_list)
        db2_goal_all_fmt = self._format_tied_winners(db2_student_goal_all_list)

        db1_goal_all_value = db1_student_goal_all_list[0]['days_met_goal'] if db1_student_goal_all_list else 0
        db2_goal_all_value = db2_student_goal_all_list[0]['days_met_goal'] if db2_student_goal_all_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Goal Met All Days',
            'honors_filter': True,
            'db1_value': {
                'value': db1_goal_all_value,
                'winner_name': db1_goal_all_fmt['names'],
                'tie_count': db1_goal_all_fmt['tie_count'],
                'context': db1_goal_all_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_goal_all_value,
                'winner_name': db2_goal_all_fmt['names'],
                'tie_count': db2_goal_all_fmt['tie_count'],
                'context': db2_goal_all_fmt['grade_context']
            },
            'change': calc_change(db1_goal_all_value, db2_goal_all_value),
            'winner': 'db1' if db1_goal_all_value > db2_goal_all_value else ('db2' if db1_goal_all_value < db2_goal_all_value else 'tie'),
            'format': 'number'
        })

        # Student - Avg Minutes Per Day
        db1_student_avg_list = db1.execute_query(get_db_comparison_student_avg_minutes_per_day(filter_period))
        db2_student_avg_list = db2.execute_query(get_db_comparison_student_avg_minutes_per_day(filter_period))

        db1_avg_fmt = self._format_tied_winners(db1_student_avg_list)
        db2_avg_fmt = self._format_tied_winners(db2_student_avg_list)

        db1_avg_value = db1_student_avg_list[0]['avg_minutes_per_day'] if db1_student_avg_list else 0
        db2_avg_value = db2_student_avg_list[0]['avg_minutes_per_day'] if db2_student_avg_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Avg Minutes Per Day',
            'honors_filter': True,
            'db1_value': {
                'value': db1_avg_value,
                'winner_name': db1_avg_fmt['names'],
                'tie_count': db1_avg_fmt['tie_count'],
                'context': db1_avg_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_avg_value,
                'winner_name': db2_avg_fmt['names'],
                'tie_count': db2_avg_fmt['tie_count'],
                'context': db2_avg_fmt['grade_context']
            },
            'change': calc_change(db1_avg_value, db2_avg_value),
            'winner': 'db1' if db1_avg_value > db2_avg_value else ('db2' if db1_avg_value < db2_avg_value else 'tie'),
            'format': 'decimal'
        })

        # Student - Total Days Active
        db1_student_days_list = db1.execute_query(get_db_comparison_student_total_days(filter_period))
        db2_student_days_list = db2.execute_query(get_db_comparison_student_total_days(filter_period))

        db1_days_fmt = self._format_tied_winners(db1_student_days_list)
        db2_days_fmt = self._format_tied_winners(db2_student_days_list)

        db1_days_value = db1_student_days_list[0]['total_days'] if db1_student_days_list else 0
        db2_days_value = db2_student_days_list[0]['total_days'] if db2_student_days_list else 0

        comparisons.append({
            'entity_level': 'Student',
            'metric': 'Total Days Active',
            'honors_filter': True,
            'db1_value': {
                'value': db1_days_value,
                'winner_name': db1_days_fmt['names'],
                'tie_count': db1_days_fmt['tie_count'],
                'context': db1_days_fmt['grade_context']
            },
            'db2_value': {
                'value': db2_days_value,
                'winner_name': db2_days_fmt['names'],
                'tie_count': db2_days_fmt['tie_count'],
                'context': db2_days_fmt['grade_context']
            },
            'change': calc_change(db1_days_value, db2_days_value),
            'winner': 'db1' if db1_days_value > db2_days_value else ('db2' if db1_days_value < db2_days_value else 'tie'),
            'format': 'number'
        })

        return {
            'db1_info': db1_info,
            'db2_info': db2_info,
            'filter_period': filter_period,
            'comparisons': comparisons
        }
