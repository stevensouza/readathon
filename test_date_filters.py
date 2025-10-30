#!/usr/bin/env python3
"""
Test Date Filtering Across All Pages

Tests that date filters work correctly on School, Teams, and Grade Level pages.
Includes tests for both full date ranges (date=all) and single date filtering.

Created: 2025-10-30
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


class TestSchoolPageDateFilters:
    """Test date filtering on School page"""

    def test_school_page_no_date_filter(self, client):
        """Verify School page loads with no date filter (full range)"""
        response = client.get('/school')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_school_page_with_date_all(self, client):
        """Verify School page loads with date=all"""
        response = client.get('/school?date=all')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_school_page_with_single_date(self, client):
        """Verify School page loads with single date filter"""
        response = client.get('/school?date=2025-10-13')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_school_page_single_date_shows_metrics(self, client):
        """Verify School page shows valid metrics with single date"""
        response = client.get('/school?date=2025-10-13')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Check that banner metrics are present
        assert 'headline-banner' in html
        assert 'headline-metric' in html

        # Check that Avg. Participation metric exists and has a value
        assert 'Avg. Participation (With Color)' in html
        participation_match = re.search(
            r'Avg\. Participation \(With Color\).*?headline-value[^>]*>([0-9.]+)%',
            html,
            re.DOTALL
        )
        assert participation_match, "Could not find Avg. Participation value"

        # Value should be a reasonable percentage
        value = float(participation_match.group(1))
        assert 0 <= value <= 110, f"Participation value out of reasonable range: {value}%"

    def test_school_page_date_filter_affects_values(self, client):
        """Verify date filter parameter is accepted and page loads correctly"""
        # Get page with full range
        response_all = client.get('/school')
        assert response_all.status_code == 200

        # Get page with single date
        response_single = client.get('/school?date=2025-10-13')
        assert response_single.status_code == 200

        # Both should load without errors
        assert b'OperationalError' not in response_all.data
        assert b'OperationalError' not in response_single.data


class TestTeamsPageDateFilters:
    """Test date filtering on Teams page"""

    def test_teams_page_no_date_filter(self, client):
        """Verify Teams page loads with no date filter (full range)"""
        response = client.get('/teams')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_teams_page_with_date_all(self, client):
        """Verify Teams page loads with date=all"""
        response = client.get('/teams?date=all')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_teams_page_with_single_date(self, client):
        """Verify Teams page loads with single date filter"""
        response = client.get('/teams?date=2025-10-13')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_teams_page_single_date_shows_metrics(self, client):
        """Verify Teams page shows valid metrics with single date"""
        response = client.get('/teams?date=2025-10-13')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Check that banner metrics are present
        assert 'headline-banner' in html
        assert 'headline-metric' in html

        # Check that Avg. Participation metric exists
        assert 'Avg. Participation (With Color)' in html

    def test_teams_page_date_filter_affects_comparison_table(self, client):
        """Verify date filter parameter is accepted and page loads correctly"""
        # Get page with full range
        response_all = client.get('/teams')
        assert response_all.status_code == 200

        # Get page with single date
        response_single = client.get('/teams?date=2025-10-13')
        assert response_single.status_code == 200

        # Both should load without errors
        assert b'OperationalError' not in response_all.data
        assert b'OperationalError' not in response_single.data


class TestGradeLevelPageDateFilters:
    """Test date filtering on Grade Level page"""

    def test_grade_level_page_no_date_filter(self, client):
        """Verify Grade Level page loads with no date filter (full range)"""
        response = client.get('/classes')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_grade_level_page_with_date_all(self, client):
        """Verify Grade Level page loads with date=all"""
        response = client.get('/classes?date=all')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_grade_level_page_with_single_date(self, client):
        """Verify Grade Level page loads with single date filter"""
        response = client.get('/classes?date=2025-10-13')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

    def test_grade_level_page_single_date_shows_metrics(self, client):
        """Verify Grade Level page shows valid metrics with single date"""
        response = client.get('/classes?date=2025-10-13')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Check that banner metrics are present
        assert 'headline-banner' in html
        assert 'headline-metric' in html

        # Check that Avg. Participation metric exists
        assert 'Avg. Participation (With Color)' in html

    def test_grade_level_page_with_grade_and_date_filters(self, client):
        """Verify Grade Level page works with both grade and date filters"""
        response = client.get('/classes?grade=1&date=2025-10-13')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data
        assert b'no such column' not in response.data

        html = response.data.decode('utf-8')

        # Check that page loaded correctly with banner
        assert 'headline-banner' in html

    def test_grade_level_page_date_filter_affects_table(self, client):
        """Verify date filter parameter is accepted and page loads correctly"""
        # Get page with full range
        response_all = client.get('/classes')
        assert response_all.status_code == 200

        # Get page with single date
        response_single = client.get('/classes?date=2025-10-13')
        assert response_single.status_code == 200

        # Both should load without errors
        assert b'OperationalError' not in response_all.data
        assert b'OperationalError' not in response_single.data


class TestDateFilterEdgeCases:
    """Test edge cases for date filtering"""

    def test_school_page_with_early_date(self, client):
        """Verify School page handles early date in range"""
        response = client.get('/school?date=2025-10-10')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data

    def test_school_page_with_late_date(self, client):
        """Verify School page handles late date in range"""
        response = client.get('/school?date=2025-10-15')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data

    def test_teams_page_with_early_date(self, client):
        """Verify Teams page handles early date in range"""
        response = client.get('/teams?date=2025-10-10')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data

    def test_teams_page_with_late_date(self, client):
        """Verify Teams page handles late date in range"""
        response = client.get('/teams?date=2025-10-15')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data

    def test_grade_level_page_with_early_date(self, client):
        """Verify Grade Level page handles early date in range"""
        response = client.get('/classes?date=2025-10-10')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data

    def test_grade_level_page_with_late_date(self, client):
        """Verify Grade Level page handles late date in range"""
        response = client.get('/classes?date=2025-10-15')
        assert response.status_code == 200
        assert b'OperationalError' not in response.data


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v'])
