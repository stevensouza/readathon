"""
Upload page layout (v2026.24.0): the three uploads are tabs, the result shows success/failure first with every
message under Details, and Upload History / Saved Name Corrections are tabs below.

The page's behaviour is JavaScript; these tests pin the structure the scripts and the read-only/simple-view rules
depend on.
"""

import re

import pytest

from app import app, registry


@pytest.fixture
def html():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['active_database_id'] = next(db['db_id'] for db in registry.list_databases()
                                              if db['db_filename'] == 'readathon_sample.db')
        return client.get('/upload').data.decode('utf-8')


def test_upload_tabs(html):
    for tab, pane in [('daily-tab', 'dailyPane'), ('cumulative-tab', 'cumulativePane'), ('bonus-tab', 'bonusPane')]:
        assert f'id="{tab}" data-bs-toggle="tab" data-bs-target="#{pane}"' in html
        assert f'id="{pane}"' in html
    # The forms each upload needs are still on the page
    for field in ['id="daily_files"', 'id="cumulative_file"', 'id="snapshot_date"', 'id="bonus_file"', 'id="bonus_event_date"']:
        assert field in html


def test_tabs_stay_usable_on_a_read_only_database(html):
    """The read-only fieldset disables buttons inside it, so the tab buttons must come before it"""
    content = html[html.index('id="uploadTabsCard"'):]
    assert content.index('id="bonus-tab"') < content.index('<fieldset')
    assert content.index('<fieldset') < content.index('id="dailyPane"')


def test_result_area_sits_between_uploads_and_records(html):
    assert html.index('id="uploadTabsCard"') < html.index('id="resultArea"') < html.index('id="recordsCard"')


def test_records_tabs(html):
    assert 'data-bs-target="#historyPane"' in html and 'data-bs-target="#nameAliasCard"' in html
    assert 'id="uploadHistory"' in html and 'id="nameAliasList"' in html and 'id="nameAliasCount"' in html


def test_outcome_first_then_details(html):
    """Success/failure banner, names not on the roster as one line, every message under Details"""
    assert 'function showUploadOutcome(outcome, messages' in html
    assert "upload-outcome-${outcome.ok ? 'success' : 'failed'}" in html
    assert "const UNMATCHED_WARNING = 'Student not found in roster (imported anyway): ';" in html
    assert re.search(r'<details class="upload-details mb-3" id="uploadDetails" \$\{outcome\.ok \? \'\' : \'open\'\}>', html)


def test_unmatched_warning_text_matches_the_server():
    """The page groups this warning by its exact prefix (database.py _report_name_fixes)"""
    source = open('database.py', encoding='utf-8').read()
    assert 'f"Student not found in roster (imported anyway): {who(typed, teacher)}"' in source


def test_tab_choice_is_remembered(html):
    assert 'data-remember="uploadTab"' in html and 'data-remember="uploadRecordsTab"' in html
    assert "localStorage.setItem(key, event.target.dataset.bsTarget)" in html
