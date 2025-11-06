#!/usr/bin/env python3
"""
Test script for database creation functionality
Tests the Admin page database creation feature with CSV uploads
"""

import os
import sys
import pytest
import tempfile
import io
from werkzeug.datastructures import FileStorage
from database import ReadathonDB, DatabaseRegistry

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Test database configuration
TEST_DB_DIR = 'db'
TEST_DB_NAME = 'test_readathon_2027.db'
TEST_DB_PATH = f'{TEST_DB_DIR}/{TEST_DB_NAME}'

# Sample CSV data for testing
ROSTER_CSV = """student_name,class_name,home_room,teacher_name,grade_level,team_name
Alice Anderson,Class A,Room 101,Ms. Adams,3,Team Phoenix
Bob Baker,Class A,Room 101,Ms. Adams,3,Team Phoenix
Carol Chen,Class B,Room 102,Mr. Brown,4,Team Dragons
David Davis,Class B,Room 102,Mr. Brown,4,Team Dragons
Eve Evans,Class C,Room 103,Mrs. Clark,5,Team Phoenix"""

CLASS_INFO_CSV = """class_name,home_room,teacher_name,grade_level,team_name,total_students
Class A,Room 101,Ms. Adams,3,Team Phoenix,2
Class B,Room 102,Mr. Brown,4,Team Dragons,2
Class C,Room 103,Mrs. Clark,5,Team Phoenix,1"""

GRADE_RULES_CSV = """grade_level,min_daily_minutes,max_daily_minutes_credit
3,20,120
4,25,120
5,30,120"""

def cleanup():
    """Remove test database if it exists"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"✓ Cleaned up test database: {TEST_DB_PATH}")

@pytest.fixture
def client():
    """Pytest fixture to create Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def run_around_tests():
    """Setup and teardown for each test"""
    cleanup()
    yield
    cleanup()


