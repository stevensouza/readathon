"""
Test suite for the Scoreboards (Feature 39): Daily Scoreboard and Prize Scoreboard.

Page tests run against the sample database (7 students, 2 contest days: 2025-10-10/11,
one saved cumulative snapshot on 2025-10-11). Tests that write data use temporary copies.
"""

import io
import os
import re
import shutil
import sqlite3

import pytest

import scoreboards
from app import app, registry
from database import DatabaseRegistry, ReadathonDB, ReportGenerator
from queries import get_db_comparison_school_participation

SAMPLE_DB_PATH = 'db/readathon_sample.db'
DAY1, DAY2 = '2025-10-10', '2025-10-11'


def sample_db_id():
    return next(db['db_id'] for db in registry.list_databases() if db['db_filename'] == 'readathon_sample.db')


@pytest.fixture
def client():
    """Test client with the sample database active"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['active_database_id'] = sample_db_id()
        yield client


@pytest.fixture
def sample_db():
    return ReadathonDB(SAMPLE_DB_PATH)


@pytest.fixture
def sample_reports(sample_db):
    return ReportGenerator(sample_db)


@pytest.fixture
def db_copy(tmp_path):
    """A writable copy of the sample database"""
    path = tmp_path / 'readathon_copy.db'
    shutil.copy(SAMPLE_DB_PATH, path)
    db = ReadathonDB(str(path))
    yield db
    db.close()


def report_html(html):
    """The report area (what "Copy as image" captures): from #report up to the page scripts"""
    return html.split('id="report"', 1)[1].split('<script', 1)[0]


def page_text(html):
    """Visible text of the report area, whitespace collapsed"""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', report_html(html)))


