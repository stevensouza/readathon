"""
Initialize SAMPLE database with simple test data
This creates a minimal dataset for easy verification
"""

from database import ReadathonDB

# Simple sample data
CLASS_INFO_CSV = """class_name,home_room,teacher_name,grade_level,team_name,total_students
class1,101,teacher1,K,team1,3
class2,102,teacher2,1,team1,3
class3,201,teacher3,2,team2,3
class4,202,teacher4,3,team2,3"""

GRADE_RULES_CSV = """grade_level,min_daily_minutes,max_daily_minutes_credit
K,20,120
1,20,120
2,25,120
3,25,120"""

ROSTER_CSV = """student_name,class_name,home_room,teacher_name,grade_level,team_name
Student1,class1,101,teacher1,K,team1
Student2,class1,101,teacher1,K,team1
Student3,class1,101,teacher1,K,team1
Student4,class2,102,teacher2,1,team1
Student5,class2,102,teacher2,1,team1
Student6,class2,102,teacher2,1,team1
Student7,class3,201,teacher3,2,team2
Student8,class3,201,teacher3,2,team2
Student9,class3,201,teacher3,2,team2
Student10,class4,202,teacher4,3,team2
Student11,class4,202,teacher4,3,team2
Student12,class4,202,teacher4,3,team2"""


def initialize_sample_database():
    """Load simple sample data into the sample database"""
    print("Initializing SAMPLE database with simple test data...")

    db = ReadathonDB('readathon_sample.db')

    # Load Class Info
    print("Loading Class Info data...")
    count = db.load_class_info_data(CLASS_INFO_CSV)
    print(f"  ✓ Loaded {count} classes")

    # Load Grade Rules
    print("Loading Grade Rules data...")
    count = db.load_grade_rules_data(GRADE_RULES_CSV)
    print(f"  ✓ Loaded {count} grade levels")

    # Load Roster
    print("Loading Roster data...")
    count = db.load_roster_data(ROSTER_CSV)
    print(f"  ✓ Loaded {count} students")

    # Initialize sample Reader_Cumulative data
    print("Initializing sample Reader_Cumulative data...")
    conn = db.get_connection()
    cursor = conn.cursor()

    from datetime import datetime
    timestamp = datetime.now().isoformat()

    # Add cumulative stats for all students
    sample_cumulative_data = [
        ('Student1', 'teacher1', 'team1', 25.50, 2, 180, timestamp),
        ('Student2', 'teacher1', 'team1', 50.00, 3, 240, timestamp),
        ('Student3', 'teacher1', 'team1', 15.75, 1, 120, timestamp),
        ('Student4', 'teacher2', 'team1', 100.00, 5, 300, timestamp),
        ('Student5', 'teacher2', 'team1', 75.25, 4, 360, timestamp),
        ('Student6', 'teacher2', 'team1', 30.00, 2, 180, timestamp),
        ('Student7', 'teacher3', 'team2', 125.50, 6, 420, timestamp),
        ('Student8', 'teacher3', 'team2', 200.00, 8, 480, timestamp),
        ('Student9', 'teacher3', 'team2', 60.00, 3, 240, timestamp),
        ('Student10', 'teacher4', 'team2', 150.00, 7, 540, timestamp),
        ('Student11', 'teacher4', 'team2', 90.50, 4, 300, timestamp),
        ('Student12', 'teacher4', 'team2', 45.00, 2, 180, timestamp),
    ]

    for student_name, teacher, team, donation, sponsors, minutes, ts in sample_cumulative_data:
        cursor.execute("""
            INSERT INTO Reader_Cumulative
            (student_name, teacher_name, team_name, donation_amount, sponsors, cumulative_minutes, upload_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_name, teacher, team, donation, sponsors, minutes, ts))

    conn.commit()
    print(f"  ✓ Loaded {len(sample_cumulative_data)} cumulative records")

    # Show summary
    print("\n" + "="*50)
    print("SAMPLE DATABASE INITIALIZED SUCCESSFULLY")
    print("="*50)

    counts = db.get_table_counts()
    for table, count in counts.items():
        print(f"{table:20s}: {count:4d} rows")

    print("\nSample Data Summary:")
    print("  - 12 students (Student1 through Student12)")
    print("  - 4 classes (class1 through class4)")
    print("  - 4 teachers (teacher1 through teacher4)")
    print("  - 2 teams (team1 and team2)")
    print("  - Grades K through 3")
    print("  - Reader_Cumulative initialized with fundraising data")
    print("\nReady to upload sample daily minutes!")
    print("Use: sample_day1_minutes.csv")
    print("\nNote: Donations are now in Reader_Cumulative table (uploaded separately)")

    db.close()


if __name__ == "__main__":
    initialize_sample_database()
