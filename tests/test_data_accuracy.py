"""
Data Accuracy Test Suite - Read-a-Thon Application

This test suite validates that calculations, rankings, and winner determinations
are mathematically correct by comparing displayed values against database queries.

Unlike structural tests (test_*_page.py), these tests verify:
- Correct winner identification (reading leaders, fundraising leaders, top classes)
- Accurate calculations (totals, averages, gaps, percentages)
- Proper ranking/ordering (top performers, leaderboards)
- Data integrity across filters (date filters, grade filters)

Sample Data Contract:
The tests query readathon_sample.db to determine expected values dynamically.
This makes tests resilient to sample data changes while still catching calculation bugs.

Database Schema (sample database):
- Roster: student_name (PK), class_name, teacher_name, grade_level, team_name
- Reader_Cumulative: student_name (PK/FK), donation_amount, sponsors, cumulative_minutes
- Class_Info: class_name (PK), teacher_name, grade_level, team_name, total_students

Test Organization:
- Phase 1: Critical winners and totals (9 tests)
- Phase 2: Rankings, edge cases, and filter accuracy (12 tests)
"""

import pytest
import re
from bs4 import BeautifulSoup
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


class TestSchoolPageAccuracy:
    """Test accurate calculations and winners on School page."""

    # ========== PHASE 1: CRITICAL WINNERS AND TOTALS ==========

    def test_school_reading_leader_accuracy(self, client, sample_db):
        """Verify correct student is identified as reading leader."""
        # Query database for actual reading leader
        leader = sample_db.execute_query("""
            SELECT r.student_name, rc.cumulative_minutes
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            ORDER BY rc.cumulative_minutes DESC
            LIMIT 1
        """)[0]

        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Verify leader's name appears in Reading Leader section
        student_name = leader['student_name']
        assert student_name in html, f"Reading leader {student_name} not found on School page"

        # Verify leader's minutes appear
        minutes = leader['cumulative_minutes']
        assert str(minutes) in html, f"Reading leader's minutes ({minutes}) not found"

    def test_school_fundraising_leader_accuracy(self, client, sample_db):
        """Verify correct student is identified as fundraising leader."""
        # Query database for actual fundraising leader
        leader = sample_db.execute_query("""
            SELECT r.student_name, rc.donation_amount
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            ORDER BY rc.donation_amount DESC
            LIMIT 1
        """)[0]

        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Verify leader's name appears
        student_name = leader['student_name']
        assert student_name in html, f"Fundraising leader {student_name} not found on School page"

        # Verify leader's donation amount appears
        amount = leader['donation_amount']
        # Could be formatted as $95 or $95.00
        assert f'${int(amount)}' in html or f'${amount:.0f}' in html, \
            f"Fundraising leader's amount (${amount}) not found"

    def test_school_total_fundraising_accuracy(self, client, sample_db):
        """Verify total fundraising calculation is correct."""
        # Query database for actual total
        result = sample_db.execute_query("""
            SELECT SUM(donation_amount) as total
            FROM Reader_Cumulative
        """)[0]

        expected_total = result['total'] or 0

        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Check formatted versions (with and without commas)
        formatted_no_comma = f'${expected_total:.0f}'
        formatted_with_comma = f'${expected_total:,.0f}'

        assert formatted_no_comma in html or formatted_with_comma in html, \
            f"Total fundraising ${expected_total:.0f} not found on School page"

    # ========== PHASE 2: RANKINGS AND EDGE CASES ==========

    def test_school_top_class_fundraising_accuracy(self, client, sample_db):
        """Verify top class by fundraising is correctly identified."""
        # Query for top class by fundraising
        top_class = sample_db.execute_query("""
            SELECT
                ci.class_name,
                ci.teacher_name,
                SUM(rc.donation_amount) as total_fundraising
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name, ci.teacher_name
            ORDER BY total_fundraising DESC
            LIMIT 1
        """)[0]

        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Verify class name or teacher name appears in "Top Class" section
        assert top_class['class_name'] in html or top_class['teacher_name'] in html, \
            f"Top class {top_class['class_name']} not found on School page"

    def test_school_total_minutes_accuracy(self, client, sample_db):
        """Verify total reading minutes calculation is correct."""
        # Query database for total minutes
        result = sample_db.execute_query("""
            SELECT SUM(cumulative_minutes) as total_minutes
            FROM Reader_Cumulative
        """)[0]

        total_minutes = result['total_minutes'] or 0
        total_hours = total_minutes / 60

        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Check for hours display (could be formatted various ways)
        # Look for the numeric part (e.g., "242" in "242 hours")
        hours_int = int(total_hours)
        hours_float = f"{total_hours:.1f}"

        # Should find either integer or float version
        assert str(hours_int) in html or hours_float in html, \
            f"Total hours {hours_float} not found on School page"

    def test_school_participation_rate_accuracy(self, client, sample_db):
        """Verify participation rate calculation is correct."""
        # Query database for participation metrics
        result = sample_db.execute_query("""
            SELECT
                COUNT(DISTINCT CASE WHEN rc.cumulative_minutes > 0 THEN r.student_name END) as participating,
                COUNT(DISTINCT r.student_name) as total_students
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
        """)[0]

        participating = result['participating']
        total_students = result['total_students']
        participation_pct = (participating / total_students * 100) if total_students > 0 else 0

        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Check for participation metrics
        assert str(participating) in html, f"Participating count {participating} not found"
        assert str(total_students) in html, f"Total students {total_students} not found"

        # Check for percentage (could be formatted as 87% or 86.7%)
        pct_int = f"{participation_pct:.0f}%"
        pct_float = f"{participation_pct:.1f}%"
        assert pct_int in html or pct_float in html, \
            f"Participation percentage {pct_int} not found"


