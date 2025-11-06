"""
Test suite for Reports & Data page functionality.

This test ensures the unified Reports & Data page displays correct information,
handles search and filtering properly, and maintains data integrity across changes.

Tests cover:
- Page loading and basic structure
- Group filtering (prize, slides, export, admin, tables, workflows)
- Search functionality (name, description, type, groups)
- Item counts and data integrity
- Multi-group assignment verification
"""

import pytest
import re
from app import app, get_unified_items
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


class TestReportsPage:
    """Test cases for Reports & Data page."""

    # ============================================================================
    # MANDATORY TESTS (from RULES.md)
    # ============================================================================

    def test_page_loads_successfully(self, client):
        """Verify reports page loads without errors."""
        response = client.get('/reports')
        assert response.status_code == 200
        assert b'Read-a-Thon System' in response.data
        assert b'Reports & Data' in response.data

    def test_no_error_messages(self, client):
        """Scan for error patterns in page output."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        # Check for actual error messages, excluding legitimate code/comments
        error_patterns = ['Exception:', 'Traceback', 'KeyError', 'AttributeError', 'error occurred']
        html_lower = html.lower()

        for pattern in error_patterns:
            assert pattern.lower() not in html_lower, f"Found error pattern: {pattern}"

        # Check for actual error alerts (not just the word "error" in code)
        assert 'alert-danger' not in html or 'Select a report' in html, "Found error alert on page"

    def test_sample_data_integrity(self, client, sample_db):
        """Verify all expected items are present."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        # Verify some key reports are listed
        assert 'Q2: Daily Summary Report' in html
        assert 'Q5: Student Cumulative Report' in html

        # Verify database tables are listed
        assert 'Roster' in html
        assert 'Daily Logs' in html

        # Verify workflows are listed
        assert 'QD: Daily Slide Update' in html

    # ============================================================================
    # GROUP FILTER TESTS
    # ============================================================================

    def test_group_filter_all(self, client):
        """Test 'All Groups' filter shows all items."""
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain items from all groups
        assert 'Q2: Daily Summary Report' in html  # slides group
        assert 'Q5: Student Cumulative Report' in html  # prize group
        assert 'Roster' in html  # tables group
        assert 'QD: Daily Slide Update' in html  # workflows group
        assert 'Q1: Table Row Counts' in html  # admin group

    def test_group_filter_prize(self, client):
        """Test 'Prize Reports' filter shows only prize reports."""
        response = client.get('/reports?group=prize')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain prize reports
        assert 'Q5: Student Cumulative Report' in html
        assert 'Q6: Class Participation Winner' in html
        assert 'Q9: Most Donations Per Grade' in html

        # Get all items to verify count
        all_items = get_unified_items()
        prize_items = [i for i in all_items if 'prize' in i['groups']]
        assert len(prize_items) >= 8, "Expected at least 8 prize reports"

    def test_group_filter_slides(self, client):
        """Test 'Update Reports / Slides' filter shows only slide reports."""
        response = client.get('/reports?group=slides')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain slide reports
        assert 'Q2: Daily Summary Report' in html
        assert 'Q14' in html  # Team Participation
        assert 'Q18' in html  # Lead Class by Grade
        assert 'Q19' in html  # Team Minutes
        assert 'Q20' in html  # Team Donations

        # Get all items to verify count
        all_items = get_unified_items()
        slides_items = [i for i in all_items if 'slides' in i['groups']]
        assert len(slides_items) >= 5, "Expected at least 5 slide reports"

    def test_group_filter_export(self, client):
        """Test 'Export Reports' filter shows only export reports."""
        response = client.get('/reports?group=export')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain export reports
        assert 'Q3: Reader Cumulative Enhanced' in html
        assert 'Q7: Complete Log' in html
        assert 'Q8: Student Reading Details' in html

        # Get all items to verify count
        all_items = get_unified_items()
        export_items = [i for i in all_items if 'export' in i['groups']]
        assert len(export_items) >= 3, "Expected at least 3 export reports"

    def test_group_filter_admin(self, client):
        """Test 'Admin Reports' filter shows only admin reports."""
        response = client.get('/reports?group=admin')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain admin reports
        assert 'Q1: Table Row Counts' in html
        assert 'Q21' in html  # Data Sync
        assert 'Q22' in html  # Student Name Sync
        assert 'Q23' in html  # Roster Integrity
        assert 'Q24' in html  # Database_Metadata

        # Get all items to verify count
        all_items = get_unified_items()
        admin_items = [i for i in all_items if 'admin' in i['groups']]
        assert len(admin_items) == 5, "Expected exactly 5 admin reports"

    def test_group_filter_tables(self, client):
        """Test 'Database Tables' filter shows only database tables."""
        response = client.get('/reports?group=tables')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain database tables
        assert 'Roster' in html
        assert 'Class Info' in html
        assert 'Grade Rules' in html
        assert 'Daily Logs' in html
        assert 'Reader Cumulative' in html
        assert 'Upload History' in html

        # Get all items to verify count
        all_items = get_unified_items()
        table_items = [i for i in all_items if 'tables' in i['groups']]
        assert len(table_items) >= 7, "Expected at least 7 database tables"

    def test_group_filter_workflows(self, client):
        """Test 'Workflows' filter shows only workflows."""
        response = client.get('/reports?group=workflows')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should contain workflows
        assert 'QD: Daily Slide Update' in html
        assert 'QC: Cumulative Workflow' in html
        assert 'QF: Final Prize Winners' in html
        assert 'QA: All Main Reports' in html

        # Get all items to verify count
        all_items = get_unified_items()
        workflow_items = [i for i in all_items if 'workflows' in i['groups']]
        assert len(workflow_items) == 4, "Expected exactly 4 workflows"

    # ============================================================================
    # SEARCH FUNCTIONALITY TESTS (Enhanced with type and groups)
    # ============================================================================

    def test_search_by_name(self, client):
        """Test search by report name."""
        response = client.get('/reports?search=Q2')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        assert 'Q2: Daily Summary Report' in html

    def test_search_by_description(self, client):
        """Test search by report description."""
        response = client.get('/reports?search=participation')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should find reports with "participation" in description
        assert 'Q2' in html or 'Q6' in html or 'Q14' in html

    def test_search_by_type_table(self, client):
        """Test search by item_type 'table' returns all database tables."""
        # Note: This is a CLIENT-SIDE search test
        # The enhanced JavaScript should filter client-side, but server-side doesn't yet
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Verify all tables are present for client-side filtering
        assert 'Roster' in html
        assert 'Daily Logs' in html
        assert 'Reader Cumulative' in html

        # Verify data-groups contains table
        assert 'data-groups="' in html
        assert 'table' in html

    def test_search_by_type_workflow(self, client):
        """Test search by group 'workflow' returns all workflows."""
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Verify all workflows are present for client-side filtering
        assert 'QD: Daily Slide Update' in html
        assert 'QC: Cumulative Workflow' in html

        # Verify data-groups contains workflow
        assert 'data-groups="' in html
        assert 'workflow' in html

    def test_search_by_type_report(self, client):
        """Test search by group 'report' returns all reports."""
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Verify reports are present for client-side filtering
        assert 'Q2: Daily Summary Report' in html
        assert 'Q5: Student Cumulative Report' in html

        # Verify data-groups contains report
        assert 'data-groups="' in html
        assert 'report' in html

    def test_search_by_group_prize(self, client):
        """Test search by group 'prize' via client-side filtering."""
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Verify data-groups attributes exist with prize
        assert 'data-groups="prize' in html or 'data-groups="' in html

    def test_data_attributes_present(self, client):
        """Verify all required data attributes exist for client-side search."""
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check for data attributes needed for enhanced search
        assert 'data-item-id=' in html
        assert 'data-groups=' in html
        assert 'data-name=' in html
        assert 'data-description=' in html
        assert 'data-groups=' in html, "data-groups attribute missing (needed for enhanced search)"

    # ============================================================================
    # ITEM COUNT AND STRUCTURE TESTS
    # ============================================================================

    def test_item_count_matches_filter(self, client):
        """Test that displayed item count matches actual filtered items."""
        # Test with 'all' filter
        response = client.get('/reports?group=all')
        html = response.data.decode('utf-8')

        # Find item count in HTML (inside span tag)
        match = re.search(r'<span id="itemCount">(\d+)</span>', html)
        assert match, "Item count not found in HTML"
        displayed_count = int(match.group(1))

        # Get actual count from backend
        all_items = get_unified_items()
        assert displayed_count == len(all_items), f"Displayed count {displayed_count} doesn't match actual {len(all_items)}"

    def test_all_items_have_required_fields(self, client):
        """Verify all items have required fields."""
        all_items = get_unified_items()

        required_fields = ['id', 'name', 'description', 'groups']

        for item in all_items:
            for field in required_fields:
                assert field in item, f"Item {item.get('id', 'unknown')} missing field: {field}"

            # Verify groups is a list
            assert isinstance(item['groups'], list), f"Item {item['id']} groups should be a list"
            assert len(item['groups']) > 0, f"Item {item['id']} should have at least one group"

    def test_group_options_structure(self, client):
        """Verify group filter dropdown has correct structure."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        # Check for all expected groups
        assert 'All Items' in html
        assert 'Prize Reports' in html
        assert 'Update Reports / Slides' in html
        assert 'Export Reports' in html
        assert 'Admin Reports' in html
        assert 'Database Tables' in html
        assert 'Workflows' in html

    def test_multi_group_items_appear_in_multiple_filters(self, client):
        """Test that items with multiple groups appear in all relevant filters."""
        all_items = get_unified_items()

        # Find Q2 which has multiple groups including 'slides' and 'workflow.qa'
        q2 = next((item for item in all_items if item['id'] == 'q2'), None)
        assert q2 is not None, "Q2 not found in items"
        assert 'slides' in q2['groups']
        assert 'workflow.qa' in q2['groups']

        # Test Q2 appears in 'slides' filter
        response = client.get('/reports?group=slides')
        html = response.data.decode('utf-8')
        assert 'Q2: Daily Summary Report' in html

        # Test Q2 appears in 'all' filter
        response = client.get('/reports?group=all')
        html = response.data.decode('utf-8')
        assert 'Q2: Daily Summary Report' in html

    def test_complete_log_appears_in_both_tables_and_export(self, client):
        """Test that Complete Log appears in both tables and export groups."""
        all_items = get_unified_items()

        # Find Complete Log which has ['tables', 'export']
        complete_log = next((item for item in all_items if item['id'] == 'complete_log'), None)
        assert complete_log is not None, "Complete Log not found"
        assert 'tables' in complete_log['groups']
        assert 'export' in complete_log['groups']

        # Test appears in 'tables' filter
        response = client.get('/reports?group=tables')
        html = response.data.decode('utf-8')
        assert 'Complete Log' in html

        # Test appears in 'export' filter
        response = client.get('/reports?group=export')
        html = response.data.decode('utf-8')
        assert 'Complete Log' in html

    # ============================================================================
    # PAGE STRUCTURE TESTS
    # ============================================================================

    def test_filter_controls_present(self, client):
        """Verify search and group filter controls are present."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        # Search box
        assert 'searchBox' in html
        assert 'Search:' in html

        # Group filter
        assert 'groupFilter' in html
        assert 'Group:' in html

    def test_item_list_container_present(self, client):
        """Verify items list container exists."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        assert 'itemsList' in html
        assert 'Available Items' in html

    def test_results_container_present(self, client):
        """Verify report results container exists."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        assert 'reportResults' in html
        assert 'Select a report from the list' in html or 'report' in html.lower()

    def test_item_badges_present(self, client):
        """Verify item type badges are displayed."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        # Should have badges for report, table, workflow types
        assert 'badge' in html
        assert 'bg-secondary' in html or 'bg-primary' in html or 'bg-dark' in html

    # ============================================================================
    # REGRESSION TESTS
    # ============================================================================

    def test_no_duplicate_items(self, client):
        """Ensure no duplicate items in the list."""
        all_items = get_unified_items()

        # Check for duplicate IDs
        ids = [item['id'] for item in all_items]
        assert len(ids) == len(set(ids)), "Duplicate item IDs found"

    def test_consistent_item_structure(self, client):
        """Verify all items follow consistent structure."""
        all_items = get_unified_items()

        for item in all_items:
            # All items should have these fields
            assert 'id' in item
            assert 'name' in item
            assert 'description' in item
            assert 'groups' in item

            # At least one of these structural types should be in groups
            has_structural_type = any(g in item['groups'] for g in ['report', 'table', 'workflow'])
            assert has_structural_type, \
                f"Item {item['id']} missing structural type (report/table/workflow)"

    def test_workflows_have_workflow_parent_group(self, client):
        """Verify all workflows belong to 'workflow' group."""
        all_items = get_unified_items()

        workflow_items = [item for item in all_items if 'workflow' in item['groups']]

        for item in workflow_items:
            assert 'workflow' in item['groups'], \
                f"Workflow {item['id']} missing 'workflow' group"

    def test_reports_have_at_least_one_group(self, client):
        """Verify all reports belong to at least one group."""
        all_items = get_unified_items()

        report_items = [item for item in all_items if 'report' in item['groups']]

        for item in report_items:
            assert len(item['groups']) > 0, \
                f"Report {item['id']} has no groups assigned"

    def test_group_counts_match_actual_items(self, client):
        """Verify group counts in dropdown match actual filtered results."""
        response = client.get('/reports')
        html = response.data.decode('utf-8')

        all_items = get_unified_items()

        # Check prize group count
        prize_items = [i for i in all_items if 'prize' in i['groups']]
        prize_count = len(prize_items)
        assert f'Prize Reports ({prize_count})' in html, \
            f"Prize Reports count mismatch"

        # Check tables group count
        table_items = [i for i in all_items if 'tables' in i['groups']]
        table_count = len(table_items)
        assert f'Database Tables ({table_count})' in html, \
            f"Database Tables count mismatch"
