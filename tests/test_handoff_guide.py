"""
Tests for the Volunteer Handoff Guide: md/HANDOFF_GUIDE.md rendered on /help/handoff and downloaded as
Word, the blank Contacts & Links template, and the small Markdown parser in handoff_doc.py.
"""

import io
import re
import zipfile

import pytest

import handoff_doc
from app import app, registry

docx = pytest.importorskip('docx')


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    sample_id = next(db['db_id'] for db in registry.list_databases() if db['db_filename'] == 'readathon_sample.db')
    with client.session_transaction() as sess:
        sess['active_database_id'] = sample_id
    return client


@pytest.fixture
def guide():
    return handoff_doc.load(handoff_doc.GUIDE_PATH)


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


class TestParser:
    def test_inline_spans(self):
        spans = handoff_doc.parse_inline('a **b** *c* `d` [e](http://x.org) [TBD: f] [TBD] see https://g.org.')
        kinds = [(s['kind'], s['text']) for s in spans if s['kind'] != 'text']
        assert kinds == [('bold', 'b'), ('italic', 'c'), ('code', 'd'), ('link', 'e'), ('tbd', 'f'), ('tbd', ''),
                         ('link', 'https://g.org')]  # trailing period is not part of the URL

    def test_blocks(self):
        blocks = handoff_doc.parse_blocks(
            '## Title\n\nline one\nline two\n\n- [ ] **Boss:** do it\n  - sub item\n1. first\n\n'
            '| A | B |\n|---|---|\n| x | [TBD] |\n\n```\nkeep  spacing\n```\n\n> note')
        assert [b['type'] for b in blocks] == ['heading', 'para', 'list', 'table', 'code', 'quote']
        assert blocks[0]['id'] == 'title'
        assert blocks[1]['text'] == 'line one line two'
        items = blocks[2]['items']
        assert [(i['level'], i['checkbox'], i['ordered']) for i in items] == [(0, True, False), (1, False, False), (0, False, True)]
        assert blocks[3]['header'] == ['A', 'B'] and blocks[3]['rows'] == [['x', '[TBD]']]  # separator row skipped
        assert blocks[4]['text'] == 'keep  spacing'

    def test_tbds_grouped_and_labeled(self):
        blocks = handoff_doc.parse_blocks(
            '## Dates\n\n| Event | 2025 | Now |\n|---|---|---|\n| Kickoff | [TBD] | [TBD] |\n| Final | Oct 1 | [TBD: ask] |\n\n'
            '## Roles\n\n- **Secretary:** prints things. [TBD: what]')
        labels = [handoff_doc.tbd_label(t) for t in handoff_doc.collect_tbds(blocks)]
        assert labels == ['Dates › Final (Now): ask', 'Dates › 2025: Kickoff', 'Dates › Now: Kickoff',
                          'Roles › Secretary: what']

    def test_nested_list_html_is_balanced(self):
        blocks = handoff_doc.parse_blocks('- a\n  - b\n    - c\n- d\n  - e\n- f')
        html = handoff_doc.to_html(blocks)
        assert html.count('<li>') == html.count('</li>') == 6
        assert html.count('<ul>') == html.count('</ul>') == 4

    def test_html_escapes_text(self):
        html = handoff_doc.to_html(handoff_doc.parse_blocks('a <script> & [TBD: x<y>]'))
        assert '<script>' not in html and '&lt;script&gt;' in html
        assert '<mark class="tbd">⚠ TBD: x&lt;y&gt;</mark>' in html


