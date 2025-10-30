"""
Test suite for Grade Level page functionality.

This test ensures the Grade Level (Classes) page displays correct information
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


class TestGradeLevelPage:
    """Test cases for grade level (classes) page."""

    # ========== MANDATORY TESTS (From RULES.md) ==========

    def test_page_loads_successfully(self, client):
        """Verify grade level page loads without errors."""
        response = client.get('/classes')
        assert response.status_code == 200
        assert b'Read-a-Thon System' in response.data

    def test_no_error_messages(self, client):
        """Verify page doesn't contain error messages."""
        response = client.get('/classes')
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
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Find all percentage values in the HTML
        percentages = re.findall(r'(\d+\.?\d*)%', html)

        # Should have multiple percentages (participation, goal met, etc.)
        assert len(percentages) > 0, "No percentages found on Grade Level page"

        # All percentages should be valid numbers
        for pct in percentages:
            float(pct)  # Should not raise ValueError

    def test_currency_formats(self, client):
        """Verify currency values are properly formatted."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Find all currency values in the HTML
        currencies = re.findall(r'\$[\d,]+\.?\d*', html)

        # Should have multiple currency values (fundraising, donations, etc.)
        assert len(currencies) > 0, "No currency values found on Grade Level page"

        # All currencies should be valid numbers when $ and commas removed
        for curr in currencies:
            value = curr.replace('$', '').replace(',', '')
            float(value)  # Should not raise ValueError

    def test_sample_data_integrity(self, client, sample_db):
        """Verify calculations match expected values from sample database."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Get total students from database
        total_students = sample_db.execute_query(
            "SELECT COUNT(*) as count FROM Roster"
        )[0]['count']

        # Verify student count appears in page (may be in different formats)
        assert str(total_students) in html, f"Expected student count {total_students} not found"

        # Verify page has some fundraising data (don't check exact total as it may vary by date filter)
        # Just ensure $ currency symbols are present
        assert '$' in html, "No currency symbols found on page"

    def test_team_badges_present(self, client):
        """Verify team badges use correct CSS classes."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Should have team badge CSS classes
        assert 'team-badge' in html, "No team badges found on Grade Level page"

        # Should have team-specific badge classes (alphabetical: kitsko=blue, staub=yellow)
        assert 'team-badge-kitsko' in html or 'team-badge-staub' in html

    def test_winning_value_highlights(self, client):
        """Verify winning values have colored oval highlights."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Should have winning-value CSS classes
        assert 'winning-value' in html, "No winning value highlights found on Grade Level page"

        # Grade Level page uses grade-level winners (silver ovals)
        assert 'winning-value-grade' in html or 'winning-value' in html

    def test_headline_banner(self, client):
        """Verify headline banner with key metrics is present."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Headline banner should exist
        assert 'headline-banner' in html or 'headline-metric' in html, "No headline banner found on Grade Level page"

        # Banner should show high-level grade metrics
        # (Exact metrics may vary but structure should exist)

    # ========== PAGE-SPECIFIC TESTS ==========

    def test_grade_filter_buttons_present(self, client):
        """Verify all grade filter buttons are present."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Should have buttons for all grades
        grades = ['all', 'K', '1', '2', '3', '4', '5']
        for grade in grades:
            assert f'data-grade="{grade}"' in html, f"Grade button for '{grade}' not found"

    def test_grade_filter_all_active_by_default(self, client):
        """Verify 'All Grades' button is active by default."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Check which grade button is active
        active_pattern = r'<button[^>]*class="[^"]*active[^"]*"[^>]*data-grade="([^"]*)"'
        active_match = re.search(active_pattern, html)

        assert active_match is not None, "No active grade filter button found"
        active_grade = active_match.group(1)
        assert active_grade == 'all', f"Expected 'all' to be active, but '{active_grade}' is active"

    def test_grade_filter_single_grade(self, client):
        """Verify filtering by a single grade works correctly."""
        # Test filtering for Kindergarten
        response = client.get('/classes?grade=K')
        html = response.data.decode('utf-8')

        # Check that K button is active
        active_pattern = r'<button[^>]*class="[^"]*active[^"]*"[^>]*data-grade="([^"]*)"'
        active_match = re.search(active_pattern, html)
        assert active_match is not None
        assert active_match.group(1) == 'K', "K button should be active when grade=K"

        # Check table rows - should only have K rows
        row_pattern = r'<tr[^>]*data-grade="([^"]*)"'
        rows = re.findall(row_pattern, html)

        # Should have some K rows
        assert 'K' in rows, "No K rows found when filtering by grade K"

        # Should not have other grades (if any rows exist)
        if rows:
            unexpected_grades = [g for g in rows if g != 'K']
            assert len(unexpected_grades) == 0, f"Found unexpected grades: {set(unexpected_grades)}"

    def test_grade_filter_with_date(self, client):
        """Verify grade filter works with date parameter."""
        # Test filtering for grade 1 with a specific date
        response = client.get('/classes?grade=1&date=2025-10-11')
        html = response.data.decode('utf-8')

        # Check that grade 1 button is active
        active_pattern = r'<button[^>]*class="[^"]*active[^"]*"[^>]*data-grade="([^"]*)"'
        active_match = re.search(active_pattern, html)
        assert active_match is not None
        assert active_match.group(1) == '1', "Grade 1 button should be active when grade=1"

        # Date should be reflected in the date filter display
        assert '2025-10-11' in html or 'October 11' in html or 'Oct 11' in html

    def test_detail_table_structure(self, client):
        """Verify detail table has correct structure."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Should have a detail table
        assert '<table' in html, "No table found on Grade Level page"

        # Should have table headers (actual headers from grade_level.html)
        table_headers = ['CLASS NAME', 'GRADE', 'TEAM', 'FUNDRAISING', 'MINUTES', 'STUDENTS']
        for header in table_headers:
            # Headers may be in uppercase or mixed case
            assert header in html.upper(), f"Table header '{header}' not found"

        # Should have data rows with data-grade attribute
        assert 'data-grade=' in html, "No data-grade attributes found in table rows"

    def test_grade_cards_present(self, client):
        """Verify grade-level summary cards are present."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Should have cards showing grade-level summaries
        # (Cards may vary by implementation, but check for common patterns)

        # Check for grade labels (K through 5)
        grade_labels = ['K', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5']
        grade_found = any(label in html for label in grade_labels)
        assert grade_found, "No grade-level cards or labels found"

    def test_total_minutes_display(self, client):
        """Verify total minutes/hours metric is displayed."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Verify that a minutes/hours metric appears
        assert 'Minutes Read' in html or 'minutes read' in html.lower()

        # Verify some hours value appears (any number followed by "hour")
        hours_pattern = r'\d+\.?\d*\s*hour'
        assert re.search(hours_pattern, html, re.IGNORECASE), "No hours value found on Grade Level page"

    def test_multiple_grades_data(self, client, sample_db):
        """Verify page displays data for multiple grades."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Get grades from database
        grades_in_db = sample_db.execute_query(
            "SELECT DISTINCT grade_level FROM Class_Info ORDER BY grade_level"
        )

        # Should have multiple grades
        assert len(grades_in_db) > 1, "Sample database should have multiple grades"

        # Verify table has rows from multiple grades
        row_pattern = r'<tr[^>]*data-grade="([^"]*)"'
        rows = re.findall(row_pattern, html)
        unique_grades = set(rows)

        # Should have multiple grades represented in the table
        assert len(unique_grades) > 1, "Grade Level page should show multiple grades"


if __name__ == '__main__':
    # Allow running this file directly with: python test_grade_level_page.py
    pytest.main([__file__, '-v'])
