#!/usr/bin/env python3
"""
Regression tests for starting a new read-a-thon year:
- No hard-coded prior-year dates/timestamps on pages
- Query-string filters that reach SQL are validated
- Database comparison only opens registered databases
- Production-only safeguards key off the registry (not the legacy session 'environment')
"""

import io
import os
import pytest
from database import DatabaseRegistry, ReadathonDB
from app import app, format_contest_range

TEST_DB_NAME = 'test_readathon_newyear.db'
TEST_DB_PATH = f'db/{TEST_DB_NAME}'

ROSTER_CSV = """student_name,class_name,home_room,teacher_name,grade_level,team_name
Alice Anderson,Class A,Room 101,Ms. Adams,3,Team Phoenix
Carol Chen,Class B,Room 102,Mr. Brown,4,Team Dragons"""

CLASS_INFO_CSV = """class_name,home_room,teacher_name,grade_level,team_name,total_students
Class A,Room 101,Ms. Adams,3,Team Phoenix,1
Class B,Room 102,Mr. Brown,4,Team Dragons,1"""

GRADE_RULES_CSV = """grade_level,min_daily_minutes,max_daily_minutes_credit
3,20,120
4,25,120"""


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def empty_year_db_id():
    """A registered, non-sample database with roster data but no reading data yet"""
    db = ReadathonDB(TEST_DB_PATH)
    db.load_class_info_data(CLASS_INFO_CSV)
    db.load_grade_rules_data(GRADE_RULES_CSV)
    db.load_roster_data(ROSTER_CSV)
    db.close()

    registry = DatabaseRegistry()
    db_id = registry.register_database(TEST_DB_NAME, 'Test New Year Read-a-Thon', 2099)
    registry.close()

    yield db_id

    registry = DatabaseRegistry()
    registry.delete_database(db_id)
    registry.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


class TestNoPriorYearHardcoding:

    def test_contest_range_without_dates(self):
        assert format_contest_range([]) == 'No reading data yet'

    def test_contest_range_from_data(self):
        assert format_contest_range(['2026-10-12', '2026-10-16']) == 'Oct 12-Oct 16, 2026'

    @pytest.mark.parametrize('page', ['/school', '/teams', '/classes', '/students'])
    def test_empty_new_year_pages_show_no_2025(self, client, empty_year_db_id, page):
        with client.session_transaction() as sess:
            sess['active_database_id'] = empty_year_db_id
        response = client.get(page)
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Oct 10-15, 2025' not in html
        assert '09/15/2025' not in html
        assert '2025-10-13 (Spirit Day)' not in html


