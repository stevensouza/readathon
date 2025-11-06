"""
Banner Values Regression Test Suite

This test suite verifies the EXACT numeric values displayed in banner metrics
across all three pages (School, Teams, Grade Level) using the sample database.

Purpose:
- Catch regressions in banner calculations (e.g., sponsor count bug)
- Verify correct formatting and display of all 6 banner metrics
- Ensure consistency across pages when showing same data

Test Strategy:
- Uses sample database with known, static values
- Tests "full contest" scenario (no date/grade filters)
- Verifies main value, subtitle, and formatting
- Tests all 6 metrics on all 3 pages

Sample Database Expected Values (Full Contest):
- Total Fundraising: $280
- Total Minutes: 390 min (6 hours)
- Total Sponsors: 28 (7 of 7 students)
- Avg. Participation (With Color): 107.1%
- Goal Met (≥1 Day): 57.1% (4 of 7 students)
- Campaign Days: 2

Team Breakdown:
- team1: $60, 190 min, 6 sponsors, 83.3% participation, 66.7% goal met
- team2: $220, 200 min, 22 sponsors, 125.0% participation, 50.0% goal met

Created: 2025-10-31
Last Updated: 2025-10-31
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


class TestSchoolPageBannerValues:
    """Test exact banner metric values on School page (full contest)."""

    def test_campaign_day_value(self, client):
        """Verify Campaign Day shows correct day count."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Campaign Day metric
        metrics = soup.find_all('div', class_='headline-metric')
        campaign_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '📅 Campaign Day' in label.text:
                campaign_metric = metric
                break

        assert campaign_metric is not None, "Campaign Day metric not found"

        # Verify value shows "Day 2 of 2"
        value = campaign_metric.find('div', class_='headline-value')
        assert value is not None, "Campaign Day value not found"
        assert '2' in value.text, f"Expected '2' in Campaign Day value, got: {value.text}"
        assert 'of' in value.text.lower(), f"Expected 'of' in Campaign Day value, got: {value.text}"

    def test_fundraising_value(self, client):
        """Verify Fundraising shows $280."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Fundraising metric
        metrics = soup.find_all('div', class_='headline-metric')
        fundraising_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '💰 Fundraising' in label.text:
                fundraising_metric = metric
                break

        assert fundraising_metric is not None, "Fundraising metric not found"

        # Verify value shows $280
        value = fundraising_metric.find('div', class_='headline-value')
        assert value is not None, "Fundraising value not found"
        value_text = value.text.strip()
        assert '$280' in value_text, f"Expected '$280' in fundraising, got: {value_text}"

    def test_minutes_value(self, client):
        """Verify Minutes Read shows 6 hours (390 min)."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Minutes metric
        metrics = soup.find_all('div', class_='headline-metric')
        minutes_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '📚 Minutes Read' in label.text:
                minutes_metric = metric
                break

        assert minutes_metric is not None, "Minutes Read metric not found"

        # Verify value shows 6 hours
        value = minutes_metric.find('div', class_='headline-value')
        assert value is not None, "Minutes value not found"
        value_text = value.text.strip()
        assert '6' in value_text and 'hour' in value_text.lower(), \
            f"Expected '6 hours' in minutes, got: {value_text}"

        # Verify subtitle shows (390 min)
        subtitle = minutes_metric.find('div', class_='headline-subtitle')
        assert subtitle is not None, "Minutes subtitle not found"
        subtitle_text = subtitle.text.strip()
        assert '390' in subtitle_text, f"Expected '390 min' in subtitle, got: {subtitle_text}"

    def test_sponsors_value(self, client):
        """Verify Sponsors shows 28 total (not 7 students)."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Sponsors metric
        metrics = soup.find_all('div', class_='headline-metric')
        sponsors_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '🎁 Sponsors' in label.text:
                sponsors_metric = metric
                break

        assert sponsors_metric is not None, "Sponsors metric not found"

        # Verify main value shows 28 (total sponsors, not student count)
        value = sponsors_metric.find('div', class_='headline-value')
        assert value is not None, "Sponsors value not found"
        value_text = value.text.strip()
        assert '28' in value_text, f"Expected '28' sponsors, got: {value_text}"
        assert '7' not in value_text, f"Main value should NOT show student count (7), got: {value_text}"

        # Verify subtitle shows "7 of 7 Students"
        subtitle = sponsors_metric.find('div', class_='headline-subtitle')
        assert subtitle is not None, "Sponsors subtitle not found"
        subtitle_text = subtitle.text.strip()
        assert '7 of 7' in subtitle_text, f"Expected '7 of 7' in subtitle, got: {subtitle_text}"
        assert '100' in subtitle_text, f"Expected '100%' in subtitle, got: {subtitle_text}"

    def test_avg_participation_value(self, client):
        """Verify Avg. Participation (With Color) shows 107.1%."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Avg. Participation metric
        metrics = soup.find_all('div', class_='headline-metric')
        participation_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '👥 Avg. Participation' in label.text:
                participation_metric = metric
                break

        assert participation_metric is not None, "Avg. Participation metric not found"

        # Verify value shows 107.1%
        value = participation_metric.find('div', class_='headline-value')
        assert value is not None, "Avg. Participation value not found"
        value_text = value.text.strip()
        assert '107.1%' in value_text, f"Expected '107.1%', got: {value_text}"

    def test_goal_met_value(self, client):
        """Verify Goal Met (≥1 Day) shows 57.1%."""
        response = client.get('/school')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Goal Met metric
        metrics = soup.find_all('div', class_='headline-metric')
        goal_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '🎯 Goal Met' in label.text:
                goal_metric = metric
                break

        assert goal_metric is not None, "Goal Met metric not found"

        # Verify value shows 57.1%
        value = goal_metric.find('div', class_='headline-value')
        assert value is not None, "Goal Met value not found"
        value_text = value.text.strip()
        assert '57' in value_text, f"Expected '57.1%', got: {value_text}"

        # Verify subtitle shows "4 of 7 students"
        subtitle = goal_metric.find('div', class_='headline-subtitle')
        assert subtitle is not None, "Goal Met subtitle not found"
        subtitle_text = subtitle.text.strip()
        assert '4 of 7' in subtitle_text, f"Expected '4 of 7' in subtitle, got: {subtitle_text}"


