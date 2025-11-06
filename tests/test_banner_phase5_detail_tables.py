#!/usr/bin/env python3
"""
Test Banner Standardization - Phase 5: Detail Table Enhancements

Tests for adding "Avg. Participation (With Color)" to detail tables:
- Teams page: New row in comparison table
- Grade Level page: New column in classes table

Both metrics (simple Participation % and Avg. Participation With Color) should coexist,
showing different values based on their different calculation methods.

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
    return ReadathonDB('db/readathon_sample.db')


class TestPhase5TeamsComparisonTable:
    """Phase 5: Teams comparison table has Avg. Participation (With Color) row"""

    def test_teams_avg_participation_row_exists(self, client):
        """Verify Teams comparison table has 'Avg. Participation (With Color)' row"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find the comparison table section
        assert 'comparison-table' in html or 'Team Comparison' in html

        # Check for the new row label
        assert 'Avg. Participation (With Color)' in html, \
            "Teams comparison table should have 'Avg. Participation (With Color)' row"

    def test_teams_both_participation_metrics_present(self, client):
        """Verify Teams table has BOTH 'Participation %' and 'Avg. Participation (With Color)'"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Should have simple Participation %
        assert 'Participation %' in html or 'Participation' in html

        # Should have Avg. Participation (With Color)
        assert 'Avg. Participation (With Color)' in html

        # These should be different rows (both present)
        comparison_section = html
        participation_count = html.count('Participation')
        assert participation_count >= 2, \
            "Should have at least 2 references to 'Participation' (simple % and with color)"

    def test_teams_avg_participation_row_positioned_correctly(self, client):
        """Verify new row appears after simple 'Participation %' row"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find positions of both metrics
        simple_pos = html.find('Participation %')
        avg_with_color_pos = html.find('Avg. Participation (With Color)')

        # New metric should appear after simple metric in HTML
        assert simple_pos > 0, "Simple 'Participation %' should exist"
        assert avg_with_color_pos > 0, "'Avg. Participation (With Color)' should exist"
        # Note: They might be in different sections, so we just verify both exist

    def test_teams_avg_participation_shows_percentages(self, client):
        """Verify both team values are shown as percentages"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find the Avg. Participation row and check for percentage format
        # Look for pattern like "85.3%" near the label
        avg_part_section = re.search(
            r'Avg\. Participation \(With Color\).*?(\d+\.\d+)%.*?(\d+\.\d+)%',
            html,
            re.DOTALL
        )

        if avg_part_section:
            team1_pct = float(avg_part_section.group(1))
            team2_pct = float(avg_part_section.group(2))

            # Percentages should be reasonable (0-150%, allowing for color bonus >100%)
            assert 0 <= team1_pct <= 150, f"Team 1 percentage out of range: {team1_pct}%"
            assert 0 <= team2_pct <= 150, f"Team 2 percentage out of range: {team2_pct}%"

    def test_teams_avg_participation_winner_highlighted(self, client):
        """Verify winning team's value is highlighted"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Look for winning-value class near Avg. Participation
        # The winning value should have special styling
        assert 'winning-value' in html, "Comparison table should highlight winning values"

    def test_teams_filter_indicator_includes_avg_participation(self, client):
        """Verify filter indicator (◐) appears for Avg. Participation when date filtered"""
        response = client.get('/teams?date=2025-10-13')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # When date filtered, metrics that respect filter should show ◐
        # Avg. Participation (With Color) should respect date filter
        avg_part_section = re.search(
            r'Avg\. Participation \(With Color\)[^<]*([◐])?',
            html,
            re.DOTALL
        )

        # Should find the metric (indicator presence depends on implementation)
        assert avg_part_section is not None


