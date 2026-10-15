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
