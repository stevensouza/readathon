"""
Test suite for teams page functionality.

This test ensures the Teams Competition page displays correct information
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


class TestTeamsPage:
    """Test cases for teams competition page."""

    def test_page_loads_successfully(self, client):
        """Verify teams page loads without errors."""
        response = client.get('/teams')
        assert response.status_code == 200
        assert b'Read-a-Thon System' in response.data

    def test_both_teams_present(self, client):
        """Verify both team sections are displayed."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Both teams should have their own sections
        assert 'TEAM KITSKO' in html or 'Team Kitsko' in html or 'KITSKO' in html
        assert 'TEAM STAUB' in html or 'Team Staub' in html or 'STAUB' in html

    def test_team_section_headers(self, client):
        """Verify team section headers are present with emojis."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Should have team emoji indicators
        assert '🔵' in html  # Blue circle for Kitsko
        assert '🟡' in html  # Yellow circle for Staub

        # Should have "TOP PERFORMERS" headers
        assert 'TOP PERFORMERS' in html

    def test_top_performers_structure(self, client):
        """Verify top performers cards for both teams (4 cards each)."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Each team should have 4 performance cards
        # Fundraising Leader, Top Class (Fundraising), Reading Leader, Top Class (Reading)
        assert html.count('FUNDRAISING LEADER') >= 2  # Both teams
        assert html.count('TOP CLASS (FUNDRAISING)') >= 2
        assert html.count('READING LEADER') >= 2
        assert html.count('TOP CLASS (READING)') >= 2

    def test_comparison_table_present(self, client):
        """Verify head-to-head comparison table exists."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Table title
        assert 'TEAM COMPARISON' in html or 'Head-to-Head' in html

        # Table headers
        assert 'Metric' in html
        assert 'Leader' in html
        assert 'Gap' in html

    def test_comparison_metrics(self, client):
        """Verify all comparison metrics are present."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Key metrics that should be in the comparison table
        metrics = [
            'Fundraising',
            'Sponsors',
            'Minutes Read',
            'Participation',
        ]

        for metric in metrics:
            assert metric in html, f"Metric '{metric}' not found in comparison table"

    def test_winning_value_highlights(self, client):
        """Verify winning values have colored oval highlights."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Should have winning-value CSS classes
        assert 'winning-value' in html

        # Should have team-specific winning value classes
        assert 'winning-value-kitsko' in html or 'winning-value-staub' in html

    def test_leader_badges_present(self, client):
        """Verify leader badges are displayed in comparison table."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Should have leader badge CSS classes
        assert 'leader-badge' in html

        # Should show team names in badges
        # (Team names will be dynamic but badges should exist)
        assert 'leader-badge-kitsko' in html or 'leader-badge-staub' in html

    def test_sample_data_integrity(self, client, sample_db):
        """Verify team data matches expected values from sample database."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Get team counts from database
        team_counts = sample_db.execute_query(
            "SELECT team_name, COUNT(*) as count FROM Roster GROUP BY team_name"
        )

        # Both teams should have student counts displayed
        for team in team_counts:
            count = team['count']
            assert str(count) in html, f"Team count {count} not found in page"

    def test_no_error_messages(self, client):
        """Verify page doesn't contain error messages."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Check for common error indicators
        error_patterns = [
            'Error:',
            'Exception:',
            'Traceback',
            'error occurred',
        ]

        html_lower = html.lower()
        for pattern in error_patterns:
            assert pattern.lower() not in html_lower, f"Found error pattern: {pattern}"

    def test_percentage_formats(self, client):
        """Verify percentages are properly formatted."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Find all percentage values in the HTML
        percentages = re.findall(r'(\d+\.?\d*)%', html)

        # Should have multiple percentages (participation, goal met, etc.)
        assert len(percentages) > 0, "No percentages found on Teams page"

        # All percentages should be valid numbers
        for pct in percentages:
            float(pct)  # Should not raise ValueError

    def test_headline_banner(self, client):
        """Verify headline banner with key metrics is present."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Headline banner should exist
        assert 'headline-banner' in html or 'headline-metric' in html

        # Should show high-level competition winners
        # (Exact metrics may vary but structure should exist)

    def test_currency_formats(self, client):
        """Verify currency values are properly formatted."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Find all currency values in the HTML
        currencies = re.findall(r'\$[\d,]+\.?\d*', html)

        # Should have multiple currency values (fundraising, donations, etc.)
        assert len(currencies) > 0, "No currency values found on Teams page"

        # All currencies should be valid numbers when $ and commas removed
        for curr in currencies:
            value = curr.replace('$', '').replace(',', '')
            float(value)  # Should not raise ValueError

    def test_total_minutes_display(self, client):
        """Verify total minutes/hours metric is displayed."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Just verify that a minutes/hours metric appears
        # (Don't validate exact calculation as it may use capped minutes, date filters, etc.)
        assert 'Minutes Read' in html or 'minutes read' in html.lower()

        # Verify some hours value appears (any number followed by "hour")
        hours_pattern = r'\d+\.?\d*\s*hour'
        assert re.search(hours_pattern, html, re.IGNORECASE), "No hours value found on Teams page"

    def test_four_column_layout(self, client):
        """Verify 4-column layout structure (2 rows x 4 cards)."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Should use Bootstrap col-lg-3 for 4-column layout
        assert 'col-lg-3' in html

        # Should have zen-card-kitsko and zen-card-staub classes
        assert 'zen-card-kitsko' in html
        assert 'zen-card-staub' in html


if __name__ == '__main__':
    # Allow running this file directly with: python test_teams_page.py
    pytest.main([__file__, '-v'])