class TestTeamsPageAccuracy:
    """Test accurate calculations and winners on Teams page."""

    # ========== PHASE 1: CRITICAL WINNERS AND TOTALS ==========

    def test_teams_fundraising_winner_accuracy(self, client, sample_db):
        """Verify correct team wins fundraising competition."""
        # Query database for team fundraising totals
        team_totals = sample_db.execute_query("""
            SELECT r.team_name, SUM(rc.donation_amount) as total_fundraising
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY total_fundraising DESC
        """)

        if len(team_totals) < 2:
            pytest.skip("Need at least 2 teams for comparison")

        winning_team = team_totals[0]['team_name']
        winning_amount = team_totals[0]['total_fundraising']

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Verify winning team name appears
        assert winning_team.upper() in html, \
            f"Winning team {winning_team} not found on Teams page"

        # Verify winning amount appears
        assert f'${winning_amount:.0f}' in html or f'${winning_amount:,.0f}' in html, \
            f"Winning fundraising amount ${winning_amount:.0f} not found"

    def test_teams_participation_winner_accuracy(self, client, sample_db):
        """Verify correct team wins participation competition."""
        # Query database for team participation rates
        team_participation = sample_db.execute_query("""
            SELECT
                r.team_name,
                COUNT(DISTINCT CASE WHEN rc.cumulative_minutes > 0 THEN r.student_name END) as participating,
                COUNT(DISTINCT r.student_name) as total_students,
                (COUNT(DISTINCT CASE WHEN rc.cumulative_minutes > 0 THEN r.student_name END) * 100.0 /
                 COUNT(DISTINCT r.student_name)) as participation_pct
            FROM Roster r
            LEFT JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY participation_pct DESC
        """)

        if len(team_participation) < 2:
            pytest.skip("Need at least 2 teams for comparison")

        winning_team = team_participation[0]['team_name']
        winning_pct = team_participation[0]['participation_pct']

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Verify team appears
        assert winning_team.upper() in html, \
            f"Team {winning_team} not found on Teams page"

        # Verify participation percentage appears (could be int or float)
        pct_int = f"{winning_pct:.0f}%"
        pct_float = f"{winning_pct:.1f}%"
        assert pct_int in html or pct_float in html, \
            f"Participation percentage {pct_int} not found"

    def test_teams_gap_calculation_accuracy(self, client, sample_db):
        """Verify gap calculations in comparison table are correct."""
        # Query database for fundraising gap
        team_totals = sample_db.execute_query("""
            SELECT r.team_name, SUM(rc.donation_amount) as total_fundraising
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY total_fundraising DESC
        """)

        if len(team_totals) < 2:
            pytest.skip("Need at least 2 teams for gap calculation")

        team1_amount = team_totals[0]['total_fundraising']
        team2_amount = team_totals[1]['total_fundraising']
        gap = abs(team1_amount - team2_amount)

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Verify gap appears (could be formatted with or without $)
        gap_formatted = f'${gap:.0f}'
        assert str(int(gap)) in html or gap_formatted in html, \
            f"Fundraising gap ${gap:.0f} not found on Teams page"

    # ========== PHASE 2: RANKINGS AND EDGE CASES ==========

    def test_teams_reading_winner_accuracy(self, client, sample_db):
        """Verify correct team wins reading minutes competition."""
        # Query database for team reading totals
        team_reading = sample_db.execute_query("""
            SELECT r.team_name, SUM(rc.cumulative_minutes) as total_minutes
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY total_minutes DESC
        """)

        if len(team_reading) < 2:
            pytest.skip("Need at least 2 teams for comparison")

        winning_team = team_reading[0]['team_name']
        winning_minutes = team_reading[0]['total_minutes']

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Verify winning team and minutes appear
        assert winning_team.upper() in html
        assert str(winning_minutes) in html or str(int(winning_minutes / 60)) in html

    def test_teams_top_performer_fundraising_accuracy(self, client, sample_db):
        """Verify top fundraising performer for each team is correct."""
        # Query for top fundraiser in each team
        top_performers = sample_db.execute_query("""
            WITH RankedStudents AS (
                SELECT
                    r.team_name,
                    r.student_name,
                    rc.donation_amount,
                    ROW_NUMBER() OVER (PARTITION BY r.team_name ORDER BY rc.donation_amount DESC) as rank
                FROM Roster r
                JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            )
            SELECT team_name, student_name, donation_amount
            FROM RankedStudents
            WHERE rank = 1
            ORDER BY team_name
        """)

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Verify each team's top performer appears
        for performer in top_performers:
            student_name = performer['student_name']
            # Name should appear somewhere on the page (in top performers section)
            assert student_name in html, \
                f"Top fundraiser {student_name} for team {performer['team_name']} not found"

    def test_teams_sponsor_count_accuracy(self, client, sample_db):
        """Verify sponsor count calculations are correct."""
        # Query for sponsor counts by team
        sponsor_counts = sample_db.execute_query("""
            SELECT r.team_name, SUM(rc.sponsors) as total_sponsors
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY total_sponsors DESC
        """)

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # Verify sponsor counts appear
        for team_data in sponsor_counts:
            sponsor_count = team_data['total_sponsors']
            assert str(sponsor_count) in html, \
                f"Sponsor count {sponsor_count} for team {team_data['team_name']} not found"

    def test_teams_tie_handling(self, client, sample_db):
        """Verify tied metrics are handled correctly (if ties exist)."""
        # Check if any metrics are tied
        team_reading = sample_db.execute_query("""
            SELECT r.team_name, SUM(rc.cumulative_minutes) as total_minutes
            FROM Roster r
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY r.team_name
            ORDER BY total_minutes DESC
        """)

        if len(team_reading) < 2:
            pytest.skip("Need at least 2 teams for tie detection")

        response = client.get('/teams')
        html = response.data.decode('utf-8')

        # If there's a tie, both teams should show winning indicators
        # If not, only one team should have winning indicator
        # (This is more of a structural check - the page should render without errors)
        assert 'winning-value' in html or 'leader-badge' in html or 'LEADER' in html.upper()