class _ScoreboardPageChecks:
    """Mandatory page tests from md/RULES.md, adapted to the scoreboard components"""
    url = None

    def test_page_loads_successfully(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assert b'Read-a-Thon System' in response.data

    def test_no_error_messages(self, client):
        html = client.get(self.url).data.decode('utf-8').lower()
        for pattern in ['error:', 'exception:', 'traceback', 'error occurred']:
            assert pattern not in html

    def test_percentage_formats(self, client):
        percentages = re.findall(r'(\d+\.?\d*)%', page_text(client.get(self.url).data.decode('utf-8')))
        assert percentages
        for value in percentages:
            float(value)

    def test_currency_formats(self, client):
        currencies = re.findall(r'\$[\d,]+\.?\d*', page_text(client.get(self.url).data.decode('utf-8')))
        assert currencies
        for value in currencies:
            float(value.replace('$', '').replace(',', ''))

    def test_team_panels_present(self, client):
        """Team colors: alphabetical first team = navy panel, second = gold panel"""
        html = client.get(self.url).data.decode('utf-8')
        blue = html.index('score-panel team-blue')
        gold = html.index('score-panel team-gold')
        assert blue < gold
        assert 'Team Team1' in html[blue:gold]
        assert 'Team Team2' in html[gold:]

    def test_winner_trophies(self, client):
        assert 'win-trophy-badge' in client.get(self.url).data.decode('utf-8')

    def test_masthead(self, client):
        html = client.get(self.url).data.decode('utf-8')
        assert 'class="masthead"' in html and 'mh-medallion' in html
        assert 'Day 2 of 10' in html
        assert 'October 11, 2025' in html

    def test_controls_outside_report(self, client):
        """The image is captured from #report only: no pickers or buttons inside it"""
        html = client.get(self.url).data.decode('utf-8')
        report = report_html(html)
        assert 'day-picker' in html and 'copy-btn' in html and 'download-btn' in html
        assert 'day-picker' not in report and 'copy-btn' not in report and '<button' not in report

    def test_nav_menu(self, client):
        html = client.get(self.url).data.decode('utf-8')
        assert '🏆 Scoreboards' in html
        assert 'href="/scoreboards/daily"' in html and 'href="/scoreboards/prize"' in html

    def test_invalid_day_falls_back_to_latest(self, client):
        for bad in ['0', '99', 'abc', '-1']:
            response = client.get(f'{self.url}?day={bad}')
            assert response.status_code == 200
            assert 'Day 2 of 10' in response.data.decode('utf-8')


class TestDailyScoreboardPage(_ScoreboardPageChecks):
    url = '/scoreboards/daily'

    def test_sample_data_integrity(self, client, sample_db):
        """Team cards match SQL: capped minutes (+ bonus through the day), money from the day's snapshot"""
        text = page_text(client.get(self.url).data.decode('utf-8'))
        # Latest day counts the whole contest, like the Reports page (Q19)
        minutes = {r['team_name']: r['total_minutes_with_color']
                   for r in ReportGenerator(sample_db).q19_team_minutes()['data']}
        assert f"{minutes['team1']:,}" in text and f"{minutes['team2']:,}" in text
        money = sample_db.execute_query("""
            SELECT r.team_name, SUM(h.donation_amount) as total FROM Reader_Cumulative_History h
            JOIN Roster r ON r.student_name = h.student_name WHERE h.snapshot_date = ? GROUP BY r.team_name""", (DAY2,))
        for row in money:
            assert f"${row['total']:,.0f}" in text

    def test_medallion_matches_sql(self, client, sample_db):
        readers = sample_db.execute_query(
            "SELECT COUNT(DISTINCT student_name) as n FROM Daily_Logs WHERE minutes_read > 0")[0]['n']
        roster = sample_db.execute_query("SELECT COUNT(*) as n FROM Roster")[0]['n']
        assert f'{100.0 * readers / roster:.0f}%' in page_text(client.get(self.url).data.decode('utf-8'))

    def test_day_one_has_no_money_snapshot(self, client):
        """Day 1 has no saved cumulative upload: money shows Not available and wins no trophy"""
        html = client.get(f'{self.url}?day=1').data.decode('utf-8')
        text = page_text(html)
        assert 'Day 1 of 10' in text
        assert 'Not available*' in text
        assert 'No fundraising total was saved for Day 1' in text

    def test_drawing_number_in_header_and_redraw_link(self, client):
        html = client.get(f'{self.url}?day=2&draw=3').data.decode('utf-8')
        assert 'Drawing #3' in page_text(html)
        assert 'draw=4' in html  # Redraw bumps the drawing number

    def test_drawing_is_stable(self, client):
        first = client.get(f'{self.url}?day=2&draw=5').data.decode('utf-8')
        again = client.get(f'{self.url}?day=2&draw=5').data.decode('utf-8')
        pick = lambda h: re.search(r'id="winners-table".*?</table>', h, re.S).group(0)
        assert pick(first) == pick(again)

    def test_classes_by_grade_and_top_tag(self, client, sample_reports):
        text = page_text(client.get(self.url).data.decode('utf-8'))
        for row in sample_reports.q18_lead_class_by_grade()['data']:
            assert f"{row['avg_participation_rate_with_color']:.1f}%" in text
        assert 'Top' in text  # school-wide leader tag

    def test_no_showdown_without_prior_year(self, client):
        assert 'Showdown' not in client.get(self.url).data.decode('utf-8')


class TestPrizeScoreboardPage(_ScoreboardPageChecks):
    url = '/scoreboards/prize'

    def test_sample_data_integrity(self, client, sample_reports):
        text = page_text(client.get(self.url).data.decode('utf-8'))
        best = sample_reports.q13_overall_best_class_simplified()['data'][0]
        assert f"{best['avg_participation_rate_with_color']:.1f}%" in text
        for row in sample_reports.q9_most_donations_by_grade(DAY2)['data']:
            assert f"${row['donation_amount']:,.0f}" in text

    def test_midway_wording(self, client):
        text = page_text(client.get(self.url).data.decode('utf-8'))
        assert 'Prize Leaders — as of Day 2' in text.replace('&mdash;', '—')
        assert 'Final Prize Winners' not in text

    def test_prize_text_from_report_notes(self, client):
        text = page_text(client.get(self.url).data.decode('utf-8'))
        for prize in ["Grandpa Joe's $25 Gift Card", 'Book Store $25 Gift Card', 'Learning Express $25 Gift Card',
                      '$100 for the teacher', 'A book for every Goal Getter']:
            assert prize in text.replace('&#39;', "'")

    def test_winner_count_medallion(self, client, sample_reports):
        winners = set()
        for report in [sample_reports.q16_top_earner_per_team(DAY2), sample_reports.q10_most_minutes_by_grade(),
                       sample_reports.q9_most_donations_by_grade(DAY2), sample_reports.q11_most_sponsors_by_grade(DAY2),
                       sample_reports.q15_goal_getters()]:
            winners.update(r['student_name'] for r in report['data'])
        html = client.get(self.url).data.decode('utf-8')
        assert f'id="winner-count">{len(winners)}<' in html

    def test_goal_getters_listed(self, client, sample_reports):
        text = page_text(client.get(self.url).data.decode('utf-8'))
        getters = sample_reports.q15_goal_getters()['data']
        assert f'{len(getters)} students' in text
        for row in getters:
            assert scoreboards.display_name(row['student_name']) in text

    def test_final_wording_when_contest_days_reached(self, client):
        original = registry.get_settings()['contest_days']
        registry.set_setting('contest_days', '2')
        try:
            text = page_text(client.get(self.url).data.decode('utf-8'))
            assert 'Final Prize Winners' in text
            assert 'Day 2 of 2' in text
            assert 'every day of the contest' in text
        finally:
            registry.set_setting('contest_days', original)


class TestEmptyDatabase:
    """A new year's database before the first upload (like the 2026 database today)"""

    @pytest.fixture
    def empty_db_id(self):
        filename = 'readathon_test_scoreboard_empty.db'
        path = f'db/{filename}'
        shutil.copy(SAMPLE_DB_PATH, path)
        with sqlite3.connect(path) as conn:
            conn.execute('DELETE FROM Daily_Logs')
            conn.execute('DELETE FROM Reader_Cumulative')
        reg = DatabaseRegistry()
        db_id = reg.register_database(filename, 'Test Empty Scoreboard', 2097)
        reg.close()
        yield db_id
        reg = DatabaseRegistry()
        reg.delete_database(db_id)
        reg.close()
        os.remove(path)

    @pytest.mark.parametrize('url', ['/scoreboards/daily', '/scoreboards/prize'])
    def test_no_reading_data_yet(self, client, empty_db_id, url):
        with client.session_transaction() as sess:
            sess['active_database_id'] = empty_db_id
        response = client.get(url)
        assert response.status_code == 200
        assert 'No reading data yet' in response.data.decode('utf-8')


class TestShowdown:
    """2026 vs 2025 Showdown with a registered prior-year database"""

    @pytest.fixture
    def year_pair(self):
        """This year (2099) and last year (2098): copies of the sample database.

        Last year only has its final snapshot (like 2025), so Day 1 money is Not available.
        """
        reg = DatabaseRegistry()
        ids, paths = [], []
        for year in (2098, 2099):
            filename = f'readathon_test_scoreboard_{year}.db'
            paths.append(f'db/{filename}')
            shutil.copy(SAMPLE_DB_PATH, paths[-1])
            ids.append(reg.register_database(filename, f'Test {year}', year))
        reg.close()
        yield ids[1]
        reg = DatabaseRegistry()
        for db_id in ids:
            reg.delete_database(db_id)
        reg.close()
        for path in paths:
            os.remove(path)

    def test_missing_prior_year_value_renders_not_available(self, client, year_pair):
        with client.session_transaction() as sess:
            sess['active_database_id'] = year_pair
        text = page_text(client.get('/scoreboards/daily?day=1').data.decode('utf-8'))
        assert '2099 vs 2098 Showdown' in text
        assert 'Day 1 this year vs Day 1 last year' in text
        assert 'Not available*' in text
        assert '2098 only kept final fundraising totals, not day-by-day amounts. 2098 finished with $280 raised.' in text

    def test_final_vs_final(self, client, year_pair):
        registry.set_setting('contest_days', '2')
        try:
            with client.session_transaction() as sess:
                sess['active_database_id'] = year_pair
            text = page_text(client.get('/scoreboards/prize').data.decode('utf-8'))
            assert 'Whole school, final totals' in text
            assert '$280' in text
        finally:
            registry.set_setting('contest_days', '10')


class TestScoreboardData:
    """As-of filters, drawing, snapshots and helpers behind the pages"""

    AS_OF_METHODS = ['q10_most_minutes_by_grade', 'q12_best_class_by_grade_simplified',
                     'q13_overall_best_class_simplified', 'q14_team_participation', 'q15_goal_getters',
                     'q18_lead_class_by_grade', 'q19_team_minutes']
    MONEY_METHODS = ['q9_most_donations_by_grade', 'q11_most_sponsors_by_grade',
                     'q16_top_earner_per_team', 'q20_team_donations']

    @pytest.mark.parametrize('method', AS_OF_METHODS + MONEY_METHODS)
    def test_reports_page_results_unchanged(self, sample_reports, method):
        """No as-of date = the whole contest from the latest upload, exactly as before"""
        default = getattr(sample_reports, method)()
        explicit = getattr(sample_reports, method)(None)
        assert default['data'] == explicit['data']
        assert 'available' not in default

    @pytest.mark.parametrize('method', AS_OF_METHODS)
    def test_as_of_last_day_equals_whole_contest_without_later_bonus(self, db_copy, method):
        with db_copy.get_connection() as conn:
            conn.execute('DELETE FROM Team_Color_Bonus')  # sample bonus is dated after the last day
        reports = ReportGenerator(db_copy)
        assert getattr(reports, method)(DAY2)['data'] == getattr(reports, method)()['data']

    def test_as_of_day_one_minutes_match_sql(self, sample_db, sample_reports):
        expected = {r['team_name']: r['m'] for r in sample_db.execute_query("""
            SELECT r.team_name, SUM(MIN(dl.minutes_read, 120)) as m FROM Daily_Logs dl
            JOIN Roster r ON r.student_name = dl.student_name WHERE dl.log_date <= ? GROUP BY r.team_name""", (DAY1,))}
        rows = {r['team_name']: r['total_minutes_with_color']
                for r in sample_reports.q19_team_minutes(DAY1)['data'] if r['team_name'] != 'TOTAL'}
        assert rows == expected  # no color bonus on or before day 1

    def test_as_of_day_one_participation_matches_sql(self, sample_db, sample_reports):
        expected = {r['team_name']: round(100.0 * r['readers'] / r['students'], 2) for r in sample_db.execute_query("""
            SELECT r.team_name, COUNT(DISTINCT r.student_name) as students,
                   COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN r.student_name END) as readers
            FROM Roster r LEFT JOIN Daily_Logs dl ON dl.student_name = r.student_name AND dl.log_date = ?
            GROUP BY r.team_name""", (DAY1,))}
        rows = {r['team_name']: r['avg_participation_rate_with_color'] for r in sample_reports.q14_team_participation(DAY1)['data']}
        assert rows == expected

    def test_money_as_of_day_without_snapshot_is_not_available(self, sample_reports):
        for method in self.MONEY_METHODS:
            result = getattr(sample_reports, method)(DAY1)
            assert result['available'] is False and result['data'] == []

    def test_money_as_of_snapshot_day(self, sample_db, sample_reports):
        result = sample_reports.q20_team_donations(DAY2)
        assert result['available'] is True
        total = sum(r['total_donations'] for r in result['data'])
        assert total == sample_db.execute_query("SELECT SUM(donation_amount) as s FROM Reader_Cumulative")[0]['s']

    def test_drawing_winner_is_eligible_and_stable(self, sample_db, sample_reports):
        eligible = {(r['grade_level'], r['student_name']) for r in sample_db.execute_query("""
            SELECT r.grade_level, r.student_name FROM Roster r JOIN Daily_Logs dl ON dl.student_name = r.student_name
            JOIN Grade_Rules g ON g.grade_level = r.grade_level WHERE dl.log_date = ? AND dl.minutes_read >= g.min_daily_minutes""", (DAY2,))}
        for drawing in range(1, 20):
            first = sample_reports.q4_prize_drawing(DAY2, drawing)['data']
            again = sample_reports.q4_prize_drawing(DAY2, drawing)['data']
            assert [w['student_name'] for w in first] == [w['student_name'] for w in again]
            for winner in first:
                assert (winner['grade_level'], winner['student_name']) in eligible

    def test_redraw_can_change_winner(self, sample_reports):
        """Grade 2 has two eligible students; some drawing number must pick the other one"""
        picks = {next(w['student_name'] for w in sample_reports.q4_prize_drawing(DAY2, d)['data'] if w['grade_level'] == '2')
                 for d in range(1, 20)}
        assert len(picks) == 2

    def test_school_totals_and_today_figures(self, sample_reports):
        totals = sample_reports.school_totals_as_of(DAY1, DAY1)
        assert totals == {'participation': 100.0, 'minutes': 245, 'donations': None}
        today = sample_reports.team_day_figures(DAY2, DAY1)
        assert today['team1']['minutes'] == 35 and today['team2']['minutes'] == 90
        assert today['team1']['donations_added'] is None  # no Day 1 snapshot

    def test_medallion_source_counts_all_students(self, sample_db):
        """Date filter must not drop students who haven't read yet from the denominator"""
        row = sample_db.execute_query(get_db_comparison_school_participation(DAY1))[0]
        assert row['total_count'] == 7

    def test_helpers(self):
        assert scoreboards.format_grade_label('K') == 'Kindergarten'
        assert scoreboards.format_grade_label('3') == '3rd Grade'
        assert scoreboards.display_name("mary o'neil-smith") == "Mary O'Neil-Smith"
        assert scoreboards.display_name('Benicio de Corral') == 'Benicio de Corral'  # already cased: left as typed
        assert scoreboards.prize_text("Prize: Grandpa Joe's $25 Gift Card per grade level. Uses 120-minute daily cap.") == "Grandpa Joe's $25 Gift Card"
        assert scoreboards.leaders({'a': 1, 'b': 1}) == {'a', 'b'}
        assert scoreboards.leaders({'a': 1, 'b': None}) == set()

    def test_half_day_kindergarten_classes_labeled_separately(self):
        """Class prizes are per class: a teacher's AM and PM classes compete separately"""
        teachers = {'smith'}
        assert scoreboards.class_label({'teacher_name': 'smith', 'class_name': 'smith am'}, teachers) == 'Smith AM'
        assert scoreboards.class_label({'teacher_name': 'smith', 'class_name': 'smith pm'}, teachers) == 'Smith PM'
        assert scoreboards.class_label({'teacher_name': 'jones', 'class_name': 'jones'}, set()) == 'Jones'
        # A single half-day class still shows its session
        assert scoreboards.class_label({'teacher_name': 'lee', 'class_name': 'lee am'}, set()) == 'Lee AM'
        # Sample-style class names: teacher only, unless the teacher has several classes
        assert scoreboards.class_label({'teacher_name': 'teacher1', 'class_name': 'class1'}, set()) == 'Teacher1'
        assert scoreboards.class_label({'teacher_name': 'teacher1', 'class_name': 'class1'}, {'teacher1'}) == 'Teacher1 (class1)'


class TestCumulativeSnapshots:
    """Reader_Cumulative_History: one saved copy of the cumulative upload per contest day"""

    CSV = ('Reader Name,Teacher,Raised,Sponsors,Minutes\n'
           'student11,teacher1,15,2,210\n'
           'student21,teacher2,25,3,60\n')

    def upload(self, db, csv_text, snapshot_date=None):
        file = io.BytesIO(csv_text.encode('utf-8'))
        file.filename = 'cumulative.csv'
        return db.upload_cumulative_stats(file, True, snapshot_date)

    def test_backfill_when_table_first_created(self, tmp_path):
        path = tmp_path / 'old_year.db'
        shutil.copy(SAMPLE_DB_PATH, path)
        with sqlite3.connect(path) as conn:
            conn.execute('DROP TABLE IF EXISTS Reader_Cumulative_History')
        db = ReadathonDB(str(path))  # opening an older database adds the table
        assert db.get_snapshot_dates() == [DAY2]
        assert db.execute_query('SELECT COUNT(*) as n FROM Reader_Cumulative_History')[0]['n'] == 7
        db.close()
        assert ReadathonDB(str(path)).get_snapshot_dates() == [DAY2]  # not backfilled twice

    def test_upload_defaults_to_latest_contest_day(self, db_copy):
        result = self.upload(db_copy, self.CSV)
        assert result['success'] and result['snapshot_date'] == DAY2
        assert result['snapshot_replaced'] is True  # replaced the backfilled copy

    def test_reupload_same_day_replaces_whole_snapshot(self, db_copy):
        self.upload(db_copy, self.CSV, DAY1)
        result = self.upload(db_copy, 'Reader Name,Teacher,Raised,Sponsors,Minutes\nstudent11,teacher1,99,9,300\n', DAY1)
        assert result['snapshot_replaced'] is True
        rows = db_copy.execute_query('SELECT student_name, donation_amount FROM Reader_Cumulative_History WHERE snapshot_date = ?', (DAY1,))
        assert rows == [{'student_name': 'student11', 'donation_amount': 99.0}]  # student21 doesn't linger
        assert len(db_copy.execute_query('SELECT * FROM Reader_Cumulative_History WHERE snapshot_date = ?', (DAY2,))) == 7

    def test_snapshot_date_in_audit_trail(self, db_copy):
        self.upload(db_copy, self.CSV, DAY1)
        audit = db_copy.execute_query("SELECT audit_details FROM Upload_History WHERE file_type = 'cumulative' ORDER BY upload_id DESC LIMIT 1")[0]
        assert f'"snapshot_date": "{DAY1}"' in audit['audit_details']

    def test_delete_cumulative_clears_snapshots(self, db_copy):
        assert db_copy.delete_cumulative_data()['success']
        assert db_copy.get_snapshot_dates() == []

    def test_fundraising_by_day_report(self, db_copy):
        self.upload(db_copy, self.CSV, DAY1)
        data = ReportGenerator(db_copy).q25_fundraising_by_day()['data']
        assert [r['snapshot_date'] for r in data] == [DAY1, DAY2]
        assert data[0]['donations_added'] is None
        assert data[1]['donations_added'] == round(280.0 - 40.0, 2)

    def test_upload_route_asks_to_confirm_date_without_minutes(self, client):
        """A snapshot date with no daily minutes needs confirmation (nothing is written)"""
        response = client.post('/api/upload_cumulative', data={
            'cumulative_file': (io.BytesIO(self.CSV.encode()), 'cumulative.csv'),
            'snapshot_date': '2025-10-20'}, content_type='multipart/form-data')
        assert response.status_code == 400
        assert response.get_json()['needs_snapshot_confirmation'] is True

    def test_upload_route_rejects_bad_date(self, client):
        response = client.post('/api/upload_cumulative', data={
            'cumulative_file': (io.BytesIO(self.CSV.encode()), 'cumulative.csv'),
            'snapshot_date': '10/20/2025'}, content_type='multipart/form-data')
        assert response.status_code == 400
        assert 'Invalid snapshot date' in response.get_json()['error']

    def test_upload_page_prefills_latest_contest_day(self, client):
        assert f'value="{DAY2}"' in client.get('/upload').data.decode('utf-8')

    def test_table_listed_everywhere(self, client, sample_db):
        assert 'Reader_Cumulative_History' in sample_db.get_table_counts()
        assert 'Reader_Cumulative_History' in sample_db.export_all_tables()
        assert client.get('/api/table_counts').get_json()['counts']['Reader_Cumulative_History'] == 7
        assert client.get('/api/table/reader_cumulative_history').get_json()['row_count'] == 7
        assert sample_db.get_table_metadata('reader_cumulative_history')['row_count'] == 7


class TestSettings:
    def test_settings_api(self, client):
        original = registry.get_settings()
        try:
            response = client.post('/api/settings', json={'school_name': 'Test School', 'contest_days': 12})
            assert response.get_json()['success']
            assert client.get('/api/settings').get_json()['settings'] == {'school_name': 'Test School', 'contest_days': '12'}
            html = client.get('/scoreboards/daily').data.decode('utf-8')
            assert 'Test School Read-a-Thon' in html and 'Day 2 of 12' in html
        finally:
            client.post('/api/settings', json=original)

    @pytest.mark.parametrize('days', [0, 61, 'ten'])
    def test_contest_days_validated(self, client, days):
        response = client.post('/api/settings', json={'school_name': '', 'contest_days': days})
        assert response.status_code == 400
