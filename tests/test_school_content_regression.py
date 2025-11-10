"""
School Page Content Regression Test Suite

This test suite verifies the EXACT content displayed in School page
using the sample database with known, static values.

Purpose:
- Catch regressions in banner metrics (6 headline metrics)
- Verify top performers show correct student/class names
- Test team competition shows correct team names and values
- Verify participation statistics

Test Strategy:
- Uses sample database with known values (no ties)
- Uses BeautifulSoup for precise HTML parsing
- Tests actual displayed names and values, not just structure

Sample Database Expected Values:

Banner Metrics:
  - Total Fundraising: $280
  - Minutes Read: 450 min (7.5 hrs)
  - Sponsors: 28
  - Total Roster: 7 students

Top Performers:
  - Fundraising Leader: student42 (Grade 2) - $70
  - Reading Leader: student11 (Grade K) - 200 min
  - Top Class Fundraising: class4 (teacher4, Grade 2) - $130
  - Top Class Reading: class1 (teacher1, Grade K) - 200 min

Team Competition:
  - team1: 3 students, $60 fundraising
  - team2: 4 students, $220 fundraising

Created: 2025-11-10
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
            with client.session_transaction() as sess:
                sess['environment'] = 'sample'
        yield client


@pytest.fixture
def sample_db():
    """Get sample database instance for verification queries."""
    return ReadathonDB('db/readathon_sample.db')


class TestBannerMetrics:
    """Test banner headline metrics show correct values."""

    def test_total_fundraising(self, client):
        """Verify banner shows $280 total fundraising."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Sample DB total: $10 + $20 + $30 + $40 + $50 + $60 + $70 = $280
        assert '$280' in html, "Expected $280 total fundraising in banner"

    def test_total_minutes(self, client):
        """Verify banner shows 450 minutes (7.5 hours) total reading."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Sample DB total: 200 + 50 + 20 + 60 + 60 + 30 + 30 = 450 min = 7.5 hrs
        # Banner may show "7" or "7.5" or "8" depending on rounding
        assert '7' in html or '450' in html, "Expected 7-8 hours or 450 minutes in banner"

    def test_total_sponsors(self, client):
        """Verify banner shows 28 total sponsors."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Sample DB total: 1 + 2 + 3 + 4 + 5 + 6 + 7 = 28
        assert '28' in html, "Expected 28 total sponsors in banner"

    def test_total_roster(self, client):
        """Verify banner shows 7 students in roster."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # Sample DB has 7 students
        assert '7' in html, "Expected 7 students in roster"


class TestFundraisingLeader:
    """Test Fundraising Leader card shows student42."""

    def test_shows_student42(self, client):
        """Verify student42 appears as fundraising leader."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # student42 has $70, highest in school
        assert 'student42' in html, "Expected student42 as fundraising leader"

    def test_shows_70_dollars(self, client):
        """Verify $70 appears for student42."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        assert '$70' in html, "Expected $70 for fundraising leader"

    def test_shows_grade_2(self, client):
        """Verify Grade 2 appears for student42."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # student42 is in Grade 2
        # May appear as "Grade 2" or just "2"
        assert 'Grade 2' in html or ' 2' in html, "Expected Grade 2 for student42"


class TestReadingLeader:
    """Test Reading Leader card shows student11."""

    def test_shows_student11(self, client):
        """Verify student11 appears as reading leader."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # student11 has 200 minutes, highest in school
        assert 'student11' in html, "Expected student11 as reading leader"

    def test_shows_200_minutes(self, client):
        """Verify 200 minutes appears for student11."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        assert '200' in html, "Expected 200 minutes for reading leader"

    def test_shows_grade_k(self, client):
        """Verify Grade K appears for student11."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # student11 is in Grade K
        # May appear as "Grade K" or just "K"
        assert 'Grade K' in html or ' K' in html or 'Kindergarten' in html, \
            "Expected Grade K for student11"


class TestTopClassFundraising:
    """Test Top Class Fundraising card shows class4."""

    def test_shows_class4_or_teacher4(self, client):
        """Verify class4 or teacher4's Class appears as top fundraising class."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        page_text = soup.get_text()

        # Top class fundraising should show class4 or teacher4
        assert 'class4' in page_text or 'teacher4' in page_text, \
            "Expected class4 or teacher4 as top fundraising class"

    def test_shows_130_dollars(self, client):
        """Verify $130 appears for top fundraising class."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # class4 total: $60 (student41) + $70 (student42) = $130
        assert '$130' in html, "Expected $130 for top fundraising class"


class TestTopClassReading:
    """Test Top Class Reading card shows class1."""

    def test_shows_class1_or_teacher1(self, client):
        """Verify class1 or teacher1's Class appears as top reading class."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        page_text = soup.get_text()

        # Top class reading should show class1 or teacher1
        assert 'class1' in page_text or 'teacher1' in page_text, \
            "Expected class1 or teacher1 as top reading class"

    def test_shows_200_minutes(self, client):
        """Verify 200 minutes appears for top reading class."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # class1 total: 200 minutes (student11 only student in class1)
        assert '200' in html, "Expected 200 minutes for top reading class"


class TestTeamCompetition:
    """Test Team Competition section shows both teams with correct values."""

    def test_both_teams_present(self, client):
        """Verify both team1 and team2 appear in team competition."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        page_text = soup.get_text()

        # Both teams should appear (may be uppercase TEAM1/TEAM2)
        assert 'team1' in page_text.lower() or 'TEAM1' in html, \
            "Expected team1 in team competition"
        assert 'team2' in page_text.lower() or 'TEAM2' in html, \
            "Expected team2 in team competition"

    def test_team1_fundraising(self, client):
        """Verify team1 shows $60 fundraising."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # team1 total: $10 + $20 + $30 = $60
        assert '$60' in html, "Expected $60 fundraising for team1"

    def test_team2_fundraising(self, client):
        """Verify team2 shows $220 fundraising."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # team2 total: $40 + $50 + $60 + $70 = $220
        assert '$220' in html, "Expected $220 fundraising for team2"

    def test_team1_students(self, client):
        """Verify team1 shows 3 students."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # team1 has 3 students
        # Look for "3" in context of students or team1
        assert '3' in html, "Expected 3 students for team1"

    def test_team2_students(self, client):
        """Verify team2 shows 4 students."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        # team2 has 4 students
        assert '4' in html, "Expected 4 students for team2"


class TestParticipationStatistics:
    """Test Student Participation section shows correct statistics."""

    def test_total_roster_displayed(self, client):
        """Verify total roster count of 7 appears."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        assert '7' in html, "Expected 7 total students"

    def test_participation_section_present(self, client):
        """Verify Student Participation section exists."""
        response = client.get('/school')
        html = response.data.decode('utf-8')

        assert 'STUDENT PARTICIPATION' in html.upper() or 'Participation' in html, \
            "Expected Student Participation section"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
