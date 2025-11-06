"""
Initialize database with school roster data from CSV files

This script reads from external CSV files (not included in the repository)
to populate the database with your school's specific data.

Required CSV files (must be in the same directory as this script):
- class_info.csv
- grade_rules.csv
- roster.csv

CSV Format Requirements:
- class_info.csv: class_name,home_room,teacher_name,grade_level,team_name,total_students
- grade_rules.csv: grade_level,min_daily_minutes,max_daily_minutes_credit
- roster.csv: student_name,class_name,home_room,teacher_name,grade_level,team_name
"""

import os
import sys
from database import ReadathonDB


def read_csv_file(filename):
    """Read CSV file and return contents as string"""
    if not os.path.exists(filename):
        print(f"❌ ERROR: Required file '{filename}' not found!")
        print(f"   Please create this file in the same directory as init_data.py")
        return None

    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def initialize_database_from_files(db_name='db/readathon_prod.db'):
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

    print()
    print("Next steps:")
    print("  1. Start the web application: python3 app.py")
    print("  2. Navigate to: http://localhost:5000")
    print("  3. Upload daily reading data via the Upload Data page")
    print()

    db.close()


if __name__ == "__main__":
    initialize_database_from_files()
