"""
Initialize database with school roster data from CSV files

This script reads from external CSV files (not included in the repository)
to populate the database with your school's specific data.

Required CSV files (must be in the same directory as this script):
- class_info.csv
- grade_rules.csv
- roster.csv

Usage:
    python3 init_data.py 2026     # creates db/readathon_2026.db and registers it as "2026 Read-a-Thon"

The same thing can be done from the web app: Admin -> Database Registry -> Create New Database.

CSV Format Requirements:
- class_info.csv: class_name,home_room,teacher_name,grade_level,team_name,total_students
- grade_rules.csv: grade_level,min_daily_minutes,max_daily_minutes_credit
- roster.csv: student_name,class_name,home_room,teacher_name,grade_level,team_name
"""

import os
import sys
from database import ReadathonDB, DatabaseRegistry


def read_csv_file(filename):
    """Read CSV file and return contents as string"""
    if not os.path.exists(filename):
        print(f"❌ ERROR: Required file '{filename}' not found!")
        print(f"   Please create this file in the same directory as init_data.py")
        return None

    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def initialize_database_from_files(year):
    """Load data from CSV files into the database"""
    print("="*60)
    print("Read-a-Thon Database Initialization")
    print("="*60)
    print()

    # Check for required files
    required_files = {
        'class_info.csv': 'Class information (teacher assignments, teams)',
        'grade_rules.csv': 'Grade-specific reading goals',
        'roster.csv': 'Student roster with class assignments'
    }

    print("Checking for required CSV files...")
    missing_files = []
    for filename, description in required_files.items():
        if os.path.exists(filename):
            print(f"  ✓ Found {filename}")
        else:
            print(f"  ❌ Missing {filename} - {description}")
            missing_files.append(filename)

    if missing_files:
        print()
        print("="*60)
        print("❌ INITIALIZATION FAILED")
        print("="*60)
        print()
        print("Please create the following CSV files:")
        for filename in missing_files:
            print(f"  - {filename}")
        print()
        print("See README.md for CSV format requirements and examples.")
        sys.exit(1)

    db_filename = f'readathon_{year}.db'
    db_name = f'db/{db_filename}'
    if os.path.exists(db_name):
        print(f"❌ ERROR: {db_name} already exists. Refusing to overwrite it.")
        sys.exit(1)

    print()
    print(f"Initializing database: {db_name}")
    print()

    # Read CSV files
    class_info_csv = read_csv_file('class_info.csv')
    grade_rules_csv = read_csv_file('grade_rules.csv')
    roster_csv = read_csv_file('roster.csv')

    if not all([class_info_csv, grade_rules_csv, roster_csv]):
        sys.exit(1)

    # Initialize database
    db = ReadathonDB(db_name)

    # Load Class Info
    print("Loading Class Info data...")
    count = db.load_class_info_data(class_info_csv)
    print(f"  ✓ Loaded {count} classes")

    # Load Grade Rules
    print("Loading Grade Rules data...")
    count = db.load_grade_rules_data(grade_rules_csv)
    print(f"  ✓ Loaded {count} grade levels")

    # Load Roster
    print("Loading Roster data...")
    count = db.load_roster_data(roster_csv)
    print(f"  ✓ Loaded {count} students")

    # Show summary
    print()
    print("="*60)
    print("✅ DATABASE INITIALIZED SUCCESSFULLY")
    print("="*60)
    print()

    counts = db.get_table_counts()
    for table, count in counts.items():
        print(f"{table:20s}: {count:4d} rows")

    student_count = counts.get('Roster', 0)
    db.close()

    # Register in the central registry so it appears in the app's database dropdown
    registry = DatabaseRegistry()
    db_id = registry.register_database(db_filename, f'{year} Read-a-Thon', int(year),
                                       f'{year} read-a-thon database')
    registry.update_stats(db_id, student_count=student_count, total_days=0, total_donations=0.0)
    registry.close()
    print(f"Registered as: {year} Read-a-Thon")

    print()
    print("Next steps:")
    print(f'  1. Start the web application: python3 app.py --db "{year} Read-a-Thon"')
    print("  2. Navigate to: http://127.0.0.1:5001")
    print("  3. Upload daily reading data via the Upload Data page")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or len(sys.argv[1]) != 4:
        print("Usage: python3 init_data.py <year>   (e.g. python3 init_data.py 2026)")
        sys.exit(1)
    initialize_database_from_files(sys.argv[1])