class TestDatabaseCreation:
    """Test suite for database creation functionality"""

    def test_admin_page_loads_successfully(self, client):
        """Test that admin page loads without errors"""
        response = client.get('/admin')
        assert response.status_code == 200
        assert b'Administration' in response.data
        print("✓ Admin page loads successfully")

    def test_admin_page_has_four_tabs(self, client):
        """Test that admin page has all four tabs in correct order"""
        response = client.get('/admin')
        data = response.data.decode('utf-8')

        # Check for all four tab buttons
        assert 'Actions' in data
        assert 'Data Management' in data
        assert 'Database Creation' in data
        assert 'Database Registry' in data

        # Verify tab order by checking positions
        actions_pos = data.find('id="actions-tab"')
        data_pos = data.find('id="data-tab"')
        db_creation_pos = data.find('id="db-creation-tab"')
        db_comparison_pos = data.find('id="db-comparison-tab"')

        assert actions_pos < data_pos < db_creation_pos < db_comparison_pos
        print("✓ Admin page has all four tabs in correct order")

    def test_database_creation_tab_has_form(self, client):
        """Test that database creation tab has the upload form"""
        response = client.get('/admin')
        data = response.data.decode('utf-8')

        # Check for form elements
        assert 'createDatabaseForm' in data
        assert 'dbYear' in data
        assert 'dbFilename' in data
        assert 'dbDescription' in data
        assert 'rosterCsv' in data
        assert 'classInfoCsv' in data
        assert 'gradeRulesCsv' in data
        assert 'Create Database' in data
        print("✓ Database Creation tab has complete form")

    def test_database_creation_with_valid_csv_files(self, client):
        """Test successful database creation with valid CSV files"""
        # Create file objects from CSV strings
        roster_file = FileStorage(
            stream=io.BytesIO(ROSTER_CSV.encode('utf-8')),
            filename='roster.csv',
            content_type='text/csv'
        )
        class_info_file = FileStorage(
            stream=io.BytesIO(CLASS_INFO_CSV.encode('utf-8')),
            filename='class_info.csv',
            content_type='text/csv'
        )
        grade_rules_file = FileStorage(
            stream=io.BytesIO(GRADE_RULES_CSV.encode('utf-8')),
            filename='grade_rules.csv',
            content_type='text/csv'
        )

        # Submit the form
        response = client.post('/api/create_database', data={
            'year': '2027',
            'filename': TEST_DB_NAME,
            'description': '2027 Test Read-a-Thon',
            'roster_csv': roster_file,
            'class_info_csv': class_info_file,
            'grade_rules_csv': grade_rules_file
        }, content_type='multipart/form-data')

        # Check response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['year'] == 2027
        assert data['db_path'] == TEST_DB_PATH
        assert data['counts']['roster'] == 5
        assert data['counts']['class_info'] == 3
        assert data['counts']['grade_rules'] == 3
        print(f"✓ Database created successfully: {TEST_DB_PATH}")
        print(f"  - Roster: {data['counts']['roster']} students")
        print(f"  - Class Info: {data['counts']['class_info']} classes")
        print(f"  - Grade Rules: {data['counts']['grade_rules']} grade levels")

        # Verify database file exists
        assert os.path.exists(TEST_DB_PATH)
        print("✓ Database file exists on disk")

        # Verify database is registered in Database_Registry
        registry = DatabaseRegistry()
        databases = registry.list_databases()
        test_db = None
        for db_entry in databases:
            if db_entry['db_filename'] == TEST_DB_NAME:
                test_db = db_entry
                break

        assert test_db is not None, f"Database {TEST_DB_NAME} not found in registry"
        assert test_db['year'] == 2027
        assert test_db['db_filename'] == TEST_DB_NAME
        assert test_db['description'] == '2027 Test Read-a-Thon'
        registry.close()
        print("✓ Database registered in Database_Registry")

    def test_database_creation_missing_year(self, client):
        """Test that database creation fails when year is missing"""
        roster_file = FileStorage(
            stream=io.BytesIO(ROSTER_CSV.encode('utf-8')),
            filename='roster.csv'
        )

        response = client.post('/api/create_database', data={
            'filename': TEST_DB_NAME,
            'roster_csv': roster_file
        }, content_type='multipart/form-data')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'Year and filename are required' in data['error']
        print("✓ Database creation properly rejects missing year")

    def test_database_creation_missing_csv_files(self, client):
        """Test that database creation fails when CSV files are missing"""
        response = client.post('/api/create_database', data={
            'year': '2027',
            'filename': TEST_DB_NAME
        }, content_type='multipart/form-data')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'All three CSV files are required' in data['error']
        print("✓ Database creation properly rejects missing CSV files")

    def test_database_creation_invalid_filename(self, client):
        """Test that database creation fails with invalid filename"""
        roster_file = FileStorage(
            stream=io.BytesIO(ROSTER_CSV.encode('utf-8')),
            filename='roster.csv'
        )
        class_info_file = FileStorage(
            stream=io.BytesIO(CLASS_INFO_CSV.encode('utf-8')),
            filename='class_info.csv'
        )
        grade_rules_file = FileStorage(
            stream=io.BytesIO(GRADE_RULES_CSV.encode('utf-8')),
            filename='grade_rules.csv'
        )

        response = client.post('/api/create_database', data={
            'year': '2027',
            'filename': 'invalid_name.txt',  # Wrong extension
            'roster_csv': roster_file,
            'class_info_csv': class_info_file,
            'grade_rules_csv': grade_rules_file
        }, content_type='multipart/form-data')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'must end with .db' in data['error']
        print("✓ Database creation properly rejects invalid filename")

    def test_database_creation_missing_roster_columns(self, client):
        """Test that database creation fails when roster CSV has missing columns"""
        # Roster CSV with missing columns
        invalid_roster = """student_name,class_name
Alice Anderson,Class A
Bob Baker,Class B"""

        roster_file = FileStorage(
            stream=io.BytesIO(invalid_roster.encode('utf-8')),
            filename='roster.csv'
        )
        class_info_file = FileStorage(
            stream=io.BytesIO(CLASS_INFO_CSV.encode('utf-8')),
            filename='class_info.csv'
        )
        grade_rules_file = FileStorage(
            stream=io.BytesIO(GRADE_RULES_CSV.encode('utf-8')),
            filename='grade_rules.csv'
        )

        response = client.post('/api/create_database', data={
            'year': '2027',
            'filename': TEST_DB_NAME,
            'roster_csv': roster_file,
            'class_info_csv': class_info_file,
            'grade_rules_csv': grade_rules_file
        }, content_type='multipart/form-data')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'CSV validation failed' in data['error']
        assert 'Roster CSV' in data['details']
        print("✓ Database creation properly validates roster CSV columns")

    def test_database_creation_duplicate_file(self, client):
        """Test that database creation fails when database file already exists"""
        # Create the database file first
        db = ReadathonDB(TEST_DB_PATH)
        db.close()

        roster_file = FileStorage(
            stream=io.BytesIO(ROSTER_CSV.encode('utf-8')),
            filename='roster.csv'
        )
        class_info_file = FileStorage(
            stream=io.BytesIO(CLASS_INFO_CSV.encode('utf-8')),
            filename='class_info.csv'
        )
        grade_rules_file = FileStorage(
            stream=io.BytesIO(GRADE_RULES_CSV.encode('utf-8')),
            filename='grade_rules.csv'
        )

        response = client.post('/api/create_database', data={
            'year': '2027',
            'filename': TEST_DB_NAME,
            'roster_csv': roster_file,
            'class_info_csv': class_info_file,
            'grade_rules_csv': grade_rules_file
        }, content_type='multipart/form-data')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'already exists' in data['error']
        print("✓ Database creation properly rejects duplicate filenames")

    def test_auto_generate_filename_function_exists(self, client):
        """Test that JavaScript auto-generate filename function exists"""
        response = client.get('/admin')
        data = response.data.decode('utf-8')

        assert 'function autoGenerateFilename()' in data
        assert 'readathon_${year}.db' in data
        print("✓ Auto-generate filename JavaScript function exists")

    def test_reset_form_function_exists(self, client):
        """Test that JavaScript reset form function exists"""
        response = client.get('/admin')
        data = response.data.decode('utf-8')

        assert 'function resetCreateForm()' in data
        assert 'createDatabaseForm' in data
        print("✓ Reset form JavaScript function exists")


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