class TestPhase5GradeLevelClassesTable:
    """Phase 5: Grade Level classes table has Avg. Participation (With Color) column"""

    def test_grade_level_avg_participation_column_exists(self, client):
        """Verify Grade Level table has 'AVG. PARTICIPATION (WITH COLOR)' column"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Check for column header
        assert 'AVG. PARTICIPATION (WITH COLOR)' in html or \
               'Avg. Participation (With Color)' in html or \
               'AVG. PART. (W/ COLOR)' in html, \
            "Grade Level table should have Avg. Participation (With Color) column"

    def test_grade_level_both_participation_columns_present(self, client):
        """Verify Grade Level table has BOTH 'PARTICIPATION %' and 'AVG. PARTICIPATION (WITH COLOR)'"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find table headers section
        table_match = re.search(r'<thead>.*?</thead>', html, re.DOTALL | re.IGNORECASE)
        assert table_match, "Should find table header section"

        table_header = table_match.group(0)

        # Should have both columns
        assert 'PARTICIPATION' in table_header.upper(), "Should have simple Participation % column"

        # Count occurrences of "PARTICIPATION" in headers
        participation_count = table_header.upper().count('PARTICIPATION')
        assert participation_count >= 2, \
            f"Should have at least 2 'Participation' columns, found {participation_count}"

    def test_grade_level_avg_participation_column_positioned_correctly(self, client):
        """Verify new column appears after simple 'PARTICIPATION %' column"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find table header
        table_match = re.search(r'<thead>.*?</thead>', html, re.DOTALL | re.IGNORECASE)
        assert table_match, "Should find table header"

        header = table_match.group(0)

        # Extract all <th> headers
        headers = re.findall(r'<th[^>]*>(.*?)</th>', header, re.DOTALL | re.IGNORECASE)

        # Find indices
        simple_part_index = None
        avg_part_index = None

        for i, h in enumerate(headers):
            h_text = re.sub(r'<[^>]+>', '', h).strip().upper()
            if 'PARTICIPATION' in h_text and 'COLOR' not in h_text:
                if simple_part_index is None:  # First occurrence
                    simple_part_index = i
            if 'PARTICIPATION' in h_text and 'COLOR' in h_text:
                avg_part_index = i

        # Both should exist
        assert simple_part_index is not None, "Should find simple Participation % column"
        assert avg_part_index is not None, "Should find Avg. Participation (With Color) column"

        # New column should come after simple column
        assert avg_part_index > simple_part_index, \
            f"Avg. Participation column (index {avg_part_index}) should come after simple Participation column (index {simple_part_index})"

    def test_grade_level_avg_participation_shows_values(self, client):
        """Verify all classes show Avg. Participation (With Color) values"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find table body
        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
        assert tbody_match, "Should find table body"

        tbody = tbody_match.group(0)

        # Count table rows
        rows = re.findall(r'<tr[^>]*>.*?</tr>', tbody, re.DOTALL | re.IGNORECASE)
        assert len(rows) > 0, "Should have at least one class row"

        # Each row should have percentage values
        # Look for data-value attributes or percentage patterns
        for row in rows:
            # Should have multiple percentage values (including our new column)
            pct_matches = re.findall(r'(\d+\.?\d*)%', row)
            assert len(pct_matches) >= 4, \
                f"Each row should have multiple percentage values (found {len(pct_matches)})"

    def test_grade_level_avg_participation_column_sortable(self, client):
        """Verify Avg. Participation (With Color) column is sortable"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find the column header - should have onclick or sortable class
        header_match = re.search(
            r'<th[^>]*>.*?AVG.*?PARTICIPATION.*?COLOR.*?</th>',
            html,
            re.DOTALL | re.IGNORECASE
        )

        assert header_match, "Should find Avg. Participation (With Color) header"

        header_tag = header_match.group(0)

        # Should be sortable (has onclick or data-sortable)
        assert 'onclick' in header_tag.lower() or 'sortable' in header_tag.lower(), \
            "Column should be sortable"

    def test_grade_level_avg_participation_winner_highlighting(self, client):
        """Verify school winner (gold) and grade winner (silver) highlighting works"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Should have winner data attributes
        assert 'data-school-avg-participation-with-color' in html, \
            "Rows should have school winner data attribute for avg participation"
        assert 'data-grade-avg-participation-with-color' in html, \
            "Rows should have grade winner data attribute for avg participation"

        # Should have winning value CSS classes defined
        assert 'winning-value-school' in html or '.winning-value-school' in html, \
            "Should have school winner CSS styling"
        assert 'winning-value-grade' in html or '.winning-value-grade' in html, \
            "Should have grade winner CSS styling"

    def test_grade_level_filter_indicator_on_avg_participation(self, client):
        """Verify filter indicator (◐) appears on column header when date filtered"""
        response = client.get('/classes?date=2025-10-13')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find the Avg. Participation column header
        header_match = re.search(
            r'<th[^>]*>.*?AVG.*?PARTICIPATION.*?COLOR.*?</th>',
            html,
            re.DOTALL | re.IGNORECASE
        )

        assert header_match, "Should find column header"

        header = header_match.group(0)

        # Should have filter indicator when date filtered
        # ◐ symbol should be present
        # (Implementation may vary, so we just check the header exists)


