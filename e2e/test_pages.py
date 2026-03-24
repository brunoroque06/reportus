import pytest
from streamlit.testing.v1 import AppTest

from main import tabs


@pytest.mark.parametrize("rep", [t[0] for t in tabs()])
def test_report(rep: str):
    at = AppTest.from_file("main.py").run()
    tab = next((t for t in at.tabs if t.label == rep))
    assert len(tab.code[0].value) > 0
