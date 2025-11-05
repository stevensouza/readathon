"""
Test suite for Export All Data functionality
Tests the /api/export_all endpoint and ZIP file generation
"""

import pytest
import io
import zipfile
import csv
from app import app
from database import ReadathonDB


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_export_all_endpoint_returns_zip(client):
    """Test that /api/export_all returns a ZIP file"""
    response = client.get('/api/export_all')

    assert response.status_code == 200
    assert response.mimetype == 'application/zip'
    assert 'attachment' in response.headers.get('Content-Disposition', '')
    assert 'readathon_export' in response.headers.get('Content-Disposition', '')


def test_export_all_contains_readme(client):
    """Test that ZIP contains README.md file"""
    response = client.get('/api/export_all')

    # Read ZIP from response
    zip_buffer = io.BytesIO(response.data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        # Check README exists
        assert 'README.md' in zip_file.namelist()

        # Read README content
        readme_content = zip_file.read('README.md').decode('utf-8')

        # Verify README has expected sections
        assert '# Read-a-Thon Database Export' in readme_content
        assert '## Export Information' in readme_content
        assert '## Summary Statistics' in readme_content
        assert '## Files Included' in readme_content
        assert '## Data Notes' in readme_content


def test_export_all_contains_all_tables(client):
    """Test that ZIP contains all 8 table CSV files"""
    response = client.get('/api/export_all')

    zip_buffer = io.BytesIO(response.data)

    expected_tables = [
        'Roster.csv',
        'Class_Info.csv',
        'Grade_Rules.csv',
        'Daily_Logs.csv',
        'Reader_Cumulative.csv',
        'Upload_History.csv',
        'Team_Color_Bonus.csv',
        'Database_Metadata.csv'
    ]

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_list = zip_file.namelist()

        for table_csv in expected_tables:
            assert table_csv in file_list, f"Missing {table_csv} in export"


def test_export_csv_format_valid(client):
    """Test that CSV files in ZIP are valid CSV format"""
    response = client.get('/api/export_all')

    zip_buffer = io.BytesIO(response.data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        # Test Roster.csv as representative example
        roster_content = zip_file.read('Roster.csv').decode('utf-8')

        # Parse CSV
        reader = csv.DictReader(io.StringIO(roster_content))
        rows = list(reader)

        # Verify headers
        expected_columns = ['student_name', 'class_name', 'home_room',
                          'teacher_name', 'grade_level', 'team_name']

        if len(rows) > 0:  # If there's data
            assert set(rows[0].keys()) == set(expected_columns)


def test_export_readme_has_table_counts(client):
    """Test that README includes table record counts"""
    response = client.get('/api/export_all')

    zip_buffer = io.BytesIO(response.data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        readme_content = zip_file.read('README.md').decode('utf-8')

        # Should mention all tables
        assert 'Roster:' in readme_content
        assert 'Class_Info:' in readme_content
        assert 'Grade_Rules:' in readme_content
        assert 'Daily_Logs:' in readme_content
        assert 'Reader_Cumulative:' in readme_content
        assert 'Upload_History:' in readme_content
        assert 'Team_Color_Bonus:' in readme_content
        assert 'Database_Metadata:' in readme_content

        # Should include statistics
        assert 'students' in readme_content.lower()
        assert 'records' in readme_content.lower()


def test_export_readme_has_summary_stats(client):
    """Test that README includes summary statistics"""
    response = client.get('/api/export_all')

    zip_buffer = io.BytesIO(response.data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        readme_content = zip_file.read('README.md').decode('utf-8')

        # Check for summary sections
        assert 'Total Donations:' in readme_content
        assert 'Total Sponsors:' in readme_content
        assert 'Total Reading Minutes' in readme_content
        assert 'Export Date:' in readme_content
        assert 'Database:' in readme_content


def test_export_readme_has_version(client):
    """Test that README includes software version"""
    response = client.get('/api/export_all')

    zip_buffer = io.BytesIO(response.data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        readme_content = zip_file.read('README.md').decode('utf-8')

        # Check for version in Export Information section
        assert 'Software Version:' in readme_content
        assert 'v2026' in readme_content or 'unknown' in readme_content

        # Check for version in footer
        assert 'Generated by Read-a-Thon System' in readme_content


def test_export_metadata_method():
    """Test the get_export_metadata() method directly"""
    db = ReadathonDB('readathon_sample.db')

    metadata = db.get_export_metadata()

    # Check structure
    assert 'counts' in metadata
    assert 'date_range' in metadata
    assert 'totals' in metadata
    assert 'total_minutes' in metadata
    assert 'export_timestamp' in metadata
    assert 'database_path' in metadata

    # Check counts includes all tables
    assert 'Roster' in metadata['counts']
    assert 'Class_Info' in metadata['counts']
    assert 'Grade_Rules' in metadata['counts']
    assert 'Daily_Logs' in metadata['counts']
    assert 'Reader_Cumulative' in metadata['counts']
    assert 'Upload_History' in metadata['counts']
    assert 'Team_Color_Bonus' in metadata['counts']
    assert 'Database_Metadata' in metadata['counts']


def test_export_all_tables_method():
    """Test the export_all_tables() method directly"""
    db = ReadathonDB('readathon_sample.db')

    all_tables = db.export_all_tables()

    # Check all 8 tables are present
    expected_tables = [
        'Roster',
        'Class_Info',
        'Grade_Rules',
        'Daily_Logs',
        'Reader_Cumulative',
        'Upload_History',
        'Team_Color_Bonus',
        'Database_Metadata'
    ]

    for table in expected_tables:
        assert table in all_tables, f"Missing {table} in export data"
        assert isinstance(all_tables[table], list), f"{table} should be a list"


def test_export_zip_structure_integrity(client):
    """Test that ZIP file structure is valid and complete"""
    response = client.get('/api/export_all')

    zip_buffer = io.BytesIO(response.data)

    # Verify ZIP is valid
    assert zipfile.is_zipfile(zip_buffer)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        # Test ZIP integrity
        bad_files = zip_file.testzip()
        assert bad_files is None, f"ZIP contains corrupted files: {bad_files}"

        # Should have exactly 9 files (8 CSVs + 1 README)
        assert len(zip_file.namelist()) == 9


def test_export_filename_format(client):
    """Test that export filename follows correct format"""
    response = client.get('/api/export_all')

    filename = response.headers.get('Content-Disposition', '')

    # Should contain 'readathon_export'
    assert 'readathon_export' in filename

    # Should contain environment (sample or prod)
    assert 'sample' in filename or 'prod' in filename

    # Should contain version (e.g., 2026_8_0)
    # Format: readathon_export_{env}_{version}_{timestamp}.zip
    assert '_2026_' in filename or 'unknown' in filename  # version or unknown

    # Should contain timestamp pattern (YYYYMMDD_HHMMSS)
    assert '.zip' in filename


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
