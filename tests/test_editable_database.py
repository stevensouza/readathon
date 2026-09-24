"""
Tests for the editable database: exactly one database accepts uploads, deletes and Clear Tables,
independent of the database being viewed. Every other database is read-only (403 + grey nav).

App tests swap in a temporary registry, so the real db/readathon_registry.db is never changed.
"""

import io
import os
import shutil

import pytest

import app as app_module
from app import app
from database import DatabaseRegistry
from test_database_creation import CLASS_INFO_CSV, GRADE_RULES_CSV, ROSTER_CSV

SAMPLE_DB_PATH = 'db/readathon_sample.db'
YEAR_DB_NAME = 'test_readathon_editable.db'
NEW_DB_NAME = 'test_readathon_editable_new.db'

GUARDED_ROUTES = [
    ('post', '/api/upload_daily', {'data': {'log_date': '2025-10-10'}}),
    ('post', '/api/upload_cumulative', {'data': {}}),
    ('post', '/api/upload_team_color_bonus', {'data': {}}),
    ('delete', '/api/delete_day/2025-10-10', {}),
    ('delete', '/api/delete_cumulative', {}),
    ('delete', '/api/delete_upload_history_batch', {'json': {'upload_ids': [1]}}),
    ('delete', '/api/clear_tables', {'json': {'tables': ['Daily_Logs']}}),
]


@pytest.fixture
def temp_registry(tmp_path):
    registry = DatabaseRegistry(str(tmp_path / 'registry.db'))
    yield registry
    registry.close()


@pytest.fixture
def env(tmp_path, monkeypatch, temp_registry):
    """App wired to a temporary registry: the sample DB plus a writable copy registered as a year DB (editable)"""
    shutil.copy(SAMPLE_DB_PATH, f'db/{YEAR_DB_NAME}')
    sample_id = temp_registry.register_database('readathon_sample.db', 'Sample', None)
    year_id = temp_registry.register_database(YEAR_DB_NAME, '2099 Read-a-Thon', 2099)
    temp_registry.set_editable_database(year_id)

    monkeypatch.setattr(app_module, 'registry', temp_registry)
    monkeypatch.setattr(app_module, 'database_cache', {})
    monkeypatch.setattr(app_module, 'DEFAULT_DATABASE_ID', sample_id)
    monkeypatch.setattr(app_module, 'CONFIG_FILE', str(tmp_path / 'readathon_config'))
    monkeypatch.setattr(app_module, 'VIEW_MODE', 'full')
    app.config['TESTING'] = True
    client = app.test_client()

    def view(db_id):
        with client.session_transaction() as sess:
            sess['active_database_id'] = db_id

    yield {'client': client, 'view': view, 'sample_id': sample_id, 'year_id': year_id, 'registry': temp_registry}

    for db in app_module.database_cache.values():
        db.close()
    for name in (YEAR_DB_NAME, NEW_DB_NAME):
        if os.path.exists(f'db/{name}'):
            os.remove(f'db/{name}')


class TestRegistry:
    def test_no_year_database_means_nothing_editable(self, temp_registry):
        temp_registry.register_database('readathon_sample.db', 'Sample', None)
        assert temp_registry.get_editable_database_id() is None

    def test_default_is_newest_year_database_and_is_saved(self, temp_registry):
        temp_registry.register_database('readathon_sample.db', 'Sample', None)
        temp_registry.register_database('readathon_2024.db', '2024 Read-a-Thon', 2024)
        newest = temp_registry.register_database('readathon_2026.db', '2026 Read-a-Thon', 2026)
        assert temp_registry.get_editable_database_id() == newest
        # Saved: a newer database registered later doesn't take over
        temp_registry.register_database('readathon_2027.db', '2027 Read-a-Thon', 2027)
        assert temp_registry.get_editable_database_id() == newest

    def test_set_editable_flags_exactly_one(self, temp_registry):
        first = temp_registry.register_database('readathon_2025.db', '2025 Read-a-Thon', 2025)
        second = temp_registry.register_database('readathon_2026.db', '2026 Read-a-Thon', 2026)
        assert temp_registry.set_editable_database(first)['success']
        flags = {db['db_id']: db['is_editable'] for db in temp_registry.list_databases()}
        assert flags == {first: True, second: False}
        assert temp_registry.get_database(first)['is_editable']

    def test_unknown_database_rejected(self, temp_registry):
        assert not temp_registry.set_editable_database(999)['success']

    def test_editable_database_cannot_be_unregistered(self, temp_registry):
        db_id = temp_registry.register_database('readathon_2026.db', '2026 Read-a-Thon', 2026)
        temp_registry.set_editable_database(db_id)
        result = temp_registry.delete_database(db_id)
        assert not result['success'] and 'editable' in result['error']

    def test_unregistered_choice_means_nothing_editable(self, temp_registry):
        db_id = temp_registry.register_database('readathon_2026.db', '2026 Read-a-Thon', 2026)
        temp_registry.set_editable_database(db_id)
        temp_registry.conn.execute('DELETE FROM Database_Registry WHERE db_id = ?', (db_id,))
        assert temp_registry.get_editable_database_id() is None

    def test_not_a_bulletin_setting(self, temp_registry):
        temp_registry.set_editable_database(temp_registry.register_database('readathon_2026.db', '2026', 2026))
        assert 'editable_database_id' not in temp_registry.get_settings()