class TestFilterValidation:

    @pytest.mark.parametrize('url', [
        "/students?date=x'",
        "/students?grade=x'",
        "/students?team=x'",
        "/classes?date=x'",
        "/classes?grade=x'",
        "/classes?team=x'",
        "/student/Nobody?date=x'",
    ])
    def test_unknown_filter_values_are_ignored(self, client, url):
        """Filters are interpolated into SQL; unknown values must fall back to 'all' instead of erroring"""
        assert client.get(url).status_code == 200

    def test_comparison_rejects_unregistered_database(self, client):
        response = client.get('/database-comparison?db1=not_registered.db&db2=readathon_sample.db')
        assert response.status_code == 200
        assert b'not found in registry' in response.data
        assert not os.path.exists('db/not_registered.db')

    def test_create_database_rejects_path_in_filename(self, client):
        data = {
            'year': '2099',
            'filename': '../escape.db',
            'roster_csv': (io.BytesIO(ROSTER_CSV.encode()), 'roster.csv'),
            'class_info_csv': (io.BytesIO(CLASS_INFO_CSV.encode()), 'class_info.csv'),
            'grade_rules_csv': (io.BytesIO(GRADE_RULES_CSV.encode()), 'grade_rules.csv'),
        }
        response = client.post('/api/create_database', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert not os.path.exists('escape.db')


class TestProductionSafeguards:

    def test_sample_file_upload_to_production_needs_confirmation(self, client, empty_year_db_id, make_editable):
        make_editable(empty_year_db_id)
        with client.session_transaction() as sess:
            sess['active_database_id'] = empty_year_db_id
        data = {
            'log_date': '2099-10-12',
            'minutes_file': (io.BytesIO(b'header\n'), 'sample_day1_minutes.csv'),
        }
        response = client.post('/api/upload_daily', data=data, content_type='multipart/form-data')
        assert response.get_json().get('needs_sample_confirmation') is True

    def test_export_filename_names_the_database(self, client, empty_year_db_id):
        with client.session_transaction() as sess:
            sess['active_database_id'] = empty_year_db_id
        response = client.get('/api/export_all')
        assert 'readathon_export_test_newyear_' in response.headers.get('Content-Disposition', '')


class TestNewDatabaseSchema:

    def test_new_database_has_upload_history_file_type(self, empty_year_db_id):
        """Pages and uploads query Upload_History.file_type; new databases must have it"""
        db = ReadathonDB(TEST_DB_PATH)
        columns = [row['name'] for row in db.execute_query("PRAGMA table_info(Upload_History)")]
        db.close()
        assert 'file_type' in columns

    def test_comparison_with_empty_new_year_database(self, client, empty_year_db_id):
        response = client.get(f'/database-comparison?db1={TEST_DB_NAME}&db2=readathon_sample.db')
        assert response.status_code == 200
        assert b'has no reading data yet' in response.data


class TestComparisonContestDays:
    """'Through Day N' compares each database through its own Nth contest date (years have different dates)"""

    @pytest.mark.parametrize('filter_period, expected', [
        ('all', 'all'),
        ('day1', '2025-10-10'),
        ('day2', '2025-10-11'),
        ('day3', 'all'),        # past the end of the sample contest -> full contest
        ('day0', 'all'),
        ("day1' OR 1=1", 'all'),
        ('2025-10-10', 'all'),
    ])
    def test_contest_day_to_date(self, filter_period, expected):
        from database import ReportGenerator
        db = ReadathonDB('db/readathon_sample.db')
        assert ReportGenerator._contest_day_to_date(db, filter_period) == expected
        db.close()

    def test_day_filter_changes_comparison(self, client):
        full = client.get('/database-comparison?db1=readathon_sample.db&db2=readathon_sample.db&filter=all').data
        day1 = client.get('/database-comparison?db1=readathon_sample.db&db2=readathon_sample.db&filter=day1').data
        assert b'Through Day 1' in day1
        assert full != day1


class TestCopiedDatabases:
    """Year databases are copied into db/ outside git; they must show up without manual steps"""

    def test_year_database_files_are_auto_registered(self, tmp_path):
        import shutil
        shutil.copy('db/readathon_sample.db', tmp_path / 'readathon_sample.db')
        shutil.copy('db/readathon_sample.db', tmp_path / 'readathon_2031.db')
        (tmp_path / 'test_readathon_2032.db').write_bytes(b'')  # not a year database name

        registry = DatabaseRegistry(str(tmp_path / 'readathon_registry.db'))
        assert registry.register_year_databases() == ['readathon_2031.db']
        assert registry.register_year_databases() == []  # idempotent

        entry = registry.get_database_by_name('readathon_2031.db')
        assert entry['display_name'] == '2031 Read-a-Thon'
        assert entry['year'] == 2031
        assert entry['student_count'] > 0
        assert registry.get_active_database()['db_filename'] == 'readathon_sample.db'
        registry.close()

    def test_register_existing_database_uses_registry(self, client):
        import shutil
        shutil.copy('db/readathon_sample.db', 'db/test_register_copy.db')
        try:
            response = client.post('/api/databases/register',
                                   json={'year': 2098, 'db_filename': 'test_register_copy.db'})
            assert response.get_json()['success'] is True
            registry = DatabaseRegistry()
            entry = registry.get_database_by_name('test_register_copy.db')
            assert entry['display_name'] == '2098 Read-a-Thon'
            registry.delete_database(entry['db_id'])
            registry.close()
        finally:
            os.remove('db/test_register_copy.db')

    @pytest.mark.parametrize('filename', ['../escape.db', 'missing_file.db', 'readathon_sample.db'])
    def test_register_existing_database_rejects_bad_input(self, client, filename):
        response = client.post('/api/databases/register', json={'year': 2098, 'db_filename': filename})
        assert response.status_code == 400


class TestStaleSessionDatabase:
    """The session cookie is shared by every copy of the app on 127.0.0.1:5001, so it can
    name a database ID this registry doesn't have - pages must fall back, not crash"""

    @pytest.mark.parametrize('page', ['/school', '/teams', '/classes', '/students', '/upload',
                                      '/scoreboards/teams', '/scoreboards/daily', '/scoreboards/prize',
                                      '/admin'])
    def test_unknown_database_id_falls_back(self, client, page):
        with client.session_transaction() as sess:
            sess['active_database_id'] = 999999
        response = client.get(page)
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert 'active_database_id' not in sess
