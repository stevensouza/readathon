#!/usr/bin/env python3
"""
Migration Script: Convert to Database Registry Architecture
============================================================

This script migrates from the hardcoded prod/sample system to the
dynamic registry database system.

Actions:
1. Backup existing databases
2. Extract metadata from readathon_prod.db
3. Create new readathon_registry.db with Database_Registry table
4. Populate registry with both databases
5. Rename readathon_prod.db → readathon_2025.db
6. Drop Database_Metadata table from both databases
7. Delete extra readathon.db file
8. Delete run_prod.sh and run_sample.sh scripts
9. Update .readathon_config file

Usage:
    python3 migrate_to_registry.py [--dry-run]
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys
import argparse

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, total, message):
    """Print formatted step message"""
    print(f"\n{Colors.OKBLUE}[Step {step_num}/{total}]{Colors.ENDC} {Colors.BOLD}{message}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠{Colors.ENDC}  {message}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")

def backup_databases(dry_run=False):
    """Step 1: Backup existing databases"""
    print_step(1, 9, "Backing up existing databases")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backups/migration_{timestamp}"

    if not dry_run:
        os.makedirs(backup_dir, exist_ok=True)

    files_to_backup = [
        'db/readathon_prod.db',
        'db/readathon_sample.db',
        'db/readathon.db'
    ]

    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = f"{backup_dir}/{os.path.basename(file_path)}"
            if dry_run:
                print(f"  Would backup: {file_path} → {backup_path}")
            else:
                shutil.copy2(file_path, backup_path)
                print_success(f"Backed up: {file_path} → {backup_path}")
        else:
            print_warning(f"File not found (skipping): {file_path}")

    return backup_dir if not dry_run else None

def extract_metadata(dry_run=False):
    """Step 2: Extract metadata from existing databases"""
    print_step(2, 9, "Extracting metadata from existing databases")

    metadata = []

    # Extract from readathon_prod.db
    if os.path.exists('db/readathon_prod.db'):
        conn = sqlite3.connect('db/readathon_prod.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get student count
        cursor.execute("SELECT COUNT(*) as count FROM Roster")
        student_count = cursor.fetchone()['count']

        # Get total days
        cursor.execute("SELECT COUNT(DISTINCT log_date) as count FROM Daily_Logs")
        total_days = cursor.fetchone()['count']

        # Get total donations
        cursor.execute("SELECT SUM(donation_amount) as total FROM Reader_Cumulative")
        row = cursor.fetchone()
        total_donations = row['total'] if row['total'] else 0.0

        conn.close()

        metadata.append({
            'db_id': 1,
            'db_filename': 'readathon_2025.db',  # Will be renamed
            'display_name': '2025 Read-a-Thon',
            'year': 2025,
            'description': '2025 production database',
            'is_active': 1,
            'student_count': student_count,
            'total_days': total_days,
            'total_donations': total_donations
        })

        print_success(f"Extracted from readathon_prod.db: {student_count} students, {total_days} days, ${total_donations:.2f}")

    # Extract from readathon_sample.db
    if os.path.exists('db/readathon_sample.db'):
        conn = sqlite3.connect('db/readathon_sample.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get student count
        cursor.execute("SELECT COUNT(*) as count FROM Roster")
        student_count = cursor.fetchone()['count']

        # Get total days
        cursor.execute("SELECT COUNT(DISTINCT log_date) as count FROM Daily_Logs")
        total_days = cursor.fetchone()['count']

        # Get total donations
        cursor.execute("SELECT SUM(donation_amount) as total FROM Reader_Cumulative")
        row = cursor.fetchone()
        total_donations = row['total'] if row['total'] else 0.0

        conn.close()

        metadata.append({
            'db_id': 2,
            'db_filename': 'readathon_sample.db',
            'display_name': 'Sample',
            'year': 2025,
            'description': 'Sample database for testing',
            'is_active': 0,
            'student_count': student_count,
            'total_days': total_days,
            'total_donations': total_donations
        })

        print_success(f"Extracted from readathon_sample.db: {student_count} students, {total_days} days, ${total_donations:.2f}")

    return metadata

def create_registry_database(metadata, dry_run=False):
    """Step 3: Create new registry database"""
    print_step(3, 9, "Creating registry database")

    if dry_run:
        print("  Would create: db/readathon_registry.db")
        print("  Would create table: Database_Registry")
        for entry in metadata:
            print(f"  Would register: {entry['display_name']} ({entry['db_filename']})")
        return

    # Create database
    conn = sqlite3.connect('db/readathon_registry.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Database_Registry (
            db_id INTEGER PRIMARY KEY AUTOINCREMENT,
            db_filename TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            year INTEGER,
            description TEXT,
            is_active INTEGER DEFAULT 0,
            created_timestamp TEXT NOT NULL,
            student_count INTEGER DEFAULT 0,
            total_days INTEGER DEFAULT 0,
            total_donations REAL DEFAULT 0.0
        )
    ''')

    print_success("Created Database_Registry table")

    # Insert metadata
    for entry in metadata:
        cursor.execute('''
            INSERT INTO Database_Registry
            (db_id, db_filename, display_name, year, description, is_active,
             created_timestamp, student_count, total_days, total_donations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry['db_id'],
            entry['db_filename'],
            entry['display_name'],
            entry['year'],
            entry['description'],
            entry['is_active'],
            datetime.now().isoformat(),
            entry['student_count'],
            entry['total_days'],
            entry['total_donations']
        ))

        print_success(f"Registered: {entry['display_name']} ({entry['db_filename']})")

    conn.commit()
    conn.close()

def rename_database_file(dry_run=False):
    """Step 4: Rename readathon_prod.db to readathon_2025.db"""
    print_step(4, 9, "Renaming database file")

    if os.path.exists('db/readathon_prod.db'):
        if dry_run:
            print("  Would rename: db/readathon_prod.db → db/readathon_2025.db")
        else:
            os.rename('db/readathon_prod.db', 'db/readathon_2025.db')
            print_success("Renamed: readathon_prod.db → readathon_2025.db")
    else:
        print_warning("readathon_prod.db not found (skipping rename)")

def drop_metadata_tables(dry_run=False):
    """Step 5: Drop Database_Metadata tables from both databases"""
    print_step(5, 9, "Dropping Database_Metadata tables")

    databases = [
        'db/readathon_2025.db',
        'db/readathon_sample.db'
    ]

    for db_path in databases:
        if os.path.exists(db_path):
            if dry_run:
                print(f"  Would drop Database_Metadata from {os.path.basename(db_path)}")
            else:
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("DROP TABLE IF EXISTS Database_Metadata")
                    conn.commit()
                    conn.close()
                    print_success(f"Dropped Database_Metadata from {os.path.basename(db_path)}")
                except Exception as e:
                    print_error(f"Failed to drop table from {os.path.basename(db_path)}: {e}")
        else:
            print_warning(f"{os.path.basename(db_path)} not found (skipping)")

def delete_extra_files(dry_run=False):
    """Step 6: Delete extra database and shell scripts"""
    print_step(6, 9, "Deleting extra files")

    files_to_delete = [
        'db/readathon.db',
        'run_prod.sh',
        'run_sample.sh'
    ]

    for file_path in files_to_delete:
        if os.path.exists(file_path):
            if dry_run:
                print(f"  Would delete: {file_path}")
            else:
                os.remove(file_path)
                print_success(f"Deleted: {file_path}")
        else:
            print_warning(f"{file_path} not found (skipping)")

def update_config_file(dry_run=False):
    """Step 7: Update .readathon_config file"""
    print_step(7, 9, "Updating config file")

    if dry_run:
        print("  Would update: .readathon_config")
        print("  New format: {\"active_database_id\": 1, \"active_database_filename\": \"readathon_2025.db\"}")
        return

    import json

    # Delete old config if it exists
    if os.path.exists('.readathon_config'):
        os.remove('.readathon_config')
        print_success("Deleted old .readathon_config")

    # Create new config
    config = {
        'active_database_id': 1,
        'active_database_filename': 'readathon_2025.db'
    }

    with open('.readathon_config', 'w') as f:
        json.dump(config, f, indent=2)

    print_success("Created new .readathon_config")

def verify_migration(dry_run=False):
    """Step 8: Verify migration was successful"""
    print_step(8, 9, "Verifying migration")

    if dry_run:
        print("  Would verify all changes")
        return

    success = True

    # Check registry database exists
    if os.path.exists('db/readathon_registry.db'):
        print_success("Registry database exists")

        # Check table contents
        conn = sqlite3.connect('db/readathon_registry.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM Database_Registry")
        count = cursor.fetchone()['count']

        if count >= 2:
            print_success(f"Registry has {count} databases registered")
        else:
            print_error(f"Registry only has {count} databases (expected 2+)")
            success = False

        conn.close()
    else:
        print_error("Registry database not found!")
        success = False

    # Check renamed database
    if os.path.exists('db/readathon_2025.db'):
        print_success("readathon_2025.db exists")
    else:
        print_error("readathon_2025.db not found!")
        success = False

    # Check sample database
    if os.path.exists('db/readathon_sample.db'):
        print_success("readathon_sample.db exists")
    else:
        print_error("readathon_sample.db not found!")
        success = False

    # Check old files deleted
    if not os.path.exists('db/readathon.db'):
        print_success("readathon.db deleted")
    else:
        print_warning("readathon.db still exists")

    if not os.path.exists('run_prod.sh'):
        print_success("run_prod.sh deleted")
    else:
        print_warning("run_prod.sh still exists")

    # Check config file
    if os.path.exists('.readathon_config'):
        print_success(".readathon_config updated")
    else:
        print_warning(".readathon_config not found")

    return success

def print_summary(backup_dir, dry_run=False):
    """Step 9: Print migration summary"""
    print_step(9, 9, "Migration Summary")

    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")

    if dry_run:
        print(f"{Colors.WARNING}DRY RUN - No changes were made{Colors.ENDC}")
        print("\nTo perform actual migration, run:")
        print(f"  {Colors.BOLD}python3 migrate_to_registry.py{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}Migration completed successfully!{Colors.ENDC}")
        print(f"\nBackup location: {backup_dir}")

        print("\n" + Colors.BOLD + "Files created:" + Colors.ENDC)
        print("  ✓ db/readathon_registry.db (new central registry)")
        print("  ✓ db/readathon_2025.db (renamed from readathon_prod.db)")
        print("  ✓ .readathon_config (updated format)")

        print("\n" + Colors.BOLD + "Files deleted:" + Colors.ENDC)
        print("  ✗ db/readathon.db")
        print("  ✗ run_prod.sh")
        print("  ✗ run_sample.sh")
        print("  ✗ Database_Metadata table (from both databases)")

        print("\n" + Colors.BOLD + "Next steps:" + Colors.ENDC)
        print("  1. Update code (database.py, app.py, templates)")
        print("  2. Update tests")
        print("  3. Update documentation")
        print("  4. Test the application")

    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def main():
    parser = argparse.ArgumentParser(description='Migrate to database registry architecture')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    args = parser.parse_args()

    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Database Registry Migration Script{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")

    if args.dry_run:
        print(f"\n{Colors.WARNING}Running in DRY RUN mode - no changes will be made{Colors.ENDC}\n")

    try:
        # Execute migration steps
        backup_dir = backup_databases(args.dry_run)
        metadata = extract_metadata(args.dry_run)
        create_registry_database(metadata, args.dry_run)
        rename_database_file(args.dry_run)
        drop_metadata_tables(args.dry_run)
        delete_extra_files(args.dry_run)
        update_config_file(args.dry_run)

        if not args.dry_run:
            success = verify_migration(args.dry_run)
            if not success:
                print_error("\nMigration completed with warnings - please review")

        print_summary(backup_dir, args.dry_run)

        if not args.dry_run:
            print(f"{Colors.OKGREEN}✓ Migration complete!{Colors.ENDC}\n")

    except Exception as e:
        print_error(f"\nMigration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
