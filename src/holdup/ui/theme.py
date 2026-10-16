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
    *[role="heading"] {{ font-size: 15px; font-weight: 700; }}
    *[role="strong"] {{ font-weight: 600; }}
    *[role="note"] {{ font-size: 13px; color: {t['mu']}; }}
    *[role="warning"] {{ font-size: 13px; color: {t['wni']}; }}
    *[role="caption"] {{ font-size: 12px; color: {t['mu']}; }}
    *[role="caption-strong"] {{ font-size: 12px; font-weight: 600; }}
    *[role="rule"] {{ background: {t['ln']}; border: none; }}
    *[role="privacy"] {{ background: {t['acs']}; border: none; border-radius: 16px; }}
    *[role="privacy"] QLabel {{ background: transparent; }}
    #segments {{ background: {t['sb']}; border: none; border-radius: 10px; }}
    #segments QPushButton {{ min-height: 32px; max-height: 32px; min-width: 60px; padding: 0 14px; border: none;
        border-radius: 8px; background: transparent; font-size: 13px; }}
    #segments QPushButton:checked {{ background: {t['cd']}; }}
    *[role="track"] {{ background: {t['sf']}; border: 1px solid {t['ln']}; border-radius: 8px; }}
    *[role="zone"] {{ background: {t['acs']}; border: none; border-left: 2px solid {t['ac']};
        border-right: 2px solid {t['ac']}; }}
    *[role="marker"] {{ background: {t['ink']}; border: none; border-radius: 1px; }}
    QComboBox {{ min-height: 38px; max-height: 38px; padding: 0 12px 0 14px; border: 1px solid {t['ln']};
        border-radius: 10px; background: {t['sf']}; }}
    QComboBox:disabled {{ color: {t['mu']}; }}
    QComboBox::drop-down {{ border: none; width: 0; }}
    QComboBox QAbstractItemView {{ background: {t['cd']}; border: 1px solid {t['ln']}; padding: 4px; outline: none;
        selection-background-color: {t['sf']}; selection-color: {t['ink']}; }}
    QPushButton[role="small"] {{ min-height: 34px; max-height: 34px; padding: 0 14px; background: transparent;
        font-size: 13px; }}
    QPushButton[role="switch"] {{ min-width: 44px; max-width: 44px; min-height: 24px; max-height: 24px; padding: 0;
        border: none; border-radius: 12px; background: {t['ln']}; }}
    QPushButton[role="switch"]:checked {{ background: {t['ac']}; }}
    *[role="knob"] {{ background: #FFFFFF; border: none; border-radius: 9px; }}
    """


_LABELS = {
    "watching": "Watching", "absent": "Absent", "unavailable": "Camera Unavailable",
    "stale": "Stale Baseline", "paused": "Paused", "calibrating": "Calibrating",
}


def status(state: MonitorState, paused: bool) -> tuple[str, str]:
    """The status pill's label and colour, matching the tray icon. Good Posture and both leans read as Watching."""
    glyph = tray_glyph(state, paused)
    return _LABELS[glyph], TRAY_COLORS[glyph]
