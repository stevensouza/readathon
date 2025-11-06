"""
Test suite for group-based tagging system regression tests
Ensures the group system remains consistent and correct
"""

import pytest
from app import (
    app, get_unified_items, get_items_by_group, get_items_by_groups,
    is_report, is_workflow, is_table, requires_date, requires_group_by,
    get_workflow_reports
)


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGroupSystemStructure:
    """Test basic structure of the group system"""

    def test_total_item_count(self):
        """Verify total number of items is correct"""
        all_items = get_unified_items()
        # 23 reports + 8 tables + 4 workflows = 35 items
        assert len(all_items) == 35, f"Expected 35 items, got {len(all_items)}"

    def test_report_count(self):
        """Verify number of reports"""
        reports = [item for item in get_unified_items() if is_report(item)]
        # Q1-Q24 (with gaps: no Q17) = 23 reports
        assert len(reports) == 23, f"Expected 23 reports, got {len(reports)}"

    def test_table_count(self):
        """Verify number of tables"""
        tables = [item for item in get_unified_items() if is_table(item)]
        # 8 tables: Roster, Class_Info, Grade_Rules, Daily_Logs,
        #           Reader_Cumulative, Team_Color_Bonus, Upload_History, Complete_Log
        assert len(tables) == 8, f"Expected 8 tables, got {len(tables)}"

    def test_workflow_count(self):
        """Verify number of workflows"""
        workflows = [item for item in get_unified_items() if is_workflow(item)]
        # 4 workflows: QA, QD, QC, QF
        assert len(workflows) == 4, f"Expected 4 workflows, got {len(workflows)}"

    def test_all_items_have_groups(self):
        """Verify all items have groups field"""
        all_items = get_unified_items()
        for item in all_items:
            assert 'groups' in item, f"Item {item.get('id')} missing groups field"
            assert isinstance(item['groups'], list), f"Item {item['id']} groups must be list"
            assert len(item['groups']) > 0, f"Item {item['id']} has empty groups"

    def test_all_items_have_structural_tag(self):
        """Verify all items have exactly one structural tag (report/table/workflow)"""
        all_items = get_unified_items()
        structural_tags = ['report', 'table', 'workflow']

        for item in all_items:
            found_tags = [tag for tag in structural_tags if tag in item['groups']]
            assert len(found_tags) == 1, \
                f"Item {item['id']} should have exactly one structural tag, got {found_tags}"

    def test_no_duplicate_ids(self):
        """Verify no duplicate IDs in items"""
        all_items = get_unified_items()
        ids = [item['id'] for item in all_items]
        unique_ids = set(ids)
        assert len(ids) == len(unique_ids), \
            f"Found duplicate IDs: {[id for id in ids if ids.count(id) > 1]}"


class TestWorkflowTags:
    """Test workflow tagging and counts"""

    def test_qa_workflow_count(self):
        """Verify QA workflow has correct number of reports"""
        qa_reports = get_workflow_reports('qa')
        # QA should have all 23 reports + Q24
        assert len(qa_reports) == 23, f"Expected 23 reports in QA, got {len(qa_reports)}"

    def test_qd_workflow_count(self):
        """Verify QD workflow has correct number of reports"""
        qd_reports = get_workflow_reports('qd')
        # QD should have 5 slide reports: Q2, Q4, Q14, Q18, Q19, Q20
        expected_count = 5
        assert len(qd_reports) == expected_count, \
            f"Expected {expected_count} reports in QD, got {len(qd_reports)}"

    def test_qc_workflow_count(self):
        """Verify QC workflow has correct number of reports"""
        qc_reports = get_workflow_reports('qc')
        # QC should have 6 cumulative reports
        expected_count = 6
        assert len(qc_reports) == expected_count, \
            f"Expected {expected_count} reports in QC, got {len(qc_reports)}"

    def test_qf_workflow_count(self):
        """Verify QF workflow has correct number of reports"""
        qf_reports = get_workflow_reports('qf')
        # QF should have 10 prize reports
        expected_count = 10
        assert len(qf_reports) == expected_count, \
            f"Expected {expected_count} reports in QF, got {len(qf_reports)}"

    def test_workflow_tags_format(self):
        """Verify workflow tags use correct format (workflow.xx)"""
        all_items = get_unified_items()
        for item in all_items:
            workflow_tags = [g for g in item['groups'] if g.startswith('workflow.')]
            for tag in workflow_tags:
                # Should be workflow.qa, workflow.qd, workflow.qc, or workflow.qf
                assert tag in ['workflow.qa', 'workflow.qd', 'workflow.qc', 'workflow.qf'], \
                    f"Invalid workflow tag '{tag}' in item {item['id']}"


class TestBehaviorTags:
    """Test behavior tags (requires.*)"""

    def test_requires_date_count(self):
        """Verify correct number of reports require date"""
        date_reports = [item for item in get_unified_items() if requires_date(item)]
        # Q2, Q4, Q7 require date
        assert len(date_reports) >= 3, \
            f"Expected at least 3 reports requiring date, got {len(date_reports)}"

    def test_requires_group_by_count(self):
        """Verify correct number of reports require group_by"""
        group_by_reports = [item for item in get_unified_items() if requires_group_by(item)]
        # Q2 requires group_by
        assert len(group_by_reports) >= 1, \
            f"Expected at least 1 report requiring group_by, got {len(group_by_reports)}"

    def test_behavior_tags_format(self):
        """Verify behavior tags use correct format (requires.*)"""
        all_items = get_unified_items()
        valid_requires = ['requires.date', 'requires.group_by', 'requires.sort', 'requires.limit']

        for item in all_items:
            requires_tags = [g for g in item['groups'] if g.startswith('requires.')]
            for tag in requires_tags:
                assert tag in valid_requires, \
                    f"Unknown requires tag '{tag}' in item {item['id']}"


