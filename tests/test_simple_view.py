"""
Tests for simple view: the nav shows only the daily job (Upload, Bulletins, Help, database
selector), the app opens on the Daily Scoreboard, and the Upload page hides its delete controls.
The preference lives in .readathon_config - tests point CONFIG_FILE at a temporary file.
"""

import json

import pytest

import app as app_module
from app import app, registry

FULL_ONLY_LINKS = ['href="/school"', 'href="/teams"', 'href="/classes"', 'href="/students"',
                   'href="/reports"', 'href="/workflows"', 'href="/admin"']
CORE_LINKS = ['href="/upload"', 'href="/scoreboards/teams"', 'href="/scoreboards/daily"', 'href="/scoreboards/prize"', 'href="/help"']


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    path = tmp_path / 'readathon_config'
    monkeypatch.setattr(app_module, 'CONFIG_FILE', str(path))
    return path


def make_client(monkeypatch, mode):
    monkeypatch.setattr(app_module, 'VIEW_MODE', mode)
    app.config['TESTING'] = True
    client = app.test_client()
    sample_id = next(db['db_id'] for db in registry.list_databases() if db['db_filename'] == 'readathon_sample.db')
    with client.session_transaction() as sess:
        sess['active_database_id'] = sample_id
    return client


@pytest.fixture
def full_client(monkeypatch, config_file):
    return make_client(monkeypatch, 'full')


@pytest.fixture
def simple_client(monkeypatch, config_file):
    return make_client(monkeypatch, 'simple')


def nav_html(html):
    return html.split('class="top-nav', 1)[1].split('<!-- Main Content -->', 1)[0]


class TestNav:
    def test_full_view_shows_everything(self, full_client):
        nav = nav_html(full_client.get('/upload').data.decode('utf-8'))
        for link in FULL_ONLY_LINKS + CORE_LINKS:
            assert link in nav
        assert '✨ Simple view' in nav and 'databaseSelector' in nav

    def test_simple_view_shows_only_the_daily_job(self, simple_client):
        html = simple_client.get('/upload').data.decode('utf-8')
        nav = nav_html(html)
        for link in FULL_ONLY_LINKS:
            assert link not in nav
        for link in CORE_LINKS:
            assert link in nav
        assert '☰ Full view' in nav and 'databaseSelector' in nav
        assert '<body class="simple-view">' in html

    @pytest.mark.parametrize('page', ['/scoreboards/teams', '/scoreboards/daily', '/scoreboards/prize', '/help'])
    def test_simple_view_pages_load(self, simple_client, page):
        assert simple_client.get(page).status_code == 200

    def test_hidden_pages_still_reachable(self, simple_client):
        """Simple view declutters the nav; it is not access control"""
        for page in ['/school', '/teams', '/admin', '/reports']:
            assert simple_client.get(page).status_code == 200


class TestHomePage:
    def test_simple_view_opens_on_daily_scoreboard(self, simple_client):
        response = simple_client.get('/')
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/scoreboards/daily')

    def test_full_view_opens_on_school(self, full_client):
        response = full_client.get('/')
        assert response.status_code == 200
        assert 'Read-a-Thon System' in response.data.decode('utf-8')


class TestUploadPage:
    def test_delete_controls_marked_full_view_only(self, simple_client):
        html = simple_client.get('/upload').data.decode('utf-8')
        assert 'id="deleteSelectedBtn" class="btn btn-sm btn-danger full-view-only"' in html
        assert '<td class="full-view-only" style="white-space: nowrap;">${deleteButton}</td>' in html
        assert '<th class="full-view-only" style="width: 40px;"><input type="checkbox" id="selectAll"' in html
        assert '.simple-view .full-view-only { display: none !important; }' in html


class TestToggle:
    def test_switching_is_remembered(self, full_client, config_file):
        app_module.write_config(1, 'readathon_sample.db')
        response = full_client.post('/api/view_mode', json={'mode': 'simple'})
        assert response.get_json() == {'success': True, 'mode': 'simple'}
        assert app_module.VIEW_MODE == 'simple'
        saved = json.loads(config_file.read_text())
        assert saved == {'active_database_id': 1, 'active_database_filename': 'readathon_sample.db', 'view_mode': 'simple'}
        assert '☰ Full view' in full_client.get('/help').data.decode('utf-8')

    def test_switching_database_keeps_view_mode(self, config_file):
        app_module.save_config(view_mode='simple')
        app_module.write_config(1, 'readathon_sample.db')
        assert json.loads(config_file.read_text())['view_mode'] == 'simple'

    def test_unknown_mode_rejected(self, full_client):
        response = full_client.post('/api/view_mode', json={'mode': 'tiny'})
        assert response.status_code == 400
        assert app_module.VIEW_MODE == 'full'


class TestStartupOption:
    @pytest.mark.parametrize('argv,expected', [(['--simple'], 'simple'), (['--full'], 'full'), ([], None),
                                               (['--db', 'sample', '--simple'], 'simple')])
    def test_parse(self, argv, expected):
        args, _ = app_module.parser.parse_known_args(argv)
        assert args.view_mode == expected

    def test_simple_and_full_are_exclusive(self):
        with pytest.raises(SystemExit):
            app_module.parser.parse_known_args(['--simple', '--full'])