class TestTeamsPageBannerValues:
    """Test exact banner metric values on Teams page (full contest)."""

    def test_fundraising_winner(self, client):
        """Verify Fundraising winner is team2 with $220."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Fundraising metric in banner
        metrics = soup.find_all('div', class_='headline-metric')
        fundraising_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '💰 Fundraising' in label.text:
                fundraising_metric = metric
                break

        assert fundraising_metric is not None, "Fundraising metric not found"

        # Verify team2 badge is shown (winner)
        winner_div = fundraising_metric.find('div', class_='headline-winner')
        assert winner_div is not None, "Fundraising winner badge not found"
        assert 'TEAM2' in winner_div.text.upper(), f"Expected TEAM2 to win fundraising, got: {winner_div.text}"

        # Verify value shows $220
        value = fundraising_metric.find('div', class_='headline-value')
        assert value is not None, "Fundraising value not found"
        value_text = value.text.strip()
        assert '$220' in value_text, f"Expected '$220', got: {value_text}"

    def test_sponsors_winner(self, client):
        """Verify Sponsors winner is team2 with 22 total sponsors."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Sponsors metric
        metrics = soup.find_all('div', class_='headline-metric')
        sponsors_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '🎁 Sponsors' in label.text:
                sponsors_metric = metric
                break

        assert sponsors_metric is not None, "Sponsors metric not found"

        # Verify team2 wins
        winner_div = sponsors_metric.find('div', class_='headline-winner')
        assert winner_div is not None, "Sponsors winner badge not found"
        assert 'TEAM2' in winner_div.text.upper(), f"Expected TEAM2 to win sponsors, got: {winner_div.text}"

        # Verify value shows 22 (total sponsors, not student count)
        value = sponsors_metric.find('div', class_='headline-value')
        assert value is not None, "Sponsors value not found"
        value_text = value.text.strip()
        assert '22' in value_text, f"Expected '22' sponsors, got: {value_text}"

    def test_avg_participation_winner(self, client):
        """Verify Avg. Participation winner is team2 with 125.0%."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Avg. Participation metric
        metrics = soup.find_all('div', class_='headline-metric')
        participation_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '👥 Avg. Participation' in label.text:
                participation_metric = metric
                break

        assert participation_metric is not None, "Avg. Participation metric not found"

        # Verify team2 wins
        winner_div = participation_metric.find('div', class_='headline-winner')
        assert winner_div is not None, "Avg. Participation winner badge not found"
        assert 'TEAM2' in winner_div.text.upper(), f"Expected TEAM2 to win participation, got: {winner_div.text}"

        # Verify value shows 125.0%
        value = participation_metric.find('div', class_='headline-value')
        assert value is not None, "Avg. Participation value not found"
        value_text = value.text.strip()
        assert '125' in value_text, f"Expected '125.0%', got: {value_text}"

    def test_goal_met_winner(self, client):
        """Verify Goal Met winner is team1 with 66.7%."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Goal Met metric
        metrics = soup.find_all('div', class_='headline-metric')
        goal_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '🎯 Goal Met' in label.text:
                goal_metric = metric
                break

        assert goal_metric is not None, "Goal Met metric not found"

        # Verify team1 wins
        winner_div = goal_metric.find('div', class_='headline-winner')
        assert winner_div is not None, "Goal Met winner badge not found"
        assert 'TEAM1' in winner_div.text.upper(), f"Expected TEAM1 to win goal met, got: {winner_div.text}"

        # Verify value shows 66.7%
        value = goal_metric.find('div', class_='headline-value')
        assert value is not None, "Goal Met value not found"
        value_text = value.text.strip()
        assert '66' in value_text or '67' in value_text, f"Expected ~66.7%, got: {value_text}"

        # Verify subtitle shows "2 of 3 students" (not "66 of 3")
        subtitle = goal_metric.find('div', class_='headline-subtitle')
        assert subtitle is not None, "Goal Met subtitle not found"
        subtitle_text = subtitle.text.strip()
        assert '2 of 3' in subtitle_text, f"Expected '2 of 3 students', got: {subtitle_text}"
        assert '66 of 3' not in subtitle_text, f"Should NOT show '66 of 3' (bug), got: {subtitle_text}"

    def test_campaign_day_value(self, client):
        """Verify Campaign Day shows correct day count."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Campaign Day metric
        metrics = soup.find_all('div', class_='headline-metric')
        campaign_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '📅 Campaign Day' in label.text:
                campaign_metric = metric
                break

        assert campaign_metric is not None, "Campaign Day metric not found"

        # Verify value shows "Day 2 of 2"
        value = campaign_metric.find('div', class_='headline-value')
        assert value is not None, "Campaign Day value not found"
        assert '2' in value.text, f"Expected '2' in Campaign Day value, got: {value.text}"
        assert 'of' in value.text.lower(), f"Expected 'of' in Campaign Day value, got: {value.text}"

    def test_minutes_winner(self, client):
        """Verify Minutes Read winner is team2 with 200 min (3.3 hours)."""
        response = client.get('/teams')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Minutes Read metric
        metrics = soup.find_all('div', class_='headline-metric')
        minutes_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '📚 Minutes Read' in label.text:
                minutes_metric = metric
                break

        assert minutes_metric is not None, "Minutes Read metric not found"

        # Verify team2 wins
        winner_div = minutes_metric.find('div', class_='headline-winner')
        assert winner_div is not None, "Minutes winner badge not found"
        assert 'TEAM2' in winner_div.text.upper(), f"Expected TEAM2 to win minutes, got: {winner_div.text}"

        # Verify value shows 200 min or 3.3 hours
        value = minutes_metric.find('div', class_='headline-value')
        assert value is not None, "Minutes value not found"
        value_text = value.text.strip()
        # Could show as "200" or "3" (hours) depending on format
        assert '200' in value_text or '3' in value_text, f"Expected '200 min' or '3 hours', got: {value_text}"


class TestGradeLevelPageBannerValues:
    """Test exact banner metric values on Grade Level page (full contest, all grades).

    NOTE: Grade Level page banner shows TOP CLASS values (winners among all classes),
    NOT school-wide totals like School page.
    """

    def test_fundraising_value(self, client):
        """Verify Fundraising shows $130 (top class: teacher4)."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Fundraising metric
        metrics = soup.find_all('div', class_='headline-metric')
        fundraising_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '💰 Fundraising' in label.text:
                fundraising_metric = metric
                break

        assert fundraising_metric is not None, "Fundraising metric not found"

        # Verify value shows $130 (top class fundraising, not school-wide total)
        value = fundraising_metric.find('div', class_='headline-value')
        assert value is not None, "Fundraising value not found"
        value_text = value.text.strip()
        assert '$130' in value_text, f"Expected '$130' (top class), got: {value_text}"

    def test_sponsors_value(self, client):
        """Verify Sponsors shows 13 (top class sponsors)."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Sponsors metric
        metrics = soup.find_all('div', class_='headline-metric')
        sponsors_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '🎁 Sponsors' in label.text:
                sponsors_metric = metric
                break

        assert sponsors_metric is not None, "Sponsors metric not found"

        # Verify value shows 13 (top class sponsors, not school-wide total)
        value = sponsors_metric.find('div', class_='headline-value')
        assert value is not None, "Sponsors value not found"
        value_text = value.text.strip()
        assert '13' in value_text, f"Expected '13' sponsors (top class), got: {value_text}"

    def test_page_loads_successfully(self, client):
        """Verify Grade Level page loads without errors."""
        response = client.get('/classes')
        assert response.status_code == 200, f"Expected 200, got: {response.status_code}"
        html = response.data.decode('utf-8')
        assert 'Grade Level' in html or 'Classes' in html, "Grade Level page content not found"

    def test_campaign_day_value(self, client):
        """Verify Campaign Day shows correct day count."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Campaign Day metric
        metrics = soup.find_all('div', class_='headline-metric')
        campaign_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '📅 Campaign Day' in label.text:
                campaign_metric = metric
                break

        assert campaign_metric is not None, "Campaign Day metric not found"

        # Verify value shows "Day 2 of 2"
        value = campaign_metric.find('div', class_='headline-value')
        assert value is not None, "Campaign Day value not found"
        assert '2' in value.text, f"Expected '2' in Campaign Day value, got: {value.text}"
        assert 'of' in value.text.lower(), f"Expected 'of' in Campaign Day value, got: {value.text}"

    def test_minutes_value(self, client):
        """Verify Minutes Read shows 120 min (top class: teacher1)."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Minutes Read metric
        metrics = soup.find_all('div', class_='headline-metric')
        minutes_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '📚 Minutes Read' in label.text or '📖 Minutes Read' in label.text:
                minutes_metric = metric
                break

        assert minutes_metric is not None, "Minutes Read metric not found"

        # Verify value shows 120 min (top class)
        value = minutes_metric.find('div', class_='headline-value')
        assert value is not None, "Minutes value not found"
        value_text = value.text.strip()
        assert '120' in value_text or '2' in value_text, f"Expected '120 min' or '2 hours' (top class), got: {value_text}"

    def test_avg_participation_value(self, client):
        """Verify Avg. Participation shows 125.0% (top class with color bonus)."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Avg. Participation metric
        metrics = soup.find_all('div', class_='headline-metric')
        participation_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '👥 Avg. Participation' in label.text:
                participation_metric = metric
                break

        assert participation_metric is not None, "Avg. Participation metric not found"

        # Verify value shows 125.0% (top class with color bonus)
        value = participation_metric.find('div', class_='headline-value')
        assert value is not None, "Avg. Participation value not found"
        value_text = value.text.strip()
        assert '125' in value_text, f"Expected '125.0%' (top class), got: {value_text}"

    def test_goal_met_value(self, client):
        """Verify Goal Met shows 100.0% (top class: teacher1)."""
        response = client.get('/classes')
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        # Find Goal Met metric
        metrics = soup.find_all('div', class_='headline-metric')
        goal_metric = None
        for metric in metrics:
            label = metric.find('div', class_='headline-label')
            if label and '🎯 Goal Met' in label.text:
                goal_metric = metric
                break

        assert goal_metric is not None, "Goal Met metric not found"

        # Verify value shows 100.0% (top class)
        value = goal_metric.find('div', class_='headline-value')
        assert value is not None, "Goal Met value not found"
        value_text = value.text.strip()
        assert '100' in value_text, f"Expected '100.0%' (top class), got: {value_text}"
