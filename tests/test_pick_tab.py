"""DeepDiver drives its own tab, never a person's tab on another site (2026-10-15)."""

from types import SimpleNamespace as Tab

from deepdiver.notebooklm_automator import pick_deepdiver_page


def test_prefers_a_notebook_tab_over_earlier_tabs():
    tabs = [Tab(url='https://aistudio.google.com/apps/x'), Tab(url='chrome://newtab/'),
            Tab(url='https://notebook.google.com/notebook/129987d0')]
    assert pick_deepdiver_page(tabs) is tabs[2]


def test_takes_a_blank_tab_when_no_notebook_tab():
    tabs = [Tab(url='https://miadi.tail3b11eb.ts.net/chronicle/x'), Tab(url='about:blank')]
    assert pick_deepdiver_page(tabs) is tabs[1]


def test_never_a_tab_on_another_site():
    tabs = [Tab(url='https://aistudio.google.com/apps/x'), Tab(url='https://miadi-author-desk.ai.studio/')]
    assert pick_deepdiver_page(tabs) is None


def test_old_notebooklm_host_counts():
    tabs = [Tab(url='https://example.com'), Tab(url='https://notebooklm.google.com/')]
    assert pick_deepdiver_page(tabs) is tabs[1]


def test_attach_timeout_names_the_open_tabs(monkeypatch):
    from deepdiver import notebooklm_automator as na

    class Answer:
        def json(self):
            return [{'type': 'page', 'url': 'https://miadi-author-desk.ai.studio/'},
                    {'type': 'iframe', 'url': 'https://accounts.google.com/RotateCookiesPage'},
                    {'type': 'page', 'url': 'https://notebook.google.com/notebook/3eb56742'}]
    monkeypatch.setattr(na.requests, 'get', lambda *a, **k: Answer())
    text = na.describe_attach_timeout('http://127.0.0.1:9222')
    assert 'miadi-author-desk.ai.studio' in text and 'notebook.google.com' in text
    assert 'RotateCookiesPage' not in text
    assert 'may be a person' in text


def test_attach_timeout_when_even_the_tab_list_is_silent(monkeypatch):
    from deepdiver import notebooklm_automator as na

    def silent(*a, **k):
        raise TimeoutError
    monkeypatch.setattr(na.requests, 'get', silent)
    assert 'the tab list did not answer either' in na.describe_attach_timeout('http://127.0.0.1:9222')