class TestGuideContent:
    SECTIONS = ['At a glance', 'People and roles', 'Timeline and checklist', 'Contest rules', 'Glossary',
                'The school app', 'Installing and running the app', 'Appendix A: Roster from the school',
                'Appendix B: Making the teams']
    GLOSSARY_TERMS = ['Participation', 'Goal Getter', 'Team', 'Student / Reader', 'Class', 'Color War',
                      'Kickoff assembly', 'Final assembly', 'Teacher', 'Daily drawing', 'Theme', 'Roster']

    def test_sections(self, guide):
        assert guide['title'] == 'Read-a-Thon Volunteer Handoff Guide'
        toc = [t['text'] for t in guide['toc']]
        assert toc[:len(self.SECTIONS)] == self.SECTIONS

    def test_glossary_terms(self):
        text = read_text(handoff_doc.GUIDE_PATH)
        glossary = text.split('## Glossary', 1)[1].split('\n## ', 1)[0]
        for term in self.GLOSSARY_TERMS:
            assert f'- **{term}' in glossary, term

    def test_every_tbd_is_listed_at_the_end(self, guide):
        assert guide['tbds'], 'no placeholders left: drop this test and the draft notice'
        last = guide['blocks'][-2:]
        assert last[0]['text'] == handoff_doc.STILL_TO_LOOK_UP
        assert len(last[1]['items']) == len(guide['tbds'])

    @pytest.mark.parametrize('path', [handoff_doc.GUIDE_PATH, handoff_doc.PRIVATE_TEMPLATE_PATH])
    def test_no_contact_details_in_tracked_files(self, path):
        """Both files are public: contact details belong in the filled-in copy on Google Drive"""
        text = read_text(path)
        assert not re.search(r'[\w.+-]+@[\w-]+\.\w+', text), 'email address'
        assert not re.search(r'\(?\d{3}\)?[ .-]\d{3}[.-]\d{4}', text), 'phone number'

    def test_private_template_is_blank(self):
        template = handoff_doc.load(handoff_doc.PRIVATE_TEMPLATE_PATH)
        people = next(b for b in template['blocks'] if b['type'] == 'table')
        assert people['header'][:2] == ['Role', 'Name']
        assert all(not cell for row in people['rows'] for cell in row[1:4])


class TestHandoffPage:
    def test_page_loads(self, client, guide):
        response = client.get('/help/handoff')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Read-a-Thon System' in html
        assert guide['title'] in html
        for item in guide['toc']:
            assert f'href="#{item["id"]}"' in html and f'id="{item["id"]}"' in html

    def test_no_error_messages(self, client):
        html = client.get('/help/handoff').data.decode('utf-8').lower()
        for pattern in ['error:', 'exception:', 'traceback', 'error occurred']:
            assert pattern not in html

    def test_draft_notice_and_downloads(self, client, guide):
        html = client.get('/help/handoff').data.decode('utf-8')
        assert 'id="tbdNotice"' in html and f'{len(guide["tbds"])} items still to look up' in html
        assert 'href="/help/handoff/download/guide"' in html
        assert 'href="/help/handoff/download/contacts"' in html

    def test_in_help_menu(self, client):
        assert 'href="/help/handoff"' in client.get('/help').data.decode('utf-8')

    def test_without_python_docx(self, client, monkeypatch):
        monkeypatch.setattr(handoff_doc, 'docx_available', lambda: False)
        html = client.get('/help/handoff').data.decode('utf-8')
        assert 'href="/help/handoff/download/guide"' not in html and './install.sh' in html
        assert client.get('/help/handoff/download/guide').status_code == 503


class TestWordDownloads:
    def open_docx(self, response):
        assert response.status_code == 200
        assert response.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        assert zipfile.is_zipfile(io.BytesIO(response.data))
        return docx.Document(io.BytesIO(response.data))

    def test_guide(self, client, guide):
        response = client.get('/help/handoff/download/guide')
        assert 'Volunteer Handoff Guide.docx' in response.headers['Content-Disposition']
        document = self.open_docx(response)
        text = '\n'.join(p.text for p in document.paragraphs)
        assert guide['title'] in text
        for item in guide['toc']:
            assert item['text'] in text
        assert f'{len(guide["tbds"])} items still to look up' in text
        assert len(document.tables) == sum(1 for b in guide['blocks'] if b['type'] == 'table')
        assert 'source: md/HANDOFF_GUIDE.md' in document.sections[0].footer.paragraphs[0].text
        links = [r.target_ref for r in document.part.rels.values() if r.reltype.endswith('/hyperlink')]
        assert 'https://github.com/stevensouza/readathon' in links

    def test_contacts_template(self, client):
        response = client.get('/help/handoff/download/contacts')
        assert '(PRIVATE).docx' in response.headers['Content-Disposition']
        document = self.open_docx(response)
        assert document.paragraphs[0].text == 'Read-a-Thon Contacts & Links (PRIVATE)'
        assert document.tables[0].cell(1, 0).text == 'PTA president'

    def test_unknown_document(self, client):
        assert client.get('/help/handoff/download/secrets').status_code == 404
