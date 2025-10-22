"""
Enhanced Report Metadata Module

Provides column descriptions, terms glossary, and analysis generators
for all Read-a-Thon reports.

Usage:
    from report_metadata import COLUMN_METADATA, get_relevant_terms, generate_q21_analysis
"""

from typing import Dict, Any, List, Optional

# ============================================================================
# GLOBAL TERMS GLOSSARY
# ============================================================================

GLOBAL_TERMS = {
    # ===== CORE CONTEST CONCEPTS =====
    'Cap / Capped / Maximum Minutes': {
        'definition': 'The maximum number of reading minutes per day that count toward the contest. Students can read more, but only the capped amount counts toward totals and goals. The cap is 120 minutes for most grades but varies by grade level (see Grade Level). For example, if a student reads 150 minutes, only 120 count.',
        'see_also': ['Goal', 'Grade Level', 'Capping / 120-Minute Daily Cap Exceeded']
    },
    'Capping / 120-Minute Daily Cap Exceeded': {
        'definition': 'When students read more than the 120-minute daily maximum, they have "exceeded the cap." The official Daily_Logs counting caps their credit at 120 minutes per day, but Reader_Cumulative may store the uncapped total. The difference between capped and uncapped totals reveals how many minutes students read beyond the daily limit. Also called "capping effect."',
        'see_also': ['Cap / Capped / Maximum Minutes', 'Daily Logs', 'Reader Cumulative']
    },
    'Class': {
        'definition': "A teacher's homeroom or group of students. Each class is assigned to one of two teams (Kitsko or Staub) to balance competition. Classes are led by teachers and include students across different grade levels in some cases.",
        'see_also': ['Teacher', 'Team']
    },
    'Contest Period': {
        'definition': 'The official dates for the read-a-thon (typically a 6-10 day period in mid-October). The actual date range shown in reports reflects the dates present in Daily_Logs uploads. Only reading during sanctioned contest dates counts toward contest totals, participation rates, team competition, and individual prizes. This is also referred to as "sanctioned dates."',
        'see_also': ['Sanctioned Dates', 'Out-of-Range']
    },
    'Cumulative': {
        'definition': 'A running total across all days. Cumulative minutes is the sum of all daily reading time for a student. Cumulative stats include total minutes read and total donations raised, updated throughout the contest.',
        'see_also': ['Reader Cumulative']
    },
    'Goal / Minimum Minutes': {
        'definition': 'The daily reading target for students, which varies by grade level. Students who meet or exceed their goal each day are eligible for prizes and recognition. For example, kindergarten students might have a 20-minute daily goal while 5th graders have a 60-minute goal. Also called "minimum minutes."',
        'see_also': ['Grade Level', 'Participation']
    },
    'Grade Level': {
        'definition': "The student's grade in school (K-5). Grade level determines both the minimum minutes (goal) and maximum minutes (cap) for daily reading. For example: K might be 20-60 minutes, 1st grade 30-80 minutes, 5th grade 60-120 minutes. Check Grade_Rules table for specific values.",
        'see_also': ['Goal', 'Cap']
    },
    'Participation': {
        'definition': 'When a student reads and logs at least 1 minute on a given day, they are considered "participating" that day. Participation rate is the percentage of students who participated on a day, or the percentage of days a student participated. High participation is a key contest metric.',
        'see_also': ['Reader', 'Goal']
    },
    'Reader / Student': {
        'definition': 'A student participating in the read-a-thon. "Reader" and "student" are used interchangeably. All students are listed in the Roster, but only those who log reading minutes become active readers.',
        'see_also': ['Participation', 'Roster']
    },
    'Sanctioned Dates': {
        'definition': 'The official contest dates (typically a 6-10 day period in mid-October) when reading counts toward the competition. Same as "contest period." Only reading on sanctioned dates is included in Daily_Logs and counts toward participation, team competition, and individual prizes. The losing team captain must perform a fun consequence (like dressing in costume).',
        'see_also': ['Contest Period', 'Out-of-Range']
    },
    'Team': {
        'definition': 'One of two groups (Kitsko or Staub) that students are divided into for friendly competition. The school is split roughly in half, with classes assigned to balance the teams. Teams compete for total minutes read, participation rates, and fundraising.',
        'see_also': ['Class']
    },
    'Teacher': {
        'definition': 'An educator who leads a class. Teachers are assigned students, and their classes are assigned to teams. Teacher names are used to identify classes (e.g., "Mrs. Spencer\'s class").',
        'see_also': ['Class']
    },

    # ===== DATA & TECHNICAL TERMS =====
    'Daily Logs': {
        'definition': 'The Daily_Logs database table containing day-by-day reading records. Each row represents one student\'s reading on one specific date, showing how many minutes they read. This is downloaded from the online system as separate daily report files and only includes sanctioned contest dates.',
        'see_also': ['Reader Cumulative', 'Sanctioned Dates']
    },
    'Discrepancy': {
        'definition': "When numbers don't match between different data sources or tables. For example, when the sum of a student's daily minutes doesn't equal their cumulative minutes total. This report identifies and explains discrepancies to help maintain data quality.",
        'see_also': ['Difference']
    },
    'Donations / Sponsors': {
        'definition': 'Money raised through the read-a-thon. Sponsors pledge to donate based on minutes read (e.g., $0.10 per minute) or make flat donations. Total donations per student are tracked in Reader_Cumulative and are a key fundraising metric alongside reading minutes.',
        'see_also': ['Reader Cumulative']
    },
    'Download / Upload': {
        'definition': 'Data files received from the online read-a-thon tracking system. "Download" is from the system\'s perspective (we download their files), "upload" is when we load them into our database. We download two types: daily logs (one file per day) and cumulative stats (running totals).',
        'see_also': ['Daily Logs', 'Reader Cumulative']
    },
    'Out-of-Range': {
        'definition': 'Reading entries for dates outside the official contest period. These appear in Reader_Cumulative totals if parents entered them, but they don\'t appear in Daily_Logs and don\'t count toward the contest. This is a common cause of discrepancies.',
        'see_also': ['Contest Period', 'Sanctioned Dates', 'Discrepancy']
    },
    'Reader Cumulative': {
        'definition': 'The Reader_Cumulative database table containing summary totals for each student: total cumulative minutes read, total donations raised, and sponsor information. Downloaded as a single cumulative stats file from the online system. May include minutes from non-sanctioned dates if parents entered them.',
        'see_also': ['Daily Logs', 'Cumulative']
    },
    'Roster': {
        'definition': 'The master list of all students in the school, stored in the Roster database table. Includes each student\'s name, class, teacher, team, and grade level. This is the authoritative source for student information and is used to join data from Daily_Logs and Reader_Cumulative.',
        'see_also': ['Student']
    },
}

