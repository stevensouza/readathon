"""
Avg. Participation (With Color) must be the same number everywhere:
(student-days read + color points) / (students x days in range) x 100.

Regression for the Grade Level page computing it as an average of per-day percentages, which added a
0% "day" for students with no Daily_Logs rows and skipped dates nobody in a class logged
(sample class1: showed 100.0, correct 50.0). Also covers Q15/Q19 fixes found in the same review.

Sample database: 7 students, 2 contest days (2025-10-10/11), color bonus for class3/class4 on 2025-10-12.
"""

import shutil

import pytest

import app as app_module
from app import app, registry
from database import ReadathonDB, ReportGenerator
from queries import get_grade_aggregations_query, get_grade_level_classes_query, get_school_wide_leaders_query

SAMPLE_DB_PATH = 'db/readathon_sample.db'
DAY1, DAY2 = '2025-10-10', '2025-10-11'

EXPECTED_RATE_SQL = """
    SELECT ci.class_name,
           ROUND((COUNT(DISTINCT CASE WHEN dl.minutes_read > 0 THEN dl.log_date || '-' || dl.student_name END)
                  + COALESCE((SELECT SUM(bonus_participation_points) FROM Team_Color_Bonus tcb
                              WHERE tcb.class_name = ci.class_name AND tcb.event_date <= :as_of), 0)) * 100.0
                 / (ci.total_students * (SELECT COUNT(DISTINCT log_date) FROM Daily_Logs WHERE log_date <= :as_of)), 1)
               as rate
    FROM Class_Info ci
    JOIN Roster r ON ci.class_name = r.class_name
    LEFT JOIN Daily_Logs dl ON r.student_name = dl.student_name AND dl.log_date <= :as_of
    GROUP BY ci.class_name, ci.total_students
"""


def date_where(as_of):
    return f" AND dl.log_date <= '{as_of}'" if as_of else ""


def expected_rates(db, as_of=None):
    return {r['class_name']: r['rate'] for r in db.execute_query(EXPECTED_RATE_SQL, {'as_of': as_of or '9999-12-31'})}


def leaderboard_rates(db, as_of=None):
    return {r['class_name']: r['avg_participation_with_color_pct']
            for r in db.execute_query(get_grade_level_classes_query(date_where(as_of), "", ""))}


@pytest.fixture
def sample_db():
    db = ReadathonDB(SAMPLE_DB_PATH)
    yield db
    db.close()


@pytest.fixture
def db_copy(tmp_path):
    """A writable copy of the sample database"""
    path = tmp_path / 'readathon_copy.db'
    shutil.copy(SAMPLE_DB_PATH, path)
    db = ReadathonDB(str(path))
    yield db
    db.close()


@pytest.fixture
def db_with_non_reader(db_copy):
    """class2 gets a third student with no Daily_Logs rows at all: 4 student-days / (3 x 2 days) = 66.7%"""
    with db_copy.get_connection() as conn:
        conn.execute("INSERT INTO Roster (student_name, class_name, home_room, teacher_name, grade_level, team_name) "
                     "VALUES ('student23', 'class2', 'hr2', 'teacher2', '1', 'team1')")
        conn.execute("UPDATE Class_Info SET total_students = 3 WHERE class_name = 'class2'")
    return db_copy


class TestGradeLevelLeaderboard:

    @pytest.mark.parametrize('as_of', [None, DAY1, DAY2])
    def test_matches_formula(self, sample_db, as_of):
        assert leaderboard_rates(sample_db, as_of) == expected_rates(sample_db, as_of)

    def test_day_nobody_logged_is_not_skipped(self, sample_db):
        """class1's only student read on day 1 only: 1 / (1 x 2) = 50%, not the average of the one logged day"""
        assert leaderboard_rates(sample_db)['class1'] == 50.0

    def test_matches_q6_report(self, sample_db):
        q6 = {r['class_name']: round(r['avg_participation_rate_with_color'], 1)
              for r in ReportGenerator(sample_db).q6_class_participation()['data']}
        assert leaderboard_rates(sample_db) == q6

    @pytest.mark.parametrize('as_of', [DAY1, DAY2])
    def test_matches_prize_bulletin_q12(self, sample_db, as_of):
        rates = leaderboard_rates(sample_db, as_of)
        for row in ReportGenerator(sample_db).q12_best_class_by_grade_simplified(as_of)['data']:
            assert rates[row['class_name']] == round(row['avg_participation_rate_with_color'], 1)

    def test_color_points_respect_date_filter(self, sample_db):
        """The sample's color points are dated after the last contest day: they count only in the full contest"""
        assert leaderboard_rates(sample_db, DAY2)['class3'] == 100.0
        assert leaderboard_rates(sample_db)['class3'] == 125.0

    @pytest.mark.parametrize('as_of', [None, DAY2])
    def test_student_without_logs_adds_no_phantom_day(self, db_with_non_reader, as_of):
        assert leaderboard_rates(db_with_non_reader, as_of)['class2'] == 66.7


class TestGradeCardsAndBanner:

    def test_grade_card_top_participation(self, db_with_non_reader):
        rows = db_with_non_reader.execute_query(get_grade_aggregations_query("", "", ""))
        top = {r['grade_level']: round(r['top_participation_pct'], 1) for r in rows}
        assert top == {'K': 50.0, '1': 66.7, '2': 125.0}

    @pytest.mark.parametrize('grade, expected', [(None, 125.0), ('K', 50.0), ('1', 66.7)])
    def test_banner_leader_value(self, db_with_non_reader, grade, expected):
        rows = db_with_non_reader.execute_query(get_school_wide_leaders_query("", grade=grade))
        assert next(r['value'] for r in rows if r['metric'] == 'participation') == expected

    def test_banner_lists_tied_classes(self):
        """class3 and class4 tie at 125.0%: the Avg. Participation banner names both"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['active_database_id'] = next(db['db_id'] for db in registry.list_databases()
                                                  if db['db_filename'] == 'readathon_sample.db')
            html = client.get('/classes').data.decode('utf-8')
        block = html[html.index('<!-- Avg. Participation (With Color) Leader -->'):html.index('<!-- Goals Met Leader -->')]
        assert 'class3, class4' in block
        assert '125.0%' in block


class TestTeamParticipation:

    @pytest.mark.parametrize('as_of', [None, DAY1])
    def test_matches_q14(self, sample_db, as_of):
        for row in ReportGenerator(sample_db).q14_team_participation(as_of)['data']:
            result = app_module.team_avg_participation(sample_db, row['team_name'], date_where(as_of))
            assert result['team_size'] == row['total_students']
            assert result['color_bonus_points'] == row['color_bonus_points']
            assert round(result['participation_pct'], 2) == row['avg_participation_rate']
            assert round(result['participation_pct_with_color'], 2) == row['avg_participation_rate_with_color']


class TestReportFixes:

    def test_q15_no_goal_getters_without_reading_data(self, db_copy):
        with db_copy.get_connection() as conn:
            conn.execute('DELETE FROM Daily_Logs')
        assert ReportGenerator(db_copy).q15_goal_getters()['data'] == []

    def test_q19_total_hours_from_total_minutes(self, sample_db):
        """team1 155 min (2 h) + team2 90 min (1 h) = 245 min = 4 h, not 2 + 1"""
        total = next(r for r in ReportGenerator(sample_db).q19_team_minutes(DAY1)['data'] if r['team_name'] == 'TOTAL')
        assert total['total_minutes_base'] == 245
        assert total['total_hours_base'] == 4
        assert total['total_hours_with_color'] == total['total_minutes_with_color'] // 60
