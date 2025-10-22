#!/usr/bin/env python3
"""
Initialize Sample Database with Simple Test Data
Run this to set up readathon_sample.db with easy-to-verify data
"""

from database import ReadathonDB

# Sample data
SAMPLE_ROSTER_CSV = """student_name,class_name,home_room,teacher_name,grade_level,team_name
student11,class1,hr1,teacher1,K,team1
student21,class2,hr2,teacher2,1,team1
student22,class2,hr2,teacher2,1,team1
student31,class3,hr3,teacher3,2,team2
student32,class3,hr3,teacher3,2,team2
student41,class4,hr4,teacher4,2,team2
student42,class4,hr4,teacher4,2,team2"""

SAMPLE_CLASS_INFO_CSV = """class_name,home_room,teacher_name,grade_level,team_name,total_students
class1,hr1,teacher1,K,team1,1
class2,hr2,teacher2,1,team1,2
class3,hr3,teacher3,2,team2,2
class4,hr4,teacher4,2,team2,2"""

SAMPLE_GRADE_RULES_CSV = """grade_level,min_daily_minutes,max_daily_minutes_credit
K,20,120
1,20,120
2,25,120"""


def initialize_sample_database():
    """Load simple sample data into the database"""
    print("\n" + "="*60)
    print("INITIALIZING SAMPLE DATABASE")
    print("="*60)
    print("\nLoading simple test data into readathon_sample.db...")

    db = ReadathonDB('readathon_sample.db')

    # Load Class Info
    print("\nLoading Class Info data...")
    count = db.load_class_info_data(SAMPLE_CLASS_INFO_CSV)
    print(f"  ✓ Loaded {count} classes")

    # Load Grade Rules
    print("Loading Grade Rules data...")
    count = db.load_grade_rules_data(SAMPLE_GRADE_RULES_CSV)
    print(f"  ✓ Loaded {count} grade levels")

    # Load Roster
    print("Loading Roster data...")
    count = db.load_roster_data(SAMPLE_ROSTER_CSV)
    print(f"  ✓ Loaded {count} students")

    # Show summary
    print("\n" + "="*60)
    print("SAMPLE DATABASE INITIALIZED SUCCESSFULLY")
    print("="*60)

    counts = db.get_table_counts()
    for table, count in counts.items():
        print(f"{table:20s}: {count:4d} rows")

    print("\n" + "="*60)
    print("SAMPLE DATA STRUCTURE")
    print("="*60)
    print("\nClasses:")
    print("  class1 (K, teacher1, team1): 1 student  - student11")
    print("  class2 (1, teacher2, team1): 2 students - student21, student22")
    print("  class3 (2, teacher3, team2): 2 students - student31, student32")
    print("  class4 (2, teacher4, team2): 2 students - student41, student42")

    print("\nTo upload sample data:")
    print("  1. Switch to 'Sample' environment in the web app")
    print("  2. Upload 'sample_day1_minutes.csv' for date 2024-01-15")
    print("  3. Upload 'sample_day2_minutes.csv' for date 2024-01-16")
    print("  4. Upload 'sample_cumulative.csv' (no date needed)")

    print("\nExpected Results:")
    print("  Day 1: All 7 students have data")
    print("  Day 2: Only 6 students (student11 missing - penalty!)")
    print("  Cumulative: Minutes match sum of both days")
    print("  Donations: student11=$10, student21=$20, ..., student42=$70")

    db.close()


if __name__ == "__main__":
    initialize_sample_database()