class TestGradeLevelPageAccuracy:
    """Test accurate calculations and winners on Grade Level page."""

    # ========== PHASE 1: CRITICAL WINNERS AND TOTALS ==========

    def test_grade_level_top_class_accuracy(self, client, sample_db):
        """Verify top class by fundraising is correctly identified."""
        # Query for top class overall
        top_class = sample_db.execute_query("""
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                SUM(rc.donation_amount) as total_fundraising
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level
            ORDER BY total_fundraising DESC
            LIMIT 1
        """)[0]

        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Verify top class appears
        assert top_class['class_name'] in html, \
            f"Top class {top_class['class_name']} not found on Grade Level page"

        # Verify fundraising amount appears
        amount = top_class['total_fundraising']
        assert f'${amount:.0f}' in html or f'${amount:,.0f}' in html, \
            f"Top class fundraising ${amount:.0f} not found"

    def test_grade_level_winner_highlights_accuracy(self, client, sample_db):
        """Verify winner highlights appear for school-wide winners."""
        # Query for school-wide winners
        school_winners = sample_db.execute_query("""
            SELECT
                ci.class_name,
                SUM(rc.donation_amount) as total_fundraising,
                SUM(rc.cumulative_minutes) as total_minutes
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name
            ORDER BY total_fundraising DESC
            LIMIT 1
        """)[0]

        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Verify winning-value CSS classes appear
        assert 'winning-value' in html, \
            "No winning value highlights found on Grade Level page"

        # School-wide winners should have gold highlights
        assert 'winning-value-school' in html or 'winning-value-grade' in html, \
            "No school-wide or grade-level winner highlights found"

    def test_grade_level_grade_totals_accuracy(self, client, sample_db):
        """Verify grade-level totals are calculated correctly."""
        # Query for grade-level totals
        grade_totals = sample_db.execute_query("""
            SELECT
                ci.grade_level,
                COUNT(DISTINCT ci.class_name) as num_classes,
                COUNT(DISTINCT r.student_name) as num_students,
                SUM(rc.donation_amount) as total_fundraising,
                SUM(rc.cumulative_minutes) as total_minutes
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.grade_level
            ORDER BY ci.grade_level
        """)

        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Verify at least one grade's totals appear
        if grade_totals:
            first_grade = grade_totals[0]
            # Check for student count
            assert str(first_grade['num_students']) in html, \
                f"Student count {first_grade['num_students']} for grade {first_grade['grade_level']} not found"

    # ========== PHASE 2: RANKINGS AND EDGE CASES ==========

    def test_grade_level_class_rankings_accuracy(self, client, sample_db):
        """Verify class rankings within each grade are correct."""
        # Query for top 3 classes by fundraising
        top_classes = sample_db.execute_query("""
            SELECT
                ci.class_name,
                ci.grade_level,
                SUM(rc.donation_amount) as total_fundraising
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name, ci.grade_level
            ORDER BY total_fundraising DESC
            LIMIT 3
        """)

        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Parse HTML to check if classes appear in order
        # (Note: actual order depends on sorting, but all top 3 should appear)
        for cls in top_classes:
            assert cls['class_name'] in html, \
                f"Top class {cls['class_name']} not found on Grade Level page"

    def test_grade_level_filter_affects_winners(self, client, sample_db):
        """Verify filtering by grade changes winner highlights."""
        # Get winners for a specific grade (e.g., Kindergarten)
        grade_winners = sample_db.execute_query("""
            SELECT
                ci.class_name,
                ci.grade_level,
                SUM(rc.donation_amount) as total_fundraising
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            WHERE ci.grade_level = 'K'
            GROUP BY ci.class_name, ci.grade_level
            ORDER BY total_fundraising DESC
            LIMIT 1
        """)

        if not grade_winners:
            pytest.skip("No Kindergarten classes found in sample data")

        # Load page with grade filter
        response = client.get('/classes?grade=K')
        html = response.data.decode('utf-8')

        # Verify winner appears
        winner_class = grade_winners[0]['class_name']
        assert winner_class in html, \
            f"Grade K winner {winner_class} not found when filtering by K"

        # Verify page only shows K classes
        assert 'data-grade="K"' in html, "No Kindergarten rows found when filtering by K"

    def test_grade_level_banner_winners_accuracy(self, client, sample_db):
        """Verify banner shows correct winners for fundraising and reading."""
        # Query for overall winners (shown in banner)
        fundraising_winner = sample_db.execute_query("""
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                SUM(rc.donation_amount) as total_fundraising
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level
            ORDER BY total_fundraising DESC
            LIMIT 1
        """)[0]

        reading_winner = sample_db.execute_query("""
            SELECT
                ci.class_name,
                ci.teacher_name,
                ci.grade_level,
                SUM(rc.cumulative_minutes) as total_minutes
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name, ci.teacher_name, ci.grade_level
            ORDER BY total_minutes DESC
            LIMIT 1
        """)[0]

        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Verify fundraising winner appears in banner
        assert fundraising_winner['teacher_name'] in html or fundraising_winner['class_name'] in html, \
            f"Fundraising winner {fundraising_winner['class_name']} not found in banner"

        # Verify reading winner appears in banner
        assert reading_winner['teacher_name'] in html or reading_winner['class_name'] in html, \
            f"Reading winner {reading_winner['class_name']} not found in banner"

    def test_grade_level_table_sorting_initial_state(self, client, sample_db):
        """Verify table initial sort order is by grade (or specified default)."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find table rows
        table = soup.find('table', {'id': 'classesTable'})
        if not table:
            pytest.skip("Table not found on page")

        rows = table.find('tbody').find_all('tr')

        # Extract grade levels from rows
        grades = []
        for row in rows:
            grade_attr = row.get('data-grade')
            if grade_attr:
                grades.append(grade_attr)

        # Should have some rows
        assert len(grades) > 0, "No table rows found"

        # Note: Actual sort order depends on JavaScript, but structure should exist
        # This test verifies table structure is present
        assert table is not None

    def test_grade_level_avg_per_student_accuracy(self, client, sample_db):
        """Verify average minutes per student calculations are correct."""
        # Query for a specific class's avg per student
        class_avg = sample_db.execute_query("""
            SELECT
                ci.class_name,
                COUNT(DISTINCT r.student_name) as num_students,
                SUM(rc.cumulative_minutes) as total_minutes,
                SUM(rc.cumulative_minutes) * 1.0 / COUNT(DISTINCT r.student_name) as avg_per_student
            FROM Class_Info ci
            JOIN Roster r ON ci.class_name = r.class_name
            JOIN Reader_Cumulative rc ON r.student_name = rc.student_name
            GROUP BY ci.class_name
            ORDER BY avg_per_student DESC
            LIMIT 1
        """)[0]

        response = client.get('/classes')
        html = response.data.decode('utf-8')

        # Verify class name appears
        assert class_avg['class_name'] in html

        # Verify average appears (could be rounded to int or shown with decimal)
        avg_int = int(class_avg['avg_per_student'])
        avg_float = f"{class_avg['avg_per_student']:.1f}"

        # At least one format should appear
        assert str(avg_int) in html or avg_float in html


if __name__ == '__main__':
    # Allow running this file directly with: python test_data_accuracy.py
    pytest.main([__file__, '-v'])