# ============================================================================
# COLUMN METADATA BY REPORT
# ============================================================================

COLUMN_METADATA = {
    # Q1: Table Counts
    'q1': {
        'table_name': {
            'source': 'Database tables',
            'description': 'The name of the database table'
        },
        'row_count': {
            'source': 'COUNT(*)',
            'formula': '[calculated]',
            'description': 'The number of rows currently in this table'
        }
    },

    # Q2: Daily Summary Report
    'q2': {
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to. Classes are assigned to teams for competition'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher who leads this class'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this class (K-5). Grade determines daily reading goals and caps'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this class is competing for (Kitsko or Staub)'
        },
        'total_students': {
            'source': 'Class_Info.total_students',
            'description': 'The number of students enrolled in this class according to the roster'
        },
        'days_with_data': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT log_date)',
            'description': 'The number of days for which reading data has been uploaded. This defines the contest period for this report'
        },
        'total_participations': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT student-day combinations)',
            'description': 'The total number of student-day instances where a student read at least 1 minute. If 20 students read on 5 days, this could be up to 100 participations'
        },
        'participation_rate': {
            'source': 'Calculated',
            'formula': '(total_participations / (total_students * days_with_data)) * 100',
            'description': 'The percentage of possible participation opportunities that were completed. 100% means every student participated every day. Expressed as a percentage (0-100)'
        },
        'student_count_met_goal_any_day': {
            'source': 'Daily_Logs + Grade_Rules',
            'formula': 'COUNT(DISTINCT students where minutes_read >= min_daily_minutes on any day)',
            'description': 'The number of unique students who met their grade-level reading goal on at least one day during the contest period'
        },
        'student_count_met_goal_all_days': {
            'source': 'Daily_Logs + Grade_Rules',
            'formula': 'COUNT(DISTINCT students where days_met_goal = total_days)',
            'description': 'The number of students who met their grade-level reading goal on every single day of the contest. These are "perfect attendance goal-getters"'
        },
        'total_minutes': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(MIN(minutes_read, 120))',
            'description': 'Total reading minutes for this class with the 120-minute daily cap applied. This is the official count for team competition'
        }
    },

    # Q3: Reader Cumulative Enhanced
    'q3': {
        'student_name': {
            'source': 'Reader_Cumulative.student_name',
            'description': "The student's full name as it appears in the cumulative stats download"
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'teacher_name': {
            'source': 'Reader_Cumulative.teacher_name',
            'description': 'The name of the teacher for this student (from cumulative download)'
        },
        'team_name': {
            'source': 'Reader_Cumulative.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'days_participated': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(CASE WHEN minutes_read > 0)',
            'description': 'The number of days this student logged at least 1 minute of reading'
        },
        'days_met_goal': {
            'source': 'Daily_Logs + Grade_Rules',
            'formula': 'SUM(CASE WHEN minutes_read >= min_daily_minutes)',
            'description': 'The number of days this student met or exceeded their grade-level daily reading goal'
        },
        'cumulative_minutes': {
            'source': 'Reader_Cumulative.cumulative_minutes',
            'description': 'Total minutes reported in the cumulative download. May include out-of-range dates if parents entered them'
        },
        'donation_amount': {
            'source': 'Reader_Cumulative.donation_amount',
            'description': 'Total money raised by this student through sponsors and pledges'
        },
        'sponsors': {
            'source': 'Reader_Cumulative.sponsors',
            'description': 'The number of sponsors supporting this student'
        }
    },

    # Q4: Prize Drawing
    'q4': {
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name"
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher for this student'
        },
        'minutes_read': {
            'source': 'Daily_Logs.minutes_read',
            'description': 'The number of minutes this student read on the selected date (uncapped)'
        },
        'min_daily_minutes': {
            'source': 'Grade_Rules.min_daily_minutes',
            'description': 'The daily reading goal for this student based on their grade level. Students in this report met or exceeded this goal'
        }
    },

    # Q5: Student Cumulative Report
    'q5': {
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name"
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'days_participated': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(CASE WHEN minutes_read > 0)',
            'description': 'The number of days this student logged at least 1 minute of reading'
        },
        'total_minutes_credited': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(MIN(minutes_read, 120))',
            'description': 'Total reading minutes with the 120-minute daily cap applied. This is the official credited amount for team competition'
        },
        'total_minutes_actual': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(minutes_read)',
            'description': 'Total reading minutes without any cap applied. Shows how much the student actually read, even if it exceeds daily caps'
        },
        'days_met_goal': {
            'source': 'Daily_Logs + Grade_Rules',
            'formula': 'SUM(CASE WHEN minutes_read >= min_daily_minutes)',
            'description': 'The number of days this student met or exceeded their grade-level daily reading goal'
        },
        'total_donations': {
            'source': 'Reader_Cumulative.donation_amount',
            'description': 'Total money raised by this student. Shows 0 if no fundraising data exists'
        },
        'total_sponsors': {
            'source': 'Reader_Cumulative.sponsors',
            'description': 'The number of sponsors supporting this student. Shows 0 if no fundraising data exists'
        }
    },

    # Q6: Class Participation
    'q6': {
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher who leads this class'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this class (K-5)'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this class is competing for (Kitsko or Staub)'
        },
        'total_students': {
            'source': 'Class_Info.total_students',
            'description': 'The number of students enrolled in this class'
        },
        'days_with_data': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT log_date)',
            'description': 'The number of days for which reading data has been uploaded'
        },
        'total_participations_base': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT student-day combinations)',
            'description': 'Total student-day instances where a student read at least 1 minute, before team color bonuses'
        },
        'color_bonus_points': {
            'source': 'Team_Color_Bonus',
            'formula': 'SUM(bonus_participation_points)',
            'description': 'Bonus participation points awarded for team color day events. Shows 0 if no bonuses have been awarded'
        },
        'total_participations_with_color': {
            'source': 'Calculated',
            'formula': 'total_participations_base + color_bonus_points',
            'description': 'Total participations including team color day bonuses. This is the official count for class participation competition'
        },
        'avg_participation_rate': {
            'source': 'Calculated',
            'formula': '(total_participations_base / (total_students * days_with_data)) * 100',
            'description': 'Base participation rate as a percentage, before team color bonuses'
        },
        'avg_participation_rate_with_color': {
            'source': 'Calculated',
            'formula': '(total_participations_with_color / (total_students * days_with_data)) * 100',
            'description': 'Official participation rate including team color bonuses. Classes are ranked by this metric'
        }
    },

    # Q7: Complete Log
    'q7': {
        'log_date': {
            'source': 'Daily_Logs.log_date',
            'description': 'The date this reading activity was logged (YYYY-MM-DD format)'
        },
        'student_name': {
            'source': 'Daily_Logs.student_name',
            'description': "The student's full name"
        },
        'minutes_read': {
            'source': 'Daily_Logs.minutes_read',
            'description': 'The number of minutes this student read on this date (uncapped)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        },
        'home_room': {
            'source': 'Roster.home_room',
            'description': 'The physical room number or location for this class'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher for this student'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        }
    },

    # Q8: Student Reading Details
    'q8': {
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name"
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher for this student'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'total_minutes_read': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(minutes_read)',
            'description': 'Total reading minutes for this student (uncapped). Only includes students who actually participated'
        },
        'days_met_goal': {
            'source': 'Daily_Logs + Grade_Rules',
            'formula': 'SUM(CASE WHEN minutes_read >= min_daily_minutes)',
            'description': 'The number of days this student met or exceeded their grade-level daily reading goal'
        },
        'days_participated': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(CASE WHEN minutes_read > 0)',
            'description': 'The number of days this student logged at least 1 minute of reading'
        }
    },

    # Q9: Most Donations by Grade
    'q9': {
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level (K-5)'
        },
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name. This student has the highest donations in their grade"
        },
        'donation_amount': {
            'source': 'Reader_Cumulative.donation_amount',
            'description': 'Total money raised by this student - the maximum for their grade level'
        },
        'sponsors': {
            'source': 'Reader_Cumulative.sponsors',
            'description': 'The number of sponsors supporting this student'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        }
    },

    # Q10: Most Minutes by Grade
    'q10': {
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level (K-5)'
        },
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name. This student has the most reading minutes in their grade"
        },
        'total_minutes_capped': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(MIN(minutes_read, 120))',
            'description': 'Total reading minutes with 120-minute daily cap applied - the maximum for their grade level. This is the official credited amount'
        },
        'days_participated': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(CASE WHEN minutes_read > 0)',
            'description': 'The number of days this student logged at least 1 minute of reading'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        }
    },

    # Q11: Most Sponsors by Grade
    'q11': {
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level (K-5)'
        },
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name. This student has the most sponsors in their grade"
        },
        'sponsor_count': {
            'source': 'Reader_Cumulative.sponsors',
            'description': 'The number of sponsors supporting this student - the maximum for their grade level'
        },
        'donation_amount': {
            'source': 'Reader_Cumulative.donation_amount',
            'description': 'Total money raised by this student from all sponsors'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        }
    },

    # Q12: Best Class by Grade
    'q12': {
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level (K-5)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class. This class has the highest participation rate in their grade'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher who leads this class'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this class is competing for (Kitsko or Staub)'
        },
        'total_participations_base': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT student-day combinations)',
            'description': 'Total student-day instances where a student read at least 1 minute, before team color bonuses'
        },
        'color_bonus_points': {
            'source': 'Team_Color_Bonus',
            'formula': 'SUM(bonus_participation_points)',
            'description': 'Bonus participation points awarded for team color day events'
        },
        'avg_participation_rate': {
            'source': 'Calculated',
            'formula': '(total_participations_base / (total_students * days_with_data)) * 100',
            'description': 'Base participation rate as a percentage, before team color bonuses'
        },
        'avg_participation_rate_with_color': {
            'source': 'Calculated',
            'formula': '(total_participations_with_color / (total_students * days_with_data)) * 100',
            'description': 'Official participation rate including team color bonuses - the maximum for their grade level'
        }
    },

    # Q13: Overall Best Class
    'q13': {
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher who leads this class'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this class (K-5)'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this class is competing for (Kitsko or Staub)'
        },
        'total_participations_base': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT student-day combinations)',
            'description': 'Total student-day instances where a student read at least 1 minute, before team color bonuses'
        },
        'color_bonus_points': {
            'source': 'Team_Color_Bonus',
            'formula': 'SUM(bonus_participation_points)',
            'description': 'Bonus participation points awarded for team color day events'
        },
        'avg_participation_rate': {
            'source': 'Calculated',
            'formula': '(total_participations_base / (total_students * days_with_data)) * 100',
            'description': 'Base participation rate as a percentage, before team color bonuses'
        },
        'avg_participation_rate_with_color': {
            'source': 'Calculated',
            'formula': '(total_participations_with_color / (total_students * days_with_data)) * 100',
            'description': 'Official participation rate including team color bonuses. Classes are sorted by this value (highest first)'
        }
    },

    # Q14: Team Participation
    'q14': {
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team name (Kitsko or Staub)'
        },
        'total_students': {
            'source': 'Roster',
            'formula': 'COUNT(DISTINCT student_name)',
            'description': 'The total number of students assigned to this team'
        },
        'days_with_data': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT log_date)',
            'description': 'The number of days for which reading data has been uploaded'
        },
        'total_participations_base': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT student-day combinations)',
            'description': 'Total student-day instances where a student read at least 1 minute, before team color bonuses'
        },
        'color_bonus_points': {
            'source': 'Team_Color_Bonus',
            'formula': 'SUM(bonus_participation_points) for team',
            'description': 'Total bonus participation points awarded to all classes on this team for team color day events'
        },
        'total_participations_with_color': {
            'source': 'Calculated',
            'formula': 'total_participations_base + color_bonus_points',
            'description': 'Total participations including team color day bonuses. This is the official count for team participation competition'
        },
        'avg_participation_rate': {
            'source': 'Calculated',
            'formula': '(total_participations_base / (total_students * days_with_data)) * 100',
            'description': 'Base participation rate as a percentage, before team color bonuses'
        },
        'avg_participation_rate_with_color': {
            'source': 'Calculated',
            'formula': '(total_participations_with_color / (total_students * days_with_data)) * 100',
            'description': 'Official participation rate including team color bonuses. Teams are ranked by this metric'
        }
    },

    # Q15: Goal Getters
    'q15': {
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name. This student met their reading goal every single day"
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'days_met_goal': {
            'source': 'Daily_Logs + Grade_Rules',
            'formula': 'SUM(CASE WHEN minutes_read >= min_daily_minutes)',
            'description': 'The number of days this student met their goal - equals total_days for all students in this report'
        },
        'total_days': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT log_date)',
            'description': 'The total number of contest days. Students in this report participated and met their goal on all of these days'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        }
    },

    # Q16: Top Earner Per Team
    'q16': {
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team name (Kitsko or Staub)'
        },
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name. This student raised the most money on their team"
        },
        'donation_amount': {
            'source': 'Reader_Cumulative.donation_amount',
            'description': 'Total money raised by this student - the maximum for their team'
        },
        'sponsors': {
            'source': 'Reader_Cumulative.sponsors',
            'description': 'The number of sponsors supporting this student'
        },
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level for this student (K-5)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to'
        }
    },

    # Q18: Lead Class by Grade
    'q18': {
        'grade_level': {
            'source': 'Roster.grade_level',
            'description': 'The grade level (K-5)'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class. This class has the highest participation rate in their grade'
        },
        'teacher_name': {
            'source': 'Roster.teacher_name',
            'description': 'The name of the teacher who leads this class'
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this class is competing for (Kitsko or Staub)'
        },
        'total_students': {
            'source': 'Class_Info.total_students',
            'description': 'The number of students enrolled in this class'
        },
        'days_with_data': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT log_date)',
            'description': 'The number of days for which reading data has been uploaded'
        },
        'total_participations_base': {
            'source': 'Daily_Logs',
            'formula': 'COUNT(DISTINCT student-day combinations)',
            'description': 'Total student-day instances where a student read at least 1 minute, before team color bonuses'
        },
        'color_bonus_points': {
            'source': 'Team_Color_Bonus',
            'formula': 'SUM(bonus_participation_points)',
            'description': 'Bonus participation points awarded for team color day events'
        },
        'total_participations_with_color': {
            'source': 'Calculated',
            'formula': 'total_participations_base + color_bonus_points',
            'description': 'Total participations including team color day bonuses'
        },
        'avg_participation_rate': {
            'source': 'Calculated',
            'formula': '(total_participations_base / (total_students * days_with_data)) * 100',
            'description': 'Base participation rate as a percentage, before team color bonuses'
        },
        'avg_participation_rate_with_color': {
            'source': 'Calculated',
            'formula': '(total_participations_with_color / (total_students * days_with_data)) * 100',
            'description': 'Official participation rate including team color bonuses - the maximum for their grade level'
        }
    },

    # Q19: Team Minutes
    'q19': {
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team name (Kitsko, Staub, or TOTAL for school-wide sum)'
        },
        'total_students': {
            'source': 'Roster',
            'formula': 'COUNT(DISTINCT student_name)',
            'description': 'The total number of students assigned to this team (or all students for TOTAL row)'
        },
        'total_minutes_base': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(MIN(minutes_read, 120))',
            'description': 'Total reading minutes with 120-minute daily cap applied, before team color bonuses'
        },
        'total_hours_base': {
            'source': 'Calculated',
            'formula': 'total_minutes_base / 60',
            'description': 'Total reading hours (base minutes divided by 60), before team color bonuses'
        },
        'bonus_minutes': {
            'source': 'Team_Color_Bonus',
            'formula': 'SUM(bonus_minutes) for team',
            'description': 'Bonus minutes awarded to all classes on this team for team color day events'
        },
        'total_minutes_with_color': {
            'source': 'Calculated',
            'formula': 'total_minutes_base + bonus_minutes',
            'description': 'Official total minutes including team color bonuses. This is the final count for team competition'
        },
        'total_hours_with_color': {
            'source': 'Calculated',
            'formula': 'total_minutes_with_color / 60',
            'description': 'Official total hours including team color bonuses'
        },
        'avg_minutes_per_student': {
            'source': 'Calculated',
            'formula': 'total_minutes_base / total_students',
            'description': 'Average reading minutes per student on this team, before team color bonuses'
        },
        'avg_minutes_per_student_with_color': {
            'source': 'Calculated',
            'formula': 'total_minutes_with_color / total_students',
            'description': 'Official average minutes per student including team color bonuses'
        }
    },

    # Q20: Team Donations
    'q20': {
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team name (Kitsko or Staub)'
        },
        'total_donations': {
            'source': 'Reader_Cumulative.donation_amount',
            'formula': 'SUM(donation_amount)',
            'description': 'Total money raised by all students on this team'
        },
        'total_sponsors': {
            'source': 'Reader_Cumulative.sponsors',
            'formula': 'SUM(sponsors)',
            'description': 'Total number of sponsors across all students on this team'
        },
        'total_students': {
            'source': 'Roster',
            'formula': 'COUNT(DISTINCT student_name)',
            'description': 'The total number of students assigned to this team'
        },
        'avg_donation_per_student': {
            'source': 'Calculated',
            'formula': 'total_donations / total_students',
            'description': 'Average fundraising per student on this team. Calculated by dividing total donations by total students'
        }
    },

    # Q21: Data Sync & Minutes Integrity Check
    'q21': {
        'student_name': {
            'source': 'Roster.student_name',
            'description': "The student's full name as it appears in school records"
        },
        'team_name': {
            'source': 'Roster.team_name',
            'description': 'The team this student is competing for (Kitsko or Staub). The school is divided into two teams to create friendly competition'
        },
        'class_name': {
            'source': 'Roster.class_name',
            'description': 'The teacher or homeroom class this student belongs to. Classes are assigned to teams'
        },
        'daily_minutes_sum': {
            'source': 'Daily_Logs.minutes_read',
            'formula': 'SUM(...) [calculated]',
            'description': 'The total uncapped minutes this student read across all contest days (10/10-10/15), calculated by adding up their daily reading time for each day they participated. This includes minutes over the 120-minute daily cap. Value is 0 if student has no daily logs'
        },
        'cumulative_minutes': {
            'source': 'Reader_Cumulative.cumulative_minutes',
            'description': 'The total minutes reported in the cumulative download from the online tracking system. May include reading from dates outside the official contest period if parents entered data for non-sanctioned dates. Value is 0 if student is not in Reader_Cumulative'
        },
        'difference': {
            'source': 'Cumulative - Daily',
            'formula': '[calculated]',
            'description': 'The difference between cumulative minutes and daily minutes sum. Positive means cumulative is higher (out-of-range dates or student missing from daily logs). Negative means daily is higher (cap differences or student missing from cumulative). Zero means perfect match or both are zero'
        },
        'status': {
            'source': 'CASE WHEN...',
            'formula': '[calculated]',
            'description': 'The data integrity status: OK (values match perfectly), MINUTES_MISMATCH (student in both tables but values differ), MISSING_CUMULATIVE (has daily logs but not in Reader_Cumulative), MISSING_DAILY (in Reader_Cumulative but no daily logs), or NO_DATA (no activity - filtered out)'
        }
    },

    # Q22: Student Name Sync Check
    'q22': {
        'student_name': {
            'source': 'Daily_Logs / Reader_Cumulative',
            'description': "The student's name as it appears in either table"
        },
        'status': {
            'source': 'CASE WHEN...',
            'formula': '[calculated]',
            'description': 'Sync status: OK (in both tables), IN_DAILY_ONLY (only in Daily_Logs), or IN_CUMULATIVE_ONLY (only in Reader_Cumulative)'
        },
        'in_daily_logs': {
            'source': 'Daily_Logs',
            'formula': '[calculated]',
            'description': 'Yes if student has entries in Daily_Logs with reading minutes > 0, No otherwise'
        },
        'in_reader_cumulative': {
            'source': 'Reader_Cumulative',
            'formula': '[calculated]',
            'description': 'Yes if student has an entry in Reader_Cumulative with cumulative minutes > 0, No otherwise'
        }
    },

    # Q23: Roster Integrity Check
    'q23': {
        'student_name': {
            'source': 'Daily_Logs / Reader_Cumulative',
            'description': 'The student name found in Daily_Logs or Reader_Cumulative'
        },
        'found_in_table': {
            'source': 'Daily_Logs / Reader_Cumulative',
            'description': 'Which table this student was found in: Daily_Logs or Reader_Cumulative'
        },
        'status': {
            'source': 'Roster lookup',
            'formula': '[calculated]',
            'description': 'OK if student exists in Roster, MISSING_FROM_ROSTER if they have reading data but no roster entry'
        }
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_relevant_terms(term_keys: List[str]) -> Dict[str, Any]:
    """
    Get a subset of the global terms glossary

    Args:
        term_keys: List of term names to include

    Returns:
        Dictionary of {term_name: term_data} for requested terms
    """
    return {k: v for k, v in GLOBAL_TERMS.items() if k in term_keys}


def get_all_terms() -> Dict[str, Any]:
    """Get the complete global terms glossary"""
    return GLOBAL_TERMS.copy()


# ============================================================================
# ANALYSIS GENERATORS
# ============================================================================

def generate_q21_analysis(results: List[Dict[str, Any]], date_range: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Generate analysis section for Q21: Data Sync & Minutes Integrity Check

    Analyzes the 922-minute reconciliation difference between capped Daily_Logs and uncapped Reader_Cumulative.
    Breaks down into: (1) Capping Effect - students exceeding 120 min/day cap, and
    (2) Data Sync Issues - out-of-range dates and other discrepancies.

    Args:
        results: Query results from q21_minutes_integrity_check()
        date_range: Optional date range string (e.g., "10/10-10/19") from Daily_Logs data.
                   If not provided, defaults to "10/10-10/15" for backward compatibility.

    Returns:
        Analysis dictionary with summary, metrics, breakdown, and insights showing:
        - 120-Minute Daily Cap Exceeded (capping effect)
        - Data Sync Issues (out-of-range, daily exceeds cumulative, missing records)
        - Total reconciliation (sum of both categories)
        Returns None if no data or no issues found
    """
    if not results:
        return None

    # Use provided date range or fall back to default
    contest_period = date_range if date_range else "10/10-10/15"

    # Calculate totals for reconciliation
    # - daily_minutes_capped: SUM(MIN(minutes_read, 120)) - official counting with 120 min/day cap
    # - daily_minutes_sum: SUM(minutes_read) - uncapped daily total
    # - cumulative_minutes: Reader_Cumulative total (uncapped, may include out-of-range dates)
    total_daily_capped = sum(r.get('daily_minutes_capped', r['daily_minutes_sum']) for r in results)
    total_daily_uncapped = sum(r['daily_minutes_sum'] for r in results)
    total_cumulative = sum(r['cumulative_minutes'] for r in results)

    # Calculate the three key numbers:
    # 1. Capping effect: How many minutes students read beyond the 120 min/day cap
    capping_effect = total_daily_uncapped - total_daily_capped

    # 2. Data sync issues: Difference between cumulative and uncapped daily (net)
    data_sync_total = total_cumulative - total_daily_uncapped

    # 3. Total reconciliation: capped daily vs cumulative (what home screen shows)
    total_reconciliation = total_cumulative - total_daily_capped

    # Sanity check: capping + data_sync should equal total reconciliation
    # total_reconciliation = (cumulative - daily_capped) = (cumulative - daily_uncapped) + (daily_uncapped - daily_capped)
    #                      = data_sync_total + capping_effect

    # If everything is perfectly in sync (no issues at all)
    if total_reconciliation == 0:
        return {
            'summary': 'All student records match perfectly between Daily_Logs and Reader_Cumulative. No discrepancies found.',
            'insights': ['Data integrity verified - all systems in sync']
        }

    # Filter for issues to identify affected students and create detailed breakdowns
    issues = [r for r in results if r['status'] in ['MINUTES_MISMATCH', 'MISSING_CUMULATIVE', 'MISSING_DAILY']]

    # Separate by status type for detailed analysis
    minutes_mismatch = [r for r in issues if r['status'] == 'MINUTES_MISMATCH']
    missing_cumulative = [r for r in issues if r['status'] == 'MISSING_CUMULATIVE']
    missing_daily = [r for r in issues if r['status'] == 'MISSING_DAILY']

    # For MINUTES_MISMATCH, separate by positive/negative differences (for data sync subcategories)
    positive_diff = [r for r in minutes_mismatch if r['difference'] > 0]  # Cumulative > Daily (out-of-range)
    negative_diff = [r for r in minutes_mismatch if r['difference'] < 0]  # Daily > Cumulative (data error)

    # Identify students who exceeded the 120-minute cap
    cap_exceders = [r for r in results if r.get('daily_minutes_capped', 0) < r['daily_minutes_sum']]

    breakdown = []

    # ============================================================================
    # SECTION 1: 120-Minute Daily Cap Exceeded (Capping Effect)
    # ============================================================================
    if capping_effect > 0:
        top_cap_exceders = sorted(
            cap_exceders,
            key=lambda x: x['daily_minutes_sum'] - x.get('daily_minutes_capped', x['daily_minutes_sum']),
            reverse=True
        )[:3]

        breakdown.append({
            'issue': '120-Minute Daily Cap Exceeded',
            'minutes': capping_effect,
            'unit': 'minutes',
            'explanation': f'{len(cap_exceders)} students read more than 120 minutes in at least one day. The official Daily_Logs counting caps their credit at 120 minutes per day, but they actually read {int(capping_effect)} more minutes total. This difference is intentional per contest rules and contributes to the reconciliation total.',
            'top_contributors': [
                {
                    'student': c['student_name'],
                    'amount': c['daily_minutes_sum'] - c.get('daily_minutes_capped', c['daily_minutes_sum'])
                }
                for c in top_cap_exceders
            ]
        })

    # ============================================================================
    # SECTION 2: Data Sync Issues (net = out-of-range + daily exceeds cumulative + missing)
    # ============================================================================

    # Subsection 2a: Out-of-Range Reading Dates (positive differences)
    if positive_diff:
        out_of_range_total = sum(r['difference'] for r in positive_diff)
        top_contributors = sorted(positive_diff, key=lambda x: x['difference'], reverse=True)[:3]

        breakdown.append({
            'issue': 'Out-of-Range Reading Dates',
            'minutes': out_of_range_total,
            'unit': 'minutes',
            'explanation': f'{len(positive_diff)} students have reading entries for dates OUTSIDE the contest period ({contest_period}). Parents may have entered data before contest start or after the last data download. Reader_Cumulative includes all dates, but Daily_Logs only contains sanctioned contest dates.',
            'top_contributors': [
                {
                    'student': c['student_name'],
                    'amount': c['difference']
                }
                for c in top_contributors
            ]
        })

    # Subsection 2b: Daily Exceeds Cumulative (negative differences - DATA ERROR)
    if negative_diff:
        daily_exceeds_total = sum(r['difference'] for r in negative_diff)  # This will be negative
        top_contributors = sorted(negative_diff, key=lambda x: x['difference'], reverse=False)[:3]  # Most negative first

        breakdown.append({
            'issue': 'Daily Exceeds Cumulative',
            'minutes': daily_exceeds_total,  # Keep as negative to show direction
            'unit': 'minutes',
            'explanation': f'{len(negative_diff)} students have uncapped daily minutes totals HIGHER than cumulative ({int(abs(daily_exceeds_total))} minutes). This is a data error - Daily_Logs should never exceed Reader_Cumulative. May indicate data sync issues or re-downloads with different data. Shows as negative because it reduces the net discrepancy.',
            'top_contributors': [
                {
                    'student': c['student_name'],
                    'amount': c['difference']  # Keep negative to show direction
                }
                for c in top_contributors
            ]
        })

    # Subsection 2c: Missing from Reader_Cumulative
    if missing_cumulative:
        missing_cum_total = sum(abs(r['difference']) for r in missing_cumulative)
        top_contributors = sorted(missing_cumulative, key=lambda x: abs(x['difference']), reverse=True)[:3]

        breakdown.append({
            'issue': 'Missing from Reader_Cumulative',
            'minutes': missing_cum_total,
            'unit': 'minutes',
            'explanation': f'{len(missing_cumulative)} students have daily reading logs but are NOT in Reader_Cumulative table. This may indicate the cumulative file was not downloaded recently, or students were added after the last cumulative upload.',
            'top_contributors': [
                {
                    'student': c['student_name'],
                    'amount': abs(c['difference'])
                }
                for c in top_contributors
            ]
        })

    # Subsection 2d: Missing from Daily_Logs
    if missing_daily:
        missing_daily_total = sum(abs(r['difference']) for r in missing_daily)
        top_contributors = sorted(missing_daily, key=lambda x: abs(x['difference']), reverse=True)[:3]

        breakdown.append({
            'issue': 'Missing from Daily_Logs',
            'minutes': missing_daily_total,
            'unit': 'minutes',
            'explanation': f'{len(missing_daily)} students are in Reader_Cumulative but have NO daily logs. This may indicate daily files were not uploaded for all dates, or students only read on non-sanctioned dates.',
            'top_contributors': [
                {
                    'student': c['student_name'],
                    'amount': abs(c['difference'])
                }
                for c in top_contributors
            ]
        })

    # ============================================================================
    # Generate summary and insights
    # ============================================================================

    # Calculate components for summary math display
    out_of_range_min = sum(r['difference'] for r in positive_diff) if positive_diff else 0
    daily_exceeds_min = sum(r['difference'] for r in negative_diff) if negative_diff else 0  # Negative value
    missing_cum_min = sum(abs(r['difference']) for r in missing_cumulative) if missing_cumulative else 0
    missing_daily_min = sum(abs(r['difference']) for r in missing_daily) if missing_daily else 0

    # Data sync issues = out_of_range + daily_exceeds (negative) + missing_cum (negative) + missing_daily (positive)
    # This should equal data_sync_total

    # Build summary with clear structure using HTML for proper rendering
    direction_note = "Reader_Cumulative is higher" if total_reconciliation > 0 else "Daily_Logs is higher"

    # Build main comparison summary with HTML line breaks
    summary_parts = []
    summary_parts.append(f'<strong>Daily_Logs (capped):</strong> {int(total_daily_capped):,} minutes')
    summary_parts.append(f'<strong>Reader_Cumulative (uncapped):</strong> {int(total_cumulative):,} minutes')
    summary_parts.append(f'<strong>Difference:</strong> {int(total_reconciliation):+,} minutes ({direction_note})')

    # Build breakdown section
    breakdown_parts = []
    breakdown_parts.append(f'<strong>Breakdown:</strong>')
    breakdown_parts.append(f'&nbsp;&nbsp;• 120-Minute Daily Cap: {int(capping_effect):,} minutes')

    if data_sync_total != 0:
        breakdown_parts.append(f'&nbsp;&nbsp;• Data Sync Issues: {int(data_sync_total):+,} minutes')

        # If we have multiple data sync components, show the detailed math
        if abs(data_sync_total) > 0 and len([x for x in [out_of_range_min, daily_exceeds_min, missing_cum_min, missing_daily_min] if x != 0]) > 1:
            if out_of_range_min > 0:
                breakdown_parts.append(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ Out-of-Range: +{int(out_of_range_min):,} min')
            if daily_exceeds_min < 0:
                breakdown_parts.append(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ Daily Exceeds Cumulative: {int(daily_exceeds_min):,} min')
            if missing_cum_min > 0:
                breakdown_parts.append(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ Missing from Cumulative: -{int(missing_cum_min):,} min')
            if missing_daily_min > 0:
                breakdown_parts.append(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ Missing from Daily: +{int(missing_daily_min):,} min')

    # Combine into final summary with HTML line breaks
    summary = '<br>'.join(summary_parts) + '<br><br>' + '<br>'.join(breakdown_parts)

    # Generate insights
    insights = []

    issue_count = len(issues)
    if issue_count > 0:
        insights.append(f'{issue_count} students have integrity issues between Daily_Logs and Reader_Cumulative')

    if capping_effect > 0:
        insights.append(f'{len(cap_exceders)} students exceeded the 120-minute daily cap, contributing {int(capping_effect)} minutes to reconciliation')

    if out_of_range_min > 0:
        insights.append(f'{len(positive_diff)} students have out-of-range reading entries (+{int(out_of_range_min)} minutes)')

    if daily_exceeds_min < 0:
        insights.append(f'{len(negative_diff)} students have daily totals exceeding cumulative ({int(daily_exceeds_min)} minutes) - DATA ERROR')

    if missing_cumulative:
        insights.append(f'{len(missing_cumulative)} students missing from Reader_Cumulative - re-download cumulative file')

    if missing_daily:
        insights.append(f'{len(missing_daily)} students missing from Daily_Logs - verify all daily files uploaded')

    insights.append(f'Verify contest date range ({contest_period}) matches data downloads')

    return {
        'summary': summary,
        'metrics': {
            'total_reconciliation': int(total_reconciliation),
            'capping_effect': int(capping_effect),
            'data_sync_total': int(data_sync_total),
            'affected_students': issue_count,
            'cap_exceders': len(cap_exceders),
            'minutes_mismatch': len(minutes_mismatch),
            'missing_cumulative': len(missing_cumulative),
            'missing_daily': len(missing_daily),
            'daily_total_capped': int(total_daily_capped),
            'daily_total_uncapped': int(total_daily_uncapped),
            'cumulative_total': int(total_cumulative),
            'unit': 'minutes'
        },
        'breakdown': breakdown,
        'insights': insights
    }


def generate_q22_analysis(results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Generate analysis for Q22: Student Name Sync Check

    Args:
        results: Query results from q22_student_name_sync_check()

    Returns:
        Analysis dictionary or None if no issues
    """
    if not results:
        return {
            'summary': 'All students with reading minutes are properly synced between Daily_Logs and Reader_Cumulative.',
            'insights': ['Data sync verified - no action needed']
        }

    in_daily_only = [r for r in results if r['status'] == 'IN_DAILY_ONLY']
    in_cumulative_only = [r for r in results if r['status'] == 'IN_CUMULATIVE_ONLY']

    breakdown = []

    if in_daily_only:
        breakdown.append({
            'issue': 'In Daily_Logs Only',
            'minutes': len(in_daily_only),
            'unit': 'students',
            'explanation': f'{len(in_daily_only)} students have daily reading logs but no cumulative stats. This may indicate the cumulative file was not downloaded or students were added after the last cumulative upload.',
            'top_contributors': [
                {'student': r['student_name'], 'amount': 1}
                for r in in_daily_only[:3]
            ]
        })

    if in_cumulative_only:
        breakdown.append({
            'issue': 'In Reader_Cumulative Only',
            'minutes': len(in_cumulative_only),
            'unit': 'students',
            'explanation': f'{len(in_cumulative_only)} students have cumulative stats but no daily logs. This may indicate daily files were not uploaded for all dates or students only read on non-sanctioned dates.',
            'top_contributors': [
                {'student': r['student_name'], 'amount': 1}
                for r in in_cumulative_only[:3]
            ]
        })

    insights = [
        f'{len(results)} students are out of sync between Daily_Logs and Reader_Cumulative',
        'Re-download cumulative stats file to capture latest data',
        'Ensure all daily files for contest period (10/10-10/15) have been uploaded'
    ]

    if in_daily_only:
        insights.append(f'{len(in_daily_only)} students need to be added to cumulative file')

    if in_cumulative_only:
        insights.append(f'{len(in_cumulative_only)} students may have reading on non-sanctioned dates')

    return {
        'summary': f'Found {len(results)} students out of sync: {len(in_daily_only)} in Daily_Logs only, {len(in_cumulative_only)} in Reader_Cumulative only.',
        'metrics': {
            'total_out_of_sync': len(results),
            'in_daily_only': len(in_daily_only),
            'in_cumulative_only': len(in_cumulative_only)
        },
        'breakdown': breakdown,
        'insights': insights
    }


def generate_q23_analysis(results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Generate analysis for Q23: Roster Integrity Check

    Args:
        results: Query results from q23_roster_integrity_check()

    Returns:
        Analysis dictionary or None if no issues
    """
    if not results:
        return {
            'summary': 'All students in Daily_Logs and Reader_Cumulative exist in Roster. Data integrity verified.',
            'insights': ['Roster is complete - no orphaned student records found']
        }

    # Group by table
    in_daily = [r for r in results if r['found_in_table'] == 'Daily_Logs']
    in_cumulative = [r for r in results if r['found_in_table'] == 'Reader_Cumulative']

    # Get unique student names (student may appear in both tables)
    unique_students = list(set(r['student_name'] for r in results))

    breakdown = []

    if in_daily:
        breakdown.append({
            'issue': 'Missing from Roster (in Daily_Logs)',
            'minutes': len(in_daily),
            'unit': 'records',
            'explanation': f'{len(in_daily)} student records in Daily_Logs have no matching Roster entry. These students have reading data but are not in the master roster.',
            'top_contributors': [
                {'student': r['student_name'], 'amount': 1}
                for r in in_daily[:3]
            ]
        })

    if in_cumulative:
        breakdown.append({
            'issue': 'Missing from Roster (in Reader_Cumulative)',
            'minutes': len(in_cumulative),
            'unit': 'records',
            'explanation': f'{len(in_cumulative)} student records in Reader_Cumulative have no matching Roster entry. These students have fundraising/cumulative data but are not in the master roster.',
            'top_contributors': [
                {'student': r['student_name'], 'amount': 1}
                for r in in_cumulative[:3]
            ]
        })

    insights = [
        f'{len(unique_students)} orphaned students found (not in Roster)',
        'Add missing students to Roster to enable proper reporting',
        'Verify student names match exactly between files (check for spelling/spacing differences)',
        'Check if students transferred schools or were withdrawn'
    ]

    return {
        'summary': f'Found {len(unique_students)} students with reading/fundraising data who are missing from Roster.',
        'metrics': {
            'orphaned_students': len(unique_students),
            'daily_logs_records': len(in_daily),
            'cumulative_records': len(in_cumulative)
        },
        'breakdown': breakdown,
        'insights': insights
    }


# ============================================================================
# REPORT-SPECIFIC TERM SETS
# ============================================================================

# Which terms are relevant for each report
REPORT_TERM_SETS = {
    'q21': ['Cap / Capped / Maximum Minutes', 'Capping / 120-Minute Daily Cap Exceeded', 'Cumulative', 'Daily Logs', 'Reader Cumulative', 'Discrepancy', 'Out-of-Range', 'Sanctioned Dates', 'Contest Period'],
    'q22': ['Daily Logs', 'Reader Cumulative', 'Roster', 'Reader / Student', 'Discrepancy'],
    'q23': ['Roster', 'Daily Logs', 'Reader Cumulative', 'Reader / Student'],
    'q1': ['Daily Logs', 'Reader Cumulative', 'Roster'],
    'q2': ['Class', 'Team', 'Participation', 'Goal / Minimum Minutes', 'Cap / Capped / Maximum Minutes', 'Daily Logs'],
    'q5': ['Reader / Student', 'Class', 'Team', 'Participation', 'Goal / Minimum Minutes', 'Donations / Sponsors'],
    'q6': ['Class', 'Participation', 'Team'],
    'q14': ['Team', 'Participation'],
    'q18': ['Class', 'Grade Level', 'Participation', 'Team'],
    'q19': ['Team', 'Cumulative', 'Reader Cumulative'],
    'q20': ['Team', 'Donations / Sponsors', 'Reader Cumulative'],
}


def get_report_terms(report_id: str) -> Dict[str, Any]:
    """
    Get relevant terms for a specific report

    Args:
        report_id: Report ID (e.g., 'q21', 'q2', etc.)

    Returns:
        Dictionary of relevant terms for this report
    """
    term_keys = REPORT_TERM_SETS.get(report_id, [])
    return get_relevant_terms(term_keys)
