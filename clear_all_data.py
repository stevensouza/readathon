#!/usr/bin/env python3
"""
Script to FULLY RESET the PROD database
Wipes: Daily_Logs, Reader_Cumulative, and ALL Upload_History
Preserves: Roster, Class_Info, Grade_Rules
"""
import sys
sys.path.insert(0, '/Users/stevesouza/my/data/readathon/v2026_development')

from database import ReadathonDB

def clear_all_data():
    """Clear ALL transactional data from PROD database"""

    print("="*70)
    print("FULL DATABASE RESET - PRODUCTION DATABASE")
    print("="*70)
    print("\n⚠️  WARNING: This will PERMANENTLY DELETE:")
    print("  ❌ ALL Daily_Logs records (all dates, all students)")
    print("  ❌ ALL Reader_Cumulative records (donations, sponsors, cumulative minutes)")
    print("  ❌ ALL Upload_History records (both daily AND cumulative)")
    print("  ❌ ALL Team_Color_Bonus records (team color day bonuses)")
    print("\n✅ This will PRESERVE:")
    print("  ✓ Roster (all student records)")
    print("  ✓ Class_Info")
    print("  ✓ Grade_Rules")
    print("\n🎯 Database: db/readathon_prod.db")
    print("="*70)

    confirm = input("\n⚠️  Type 'reset' to confirm: ")

    if confirm.lower() != "reset":
        print("\n❌ Cancelled - confirmation text did not match")
        return False

    # Connect to PROD database
    db = ReadathonDB('db/readathon_prod.db')
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        print("\n" + "="*70)
        print("📊 CURRENT DATA (before deletion)")
        print("="*70)

        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM Daily_Logs")
        daily_logs_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT log_date) FROM Daily_Logs")
        unique_dates_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Reader_Cumulative")
        reader_cumulative_count = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(donation_amount), 0) FROM Reader_Cumulative")
        total_donations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Upload_History")
        upload_history_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Team_Color_Bonus")
        team_color_bonus_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Roster")
        roster_count = cursor.fetchone()[0]

        print(f"Daily_Logs: {daily_logs_count} records ({unique_dates_count} unique dates)")
        print(f"Reader_Cumulative: {reader_cumulative_count} records (${total_donations:,.2f} total donations)")
        print(f"Upload_History: {upload_history_count} records")
        print(f"Team_Color_Bonus: {team_color_bonus_count} records")
        print(f"Roster: {roster_count} students (will be PRESERVED)")

        if daily_logs_count == 0 and reader_cumulative_count == 0 and upload_history_count == 0 and team_color_bonus_count == 0:
            print("\n⚠️  Database already empty - nothing to delete")
            db.close()
            return True

        print("\n" + "="*70)
        print("🗑️  DELETING DATA...")
        print("="*70)

        # Delete all Daily_Logs
        print("🗑️  Deleting Daily_Logs...")
        cursor.execute("DELETE FROM Daily_Logs")
        deleted_daily = cursor.rowcount

        # Delete all Reader_Cumulative
        print("🗑️  Deleting Reader_Cumulative...")
        cursor.execute("DELETE FROM Reader_Cumulative")
        deleted_cumulative = cursor.rowcount

        # Delete ALL Upload_History (both daily and cumulative)
        print("🗑️  Deleting ALL Upload_History...")
        cursor.execute("DELETE FROM Upload_History")
        deleted_history = cursor.rowcount

        # Delete all Team_Color_Bonus
        print("🗑️  Deleting Team_Color_Bonus...")
        cursor.execute("DELETE FROM Team_Color_Bonus")
        deleted_team_color_bonus = cursor.rowcount

        conn.commit()

        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM Daily_Logs")
        remaining_daily = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Reader_Cumulative")
        remaining_cumulative = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Upload_History")
        remaining_history = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Team_Color_Bonus")
        remaining_team_color_bonus = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Roster")
        preserved_roster = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Class_Info")
        preserved_class_info = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Grade_Rules")
        preserved_grade_rules = cursor.fetchone()[0]

        print("\n" + "="*70)
        print("✅ SUCCESS - DATABASE RESET COMPLETE")
        print("="*70)
        print(f"\n📊 DELETED:")
        print(f"  ❌ Daily_Logs: {deleted_daily} records")
        print(f"  ❌ Reader_Cumulative: {deleted_cumulative} records")
        print(f"  ❌ Upload_History: {deleted_history} records")
        print(f"  ❌ Team_Color_Bonus: {deleted_team_color_bonus} records")
        print(f"\n📊 CLEARED (verified 0 records):")
        print(f"  ✓ Daily_Logs: {remaining_daily} records")
        print(f"  ✓ Reader_Cumulative: {remaining_cumulative} records")
        print(f"  ✓ Upload_History: {remaining_history} records")
        print(f"  ✓ Team_Color_Bonus: {remaining_team_color_bonus} records")
        print(f"\n📊 PRESERVED SYSTEM TABLES:")
        print(f"  ✓ Roster: {preserved_roster} students")
        print(f"  ✓ Class_Info: {preserved_class_info} classes")
        print(f"  ✓ Grade_Rules: {preserved_grade_rules} grade levels")
        print("="*70)
        print("\n🎉 Database is now clean and ready for fresh data uploads!")
        print("="*70)

        db.close()
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        db.close()
        return False

if __name__ == "__main__":
    success = clear_all_data()
    sys.exit(0 if success else 1)
