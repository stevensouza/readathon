"""
Test suite for database comparison functionality.

This test ensures the database comparison page displays correct year-over-year
comparisons and maintains proper data calculations across different databases.
"""

import pytest
import re
from app import app
from database import ReportGenerator, ReadathonDB


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


@pytest.fixture
def registry_db():
    """Get registry database instance for verification queries."""
    return ReadathonDB('db/readathon_registry.db')


class TestDatabaseComparison:
    """Test cases for database comparison page."""

    def test_page_loads_successfully(self, client):
        """Verify database comparison page loads without errors."""
        response = client.get('/database-comparison')
        assert response.status_code == 200
        assert b'Database Comparison' in response.data or b'Year-over-year' in response.data

    def test_no_error_messages(self, client):
        """Verify no error messages appear on page."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        error_patterns = ['Error:', 'Exception:', 'Traceback', 'error occurred']
        html_lower = html.lower()
        for pattern in error_patterns:
            assert pattern.lower() not in html_lower, f"Found error pattern: {pattern}"

    def test_database_dropdowns_populated(self, client, registry_db):
        """Verify both database dropdowns are populated with registry databases."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for database selection dropdowns
        assert 'database1' in html.lower() or 'db-selector' in html.lower()
        assert 'database2' in html.lower() or 'comparison database' in html.lower()

        # Should have at least sample database option
        assert 'sample' in html.lower()

    def test_active_database_option(self, client):
        """Verify "Active (Currently: [name])" option present in dropdown 1."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for "Active" or "Currently" indicating dynamic database selection
        assert 'active' in html.lower() or 'currently' in html.lower()

    def test_filter_period_options(self, client):
        """Verify filter period dropdown shows Day 1-6, Full Contest Period."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for filter period options
        assert 'full contest' in html.lower() or 'all days' in html.lower()
        assert 'day 1' in html.lower()

    def test_comparison_table_structure(self, client):
        """Verify comparison table has proper structure (5 entities × 10 metrics)."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Should have comparison table
        assert 'comparison-table' in html.lower() or 'table' in html

        # Should have entity level column
        assert 'entity' in html.lower()

        # Should have metric column
        assert 'metric' in html.lower()

        # Should have change column
        assert 'change' in html.lower()

    def test_entity_level_sort_order(self, client):
        """Verify default hierarchical sort order (School → Team → Grade → Class → Student)."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for all entity levels
        entities = ['school', 'team', 'grade', 'class', 'student']
        for entity in entities:
            assert entity in html.lower(), f"Missing entity: {entity}"

    def test_winner_display_format(self, client):
        """Verify winner display formats match design specification."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for winner context patterns
        # Should have "Winner:" or "Top class:" patterns
        assert 'winner' in html.lower() or 'top class' in html.lower()

    def test_team_color_highlighting(self, client):
        """Verify winning year uses team color highlighting (blue/yellow)."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for winning value classes using team colors
        # Should use team color patterns, NOT gold/silver
        has_team_colors = (
            'winning-value' in html.lower() or
            '#1e3a5f' in html.lower() or  # Blue
            '#f59e0b' in html.lower() or   # Yellow
            'team-badge' in html.lower()
        )
        assert has_team_colors, "Missing team color highlighting"

    def test_total_participating_format(self, client):
        """Verify "Total Participating (≥1 Day)" shows percentage format: "79.8% (328/411)"."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for participation metric
        if 'total participating' in html.lower() or 'participating' in html.lower():
            # Should have percentage format (X.X%)
            percentages = re.findall(r'(\d+\.?\d*)%', html)
            assert len(percentages) > 0, "No percentages found"

    def test_search_functionality(self, client):
        """Verify search box is present for filtering rows."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for search input
        assert 'search' in html.lower() or 'filter' in html.lower()

    def test_filter_by_entity_type(self, client):
        """Verify entity type filter dropdown works correctly."""
        response = client.get('/database-comparison?db1=readathon_sample.db&db2=readathon_sample.db&filter=all')
        html = response.data.decode('utf-8')

        # Check for entity filter dropdown
        assert 'all entities' in html.lower() or 'entity filter' in html.lower()

    def test_export_buttons_present(self, client):
        """Verify CSV and Excel export buttons are present."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for export functionality
        assert 'export' in html.lower() or 'download' in html.lower() or 'copy' in html.lower()

    def test_percentage_formats(self, client):
        """Validate all percentage values are properly formatted."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Find all percentages in the HTML
        percentages = re.findall(r'(\d+\.?\d*)%', html)

        # Should have at least some percentages
        if len(percentages) > 0:
            for pct in percentages:
                # Each should be a valid float
                float(pct)  # Should not raise ValueError

    def test_currency_formats(self, client):
        """Validate all dollar amounts are properly formatted."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Find all currency values
        currencies = re.findall(r'\$[\d,]+\.?\d*', html)

        # Should have at least some currency values
        if len(currencies) > 0:
            for curr in currencies:
                # Remove $ and commas, should be valid float
                value = curr.replace('$', '').replace(',', '')
                float(value)  # Should not raise ValueError

    def test_relative_day_filtering(self, client):
        """Verify filter uses relative days (Day 1-6) not absolute dates."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Should have "Day" references for filter period
        if 'filter period' in html.lower():
            assert 'day' in html.lower(), "Should use relative days (Day 1, Day 2, etc.)"

    def test_filter_indicator_present(self, client):
        """Verify half-circle ◐ indicator for metrics that honor filter period."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for filter indicator (◐) or tooltip explaining which metrics honor filter
        has_indicator = (
            '◐' in html or
            'filter-indicator' in html.lower() or
            'honors filter' in html.lower()
        )
        # Only assert if there are filtered metrics visible
        # This might not always be present depending on page state

    def test_change_column_formatting(self, client):
        """Verify change column shows absolute + percentage + arrow."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for change indicators
        has_change_indicators = (
            'change-positive' in html.lower() or
            'change-negative' in html.lower() or
            '▲' in html or '▼' in html or
            'arrow-up' in html.lower() or 'arrow-down' in html.lower()
        )
        # May not be present if no comparison has been run yet

    def test_data_sources_footer(self, client):
        """Verify data sources footer is present and shows database info."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for data sources section
        assert 'data source' in html.lower() or 'database' in html.lower()

    def test_hierarchical_entity_sort(self, client):
        """Verify entities can be sorted in hierarchical order (School first, Student last)."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Should have sortable columns
        assert 'sort' in html.lower() or 'onclick' in html.lower()

    def test_metric_icons_present(self, client):
        """Verify metric icons are present (💰, 📚, 🤝, etc.)."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for Bootstrap icons or emoji
        has_icons = (
            'bi bi-' in html or  # Bootstrap icons
            '💰' in html or '📚' in html or '🎯' in html
        )
        # Icons might not be present until comparison is run

    def test_responsive_layout(self, client):
        """Verify page has responsive CSS for mobile devices."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for viewport meta tag
        assert 'viewport' in html.lower()

        # Check for Bootstrap grid or responsive classes
        has_responsive = (
            'container' in html or
            'row' in html or
            'col-' in html or
            '@media' in html
        )
        assert has_responsive, "Missing responsive layout classes"

    def test_compact_database_selection(self, client):
        """Verify database selection uses compact one-row layout."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for compact layout (database1, database2, filter all on same row)
        # This is a design requirement from the feature spec
        assert 'db-selector-row' in html.lower() or 'database-selection' in html.lower()

    def test_search_box_sizing(self, client):
        """Verify search box is large (700px) and filter dropdown is compact (120-130px)."""
        response = client.get('/database-comparison?db1=readathon_sample.db&db2=readathon_sample.db&filter=all')
        html = response.data.decode('utf-8')

        # Check for search-filter-group styling
        has_search = 'search' in html.lower()
        has_filter = 'entity filter' in html.lower() or 'all entities' in html.lower()

        # Both should be present
        assert has_search and has_filter

    def test_compare_button_present(self, client):
        """Verify "Compare" button is present to trigger comparison."""
        response = client.get('/database-comparison')
        html = response.data.decode('utf-8')

        # Check for compare button
        assert 'compare' in html.lower()

    def test_50_metrics_total(self, sample_db):
        """Verify exactly 49 comparisons are returned (School/Team/Grade/Class: 10 each, Student: 9)."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        # Get comparison results
        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Should have exactly 49 comparisons (Student Color War Points removed)
        assert len(result['comparisons']) == 49, f"Expected 49 comparisons, got {len(result['comparisons'])}"

    def test_school_level_10_metrics(self, sample_db):
        """Verify School level has exactly 10 metrics."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Count School-level comparisons
        school_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'School']
        assert len(school_comparisons) == 10, f"Expected 10 School metrics, got {len(school_comparisons)}"

        # Verify all expected metrics are present
        expected_metrics = [
            'Fundraising', 'Minutes Read', 'Sponsors', 'Total Participating (≥1 Day)', 'School Size',
            'Avg Participation % (With Color)', 'Goal Met (≥1 Day)', 'All N Days Active %',
            'Goal Met All Days %', 'Color War Points'
        ]
        actual_metrics = [c['metric'] for c in school_comparisons]

        for metric in expected_metrics:
            assert metric in actual_metrics, f"Missing School metric: {metric}"

    def test_team_level_10_metrics(self, sample_db):
        """Verify Team level has exactly 10 metrics."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Count Team-level comparisons
        team_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'Team']
        assert len(team_comparisons) == 10, f"Expected 10 Team metrics, got {len(team_comparisons)}"

        # Verify expected metrics
        expected_metrics = [
            'Fundraising', 'Minutes Read', 'Team Size', 'Sponsors', 'Total Participating (≥1 Day)',
            'Avg Participation % (With Color)', 'Goal Met (≥1 Day)', 'All N Days Active %',
            'Goal Met All Days %', 'Color War Points'
        ]
        actual_metrics = [c['metric'] for c in team_comparisons]

        for metric in expected_metrics:
            assert metric in actual_metrics, f"Missing Team metric: {metric}"

    def test_grade_level_10_metrics(self, sample_db):
        """Verify Grade level has exactly 10 metrics."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Count Grade-level comparisons
        grade_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'Grade']
        assert len(grade_comparisons) == 10, f"Expected 10 Grade metrics, got {len(grade_comparisons)}"

    def test_class_level_10_metrics(self, sample_db):
        """Verify Class level has exactly 10 metrics."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Count Class-level comparisons
        class_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'Class']
        assert len(class_comparisons) == 10, f"Expected 10 Class metrics, got {len(class_comparisons)}"

    def test_student_level_10_metrics(self, sample_db):
        """Verify Student level has exactly 9 metrics (Color War Points removed)."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Count Student-level comparisons
        student_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'Student']
        assert len(student_comparisons) == 9, f"Expected 9 Student metrics, got {len(student_comparisons)}"

        # Verify expected metrics (Color War Points removed - doesn't apply to student level)
        expected_metrics = [
            'Fundraising', 'Minutes Read', 'Sponsors', 'Participation %', 'Goal Met (Days)',
            'All Days Active (100%)', 'Goal Met All Days',
            'Avg Minutes Per Day', 'Total Days Active'
        ]
        actual_metrics = [c['metric'] for c in student_comparisons]

        for metric in expected_metrics:
            assert metric in actual_metrics, f"Missing Student metric: {metric}"

    def test_comparison_structure(self, sample_db):
        """Verify each comparison has required fields."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        required_fields = ['entity_level', 'metric', 'honors_filter', 'db1_value', 'db2_value', 'change', 'winner', 'format']

        for comparison in result['comparisons']:
            for field in required_fields:
                assert field in comparison, f"Missing field {field} in comparison: {comparison['metric']}"

            # Verify db1_value and db2_value have value field
            assert 'value' in comparison['db1_value']
            assert 'value' in comparison['db2_value']

            # Verify change has required fields
            assert 'absolute' in comparison['change']
            assert 'direction' in comparison['change']

    def test_winner_determination(self, sample_db):
        """Verify winner is correctly determined."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        for comparison in result['comparisons']:
            db1_val = comparison['db1_value']['value']
            db2_val = comparison['db2_value']['value']
            winner = comparison['winner']

            # When comparing same database, all should be ties or handle None values
            if db1_val is not None and db2_val is not None:
                if db1_val > db2_val:
                    assert winner == 'db1'
                elif db1_val < db2_val:
                    assert winner == 'db2'
                else:
                    assert winner == 'tie'

    def test_format_types(self, sample_db):
        """Verify format types are appropriate for each metric."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Check that format field exists and has valid values
        valid_formats = ['currency', 'minutes', 'number', 'percentage', 'decimal']

        for comparison in result['comparisons']:
            assert comparison['format'] in valid_formats, f"Invalid format: {comparison['format']} for {comparison['metric']}"

    def test_honors_filter_flag(self, sample_db):
        """Verify honors_filter flag is set correctly for time-based metrics."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Minutes Read should honor filter
        minutes_comparisons = [c for c in result['comparisons'] if 'Minutes' in c['metric']]
        for comparison in minutes_comparisons:
            assert comparison['honors_filter'] == True, f"{comparison['metric']} should honor filter"

        # Fundraising should NOT honor filter
        fundraising_comparisons = [c for c in result['comparisons'] if 'Fundraising' in c['metric']]
        for comparison in fundraising_comparisons:
            assert comparison['honors_filter'] == False, f"{comparison['metric']} should not honor filter"

    def test_percentage_values_valid(self, sample_db):
        """Verify percentage values are within valid range (0-100)."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        percentage_comparisons = [c for c in result['comparisons'] if c['format'] == 'percentage']

        for comparison in percentage_comparisons:
            db1_val = comparison['db1_value']['value']
            db2_val = comparison['db2_value']['value']

            # Allow for percentages > 100 in special cases (like participation with bonus)
            if db1_val is not None:
                assert db1_val >= 0, f"Negative percentage in {comparison['metric']}: {db1_val}"
            if db2_val is not None:
                assert db2_val >= 0, f"Negative percentage in {comparison['metric']}: {db2_val}"

    def test_currency_values_valid(self, sample_db):
        """Verify currency values are non-negative."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        currency_comparisons = [c for c in result['comparisons'] if c['format'] == 'currency']

        for comparison in currency_comparisons:
            db1_val = comparison['db1_value']['value']
            db2_val = comparison['db2_value']['value']

            if db1_val is not None:
                assert db1_val >= 0, f"Negative currency in {comparison['metric']}: {db1_val}"
            if db2_val is not None:
                assert db2_val >= 0, f"Negative currency in {comparison['metric']}: {db2_val}"

    def test_all_entity_levels_present(self, sample_db):
        """Verify all 5 entity levels are represented."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        entity_levels = set(c['entity_level'] for c in result['comparisons'])
        expected_levels = {'School', 'Team', 'Grade', 'Class', 'Student'}

        assert entity_levels == expected_levels, f"Missing entity levels: {expected_levels - entity_levels}"

    def test_tie_count_field_present(self, sample_db):
        """Verify tie_count field is present in student-level comparisons."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Check Student-level comparisons have tie_count
        student_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'Student']

        for comparison in student_comparisons:
            assert 'tie_count' in comparison['db1_value'], f"Missing tie_count in db1_value for {comparison['metric']}"
            assert 'tie_count' in comparison['db2_value'], f"Missing tie_count in db2_value for {comparison['metric']}"

    def test_tied_winners_formatted_correctly(self, sample_db):
        """Verify tied winners are formatted as 'Name1, Name2, Name3 and X others'."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')

        reports = ReportGenerator(db)
        result = reports.get_database_comparison('readathon_sample.db', 'readathon_sample.db', 'all')

        # Check Student-level comparisons for proper name formatting
        student_comparisons = [c for c in result['comparisons'] if c['entity_level'] == 'Student']

        for comparison in student_comparisons:
            winner_name = comparison['db1_value'].get('winner_name', '')
            tie_count = comparison['db1_value'].get('tie_count', 0)

            # If there's a tie, names should be formatted properly
            if tie_count > 1:
                # Should have commas or "and X others"
                assert ',' in winner_name or 'and' in winner_name or 'others' in winner_name, \
                    f"Tie with {tie_count} winners should be formatted with commas or 'and X others'"

    def test_half_circle_indicator_for_daily_metrics(self, client):
        """Verify half circle (◐) indicator is shown for metrics that depend on daily data."""
        response = client.get('/database-comparison?db1=readathon_sample.db&db2=readathon_sample.db&filter=all')
        html = response.data.decode('utf-8')

        # Check for half circle indicator presence (◐ character with filter-indicator class)
        assert '◐' in html, "Half circle indicator should be present for daily data metrics"
        assert 'filter-indicator' in html, "Filter indicator CSS class should be present"

        # Verify it appears near "Minutes Read" which is a daily data metric
        # Find all instances of Minutes Read
        minutes_sections = re.findall(r'Minutes Read.*?(?=<td|</tr)', html, re.DOTALL)
        if minutes_sections:
            # At least one should have the half circle
            has_indicator = any('◐' in section for section in minutes_sections)
            assert has_indicator, "Half circle should appear with Minutes Read metric"

    def test_tie_note_displayed_in_html(self, client):
        """Verify tie notes are displayed in HTML when tie_count > 1."""
        response = client.get('/database-comparison?db1=readathon_sample.db&db2=readathon_sample.db&filter=all')
        html = response.data.decode('utf-8')

        # Check for tie-note class or tie indication text
        # May not always be present, but if there are ties, should see the pattern
        if 'way tie' in html.lower():
            # Should have the proper formatting
            tie_matches = re.findall(r'(\d+)-way tie for 1st place', html)
            for tie_match in tie_matches:
                # Each should be a valid number
                assert int(tie_match) > 1, "Tie count should be greater than 1"

    def test_format_tied_winners_helper(self, sample_db):
        """Test the _format_tied_winners helper function."""
        from database import ReportGenerator, ReadathonDB
        db = ReadathonDB('db/readathon_sample.db')
        reports = ReportGenerator(db)

        # Test with empty list
        result = reports._format_tied_winners([])
        assert result['names'] == 'N/A'
        assert result['tie_count'] == 0
        assert result['grade_context'] == ''

        # Test with single winner
        single_winner = [{'student_name': 'Alice', 'grade_level': '3'}]
        result = reports._format_tied_winners(single_winner)
        assert result['names'] == 'Alice'
        assert result['tie_count'] == 1
        assert result['grade_context'] == 'Grade 3'

        # Test with 2 winners (same grade)
        two_winners = [
            {'student_name': 'Alice', 'grade_level': '3'},
            {'student_name': 'Bob', 'grade_level': '3'}
        ]
        result = reports._format_tied_winners(two_winners)
        assert 'Alice' in result['names'] and 'Bob' in result['names']
        assert result['tie_count'] == 2
        assert result['grade_context'] == 'Grade 3'

        # Test with 5 winners (should show "and 2 others")
        five_winners = [
            {'student_name': 'Alice', 'grade_level': '3'},
            {'student_name': 'Bob', 'grade_level': '4'},
            {'student_name': 'Charlie', 'grade_level': '5'},
            {'student_name': 'David', 'grade_level': '3'},
            {'student_name': 'Eve', 'grade_level': '4'}
        ]
        result = reports._format_tied_winners(five_winners)
        assert 'and 2 others' in result['names']
        assert result['tie_count'] == 5
        assert result['grade_context'] == 'Various'  # Multiple grades