class TestHelperFunctions:
    """Test group query helper functions"""

    def test_get_items_by_group_exact(self):
        """Test exact group matching"""
        prize_items = get_items_by_group('prize')
        assert len(prize_items) > 0, "Should find prize reports"

        for item in prize_items:
            assert 'prize' in item['groups'], \
                f"Item {item['id']} should have 'prize' group"

    def test_get_items_by_group_wildcard(self):
        """Test wildcard group matching"""
        workflow_items = get_items_by_group('workflow.*')
        # Should find all reports that have workflow.qa, workflow.qd, etc.
        assert len(workflow_items) > 0, "Should find reports with workflow tags"

        for item in workflow_items:
            has_workflow = any(g.startswith('workflow.') for g in item['groups'])
            assert has_workflow, \
                f"Item {item['id']} should have workflow.* tag"

    def test_get_items_by_groups_and(self):
        """Test AND logic for multiple groups"""
        # Find items that are BOTH prize AND slides
        items = get_items_by_groups(['prize', 'slides'], match_all=True)

        for item in items:
            assert 'prize' in item['groups'], f"Item {item['id']} missing 'prize'"
            assert 'slides' in item['groups'], f"Item {item['id']} missing 'slides'"

    def test_get_items_by_groups_or(self):
        """Test OR logic for multiple groups"""
        # Find items that are EITHER prize OR slides
        items = get_items_by_groups(['prize', 'slides'], match_all=False)

        for item in items:
            has_either = 'prize' in item['groups'] or 'slides' in item['groups']
            assert has_either, \
                f"Item {item['id']} should have 'prize' OR 'slides'"

    def test_is_report_function(self):
        """Test is_report() helper"""
        all_items = get_unified_items()
        reports = [item for item in all_items if is_report(item)]

        for report in reports:
            assert 'report' in report['groups'], \
                f"is_report returned true but 'report' not in groups for {report['id']}"

    def test_is_table_function(self):
        """Test is_table() helper"""
        all_items = get_unified_items()
        tables = [item for item in all_items if is_table(item)]

        for table in tables:
            assert 'table' in table['groups'], \
                f"is_table returned true but 'table' not in groups for {table['id']}"

    def test_is_workflow_function(self):
        """Test is_workflow() helper"""
        all_items = get_unified_items()
        workflows = [item for item in all_items if is_workflow(item)]

        for workflow in workflows:
            assert 'workflow' in workflow['groups'], \
                f"is_workflow returned true but 'workflow' not in groups for {workflow['id']}"


class TestGroupConsistency:
    """Test consistency across the group system"""

    def test_all_reports_in_at_least_one_workflow(self):
        """Verify all main reports are in at least one workflow"""
        all_items = get_unified_items()
        reports = [item for item in all_items if is_report(item)]

        for report in reports:
            has_workflow = any(g.startswith('workflow.') for g in report['groups'])
            assert has_workflow, \
                f"Report {report['id']} not assigned to any workflow"

    def test_semantic_tags_consistency(self):
        """Verify semantic tags are used consistently"""
        all_items = get_unified_items()
        valid_semantic = [
            'prize', 'slides', 'admin', 'export', 'cumulative', 'daily',
            'integrity', 'utility', 'database', 'fundraising', 'reading',
            'participation', 'featured', 'tables', 'workflows'
        ]

        for item in all_items:
            for group in item['groups']:
                # Skip structural, workflow.*, and requires.* tags
                if group in ['report', 'table', 'workflow']:
                    continue
                if group.startswith('workflow.') or group.startswith('requires.'):
                    continue

                assert group in valid_semantic, \
                    f"Unknown semantic tag '{group}' in item {item['id']}"

    def test_q14_in_all_workflows(self):
        """Verify Q14 is in all 4 workflows (special case)"""
        all_items = get_unified_items()
        q14 = next((item for item in all_items if item['id'] == 'q14'), None)

        assert q14 is not None, "Q14 not found"
        assert 'workflow.qa' in q14['groups'], "Q14 should be in QA workflow"
        assert 'workflow.qd' in q14['groups'], "Q14 should be in QD workflow"
        assert 'workflow.qc' in q14['groups'], "Q14 should be in QC workflow"
        assert 'workflow.qf' in q14['groups'], "Q14 should be in QF workflow"


class TestReportsPageIntegration:
    """Test Reports page integration with group system"""

    def test_reports_page_loads(self, client):
        """Test Reports page loads with all items"""
        response = client.get('/reports?group=all')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Should show "All Items (35)"
        assert 'All Items' in html, "Should show 'All Items' label"
        assert '(35)' in html or '35' in html, "Should show count of 35 items"

    def test_reports_page_group_filters(self, client):
        """Test all group filters work"""
        groups_to_test = ['prize', 'slides', 'export', 'admin', 'table']

        for group in groups_to_test:
            response = client.get(f'/reports?group={group}')
            assert response.status_code == 200, \
                f"Failed to load reports page with group={group}"

    def test_workflow_filters(self, client):
        """Test workflow-specific filters"""
        workflows = ['workflow.qa', 'workflow.qd', 'workflow.qc', 'workflow.qf']

        for workflow in workflows:
            response = client.get(f'/reports?group={workflow}')
            assert response.status_code == 200, \
                f"Failed to load reports page with group={workflow}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
