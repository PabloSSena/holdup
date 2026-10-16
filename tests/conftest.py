import pytest

from holdup.ui import strings


@pytest.fixture(autouse=True)
def english(monkeypatch):
    """The copy follows the Windows display language; tests read it in English unless they switch."""
    monkeypatch.setattr(strings, "LANG", "en")
