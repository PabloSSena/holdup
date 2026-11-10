"""The copy in Brazilian Portuguese, from the design, when the system is set to Portuguese."""
from datetime import date, datetime

from holdup.posture_monitor import DailyStats, MonitorState
from holdup.ui import strings
from holdup.ui.history import history
from holdup.ui.settings import baseline_text
from holdup.ui.today import headline

TODAY = date(2026, 10, 16)  # a Friday


def test_portuguese_dates_read_as_in_the_design(monkeypatch):
    monkeypatch.setattr(strings, "LANG", "pt")

    assert strings.long_date(TODAY) == "Sexta-feira, 16 de outubro"
    assert strings.short_date(date(2026, 10, 14)) == "Qua, 14 out"
    assert strings.day_month(TODAY) == "16 out"


def test_portuguese_pages(monkeypatch):
    monkeypatch.setattr(strings, "LANG", "pt")
    stats = {TODAY: DailyStats(good_posture=600, forward_lean=0, side_lean=0, mirror_count=0)}

    view = history(stats, TODAY, 7)
    assert [row.day for row in view.rows[:3]] == ["Hoje", "Ontem", "Qua, 14 out"]
    assert [bar.label for bar in view.bars] == ["Sáb", "Dom", "Seg", "Ter", "Qua", "Qui", "Hoje"]
    assert headline(MonitorState.ABSENT, False, None) == (
        "Ausente", "Ninguém está em frente à câmera. O monitoramento volta quando você retornar.")
    assert headline(MonitorState.GOOD_POSTURE, True, datetime(2026, 10, 16, 14, 30))[0] == "Pausado até 14:30"
    now = datetime(2026, 10, 16, 12)
    assert baseline_text(datetime(2026, 10, 16, 9, 10), now, False, True) == "Capturada hoje às 09:10"


def test_english_is_the_key_and_unknown_text_passes_through(monkeypatch):
    assert strings.tr("Good Posture") == "Good Posture"
    monkeypatch.setattr(strings, "LANG", "pt")
    assert strings.tr("Good Posture") == "Boa Postura"
    assert strings.tr("Logitech C920") == "Logitech C920"