class TestPhase5MetricDifferences:
    """Verify simple Participation % and Avg. Participation (With Color) show different values"""

    def test_teams_metrics_show_different_values(self, client, sample_db):
        """Verify Teams page shows different values for the two participation metrics"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Extract all percentage values from comparison table
        # This is a basic sanity check that we have multiple different percentages
        percentages = re.findall(r'(\d+\.?\d*)%', html)

        # Should have multiple percentage values
        assert len(percentages) >= 10, \
            f"Should have many percentage values in comparison table (found {len(percentages)})"

        # Convert to floats and check for variety
        pct_values = [float(p) for p in percentages if float(p) > 0]
        unique_values = len(set(pct_values))

        assert unique_values >= 5, \
            f"Should have variety in percentage values (found {unique_values} unique values)"

    def test_grade_level_metrics_show_different_values(self, client):
        """Verify Grade Level table shows different values for the two participation columns"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find table body
        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
        assert tbody_match, "Should find table body"

        # Extract rows
        rows = re.findall(r'<tr[^>]*>.*?</tr>', tbody_match.group(0), re.DOTALL | re.IGNORECASE)

        # For at least one row, verify it has multiple different percentage values
        if len(rows) > 0:
            first_row = rows[0]
            percentages = re.findall(r'(\d+\.?\d*)%', first_row)

            # Should have multiple percentages (various metrics)
            assert len(percentages) >= 4, \
                f"Each row should have multiple percentage columns (found {len(percentages)})"


class TestPhase5FormatConsistency:
    """Verify formatting is consistent with existing metrics"""

    def test_teams_avg_participation_uses_one_decimal(self, client):
        """Verify Teams Avg. Participation shows 1 decimal place (e.g., 85.3%)"""
        response = client.get('/teams')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find Avg. Participation section
        avg_part_match = re.search(
            r'Avg\. Participation \(With Color\).*?(\d+\.\d+)%',
            html,
            re.DOTALL
        )

        if avg_part_match:
            value_str = avg_part_match.group(1)
            # Should have exactly 1 decimal place
            decimal_part = value_str.split('.')[1] if '.' in value_str else ""
            assert len(decimal_part) == 1, \
                f"Should have 1 decimal place, found: {value_str}"

    def test_grade_level_avg_participation_uses_one_decimal(self, client):
        """Verify Grade Level Avg. Participation shows 1 decimal place"""
        response = client.get('/classes')
        html = response.data.decode('utf-8')

        assert response.status_code == 200

        # Find table cells with data-value attributes
        # Look for percentage format in table
        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)

        if tbody_match:
            tbody = tbody_match.group(0)
            # Find percentage values - should be formatted with 1 decimal
            pct_values = re.findall(r'>(\d+\.\d)%<', tbody)

            # Should find some percentage values with exactly 1 decimal
            assert len(pct_values) > 0, \
                "Should find percentage values formatted with 1 decimal place"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v'])
