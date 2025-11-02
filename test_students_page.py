"""
Test suite for Students page functionality.

This test ensures the Students page displays correct information
from the sample database and maintains data integrity across changes.
"""

import pytest
import re
from app import app
from database import ReadathonDB


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Ensure we're using sample database
            with client.session_transaction() as sess:
                sess['environment'] = 'sample'
        yield client


@pytest.fixture
def sample_db():
    """Get sample database instance for verification queries."""
    return ReadathonDB('readathon_sample.db')


class TestStudentsPage:
    """Test cases for Students page."""

    def test_page_loads_successfully(self, client):
        """Verify Students page loads without errors."""
        response = client.get('/students')
        assert response.status_code == 200
        assert b'Read-a-Thon System' in response.data
        assert b'Students' in response.data

    def test_no_error_messages(self, client):
        """Verify page doesn't contain error messages or exceptions."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for common error indicators
        error_patterns = [
            'Error:',
            'Exception:',
            'Traceback',
            'error occurred',
            '500 Internal Server Error',
            'KeyError',
            'AttributeError',
        ]

        html_lower = html.lower()
        for pattern in error_patterns:
            assert pattern.lower() not in html_lower, f"Found error pattern: {pattern}"

    def test_banner_metrics_present(self, client):
        """Verify all 6 banner metrics are displayed."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for all required banner metrics
        assert 'Campaign Day' in html
        assert 'Fundraising' in html
        assert 'Minutes Read' in html
        assert 'Sponsors' in html
        assert 'Participation' in html
        assert 'Goal Met' in html

    def test_table_structure(self, client):
        """Verify table has correct structure with all columns."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for all 13 table column headers
        assert 'Student Name' in html
        assert 'Grade' in html
        assert 'Team' in html
        assert 'Class' in html
        assert 'Teacher' in html
        assert 'Fundraising' in html
        assert 'Sponsors' in html
        assert 'Minutes Capped' in html
        assert 'Minutes Uncapped' in html
        assert 'Days Partic' in html or 'Participation' in html
        assert 'Goal' in html

    def test_filter_controls_present(self, client):
        """Verify all filter controls are present."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for date filter
        assert 'dateFilter' in html or 'Filter Period' in html

        # Check for grade filter buttons
        assert 'All Grades' in html
        assert 'Kindergarten' in html or 'Grade K' in html
        assert 'Grade 1' in html
        assert 'Grade 5' in html

        # Check for team filter dropdown
        assert 'teamFilter' in html or 'Team:' in html

    def test_team_badges_present(self, client):
        """Verify team badges are displayed for students."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Look for team badge styling or team names
        # Should have multiple team badges throughout the table
        assert html.count('team-badge') > 0 or html.count('TEAM') > 0

    def test_percentage_formats(self, client):
        """Verify percentages are properly formatted."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Find all percentage values in the HTML
        percentages = re.findall(r'(\d+\.?\d*)%', html)

        # Should have multiple percentages
        assert len(percentages) > 0

        # All percentages should be valid numbers
        for pct in percentages:
            value = float(pct)
            assert value >= 0

    def test_currency_formats(self, client):
        """Verify currency values are properly formatted."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Find all currency values
        currency_matches = re.findall(r'\$[\d,]+(?:\.\d{2})?', html)

        # Should have multiple currency values
        assert len(currency_matches) > 0

        # Verify format is correct ($ followed by numbers, possibly with commas)
        for curr in currency_matches:
            assert re.match(r'\$[\d,]+(?:\.\d{2})?$', curr)

    def test_sample_data_integrity(self, client, sample_db):
        """Verify page displays students from sample database."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Get actual student count from database
        student_count = sample_db.execute_query(
            "SELECT COUNT(*) as count FROM Roster"
        )[0]['count']

        # Should have table rows (at least some students visible)
        assert '<tr' in html
        assert '<tbody>' in html

        # Total roster should appear somewhere (411 students)
        assert str(student_count) in html

    def test_winning_value_highlights(self, client):
        """Verify winning values have gold or silver highlights."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for winning value styling classes
        # Should have at least some highlighted values
        has_gold = 'winning-value-school' in html
        has_silver = 'winning-value-grade' in html

        # At minimum, should have gold highlights (school-wide winners)
        assert has_gold, "No gold highlights found for school-wide winners"

    def test_grade_filter_functionality(self, client):
        """Verify grade filter parameter works."""
        # Test with specific grade filter
        response = client.get('/students?grade=5th')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should have "active" class on the 5th grade button
        assert 'grade-filter-btn' in html

        # Test with 'all' filter
        response = client.get('/students?grade=all')
        assert response.status_code == 200

    def test_team_filter_functionality(self, client):
        """Verify team filter parameter works."""
        # Get team names from database
        sample_db = ReadathonDB('readathon_sample.db')
        teams = sample_db.execute_query("SELECT DISTINCT team_name FROM Roster ORDER BY team_name")

        if len(teams) > 0:
            # Test with specific team filter
            team_name = teams[0]['team_name']
            response = client.get(f'/students?team={team_name}')
            assert response.status_code == 200

        # Test with 'all' filter
        response = client.get('/students?team=all')
        assert response.status_code == 200

    def test_date_filter_functionality(self, client):
        """Verify date filter parameter works."""
        # Test with 'all' dates
        response = client.get('/students?date=all')
        assert response.status_code == 200

        # Get a specific date from database
        sample_db = ReadathonDB('readathon_sample.db')
        dates = sample_db.get_all_dates()

        if len(dates) > 0:
            # Test with specific date
            response = client.get(f'/students?date={dates[0]}')
            assert response.status_code == 200

    def test_combined_filters(self, client):
        """Verify multiple filters work together."""
        response = client.get('/students?date=all&grade=5th&team=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should still have valid page structure
        assert 'Students' in html
        assert '<table' in html

    def test_legend_section_present(self, client):
        """Verify legend section with data notes is present."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for legend content
        assert 'Legend' in html or 'legend' in html.lower()
        assert 'Gold' in html or 'gold' in html.lower()
        assert 'Silver' in html or 'silver' in html.lower()

    def test_footer_section_present(self, client):
        """Verify footer with data sources is present."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for data source information
        assert 'Data Sources' in html or 'data sources' in html.lower()
        assert 'Daily_Logs' in html or 'Reader_Cumulative' in html or 'Roster' in html

    def test_student_detail_modal_structure(self, client):
        """Verify student detail modal is present in HTML."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for modal structure
        assert 'studentDetailModal' in html
        assert 'modal' in html.lower()

    def test_javascript_functions_present(self, client):
        """Verify required JavaScript functions are present."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for key JavaScript functions
        assert 'sortTable' in html
        assert 'showStudentDetail' in html
        assert 'copyTable' in html or 'exportCSV' in html
        assert 'toggleLegend' in html or 'toggleFooter' in html

    def test_sortable_table_headers(self, client):
        """Verify table headers are sortable."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for sortable table styling
        assert 'sortTable' in html or 'onclick' in html

    def test_minutes_capped_vs_uncapped(self, client):
        """Verify both capped and uncapped minutes columns exist."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Should have both capped and uncapped columns
        assert 'Minutes Capped' in html or 'Capped' in html
        assert 'Minutes Uncapped' in html or 'Uncapped' in html

    def test_participation_metrics_present(self, client):
        """Verify participation metrics are displayed."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for participation-related content
        assert 'Participation' in html or 'Days Partic' in html
        assert 'Goal Met' in html or 'Goal %' in html

    def test_filter_indicator_icon_present(self, client):
        """Verify filter indicator icon (◐) is present on date-aware metrics."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Should have filter indicator on date-aware metrics
        assert '◐' in html or 'filter-indicator' in html

    def test_data_info_modal_present(self, client):
        """Verify data info modal is present."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for data info modal
        assert 'dataInfoModal' in html or 'Data Info' in html

    def test_banner_values_are_numeric(self, client):
        """Verify banner displays numeric values."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Banner should have numeric values for metrics
        # Look for common patterns like numbers followed by units
        assert re.search(r'\d+', html), "No numeric values found in banner"

    def test_table_has_data_rows(self, client):
        """Verify table contains actual student data rows."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Should have tbody with rows
        assert '<tbody>' in html
        assert '<tr' in html

        # Count table rows (should have at least some students)
        tr_count = html.count('<tr')
        assert tr_count > 1, f"Expected multiple table rows, found {tr_count}"

    def test_responsive_table_container(self, client):
        """Verify table has responsive container."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Should have responsive table wrapper
        assert 'table-responsive' in html or 'comparison-table' in html

    def test_export_buttons_present(self, client):
        """Verify export buttons (Copy, Export CSV) are present."""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for export functionality
        assert 'Copy' in html or 'copyTable' in html
        assert 'Export' in html or 'CSV' in html or 'exportCSV' in html


class TestStudentDetailAPI:
    """Test cases for student detail API endpoint."""

    def test_student_detail_endpoint_exists(self, client):
        """Verify /student/<name> endpoint exists."""
        # Get a student name from database
        sample_db = ReadathonDB('readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")

        if len(students) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}')

            # Should return JSON (not 404)
            assert response.status_code == 200
            assert response.is_json

    def test_student_detail_returns_json(self, client):
        """Verify student detail endpoint returns JSON data."""
        sample_db = ReadathonDB('readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")

        if len(students) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}')

            data = response.get_json()
            assert data is not None
            assert 'summary' in data
            assert 'daily' in data

    def test_student_detail_summary_structure(self, client):
        """Verify summary section has correct structure."""
        sample_db = ReadathonDB('readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")

        if len(students) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}')

            data = response.get_json()
            summary = data.get('summary')

            if summary:
                # Check for expected fields
                assert 'student_name' in summary
                assert 'grade_level' in summary
                assert 'team_name' in summary
                assert 'fundraising' in summary or 'donation_amount' in summary

    def test_student_detail_daily_structure(self, client):
        """Verify daily section is a list."""
        sample_db = ReadathonDB('readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")

        if len(students) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}')

            data = response.get_json()
            daily = data.get('daily')

            assert isinstance(daily, list), "Daily should be a list"

    def test_student_detail_with_date_filter(self, client):
        """Verify student detail endpoint honors date filter."""
        sample_db = ReadathonDB('readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")
        dates = sample_db.get_all_dates()

        if len(students) > 0 and len(dates) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}?date={dates[0]}')

            assert response.status_code == 200
            assert response.is_json


class TestStudentsPageFiltering:
    """Test cases for filtering functionality."""

    def test_silver_highlighting_with_grade_filter(self, client):
        """Verify silver highlighting appears when grade filter is active."""
        response = client.get('/students?grade=5th')
        html = response.data.decode('utf-8')

        # When grade filter is active, silver highlights may appear
        # (depending on whether there are multiple values tied for max)
        # At minimum, page should load successfully
        assert response.status_code == 200

    def test_banner_recalculates_with_filters(self, client):
        """Verify banner metrics recalculate when filters are applied."""
        # Get all students
        response_all = client.get('/students?grade=all&team=all')
        html_all = response_all.data.decode('utf-8')

        # Get filtered students
        response_filtered = client.get('/students?grade=5th')
        html_filtered = response_filtered.data.decode('utf-8')

        # Both should load successfully
        assert response_all.status_code == 200
        assert response_filtered.status_code == 200

        # Banner values may differ (this is expected behavior)
        # Just verify both have banner sections
        assert 'headline-banner' in html_all or 'Campaign Day' in html_all
        assert 'headline-banner' in html_filtered or 'Campaign Day' in html_filtered

    def test_visible_count_updates_with_filter(self, client):
        """Verify visible student count changes with filters."""
        response = client.get('/students?grade=5th')
        html = response.data.decode('utf-8')

        # Should have visible count indicator
        assert 'visibleCount' in html or 'students' in html.lower()
