#!/usr/bin/env python3
"""
Uploads and deletes that must not lose data by accident: stale cumulative snapshot dates, deleting a day,
Admin -> Clear Tables. Uses the fictitious csv/sample_names_* database from test_name_matching.py.
"""

import io
import re

from test_name_matching import (  # noqa: F401 - pytest fixtures
    CUMULATIVE_CSV, DAY1, DAY1_CSV, DAY2, DAY2_CSV, client, names_db, names_db_id, read, upload_file, use_db)

CLEARABLE_TABLES = ['Upload_History', 'Reader_Cumulative', 'Reader_Cumulative_History', 'Daily_Logs',
                    'Team_Color_Bonus', 'Drawing_Winners', 'Name_Alias']


def count(db, table):
    return db.execute_query(f'SELECT COUNT(*) as n FROM {table}')[0]['n']


class TestDeleteDay:
    def test_delete_day_removes_that_days_drawing_winners(self, names_db):
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        names_db.upload_daily_data(DAY2, upload_file(DAY2_CSV))
        conn = names_db.get_connection()
        for day in (DAY1, DAY2):
            conn.execute("INSERT INTO Drawing_Winners (log_date, grade_level, student_name, class_name, drawing_number, "
                         "saved_timestamp) VALUES (?, 'K', 'Maya Patel', 'Alvarez-K', 1, 'now')", (day,))
        conn.commit()
        result = names_db.delete_day_data(DAY1)
        assert result['success'] and result['drawing_winners_deleted'] == 1
        assert [r['log_date'] for r in names_db.execute_query('SELECT log_date FROM Drawing_Winners')] == [DAY2]


class TestSnapshotDate:
    def test_cumulative_upload_for_an_earlier_day_asks_first(self, client, names_db_id, make_editable, names_db):
        make_editable(names_db_id)
        use_db(client, names_db_id)
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        names_db.upload_daily_data(DAY2, upload_file(DAY2_CSV))

        def post(**extra):
            return client.post('/api/upload_cumulative', data={
                'cumulative_file': (io.BytesIO(read(CUMULATIVE_CSV).encode()), 'cumulative.csv'), **extra},
                content_type='multipart/form-data')

        stale = post(snapshot_date=DAY1)
        assert stale.status_code == 400 and stale.get_json()['needs_snapshot_confirmation']
        assert f'through {DAY2}' in stale.get_json()['error']
        assert count(names_db, 'Reader_Cumulative') == 0
        assert post(snapshot_date=DAY1, snapshot_confirmed='true').get_json()['success']
        assert post(snapshot_date=DAY2).get_json()['success']

    def test_daily_upload_moves_the_snapshot_date_forward(self, client):
        html = client.get('/upload').data.decode('utf-8')
        assert 'moveSnapshotDateForward(results.filter(r => r.success)' in html


class TestClearTables:
    def test_every_clearable_table_has_a_count_badge(self, client):
        """clearSelectedTables() finds each table's count as count<Table name without underscores>"""
        html = client.get('/admin').data.decode('utf-8')
        for table in CLEARABLE_TABLES:
            assert f'value="{table}"' in html, table
            assert f'id="count{table.replace("_", "")}"' in html, table
        assert "replace(/_/g, '')" in html and "replace('_', '')" not in html

    def test_select_all_leaves_name_corrections(self, client):
        html = client.get('/admin').data.decode('utf-8')
        assert re.search(r"function selectAllTables\(\) \{\s*const checkboxes = document\.querySelectorAll"
                         r"\('\.table-checkbox:not\(\[value=\"Name_Alias\"\]\)'\)", html)

    def test_clear_every_table(self, client, names_db_id, make_editable, names_db):
        make_editable(names_db_id)
        use_db(client, names_db_id)
        names_db.upload_daily_data(DAY1, upload_file(DAY1_CSV))
        names_db.upload_cumulative_stats(upload_file(CUMULATIVE_CSV), snapshot_date=DAY1)
        result = client.delete('/api/clear_tables', json={'tables': CLEARABLE_TABLES}).get_json()
        assert result['success'] and result['deleted']['Daily_Logs'] > 0
        assert all(count(names_db, table) == 0 for table in CLEARABLE_TABLES)


class TestEscaping:
    def test_table_cells_are_escaped(self, client):
        assert 'function escapeHtml' in client.get('/reports').data.decode('utf-8')
        for page in ('/reports', '/tables', '/workflows', '/admin'):
            html = client.get(page, follow_redirects=True).data.decode('utf-8')
            assert '<td>${row[col] ?? \'\'}</td>' not in html, page
