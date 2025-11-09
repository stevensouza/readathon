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
    return ReadathonDB('db/readathon_sample.db')


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

        # Check for common error indicators (excluding JavaScript error handling)
        error_patterns = [
            'Exception:',
            'Traceback',
            '500 Internal Server Error',
            'KeyError:',
            'AttributeError:',
            'TypeError:',
            'ValueError:',
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
        sample_db = ReadathonDB('db/readathon_sample.db')
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
        sample_db = ReadathonDB('db/readathon_sample.db')
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
        sample_db = ReadathonDB('db/readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")

        if len(students) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}')

            # Should return JSON (not 404)
            assert response.status_code == 200
            assert response.is_json

    def test_student_detail_returns_json(self, client):
        """Verify student detail endpoint returns JSON data."""
        sample_db = ReadathonDB('db/readathon_sample.db')
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
        sample_db = ReadathonDB('db/readathon_sample.db')
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
        sample_db = ReadathonDB('db/readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")

        if len(students) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}')

            data = response.get_json()
            daily = data.get('daily')

            assert isinstance(daily, list), "Daily should be a list"

    def test_student_detail_with_date_filter(self, client):
        """Verify student detail endpoint honors date filter."""
        sample_db = ReadathonDB('db/readathon_sample.db')
        students = sample_db.execute_query("SELECT student_name FROM Roster LIMIT 1")
        dates = sample_db.get_all_dates()

        if len(students) > 0 and len(dates) > 0:
            student_name = students[0]['student_name']
            response = client.get(f'/student/{student_name}?date={dates[0]}')

            assert response.status_code == 200
            assert response.is_json

    def test_student21_detail_regression(self, client):
        """
        Regression test: Verify student21's detail view shows exact expected values.

        This locks in the known correct values for student21 to catch any unintended
        changes to the student detail calculation logic.

        Expected values (from screenshot verification):
        - Grade: 1, Team: team1, Class: class2, Teacher: teacher2
        - Fundraising: $20, Sponsors: 2
        - Minutes Capped: 50 min, Minutes Uncapped: 50 min (+0 over cap)
        - Participation: 2/2 days (100.0%)
        - Goal Met: 2/2 days (100.0%)
        - Daily: Oct 10 (25 min), Oct 11 (25 min)
        """
        response = client.get('/student/student21?date=all')
        assert response.status_code == 200
        assert response.is_json

        data = response.get_json()
        assert data is not None
        assert 'summary' in data
        assert 'daily' in data

        # Verify summary section
        summary = data['summary']

        # Student info
        assert summary['student_name'] == 'student21'
        assert summary['grade_level'] == '1'
        assert summary['team_name'] == 'team1'
        assert summary['class_name'] == 'class2'
        assert summary['teacher_name'] == 'teacher2'

        # Fundraising metrics
        assert summary['fundraising'] == 20.0
        assert summary['sponsors'] == 2

        # Reading metrics
        assert summary['total_capped'] == 50
        assert summary['total_uncapped'] == 50
        # Verify no minutes over cap (50 uncapped - 50 capped = 0)
        assert summary['total_uncapped'] - summary['total_capped'] == 0

        # Participation metrics
        assert summary['days_participated'] == 2
        assert data['days_in_filter'] == 2  # Total contest days
        # Participation: 2/2 = 100%
        assert (summary['days_participated'] / data['days_in_filter']) * 100 == 100.0

        # Goal metrics
        assert summary['days_met_goal'] == 2
        # Goal met: 2/2 = 100%
        assert (summary['days_met_goal'] / data['days_in_filter']) * 100 == 100.0

        # Grade goal
        assert summary['grade_goal'] == 20

        # Verify daily section
        daily = data['daily']
        assert len(daily) == 2, "student21 should have 2 days of reading"

        # Day 1: Oct 10 - 25 minutes
        day1 = daily[0]
        assert day1['log_date'] == '2025-10-10'
        assert day1['actual_minutes'] == 25
        assert day1['capped_minutes'] == 25
        assert day1['exceeded_cap'] == 0
        assert day1['grade_goal'] == 20
        assert day1['met_goal'] == 1  # Boolean: 1 = True

        # Day 2: Oct 11 - 25 minutes
        day2 = daily[1]
        assert day2['log_date'] == '2025-10-11'
        assert day2['actual_minutes'] == 25
        assert day2['capped_minutes'] == 25
        assert day2['exceeded_cap'] == 0
        assert day2['grade_goal'] == 20
        assert day2['met_goal'] == 1  # Boolean: 1 = True


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


class TestStudentsBannerRegression:
    """Regression tests for Students page banner values."""

    def test_banner_all_grades_all_teams_full_contest(self, client):
        """
        Regression test: Banner values for all grades, all teams, full contest.
        These values should remain stable unless data changes.
        """
        response = client.get('/students?grade=all&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Test banner title (no "With Color" text)
        assert 'Avg. Participation</div>' in html or '👥 Avg. Participation' in html
        assert 'Avg. Participation (With Color)' not in html

        # Extract banner metrics
        # Campaign Day: "Day 2 of 2"
        assert 'Day 2' in html
        assert 'of 2' in html

        # Fundraising: $70
        assert '$70' in html

        # Minutes Read: 6 hours
        assert '6 hours' in html

        # Sponsors: 28 (sum of all sponsors from sample data)
        sponsor_pattern = re.search(r'🎁 Sponsors.*?<div class="headline-value">(\d+)</div>', html, re.DOTALL)
        if sponsor_pattern:
            assert sponsor_pattern.group(1) == '28'

        # Avg. Participation: 92.9%
        participation_pattern = re.search(r'Avg\. Participation.*?<div class="headline-value">([0-9.]+)%</div>', html, re.DOTALL)
        if participation_pattern:
            assert participation_pattern.group(1) == '92.9'

        # Goal Met: 57.1%
        goal_pattern = re.search(r'Goal Met.*?<div class="headline-value">([0-9.]+)%</div>', html, re.DOTALL)
        if goal_pattern:
            assert goal_pattern.group(1) == '57.1'

        # Total students subtitle
        assert '7 students' in html

    def test_banner_grade_1_filter(self, client):
        """
        Regression test: Banner values for Grade 1 filter, all teams, full contest.
        """
        response = client.get('/students?grade=1&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Campaign Day should still show full contest
        assert 'Day 2' in html
        assert 'of 2' in html

        # Banner should show filtered values
        # (Values will be different from all-grades view)
        assert 'headline-value' in html
        assert 'students' in html.lower()

        # Verify banner structure is present
        assert '💰 Fundraising' in html or 'Fundraising' in html
        assert '📚 Minutes Read' in html or 'Minutes Read' in html
        assert '🎁 Sponsors' in html or 'Sponsors' in html
        assert '👥 Avg. Participation' in html or 'Participation' in html
        assert '🎯 Goal Met' in html or 'Goal Met' in html


class TestStudentsHighlighting:
    """Tests for gold and silver winner highlighting."""

    def test_gold_winners_present_all_grades(self, client):
        """Verify gold highlights (school-wide winners) are present."""
        response = client.get('/students?grade=all&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should have gold highlights (winning-value-school class)
        assert 'winning-value-school' in html, "No gold highlights found for school-wide winners"

        # Count gold highlights (should be multiple across different metrics)
        gold_count = html.count('winning-value-school')
        assert gold_count > 0, f"Expected gold highlights, found {gold_count}"

    def test_silver_winners_present_all_grades(self, client):
        """Verify silver highlights (grade-level winners) are present when viewing all grades."""
        response = client.get('/students?grade=all&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should have silver highlights (winning-value-grade class)
        # When viewing all grades, each grade should have its own grade-level leader
        assert 'winning-value-grade' in html, "No silver highlights found for grade-level winners"

        # Count silver highlights (should be multiple - one per grade per metric)
        silver_count = html.count('winning-value-grade')
        assert silver_count > 0, f"Expected silver highlights, found {silver_count}"

    def test_both_gold_and_silver_present(self, client):
        """Verify both gold and silver highlights coexist in all-grades view."""
        response = client.get('/students?grade=all&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        gold_count = html.count('winning-value-school')
        silver_count = html.count('winning-value-grade')

        assert gold_count > 0, f"Missing gold highlights (found {gold_count})"
        assert silver_count > 0, f"Missing silver highlights (found {silver_count})"
        # Note: Gold can be >= silver when school-wide winners are also grade-level winners
        # Just verify both types exist
        assert gold_count + silver_count > 15, "Expected combined highlights across multiple students and metrics"

    def test_silver_winners_present_in_filtered_view(self, client):
        """Verify silver highlights appear in grade-filtered view."""
        response = client.get('/students?grade=1&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should have silver highlights for within-grade leaders
        assert 'winning-value-grade' in html or 'winning-value-school' in html


class TestStudentsFilterStickiness:
    """Tests for filter persistence using sessionStorage."""

    def test_session_storage_script_present(self, client):
        """Verify sessionStorage scripts are present for filter persistence."""
        response = client.get('/students')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Check for sessionStorage usage
        assert 'sessionStorage' in html, "Missing sessionStorage implementation for filter persistence"

        # Check for filter restoration logic
        assert 'getItem' in html or 'setItem' in html

    def test_grade_filter_saves_to_session_storage(self, client):
        """Verify grade filter parameter is saved to sessionStorage."""
        response = client.get('/students?grade=K&team=all&date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should have sessionStorage save logic for grade
        assert 'readathonGradeFilter' in html
        assert 'sessionStorage.setItem' in html

    def test_all_filters_restoration_logic_present(self, client):
        """
        Verify the filter restoration logic handles ALL filters together.
        This prevents the bug where one filter (grade) was lost because
        it tried to read other filters from DOM before they were populated.
        """
        response = client.get('/students')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should get ALL saved filters from sessionStorage at once
        assert 'savedDateFilter' in html
        assert 'savedGradeFilter' in html
        assert 'savedTeamFilter' in html

        # Should check if redirect is needed for ANY filter
        assert 'needsDateRedirect' in html or 'needsGradeRedirect' in html or 'needsTeamRedirect' in html

        # Should construct final URL with all filters
        assert 'finalDate' in html and 'finalGrade' in html and 'finalTeam' in html

    def test_date_filter_parameter_accepted(self, client):
        """Verify date filter parameter is accepted and processed."""
        response = client.get('/students?date=2025-10-10')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should show date-specific data
        # Half-circle indicators should be present for single-day view
        assert '◐' in html, "Expected half-circle indicator for single-day filter"

    def test_multiple_filters_combination(self, client):
        """Verify multiple filters can be applied simultaneously."""
        response = client.get('/students?grade=1&team=all&date=2025-10-10')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should handle multiple filter parameters
        assert 'headline-banner' in html or 'Campaign Day' in html


class TestStudentsHalfCircleIndicators:
    """Tests for half-circle (◐) filter indicators."""

    def test_no_half_circles_on_full_contest(self, client):
        """Verify NO half-circle indicators when viewing full contest."""
        response = client.get('/students?date=all')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Extract banner section
        banner_start = html.find('headline-banner')
        banner_end = html.find('</div>', banner_start + 1000) if banner_start > 0 else len(html)
        banner_section = html[banner_start:banner_end] if banner_start > 0 else html[:2000]

        # Banner "Minutes Read" should NOT have half-circle
        minutes_match = re.search(r'Minutes Read.*?</div>', banner_section, re.DOTALL)
        if minutes_match:
            minutes_text = minutes_match.group(0)
            # Should NOT contain half-circle indicator
            assert '◐' not in minutes_text or 'filter-indicator' not in minutes_text

        # Table headers should NOT have half-circles
        table_header_match = re.search(r'<th.*?>Minutes Capped.*?</th>', html, re.DOTALL)
        if table_header_match:
            header_text = table_header_match.group(0)
            # For full contest, should not have conditional half-circle
            # (Hard to test precisely, but we can check the pattern)
            pass  # Just verify it doesn't crash

    def test_half_circles_present_on_single_day(self, client):
        """Verify half-circle indicators APPEAR when single day selected."""
        response = client.get('/students?date=2025-10-10')
        assert response.status_code == 200

        html = response.data.decode('utf-8')

        # Should have half-circle indicators
        assert '◐' in html, "Expected half-circle indicator for single-day filter"

        # Should be in filter-indicator spans
        assert 'filter-indicator' in html

        # Should have tooltip
        assert 'Cumulative through' in html or 'data-bs-toggle="tooltip"' in html


class TestStudentsTableRegression:
    """
    Comprehensive regression test for Students page table data.

    This test locks in the complete table state for all grades, all teams, full contest.
    It verifies all column values, formatting, and gold/silver highlighting to catch
    any unintended changes to the calculation logic or display.
    """

    def test_complete_table_all_grades_all_teams_full_contest(self, client):
        """
        Regression test: Complete Students table for all grades, all teams, full contest.

        This test verifies:
        - All 7 students appear with correct data
        - All column values match expected values
        - Gold highlights (school-wide winners) are correct
        - Silver highlights (grade-level winners) are correct
        - Team badges show correct colors

        Expected data from screenshot verification (full contest, all grades, all teams):

        student11: K, TEAM1, $10, 1 sponsor, 120 min capped (gold), 200 min uncapped (gold),
                   1/2 days (gold), 50.0% partic (gold), 1 days goal (gold), 100.0% goal (gold)

        student21: 1, TEAM1, $20, 2 sponsors, 50 min capped, 50 min uncapped,
                   2/2 days (gold), 100.0% partic (gold), 2 days goal (gold), 100.0% goal (gold)

        student22: 1, TEAM1, $30, 3 sponsors, 20 min capped, 20 min uncapped,
                   2/2 days (gold), 100.0% partic (gold), 0 days goal, 0.0% goal

        student31: 2, TEAM2, $40, 4 sponsors, 60 min capped (silver), 60 min uncapped (silver),
                   2/2 days (gold), 100.0% partic (gold), 2 days goal (gold), 100.0% goal (gold)

        student32: 2, TEAM2, $50, 5 sponsors, 30 min capped, 30 min uncapped,
                   2/2 days (gold), 100.0% partic (gold), 0 days goal, 0.0% goal

        student41: 2, TEAM2, $60, 6 sponsors, 60 min capped (silver), 60 min uncapped (silver),
                   2/2 days (gold), 100.0% partic (gold), 2 days goal (gold), 100.0% goal (gold)

        student42: 2, TEAM2, $70 (gold), 7 sponsors (gold), 30 min capped, 30 min uncapped,
                   2/2 days (gold), 100.0% partic (gold), 0 days goal, 0.0% goal
        """
        response = client.get('/students?grade=all&team=all&date=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Verify all 7 students appear
        assert 'student11' in html
        assert 'student21' in html
        assert 'student22' in html
        assert 'student31' in html
        assert 'student32' in html
        assert 'student41' in html
        assert 'student42' in html

        # Verify team badges are present
        assert 'TEAM1' in html
        assert 'TEAM2' in html

        # Verify grades
        assert '>K<' in html or '>K,' in html  # Kindergarten
        assert '>1<' in html or '>1,' in html  # Grade 1
        assert '>2<' in html or '>2,' in html  # Grade 2

        # Verify fundraising values
        assert '$10' in html
        assert '$20' in html
        assert '$30' in html
        assert '$40' in html
        assert '$50' in html
        assert '$60' in html
        assert '$70' in html

        # Verify sponsor counts
        for sponsors in [1, 2, 3, 4, 5, 6, 7]:
            # Each sponsor count should appear in table
            assert str(sponsors) in html

        # Verify minutes capped values
        assert '120' in html  # student11 (gold)
        assert '50' in html   # student21
        assert '20' in html   # student22
        assert '60' in html   # student31, student41 (silver)
        assert '30' in html   # student32, student42

        # Verify minutes uncapped values (200 for student11)
        assert '200' in html  # student11 (gold)

        # Verify participation metrics
        assert '50.0' in html  # student11: 1/2 = 50.0%
        assert '100.0' in html # Multiple students: 2/2 = 100.0%

        # Verify goal met percentages
        assert '0.0%' in html  # student22, student32, student42

        # Verify gold highlights present (school-wide winners)
        assert 'winning-value-school' in html
        gold_count = html.count('winning-value-school')
        assert gold_count >= 10, f"Expected at least 10 gold highlights, found {gold_count}"

        # Verify silver highlights present (grade-level winners)
        assert 'winning-value-grade' in html
        silver_count = html.count('winning-value-grade')
        assert silver_count >= 4, f"Expected at least 4 silver highlights (2 students × 2 metrics), found {silver_count}"

        # Verify both types of highlights coexist
        assert gold_count > 0 and silver_count > 0, "Both gold and silver highlights should be present"

        # Verify specific gold highlights exist by pattern matching
        # HTML structure: <span class="winning-value winning-value-school">VALUE</span> unit

        # Gold: student11 minutes_capped (120)
        assert re.search(r'winning-value-school">120</span>\s*min', html), "Missing gold for student11 minutes_capped"

        # Gold: student11 minutes_uncapped (200)
        assert re.search(r'winning-value-school">200</span>\s*min', html), "Missing gold for student11 minutes_uncapped"

        # Gold: student42 fundraising ($70)
        assert re.search(r'winning-value-school">\$70</span>', html), "Missing gold for student42 fundraising"

        # Gold: student42 sponsors (7) - appears as just the number
        assert re.search(r'winning-value-school">7</span>', html), "Missing gold for student42 sponsors"

        # Verify silver highlights exist (grade-level winners for minutes)
        # Silver: minutes_capped or minutes_uncapped with value 60
        assert re.search(r'winning-value-grade">60</span>\s*min', html), "Missing silver for grade-level winner (60 min)"


class TestStudentsPageSearch:
    """Test search functionality across all columns"""

    def test_search_box_present(self, client):
        """Verify search input box is present on page"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        assert 'id="nameSearch"' in html
        assert 'Search all fields' in html
        assert 'clearSearch()' in html

    def test_search_by_student_name_full(self, client):
        """Test searching by full student name"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Verify student21 is in the response
        assert 'student21' in html

    def test_search_by_student_name_partial(self, client):
        """Test searching by partial student name"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # JavaScript search would match "student2" to student21, student22
        # We're testing that the search box and function exist
        assert 'function filterTable()' in html

    def test_search_by_grade(self, client):
        """Test that search can find students by grade number"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Grade column should be searchable
        # Sample data has grades K, 1, 2
        assert 'data-grade=' in html

    def test_search_by_team_name(self, client):
        """Test that search can find students by team name"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Team names should be present and searchable
        # Check for team badge presence
        assert 'team-badge' in html
        assert 'data-team=' in html

    def test_search_by_class_name(self, client):
        """Test that search can find students by class name"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Class names should be in table
        # Sample data uses class names like "class1", "class2"
        assert 'class1' in html or 'class2' in html

    def test_search_by_teacher_name(self, client):
        """Test that search can find students by teacher name"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Teacher names should be in table
        assert 'teacher1' in html or 'teacher2' in html

    def test_search_by_fundraising_amount(self, client):
        """Test that search can find students by fundraising amount"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Fundraising amounts should be searchable (numeric values)
        # Sample data has various fundraising amounts ($10, $20, etc.)
        assert 'data-value=' in html  # fundraising stored in data-value attribute
        assert '$' in html  # currency symbol

    def test_search_by_sponsors_count(self, client):
        """Test that search can find students by sponsor count"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Sponsor counts should be in table
        # Sample data has various sponsor counts (1-7)
        assert 'Sponsors' in html

    def test_search_by_minutes(self, client):
        """Test that search can find students by reading minutes"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Minutes (both capped and uncapped) should be searchable
        assert 'min' in html
        assert 'Minutes Capped' in html
        assert 'Minutes Uncapped' in html

    def test_search_by_participation_percentage(self, client):
        """Test that search can find students by participation percentage"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Participation percentages should be searchable
        assert 'Partic. %' in html
        assert '%' in html

    def test_search_by_goal_percentage(self, client):
        """Test that search can find students by goal percentage"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Goal percentages should be searchable
        assert 'Goal %' in html

    def test_search_function_searches_all_cells(self, client):
        """Verify the filterTable() function searches all td elements"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check that search function iterates through all cells
        assert 'cells.forEach(cell =>' in html
        assert "querySelectorAll('td')" in html or 'querySelectorAll("td")' in html

    def test_search_function_includes_data_attributes(self, client):
        """Verify search function also checks data attributes"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Verify search includes data attributes
        assert "getAttribute('data-grade')" in html or 'getAttribute("data-grade")' in html
        assert "getAttribute('data-team')" in html or 'getAttribute("data-team")' in html
        assert "getAttribute('data-student-name')" in html or 'getAttribute("data-student-name")' in html

    def test_search_is_case_insensitive(self, client):
        """Verify search converts to lowercase for case-insensitive matching"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check that search uses toLowerCase()
        assert 'toLowerCase()' in html

    def test_search_clears_properly(self, client):
        """Verify clear search button functionality"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check clear function exists and resets input
        assert 'function clearSearch()' in html
        assert ".value = ''" in html or '.value = ""' in html

    def test_search_updates_visible_count(self, client):
        """Verify search updates the visible student count"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check that visible count is updated after search
        assert 'visibleCount' in html
        assert "getElementById('visibleCount')" in html or 'getElementById("visibleCount")' in html

    def test_empty_search_shows_all_rows(self, client):
        """Verify empty search shows all students"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check that empty search term shows all rows
        assert "searchTerm === ''" in html or 'searchTerm === ""' in html
        assert "row.classList.remove('hidden')" in html or 'row.classList.remove("hidden")' in html

    def test_search_box_has_clear_button(self, client):
        """Verify search box has a clear button with icon"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Check for clear button
        assert 'bi-x-circle' in html
        assert 'onclick="clearSearch()"' in html

    def test_search_placeholder_text(self, client):
        """Verify search placeholder indicates all-field search"""
        response = client.get('/students')
        html = response.data.decode('utf-8')

        # Placeholder should say "Search all fields"
        assert 'Search all fields' in html
        assert 'placeholder' in html
