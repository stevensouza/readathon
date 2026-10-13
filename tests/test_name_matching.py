#!/usr/bin/env python3
"""
Roster name matching: parent-typed reader names in read-a-thon.com uploads (name_matching.py,
Name_Alias table, Upload page "Match names to the roster" panel).

Uses the fictitious csv/sample_names_* files: a 16-student roster plus daily and cumulative
uploads with first-name-only, nickname, typo, ambiguous, sibling and case/spacing names.
"""

import io
import os

import pytest
from werkzeug.datastructures import FileStorage

import app as app_module
from app import app
from database import DatabaseRegistry, ReadathonDB
from name_matching import NameMatcher, first_names_related, name_key, teacher_key

TEST_DB_NAME = 'test_readathon_names.db'
TEST_DB_PATH = f'db/{TEST_DB_NAME}'
DAY1, DAY2 = '2026-10-10', '2026-10-11'
DAY1_CSV = 'csv/sample_names_day1_2026-10-10.csv'
DAY2_CSV = 'csv/sample_names_day2_2026-10-11.csv'
CUMULATIVE_CSV = 'csv/sample_names_cumulative.csv'

ROSTER = [
    {'student_name': 'Maya Patel', 'teacher_name': 'Ms. Alvarez', 'class_name': 'Alvarez-K'},
    {'student_name': 'Jack Turner', 'teacher_name': 'Ms. Alvarez', 'class_name': 'Alvarez-K'},
    {'student_name': 'Noah Wilson', 'teacher_name': 'Mr. Kim', 'class_name': 'Kim-1'},
    {'student_name': 'Samuel Lee', 'teacher_name': 'Mr. Kim', 'class_name': 'Kim-1'},
    {'student_name': 'Theodore Lambert', 'teacher_name': 'Mr. Kim', 'class_name': 'Kim-1'},
    {'student_name': 'Olivia Chen', 'teacher_name': 'Mrs. Hart', 'class_name': 'Hart-2'},
    {'student_name': 'Olivia Grant', 'teacher_name': 'Mrs. Hart', 'class_name': 'Hart-2'},
    {'student_name': 'Ethan Brookes', 'teacher_name': 'Mrs. Hart', 'class_name': 'Hart-2'},
    {'student_name': 'Noah Martinez', 'teacher_name': 'Ms. Lopez', 'class_name': 'Lopez-2'},
    {'student_name': 'Clara Rose Wells', 'teacher_name': 'Ms. Lopez', 'class_name': 'Lopez-2'},
]


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def upload_file(path):
    return FileStorage(io.BytesIO(read(path).encode('utf-8')), filename=os.path.basename(path))


