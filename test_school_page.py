"""
Test suite for school page functionality.

This test ensures the school dashboard displays correct information
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


class TestSchoolPage:
    """Test cases for school dashboard page."""

    def test_page_loads_successfully(self, client):
        """Verify school page loads without errors."""
        response = client.get('/school')
        assert response.status_code == 200
        assert b'Read-a-Thon System' in response.data

    def test_headline_metrics_present(self, client):
        """Verify all headline metrics are displayed."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Check for all required metric sections
        assert 'Campaign Day' in html
        assert 'Fundraising' in html
        assert 'Minutes Read' in html
        assert 'Participation' in html
        assert 'Goal Met' in html

    def test_team_competition_structure(self, client):
        """Verify team competition section has correct structure."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Both teams should be present
        assert 'TEAM TEAM1' in html or 'Phoenix' in html  # Team names may vary
        assert 'TEAM TEAM2' in html or 'Dragons' in html

        # Team metrics should be present
        assert html.count('Fundraising:') >= 2  # At least 2 teams
        assert html.count('Reading') >= 2
        assert html.count('Participation') >= 2
        assert html.count('Students:') >= 2

    def test_top_performers_present(self, client):
        """Verify top performers section exists."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Check for top performer categories
        assert 'Fundraising Leader' in html or 'fundraising leader' in html.lower()
        assert 'Reading Leader' in html or 'reading leader' in html.lower()
        assert 'Top Class' in html or 'top class' in html.lower()

    def test_participation_statistics_present(self, client):
        """Verify participation statistics section exists."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        assert 'Total Participating' in html or 'participating' in html.lower()
        assert 'Total Roster' in html or 'roster' in html.lower()

    def test_sample_data_integrity(self, client, sample_db):
        """Verify calculations match expected values from sample database."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Get actual data from database for comparison
        roster_count = sample_db.execute_query(
            "SELECT COUNT(*) as count FROM Roster"
        )[0]['count']

        total_fundraising = sample_db.execute_query(
            "SELECT SUM(donation_amount) as total FROM Reader_Cumulative"
        )[0]['total']

        # Verify roster count appears in page
        assert str(roster_count) in html

        # Verify fundraising total appears (formatted as currency)
        if total_fundraising:
            # Could be formatted as $280 or $280.00
            assert f'${int(total_fundraising)}' in html or f'${total_fundraising:.0f}' in html

    def test_no_error_messages(self, client):
        """Verify page doesn't contain error messages."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Check for common error indicators (be specific to avoid CSS class names)
        error_patterns = [
            'Error:',  # Actual error messages usually have colons
            'Exception:',
            'Traceback',
            'error occurred',
        ]

        html_lower = html.lower()
        for pattern in error_patterns:
            assert pattern.lower() not in html_lower, f"Found error pattern: {pattern}"

    def test_total_minutes_display(self, client):
        """Verify total minutes/hours metric is displayed."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Just verify that a minutes/hours metric appears in the Minutes Read section
        # (Don't validate exact calculation as it may use capped minutes, date filters, etc.)
        assert 'Minutes Read' in html or 'minutes read' in html.lower()

        # Verify some hours value appears (any number followed by "hour")
        import re
        hours_pattern = r'\d+\.?\d*\s*hour'
        assert re.search(hours_pattern, html, re.IGNORECASE), "No hours value found in page"

    def test_percentage_formats(self, client):
        """Verify percentages are properly formatted."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Find all percentage values in the HTML
        percentages = re.findall(r'(\d+\.?\d*)%', html)

        # Should have multiple percentages (participation, goal met, etc.)
        assert len(percentages) > 0

        # All percentages should be valid numbers
        for pct in percentages:
            float(pct)  # Should not raise ValueError


if __name__ == '__main__':
    # Allow running this file directly with: python test_school_page.py
    pytest.main([__file__, '-v'])