class TestWriteGuard:
    @pytest.mark.parametrize('method, url, kwargs', GUARDED_ROUTES)
    def test_read_only_database_refuses_changes(self, env, method, url, kwargs):
        env['view'](env['sample_id'])
        response = getattr(env['client'], method)(url, **kwargs)
        assert response.status_code == 403
        body = response.get_json()
        assert body['read_only'] is True
        assert "'Sample' is read-only" in body['error'] and "Only '2099 Read-a-Thon'" in body['error']

    def test_editable_database_accepts_uploads_and_deletes(self, env):
        env['view'](env['year_id'])
        client = env['client']
        response = client.post('/api/upload_daily', data={
            'log_date': '2025-10-12',
            'minutes_file': (io.BytesIO(b'ReaderName,Minutes\nstudent11,30\n'), 'daily_2025-10-12.csv'),
        }, content_type='multipart/form-data')
        assert response.status_code == 200 and response.get_json()['success']
        assert client.delete('/api/delete_day/2025-10-12').get_json()['success']

    def test_switching_databases_keeps_the_editable_one(self, env):
        env['view'](env['year_id'])
        response = env['client'].post('/api/set_active_database', json={'database_id': env['sample_id']})
        assert response.get_json()['success']
        assert env['registry'].get_editable_database_id() == env['year_id']

    def test_make_editable_route(self, env):
        client = env['client']
        assert client.put(f"/api/databases/{env['sample_id']}/editable").get_json()['success']
        assert env['registry'].get_editable_database_id() == env['sample_id']
        env['view'](env['year_id'])
        assert client.delete('/api/delete_cumulative').status_code == 403
        assert client.put('/api/databases/999/editable').status_code == 400

    def test_database_list_includes_editable_flag(self, env):
        flags = {db['db_id']: db['is_editable'] for db in env['client'].get('/api/databases').get_json()}
        assert flags == {env['sample_id']: False, env['year_id']: True}


class TestReadOnlyDisplay:
    def test_read_only_nav_and_upload_banner(self, env):
        env['view'](env['sample_id'])
        html = env['client'].get('/upload').data.decode('utf-8')
        assert 'class="top-nav read-only-mode sample-mode"' in html
        assert '<body class="read-only-db">' in html
        assert '🔒 READ-ONLY' in html
        assert 'id="readOnlyBanner"' in html and 'Switch to 2099 Read-a-Thon' in html
        assert '🔒 <strong>Sample</strong> is <strong>read-only</strong>' in html
        assert '<fieldset disabled' in html

    def test_editable_nav_has_no_banner(self, env):
        env['view'](env['year_id'])
        html = env['client'].get('/upload').data.decode('utf-8')
        assert 'class="top-nav"' in html and '<body class="">' in html
        assert '✏️ EDITABLE' in html
        assert 'id="readOnlyBanner"' not in html and '<fieldset disabled' not in html

    def test_admin_clear_tables_note(self, env):
        env['view'](env['sample_id'])
        html = env['client'].get('/admin').data.decode('utf-8')
        assert 'id="clearTablesReadOnly"' in html
        assert 'id="clearTablesBtn" class="btn btn-danger btn-lg editable-only"' in html
        assert 'id="dbMakeEditable" checked' in html


class TestCreateDatabase:
    def post_create(self, client, **extra):
        return client.post('/api/create_database', data={
            'year': '2098',
            'filename': NEW_DB_NAME,
            'roster_csv': (io.BytesIO(ROSTER_CSV.encode()), 'roster.csv'),
            'class_info_csv': (io.BytesIO(CLASS_INFO_CSV.encode()), 'class_info.csv'),
            'grade_rules_csv': (io.BytesIO(GRADE_RULES_CSV.encode()), 'grade_rules.csv'),
            **extra,
        }, content_type='multipart/form-data').get_json()

    def test_new_database_becomes_editable_by_default(self, env):
        result = self.post_create(env['client'])
        assert result['success'] and result['editable'] is True
        new_db = next(db for db in env['registry'].list_databases() if db['db_filename'] == NEW_DB_NAME)
        assert env['registry'].get_editable_database_id() == new_db['db_id']

    def test_new_database_can_stay_read_only(self, env):
        result = self.post_create(env['client'], make_editable='false')
        assert result['success'] and result['editable'] is False
        assert env['registry'].get_editable_database_id() == env['year_id']