@pytest.fixture
def names_db():
    """A fresh database with the sample_names roster (no uploads yet)"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = ReadathonDB(TEST_DB_PATH)
    db.load_class_info_data(read('csv/sample_names_class_info.csv'))
    db.load_grade_rules_data(read('csv/sample_names_grade_rules.csv'))
    db.load_roster_data(read('csv/sample_names_roster.csv'))
    yield db
    db.close()
    os.remove(TEST_DB_PATH)


@pytest.fixture
def names_db_id(names_db):
    """names_db registered, so the routes can use it"""
    registry = DatabaseRegistry()
    db_id = registry.register_database(TEST_DB_NAME, 'Test Name Matching', 2099)
    registry.close()
    yield db_id
    cached = app_module.database_cache.pop(db_id, None)
    if cached:
        cached.close()
    registry = DatabaseRegistry()
    registry.delete_database(db_id)
    registry.close()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def use_db(client, db_id):
    with client.session_transaction() as sess:
        sess['active_database_id'] = db_id


def total(db, sql):
    return db.execute_query(sql)[0]['n'] or 0


def minutes_all(db):
    return total(db, 'SELECT SUM(minutes_read) as n FROM Daily_Logs')


def minutes_on_roster(db):
    return total(db, 'SELECT SUM(dl.minutes_read) as n FROM Roster r JOIN Daily_Logs dl ON dl.student_name = r.student_name')


def minutes(db, date, student):
    rows = db.execute_query('SELECT minutes_read FROM Daily_Logs WHERE log_date = ? AND student_name = ?', (date, student))
    return rows[0]['minutes_read'] if rows else None


def save_suggestions(db, overrides=None):
    """Check both daily files and save every suggestion (overrides: uploaded name -> roster name or None)"""
    overrides = overrides or {}
    check = db.check_upload_names('daily', [read(DAY1_CSV), read(DAY2_CSV)])
    corrections = [{'uploaded_name': u['uploaded_name'], 'teacher_name': u['teacher_name'],
                    'student_name': overrides.get(u['uploaded_name'], u['suggestion'])} for u in check['unmatched']]
    return db.save_name_aliases(corrections)


class TestNameKeys:
    def test_name_key_ignores_case_spacing_and_punctuation(self):
        assert name_key('  jack   TURNER ') == name_key('Jack Turner') == 'jack turner'
        assert name_key("Liam O'Brien") == "liam o'brien"

    def test_name_key_ignores_accents_and_curly_apostrophes(self):
        assert name_key('Liam O\u2019Brien') == name_key("Liam O'Brien")
        assert name_key('Zoë Adams') == name_key('Zoe Adams') == 'zoe adams'
        assert NameMatcher(ROSTER).resolve('Clára Rose Wells', 'Ms. Lopez') == ('Clara Rose Wells', 'normalized')

    @pytest.mark.parametrize('teacher', ['Mrs. Delgado', 'delgado', 'Delgado', 'Ms Delgado'])
    def test_teacher_key_drops_titles_and_case(self, teacher):
        assert teacher_key(teacher) == 'delgado'

    @pytest.mark.parametrize('typed,formal,related', [
        ('ben', 'benjamin', True), ('abby', 'abigail', True), ('teddy', 'theodore', True), ('huck', 'henry', True),
        ('liza', 'eliza', True), ('ellie', 'eleanor', True), ('hudson', 'nicholas', False), ('sam', 'olivia', False),
    ])
    def test_first_names_related(self, typed, formal, related):
        assert first_names_related(typed, formal) is related


class TestResolve:
    def test_exact_alias_skip_normalized_and_unmatched(self):
        matcher = NameMatcher(ROSTER, [
            {'name_key': 'maya', 'teacher_key': 'alvarez', 'student_name': 'Maya Patel'},
            {'name_key': 'ruby patel', 'teacher_key': 'alvarez', 'student_name': None},
        ])
        assert matcher.resolve('Maya Patel', 'Ms. Alvarez') == ('Maya Patel', 'exact')
        assert matcher.resolve('MAYA', 'alvarez') == ('Maya Patel', 'alias')
        assert matcher.resolve('Ruby Patel', 'Ms. Alvarez') == (None, 'skip')
        assert matcher.resolve('jack  turner', 'Ms. Alvarez') == ('Jack Turner', 'normalized')
        assert matcher.resolve('Maya', 'Mr. Kim') == ('Maya', 'unmatched')  # correction is for another teacher

    def test_same_typed_name_resolves_per_teacher(self):
        matcher = NameMatcher(ROSTER, [
            {'name_key': 'noah', 'teacher_key': 'kim', 'student_name': 'Noah Wilson'},
            {'name_key': 'noah', 'teacher_key': 'lopez', 'student_name': 'Noah Martinez'},
        ])
        assert matcher.resolve('Noah', 'Mr. Kim')[0] == 'Noah Wilson'
        assert matcher.resolve('Noah', 'Ms. Lopez')[0] == 'Noah Martinez'
        assert matcher.resolve_any_teacher('Noah') == ('Noah', 'ambiguous')

    def test_old_row_without_teacher_is_not_moved_when_another_class_has_no_correction(self):
        matcher = NameMatcher(ROSTER, [{'name_key': 'noah', 'teacher_key': 'kim', 'student_name': 'Noah Wilson'}])
        assert matcher.resolve_any_teacher('Noah') == ('Noah Wilson', 'alias')
        assert matcher.resolve_any_teacher('Noah', ['Mr. Kim']) == ('Noah Wilson', 'alias')
        assert matcher.resolve_any_teacher('Noah', ['Mr. Kim', 'Ms. Lopez']) == ('Noah', 'ambiguous')

    def test_correction_to_a_student_no_longer_on_the_roster_is_ignored(self):
        matcher = NameMatcher(ROSTER, [{'name_key': 'maya', 'teacher_key': 'alvarez', 'student_name': 'Maya Old'}])
        assert matcher.resolve('Maya', 'Ms. Alvarez') == ('Maya', 'unmatched')


class TestSuggest:
    @pytest.mark.parametrize('typed,teacher,expected', [
        ('Noah', 'Mr. Kim', 'Noah Wilson'),                     # first name only, one Noah in the class
        ('Teddy Lambert', 'Mr. Kim', 'Theodore Lambert'),       # known nickname + same last name
        ('Ethan Brooks', 'Mrs. Hart', 'Ethan Brookes'),         # typo
        ('Clara Wells', 'Ms. Lopez', 'Clara Rose Wells'),  # middle name left out
    ])
    def test_strong_single_match_is_pre_checked(self, typed, teacher, expected):
        result = NameMatcher(ROSTER).suggest(typed, teacher)
        assert result['suggestion'] == expected and result['confident']

    @pytest.mark.parametrize('typed,expected', [
        ('Sam Lee', 'Samuel Lee'),     # shared letters only: a nickname, or a sibling?
        ('Sa Lee', 'Samuel Lee'),
        ('Theo Lambert', 'Theodore Lambert'),
    ])
    def test_shared_letters_are_only_a_possible_match(self, typed, expected):
        result = NameMatcher(ROSTER).suggest(typed, 'Mr. Kim')
        assert result['suggestion'] == expected and not result['confident']
        assert 'starts the same' in result['candidates'][0]['reason']

    def test_two_strong_matches_in_class_are_not_pre_checked(self):
        result = NameMatcher(ROSTER).suggest('Olivia', 'Mrs. Hart')
        assert {c['student_name'] for c in result['candidates'][:2]} == {'Olivia Chen', 'Olivia Grant'}
        assert not result['confident']

    def test_student_with_own_data_is_not_pre_checked(self):
        result = NameMatcher(ROSTER).suggest('Noah', 'Mr. Kim', has_data={'Noah Wilson'})
        assert result['suggestion'] == 'Noah Wilson' and not result['confident']

    def test_same_last_name_only_is_not_pre_checked(self):
        result = NameMatcher(ROSTER).suggest('Hudson Brookes', 'Mrs. Hart')
        assert result['suggestion'] == 'Ethan Brookes' and not result['confident']
        assert 'sibling' in result['candidates'][0]['reason']

    def test_other_class_is_suggested_but_not_pre_checked(self):
        result = NameMatcher(ROSTER).suggest('Sam Lee', 'Mrs. Hart')
        assert result['suggestion'] == 'Samuel Lee' and not result['confident']
        assert "Mr. Kim's class" in result['candidates'][0]['reason']

    def test_sibling_is_suggested_but_not_pre_checked(self):
        result = NameMatcher(ROSTER).suggest('Ruby Patel', 'Ms. Alvarez')
        assert result['suggestion'] == 'Maya Patel' and not result['confident']

    def test_no_suggestion(self):
        result = NameMatcher(ROSTER).suggest('Zed Quinn', 'Ms. Alvarez')
        assert result == {'candidates': [], 'suggestion': None, 'confident': False}


class TestMatchPanelOrder:
    def test_strong_matches_first_then_possible_then_no_suggestion(self, names_db):
        check = names_db.check_upload_names('daily', [read(DAY1_CSV), read(DAY2_CSV)])
        groups = [0 if u['confident'] else 1 if u['suggestion'] else 2 for u in check['unmatched']]
        assert groups == sorted(groups) and groups[0] == 0 and groups[-1] == 2
        strong = [u['uploaded_name'] for u in check['unmatched'] if u['confident']]
        assert strong == ['Ethan Brooks', 'Noah']  # by teacher: Mrs. Hart, Mr. Kim
        assert check['matched_count'] == 13

    def test_two_typed_names_strongly_matching_one_student_are_not_pre_checked(self, names_db):
        csv_text = ('ClassID,Teacher,ReaderID,ReaderName,Minutes\n'
                    '3,Mrs. Hart,1,Ethan Brooks,30\n3,Mrs. Hart,2,Ethan Brokes,20\n')
        check = names_db.check_upload_names('daily', [csv_text])
        assert [u['suggestion'] for u in check['unmatched']] == ['Ethan Brookes', 'Ethan Brookes']
        assert not any(u['confident'] for u in check['unmatched'])
        assert 'another typed name' in check['unmatched'][0]['candidates'][0]['reason']


class TestUploads:
    def test_unmatched_names_are_left_out_of_roster_totals_today(self, names_db):
        result = names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        unmatched = [w for w in result['warnings'] if w.startswith('Student not found in roster')]
        assert len(unmatched) == 4  # Maya, Noah, Sam Lee, Ethan Brooks - "jack  turner" only differs in case/spacing
        assert any('jack  turner (Ms. Alvarez) → Jack Turner' in i for i in result['info'])
        assert minutes_on_roster(names_db) < minutes_all(names_db)

    def test_check_lists_unmatched_names_with_suggestions(self, names_db):
        check = names_db.check_upload_names('daily', [read(DAY1_CSV), read(DAY2_CSV)])
        found = {u['uploaded_name']: u for u in check['unmatched']}
        assert set(found) == {'Maya', 'Noah', 'Sam Lee', 'Ethan Brooks', 'Olivia', 'Ruby Patel'}
        assert found['Noah']['confident'] and found['Noah']['suggestion'] == 'Noah Wilson'
        assert found['Noah']['minutes'] == 75 and found['Noah']['rows'] == 2
        assert not found['Maya']['confident']  # Maya Patel has her own row on day 2
        assert found['Ruby Patel']['suggestion'] is None
        assert 'Maya Patel' in found['Maya']['class_students']
        assert [c['how'] for c in check['corrected']] == ['normalized']
        assert len(check['all_students']) == 16
        assert names_db.get_name_aliases() == []  # checking saves nothing

    def test_saved_corrections_fix_this_and_later_uploads(self, names_db):
        assert save_suggestions(names_db, {'Olivia': 'Olivia Grant', 'Ruby Patel': None})['success']
        day1 = names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        day2 = names_db.upload_daily_data(DAY2, upload_file(DAY2_CSV))
        assert not [w for w in day1['warnings'] + day2['warnings'] if 'not found in roster' in w]
        assert any(i.startswith('Corrected 4 names using saved name corrections') for i in day2['info'])
        assert any('Left out 1 name saved as not roster students: Ruby Patel (Ms. Alvarez)' == i for i in day2['info'])
        assert minutes(names_db, DAY2, 'Maya Patel') == 35  # "Maya" 20 + "Maya Patel" 15
        assert minutes(names_db, DAY2, 'Ruby Patel') is None
        assert minutes_on_roster(names_db) == minutes_all(names_db) == 1090

        cumulative = names_db.upload_cumulative_stats(upload_file(CUMULATIVE_CSV), snapshot_date=DAY2)
        assert cumulative['students_unmatched'] == 0
        raised = total(names_db, 'SELECT SUM(donation_amount) as n FROM Reader_Cumulative')
        raised_on_roster = total(names_db, 'SELECT SUM(rc.donation_amount) as n FROM Roster r '
                                           'JOIN Reader_Cumulative rc ON rc.student_name = r.student_name')
        assert raised == raised_on_roster == 650  # $665 in the file minus the $15 sibling page
        teams = names_db.execute_query('SELECT DISTINCT team_name FROM Reader_Cumulative ORDER BY 1')
        assert [t['team_name'] for t in teams] == ['Dragons', 'Phoenix']

    def test_saving_corrections_moves_rows_uploaded_earlier(self, names_db):
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        names_db.upload_cumulative_stats(upload_file(CUMULATIVE_CSV), snapshot_date=DAY1)
        result = save_suggestions(names_db, {'Olivia': 'Olivia Grant', 'Ruby Patel': None})
        assert result['success'] and result['rows_moved'] > 0
        for table in ['Daily_Logs', 'Reader_Cumulative', 'Reader_Cumulative_History']:
            assert total(names_db, f'SELECT COUNT(*) as n FROM {table} '
                                   f'WHERE student_name NOT IN (SELECT student_name FROM Roster)') == 0
        assert minutes(names_db, DAY1, 'Noah Wilson') == 35
        history = names_db.execute_query("SELECT donation_amount, team_name FROM Reader_Cumulative_History "
                                         "WHERE snapshot_date = ? AND student_name = 'Maya Patel'", (DAY1,))
        assert history == [{'donation_amount': 35.0, 'team_name': 'Phoenix'}]  # "Maya" $25 + "Maya Patel" $10

    def test_same_typed_name_in_two_classes_stays_two_students(self, names_db):
        names_db.save_name_aliases([
            {'uploaded_name': 'Noah', 'teacher_name': 'Mr. Kim', 'student_name': 'Noah Wilson'},
            {'uploaded_name': 'Noah', 'teacher_name': 'Ms. Lopez', 'student_name': 'Noah Martinez'}])
        csv_text = 'ClassID,Teacher,ReaderID,ReaderName,Minutes\n1,Mr. Kim,1,Noah,30\n2,Ms. Lopez,2,Noah,50\n'
        names_db.upload_daily_data(DAY1, FileStorage(io.BytesIO(csv_text.encode()), filename='daily.csv'))
        assert minutes(names_db, DAY1, 'Noah Wilson') == 30
        assert minutes(names_db, DAY1, 'Noah Martinez') == 50

    def test_reupload_replaces_rows_saved_under_unmatched_names(self, names_db):
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        csv_text = read(DAY1_CSV).replace('"Ethan Brooks"', '"Ethan Brookes"')
        assert minutes(names_db, DAY1, 'Ethan Brooks (Mrs. Hart)') == 60  # unmatched: saved with its teacher
        names_db.upload_daily_data(DAY1, FileStorage(io.BytesIO(csv_text.encode()), filename='daily.csv'))
        assert minutes(names_db, DAY1, 'Ethan Brooks (Mrs. Hart)') is None
        assert minutes(names_db, DAY1, 'Ethan Brookes') == 60

    def test_placeholder_duplicate_rows_do_not_warn(self, names_db):
        csv_text = ('Reader Name,Teacher,Email,Raised,Sponsors,Sessions,PageCreated,Minutes\n'
                    'Maya Patel,Ms. Alvarez,a@example.com,25,2,2,Yes,50\n'
                    'Maya Patel,Ms. Alvarez,b@example.com,,0,0,No,0\n'
                    'Noah Wilson,Mr. Kim,c@example.com,10,1,1,Yes,20\n'
                    'Noah Wilson,Mr. Kim,d@example.com,5,1,1,Yes,10\n')
        result = names_db.upload_cumulative_stats(FileStorage(io.BytesIO(csv_text.encode()), filename='c.csv'),
                                                  snapshot_date=DAY1)
        duplicates = [w for w in result['warnings'] if w.startswith('Duplicate rows')]
        assert len(duplicates) == 1 and 'Noah Wilson' in duplicates[0]

    def test_names_not_on_roster_after_the_fact(self, names_db):
        assert names_db.get_unmatched_names()['unmatched'] == []
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        names_db.upload_cumulative_stats(upload_file(CUMULATIVE_CSV), snapshot_date=DAY1)
        result = names_db.get_unmatched_names()
        found = {u['uploaded_name']: u for u in result['unmatched']}
        assert set(found) == {'Maya', 'Noah', 'Sam Lee', 'Ethan Brooks', 'Olivia', 'Ruby Patel'}
        assert found['Noah']['teacher_name'] == 'Mr. Kim'  # from the cumulative row (Daily_Logs has no teacher)
        assert found['Noah']['suggestion'] == 'Noah Wilson' and found['Noah']['confident']
        assert (found['Noah']['minutes'], found['Noah']['days'], found['Noah']['raised']) == (35, 1, 50.0)
        assert result['total_minutes'] == 30 + 35 + 45 + 60  # day 1: Maya, Noah, Sam Lee, Ethan Brooks
        assert result['total_raised'] == 25 + 50 + 20 + 5 + 70 + 15

        names_db.save_name_aliases([{'uploaded_name': u['uploaded_name'], 'teacher_name': u['teacher_name'],
                                     'student_name': u['suggestion']} for u in result['unmatched'] if u['confident']])
        left = {u['uploaded_name'] for u in names_db.get_unmatched_names()['unmatched']}
        assert left == {u['uploaded_name'] for u in result['unmatched'] if not u['confident']}

    def test_unmatched_same_name_in_two_classes_is_kept_apart(self, names_db):
        csv_text = 'ClassID,Teacher,ReaderID,ReaderName,Minutes\n1,Mr. Kim,1,Noah,30\n2,Ms. Lopez,2,Noah,50\n'
        names_db.upload_daily_data(DAY1, FileStorage(io.BytesIO(csv_text.encode()), filename='daily.csv'))
        assert minutes(names_db, DAY1, 'Noah (Mr. Kim)') == 30 and minutes(names_db, DAY1, 'Noah (Ms. Lopez)') == 50
        listed = {(u['uploaded_name'], u['teacher_name']): u for u in names_db.get_unmatched_names()['unmatched']}
        assert set(listed) == {('Noah', 'Mr. Kim'), ('Noah', 'Ms. Lopez')}
        assert listed[('Noah', 'Ms. Lopez')]['suggestion'] == 'Noah Martinez'

        names_db.save_name_aliases([{'uploaded_name': 'Noah', 'teacher_name': 'Ms. Lopez', 'student_name': 'Noah Martinez'}])
        assert minutes(names_db, DAY1, 'Noah Martinez') == 50
        assert minutes(names_db, DAY1, 'Noah (Mr. Kim)') == 30  # the other class's Noah isn't touched

    def test_daily_upload_replaces_the_whole_date(self, names_db):
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        csv_text = 'ClassID,Teacher,ReaderID,ReaderName,Minutes\n1,Ms. Alvarez,1,Maya Patel,10\n'
        names_db.upload_daily_data(DAY1, FileStorage(io.BytesIO(csv_text.encode()), filename='daily.csv'))
        assert names_db.execute_query('SELECT student_name, minutes_read FROM Daily_Logs WHERE log_date = ?', (DAY1,)) == [
            {'student_name': 'Maya Patel', 'minutes_read': 10}]

    def test_changed_correction_applies_when_the_day_is_uploaded_again(self, names_db):
        correction = {'uploaded_name': 'Olivia', 'teacher_name': 'Mrs. Hart', 'student_name': 'Olivia Chen'}
        names_db.save_name_aliases([correction])
        names_db.upload_daily_data(DAY2, upload_file(DAY2_CSV))
        assert minutes(names_db, DAY2, 'Olivia Chen') == 45
        names_db.save_name_aliases([{**correction, 'student_name': 'Olivia Grant'}])
        assert len(names_db.get_name_aliases()) == 1
        assert minutes(names_db, DAY2, 'Olivia Chen') == 45  # already moved: stays until the day is uploaded again
        names_db.upload_daily_data(DAY2, upload_file(DAY2_CSV))
        assert minutes(names_db, DAY2, 'Olivia Chen') is None
        assert minutes(names_db, DAY2, 'Olivia Grant') == 45

    def test_name_added_to_the_roster_later_is_moved_when_matched(self, names_db):
        csv_text = 'ClassID,Teacher,ReaderID,ReaderName,Minutes\n1,Ms. Alvarez,1,Zed Quinn,40\n'
        names_db.upload_daily_data(DAY1, FileStorage(io.BytesIO(csv_text.encode()), filename='daily.csv'))
        assert minutes(names_db, DAY1, 'Zed Quinn (Ms. Alvarez)') == 40
        names_db.get_connection().execute(
            "INSERT INTO Roster (student_name, class_name, home_room, teacher_name, grade_level, team_name) "
            "VALUES ('Zed Quinn', 'Alvarez-K', '101', 'Ms. Alvarez', 'K', 'Phoenix')")
        result = names_db.save_name_aliases([{'uploaded_name': 'Zed Quinn', 'teacher_name': 'Ms. Alvarez',
                                              'student_name': 'Zed Quinn'}])
        assert result['success'] and result['rows_moved'] == 1
        assert minutes(names_db, DAY1, 'Zed Quinn') == 40

    def test_empty_daily_file_keeps_the_day(self, names_db):
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        before = minutes_all(names_db)
        empty = FileStorage(io.BytesIO(b'ClassID,Teacher,ReaderID,ReaderName,Minutes\n'), filename='daily.csv')
        result = names_db.upload_daily_data(DAY1, empty)
        assert not result['success'] and 'No reader rows' in result['errors'][0]
        assert minutes_all(names_db) == before

    def test_cumulative_file_with_no_readable_rows_keeps_the_money(self, names_db):
        names_db.upload_cumulative_stats(upload_file(CUMULATIVE_CSV), snapshot_date=DAY1)
        before = total(names_db, 'SELECT SUM(donation_amount) as n FROM Reader_Cumulative')
        header_only = FileStorage(io.BytesIO(b'Reader Name,Teacher,Raised,Sponsors,Minutes\n'), filename='c.csv')
        result = names_db.upload_cumulative_stats(header_only, snapshot_date=DAY1)
        assert not result['success'] and 'No reader rows' in result['errors'][0]
        assert total(names_db, 'SELECT SUM(donation_amount) as n FROM Reader_Cumulative') == before > 0

    def test_every_accepted_column_name_is_read(self, names_db):
        csv_text = ('Student Name,Teacher Name,Donation Amount,Sponsor Count,Cumulative Minutes\n'
                    'Maya Patel,Ms. Alvarez,12.5,2,90\n'
                    'Noah Wilson,Mr. Kim\n')  # short row
        result = names_db.upload_cumulative_stats(FileStorage(io.BytesIO(csv_text.encode()), filename='c.csv'),
                                                  snapshot_date=DAY1)
        assert result['success'], result
        row = names_db.execute_query("SELECT donation_amount, sponsors, cumulative_minutes FROM Reader_Cumulative "
                                     "WHERE student_name = 'Maya Patel'")
        assert row == [{'donation_amount': 12.5, 'sponsors': 2, 'cumulative_minutes': 90}]
        daily = 'ReaderName,Teacher,Minutes Read\nMaya Patel,Ms. Alvarez,30\n'
        assert names_db.upload_daily_data(DAY1, FileStorage(io.BytesIO(daily.encode()), filename='d.csv'))['success']
        assert minutes(names_db, DAY1, 'Maya Patel') == 30

    def test_bad_corrections_are_rejected(self, names_db):
        result = names_db.save_name_aliases([{'uploaded_name': 'Maya', 'teacher_name': 'Ms. Alvarez',
                                              'student_name': 'Not On Roster'}])
        assert not result['success'] and 'Not a roster student' in result['error']
        assert not names_db.save_name_aliases([{'uploaded_name': ' ', 'student_name': None}])['success']

    def test_delete_correction(self, names_db):
        save_suggestions(names_db)
        alias = names_db.get_name_aliases()[0]
        assert names_db.delete_name_alias(alias['name_key'], alias['teacher_key'])['success']
        assert not names_db.delete_name_alias(alias['name_key'], alias['teacher_key'])['success']


class TestRoutes:
    def test_check_and_save_routes(self, client, names_db_id, make_editable):
        make_editable(names_db_id)
        use_db(client, names_db_id)
        response = client.post('/api/check_upload_names', data={
            'upload_type': 'daily', 'files': [(io.BytesIO(read(DAY1_CSV).encode()), 'daily_2026-10-10.csv')]},
            content_type='multipart/form-data')
        check = response.get_json()
        assert check['success'] and {u['uploaded_name'] for u in check['unmatched']} == {'Maya', 'Noah', 'Sam Lee', 'Ethan Brooks'}

        corrections = [{'uploaded_name': u['uploaded_name'], 'teacher_name': u['teacher_name'],
                        'student_name': u['suggestion']} for u in check['unmatched']]
        saved = client.post('/api/name_aliases', json={'corrections': corrections}).get_json()
        assert saved['success'] and saved['saved'] == 4

        listed = client.get('/api/name_aliases').get_json()
        aliases = listed['aliases']
        assert {a['student_name'] for a in aliases} == {'Maya Patel', 'Noah Wilson', 'Samuel Lee', 'Ethan Brookes'}
        assert len(listed['all_students']) == 16
        noah = next(a for a in aliases if a['uploaded_name'] == 'Noah')
        assert noah['class_students'] == ['Ava Johnson', 'Leo Garcia', 'Noah Wilson', 'Samuel Lee']
        assert client.post('/api/name_aliases/delete', json={'name_key': aliases[0]['name_key'],
                                                             'teacher_key': aliases[0]['teacher_key']}).status_code == 200
        assert client.post('/api/name_aliases/delete', json={'name_key': 'nobody', 'teacher_key': ''}).status_code == 404

    def test_unmatched_names_route(self, client, names_db_id, make_editable, names_db):
        use_db(client, names_db_id)
        assert client.get('/api/unmatched_names').get_json()['unmatched'] == []
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        result = client.get('/api/unmatched_names').get_json()
        assert result['success'] and len(result['unmatched']) == 4 and result['total_minutes'] == 170

    def test_upload_page_explains_name_matching(self, client):
        html = client.get('/upload').data.decode('utf-8')
        for text in ['unmatchedNamesAlert', 'Saved Name Corrections', 'Match names to the roster',
                     'Strong match', 'Possible match', 'Accept (box ticked)', 'Each class is separate']:
            assert text in html, text

    def test_route_validation(self, client, names_db_id, make_editable):
        make_editable(names_db_id)
        use_db(client, names_db_id)
        assert client.post('/api/check_upload_names', data={'upload_type': 'weekly'}).status_code == 400
        assert client.post('/api/check_upload_names', data={'upload_type': 'daily'}).status_code == 400
        assert client.post('/api/name_aliases', json={'corrections': []}).status_code == 400
        bad = client.post('/api/name_aliases', json={'corrections': [
            {'uploaded_name': 'Maya', 'teacher_name': 'Ms. Alvarez', 'student_name': 'Nobody'}]})
        assert bad.status_code == 400
        assert client.post('/api/name_aliases', json={'corrections': ['Maya']}).status_code == 400

    def test_saving_refused_on_read_only_database(self, client, names_db_id, make_editable):
        make_editable(-1)
        use_db(client, names_db_id)
        correction = {'uploaded_name': 'Maya', 'teacher_name': 'Ms. Alvarez', 'student_name': 'Maya Patel'}
        assert client.post('/api/name_aliases', json={'corrections': [correction]}).status_code == 403
        assert client.post('/api/name_aliases/delete', json={'name_key': 'maya', 'teacher_key': 'alvarez'}).status_code == 403

    def test_table_listed_everywhere(self, client, names_db_id):
        use_db(client, names_db_id)
        db = app_module.get_database(names_db_id)
        assert 'Name_Alias' in db.get_table_counts()
        assert 'Name_Alias' in db.export_all_tables()
        assert db.get_table_metadata('name_alias')['row_count'] == 0
        assert client.get('/api/table_counts').get_json()['counts']['Name_Alias'] == 0
        assert client.get('/api/table/name_alias').get_json()['row_count'] == 0
        assert 'name_alias' in {item['id'] for item in app_module.get_unified_items()}


class TestDownloadLinks:
    def test_upload_page_has_download_links(self, client):
        html = client.get('/upload').data.decode('utf-8')
        settings = app_module.registry.get_settings()
        assert 'Open Minutes Report' in html and 'Open Comprehensive Readers Report' in html
        assert f'href="{settings["readers_report_url"]}"' in html
        assert 'date_report/?Date={date}' in settings['minutes_report_url']

    def test_download_links_are_validated(self, client):
        settings = {'school_name': '', 'contest_days': 10, 'drawing_winners_per_grade': 2,
                    'minutes_report_url': 'javascript:alert(1)'}
        response = client.post('/api/settings', json=settings)
        assert response.status_code == 400 and 'Download links' in response.get_json()['error']
