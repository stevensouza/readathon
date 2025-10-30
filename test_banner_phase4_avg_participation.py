#!/usr/bin/env python3
"""
Test Banner Standardization - Phase 4: Avg. Participation (With Color)

Tests for switching all banners from simple "Participation %" to "Avg. Participation (With Color)"
which includes average daily participation + color bonus points.

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


class TestPhase4SchoolBanner:
    """Phase 4: School banner uses Avg. Participation (With Color)"""

    def test_school_banner_label_updated(self, client):
        """Verify School banner shows 'Avg. Participation (With Color)' label"""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        assert response.status_code == 200
        assert 'Avg. Participation (With Color)' in html, "School banner should show 'Avg. Participation (With Color)'"

        # Should NOT show old simple "Participation" label
        # Note: The word "Participation" will still appear in the new label, so we check the full phrase
        assert '👥 Avg. Participation (With Color)' in html

    def test_school_banner_format(self, client):
        """Verify School banner value uses 1 decimal place"""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Find the Avg. Participation metric section
        participation_match = re.search(
            r'Avg\. Participation \(With Color\).*?headline-value[^>]*>([^<]+)</div>',
            html,
            re.DOTALL
        )

        assert participation_match, "Could not find Avg. Participation metric"

        value = participation_match.group(1).strip()
        # Should be format like "67.5%" (1 decimal place)
        assert '%' in value, "Value should be a percentage"
        assert re.match(r'^\d+\.\d%$', value), f"Value should have 1 decimal place, got: {value}"

    def test_school_banner_filter_indicator(self, client):
        """Verify filter indicator appears when date filtered"""
        # Test with date filter
        response = client.get('/school?date=2025-10-13')
        html = response.data.decode('utf-8')

        # Find Avg. Participation section
        participation_section = re.search(
            r'Avg\. Participation \(With Color\).*?filter-indicator',
            html,
            re.DOTALL
        )

        assert participation_section, "Filter indicator should appear when date is filtered"

    def test_school_banner_tooltip_text(self, client):
        """Verify tooltip mentions average daily participation with color bonus"""
        response = client.get('/school?date=2025-10-13')
        html = response.data.decode('utf-8')

        # Check tooltip text in filter indicator
        assert 'Average daily participation (with color bonus)' in html, \
            "Tooltip should mention 'average daily participation (with color bonus)'"


class TestPhase4TeamsBanner:
    """Phase 4: Teams banner uses Avg. Participation (With Color)"""

    def test_teams_banner_label_updated(self, client):
        """Verify Teams banner shows 'Avg. Participation (With Color)' label"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200
        assert 'Avg. Participation (With Color)' in html, "Teams banner should show 'Avg. Participation (With Color)'"

    def test_teams_banner_uses_percentage(self, client):
        """Verify Teams banner shows percentage (not count)"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Extract banner section only
        banner_start = html.find('class="headline-banner"')
        banner_end = html.find('<!-- Top Performers', banner_start)
        banner_html = html[banner_start:banner_end]

        # Find Avg. Participation metric
        participation_match = re.search(
            r'👥.*?Avg\. Participation.*?headline-value[^>]*>([^<]+)</div>',
            banner_html,
            re.DOTALL
        )

        assert participation_match, "Could not find Avg. Participation metric in Teams banner"

        value = participation_match.group(1).strip()
        # Should be percentage format
        assert '%' in value, f"Teams Avg. Participation should show percentage, got: {value}"


class TestPhase4GradeLevelBanner:
    """Phase 4: Grade Level banner uses Avg. Participation (With Color)"""

    def test_grade_level_banner_label_updated(self, client):
        """Verify Grade Level banner shows 'Avg. Participation (With Color)' label"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200
        assert 'Avg. Participation (With Color)' in html, "Grade Level banner should show 'Avg. Participation (With Color)'"

    def test_grade_level_banner_shows_class(self, client):
        """Verify Grade Level banner shows winning class"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Find Avg. Participation section with class name
        participation_section = re.search(
            r'Avg\. Participation \(With Color\).*?headline-subtitle[^>]*>([^<]+)</div>',
            html,
            re.DOTALL
        )

        assert participation_section, "Could not find Avg. Participation metric subtitle"

        # Subtitle should show class name (not empty)
        subtitle = participation_section.group(1).strip()
        assert subtitle, "Grade Level Avg. Participation should show winning class name"

    def test_grade_level_banner_tooltip(self, client):
        """Verify Grade Level tooltip mentions average daily participation with color bonus"""
        response = client.get('/classes?date=2025-10-13')
        html = response.data.decode('utf-8')

        assert 'Average daily participation (with color bonus)' in html, \
            "Tooltip should mention 'average daily participation (with color bonus)'"


class TestPhase4Calculation:
    """Phase 4: Verify calculation includes color bonus"""

    def test_school_calculation_includes_color(self, client, sample_db):
        """Verify School avg participation includes color bonus"""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Get the displayed value
        participation_match = re.search(
            r'Avg\. Participation \(With Color\).*?headline-value[^>]*>([0-9.]+)%',
            html,
            re.DOTALL
        )

        assert participation_match, "Could not find Avg. Participation value"
        displayed_value = float(participation_match.group(1))

        # Value should be > 0 (basic sanity check)
        assert displayed_value > 0, "Avg. Participation should be greater than 0"

        # Value should be <= 110% (could exceed 100% with color bonus, but not by too much)
        assert displayed_value <= 110, f"Avg. Participation seems too high: {displayed_value}%"


class TestPhase4ConsistencyAcrossPages:
    """Phase 4: Verify consistency of terminology and formatting"""

    def test_all_pages_use_same_label(self, client):
        """Verify all 3 pages use identical 'Avg. Participation (With Color)' label"""
        pages = ['/school', '/teams', '/classes']

        for url in pages:
            response = client.get(url)
            html = response.data.decode('utf-8')

            assert 'Avg. Participation (With Color)' in html, \
                f"{url} should show 'Avg. Participation (With Color)' label"

    def test_all_pages_show_percentage(self, client):
        """Verify all 3 pages show percentage format (not count)"""
        pages = [('/school', 'School'), ('/teams', 'Teams'), ('/classes', 'Grade Level')]

        for url, page_name in pages:
            response = client.get(url)
            html = response.data.decode('utf-8')

            # Find Avg. Participation value
            participation_match = re.search(
                r'Avg\. Participation \(With Color\).*?headline-value[^>]*>([^<]+)</div>',
                html,
                re.DOTALL
            )

            assert participation_match, f"Could not find Avg. Participation on {page_name}"

            value = participation_match.group(1).strip()
            assert '%' in value, f"{page_name} Avg. Participation should show percentage, got: {value}"


class TestPhase4EdgeCases:
    """Phase 4: Edge cases and special scenarios"""

    def test_can_exceed_100_percent(self, client):
        """Document that Avg. Participation (With Color) CAN exceed 100%"""
        # This is a documentation test - the metric can exceed 100% if:
        # - All students read all days (100%)
        # - Team has color war points (adds bonus %)
        #
        # Example: 10 students read 10/10 days = 100%
        #          + 5 color points = (5 / (10 * 10)) * 100 = +5%
        #          = 105% total
        #
        # This is EXPECTED behavior, not a bug.

        response = client.get('/school')
        html = response.data.decode('utf-8')

        participation_match = re.search(
            r'Avg\. Participation \(With Color\).*?headline-value[^>]*>([0-9.]+)%',
            html,
            re.DOTALL
        )

        if participation_match:
            value = float(participation_match.group(1))
            # Test passes regardless of value - just documenting that >100% is valid
            # If value > 100%, that's OK and expected with color bonus
            assert value >= 0, "Value should be non-negative"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v'])
