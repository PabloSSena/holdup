"""Design tokens (light and dark), status colours and the Qt stylesheet, from the design prototype."""
from pathlib import Path

from holdup.icons import TRAY_COLORS, tray_glyph
from holdup.posture_monitor import MonitorState

THEMES = {
    "light": dict(bg="#F4F1EB", sb="#ECE7DE", cd="#FFFFFF", ink="#1F2A26", mu="#5E6A64", ln="#E3DED4", sf="#F7F4EE",
                  ac="#2F7D62", acs="#E0EEE6", aci="#FFFFFF", fw="#C27A26", fws="#F7EBDA", sd="#6870B5", sds="#E8E9F6",
                  wn="#FBF0E1", wni="#7A4A12", scrim="rgba(20,24,22,.38)"),
    "dark": dict(bg="#161B19", sb="#1B211F", cd="#222A27", ink="#E8EDEA", mu="#9BA6A1", ln="#313B37", sf="#1C2321",
                 ac="#5DBB93", acs="#22382E", aci="#0F1A15", fw="#E2A45C", fws="#3A2D1E", sd="#A0A7E6", sds="#2A2D45",
                 wn="#33291C", wni="#F1C58F", scrim="rgba(0,0,0,.55)"),
}

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
FONT_FAMILY = "Figtree"  # falls back to Segoe UI when the bundled files are missing
PAGE_MARGINS = (30, 26, 30, 30)  # left, top, right, bottom of every page's content, as in the design
CARD_MARGINS = (22, 20, 22, 20)


def load_fonts() -> None:
    """Register the bundled Figtree weights (400/500/600/700) with Qt. Call once, after the QApplication exists."""
    from PySide6.QtGui import QFontDatabase

    for path in sorted(FONT_DIR.glob("Figtree-*.ttf")):
        QFontDatabase.addApplicationFont(str(path))


def stylesheet(t: dict[str, str]) -> str:
    """The main window's stylesheet. Pages pick styles by a `role` property, e.g. setProperty("role", "card")."""
    return f"""
    QWidget {{ color: {t['ink']}; font-family: "{FONT_FAMILY}", "Segoe UI"; font-size: 14px; }}
    QMainWindow {{ background: {t['bg']}; }}
    QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
    #sidebar {{ background: {t['sb']}; border: none; border-right: 1px solid {t['ln']}; }}
    #sidebar QPushButton {{ min-height: 40px; max-height: 40px; padding: 0 12px; border: none; border-radius: 10px;
        background: transparent; text-align: left; }}
    #sidebar QPushButton:checked {{ background: {t['cd']}; }}
    #pill {{ background: {t['cd']}; border: 1px solid {t['ln']}; border-radius: 10px; }}
    #pill QLabel {{ font-size: 13px; font-weight: 600; }}
    *[role="title"] {{ font-size: 26px; font-weight: 700; }}
    *[role="muted"] {{ color: {t['mu']}; }}
    *[role="card"] {{ background: {t['cd']}; border: 1px solid {t['ln']}; border-radius: 16px; }}
    *[role="card"] QLabel {{ background: transparent; border: none; }}
    QPushButton {{ min-height: 36px; max-height: 36px; padding: 0 16px; border-radius: 10px; border: 1px solid {t['ln']};
        background: {t['cd']}; font-weight: 600; }}
    QPushButton[role="primary"] {{ background: {t['ac']}; color: {t['aci']}; border: none; }}
    """


_LABELS = {
    "watching": "Watching", "absent": "Absent", "unavailable": "Camera Unavailable",
    "stale": "Stale Baseline", "paused": "Paused", "calibrating": "Calibrating",
}


def status(state: MonitorState, paused: bool) -> tuple[str, str]:
    """The status pill's label and colour, matching the tray icon. Good Posture and both leans read as Watching."""
    glyph = tray_glyph(state, paused)
    return _LABELS[glyph], TRAY_COLORS[glyph]
