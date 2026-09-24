"""Shared pytest fixtures"""

import pytest

import app as app_module


@pytest.fixture
def make_editable(monkeypatch):
    """Let one test write to a database: makes db_id the editable database for the test only
    (the real registry's editable setting is never changed)"""
    def make(db_id):
        monkeypatch.setattr(app_module.registry, 'get_editable_database_id', lambda: db_id)
    return make
