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
    return ReadathonDB('db/readathon_sample.db')


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

    def test_tie_badge_in_comparison_table(self, client, sample_db):
        """Verify TIE badge appears when teams have equal values."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Check if any ties exist in the comparison table
        # Get team metrics to verify ties
        team_query = """
            SELECT r.team_name,
                   SUM(rc.donation_amount) as fundraising,
                   SUM(rc.sponsors) as sponsors
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY r.team_name
        """
        team_results = sample_db.execute_query(team_query)

        if len(team_results) == 2:
            team1 = team_results[0]
            team2 = team_results[1]

            # Check for ties in any metric
            has_tie = (
                team1['fundraising'] == team2['fundraising'] or
                team1['sponsors'] == team2['sponsors']
            )

            if has_tie:
                # If there's a tie, verify TIE badge appears
                assert 'leader-badge-tie' in html or 'TIE' in html

    def test_tie_indicator_in_top_performer_cards(self, client, sample_db):
        """Verify tie indicators appear in top performer cards when multiple students/classes share the top value."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Check for tie indicators in the HTML
        # Pattern: "name1, name2" (multiple names) or "name1, name2, name3 and X others"
        # When there's a tie, we should see commas in the leader name field

        # Check if there are any "and X others" patterns (indicating >3 ties)
        others_pattern = r'and \d+ others'
        others_matches = re.findall(others_pattern, html)

        # If we found "and X others", that's a tie indicator
        for match in others_matches:
            # Extract the number
            num = int(re.search(r'\d+', match).group())
            # Should be at least 1 (meaning at least 4 total tied)
            assert num >= 1, f"Invalid 'others' count: {num}"

    def test_both_values_highlighted_on_tie(self, client, sample_db):
        """Verify both team values get highlighted when there's a tie."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Get team metrics to check for ties
        team_query = """
            SELECT r.team_name,
                   SUM(rc.donation_amount) as fundraising
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY r.team_name
        """
        team_results = sample_db.execute_query(team_query)

        if len(team_results) == 2:
            team1 = team_results[0]
            team2 = team_results[1]

            # If there's a fundraising tie, both values should be highlighted
            if team1['fundraising'] == team2['fundraising']:
                # Both winning-value-kitsko and winning-value-staub should appear
                assert 'winning-value-kitsko' in html
                assert 'winning-value-staub' in html

    def test_tie_count_data_structure(self, client):
        """Verify tie_count fields are present in top_performers data structure."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # The page should load successfully even if all tie_count values are 1 (no ties)
        # This test verifies the template doesn't crash when accessing tie_count fields
        assert response.status_code == 200
        assert 'TOP PERFORMERS' in html

        # Verify no template errors related to missing tie_count fields
        assert 'fundraising_leader_tie_count' not in html  # Should not leak variable names
        assert 'reading_leader_tie_count' not in html
        assert 'top_class_fundraising_tie_count' not in html
        assert 'top_class_reading_tie_count' not in html


if __name__ == '__main__':
    # Allow running this file directly with: python test_teams_page.py
    pytest.main([__file__, '-v'])
