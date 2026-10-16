"""The main window shell: a sidebar with Today / History / Settings and the live status pill, one page per item."""
from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea, QStackedWidget, QVBoxLayout,
    QWidget,
)

from holdup.posture_monitor import PostureMonitor
from holdup.ui.actions import Actions
from holdup.ui.history import HistoryPage
from holdup.ui.settings import SettingsPage
from holdup.ui.theme import THEMES, status, stylesheet
from holdup.ui.today import TodayPage
from holdup.windows import CalibrationWindow

COMPACT_BELOW = 900  # window width under which the sidebar shows icons only
SIDEBAR_WIDTH = {False: 196, True: 60}  # by compact

_NAV_ICONS = {  # the design's 18x18 strokes; INK becomes the theme's text colour
    "Today": '<circle cx="9" cy="9" r="7" fill="none" stroke="INK" stroke-width="1.6"/>'
             '<path d="M9 5v4l2.5 2" fill="none" stroke="INK" stroke-width="1.6" stroke-linecap="round"/>',
    "History": '<path d="M3 15V9M7 15V4M11 15V7M15 15V11" fill="none" stroke="INK" stroke-width="1.8" stroke-linecap="round"/>',
    "Settings": '<path d="M2 5h8M14 5h2M2 13h2M8 13h8" fill="none" stroke="INK" stroke-width="1.6" stroke-linecap="round"/>'
                '<circle cx="12" cy="5" r="2" fill="none" stroke="INK" stroke-width="1.6"/>'
                '<circle cx="6" cy="13" r="2" fill="none" stroke="INK" stroke-width="1.6"/>',
}


def _nav_icon(body: str, ink: str) -> QIcon:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18">{body.replace("INK", ink)}</svg>'
    pixmap = QPixmap(54, 54)  # 3x, so it stays sharp on high-DPI screens
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode())).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(3)
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    """Closing hides it to the tray. Follows the Windows light/dark app theme."""

    def __init__(self, monitor: PostureMonitor, actions: Actions):
        super().__init__()
        self._monitor = monitor
        self.setWindowTitle("Holdup")
        self.resize(960, 640)
        self.setMinimumSize(760, 520)
        # shortcut: Calibration is still the separate window; issue 05 turns it into a view over this window's content.
        self.calibration = CalibrationWindow(monitor)
        self._pages = {
            "Today": TodayPage(monitor, actions),
            "History": HistoryPage(monitor, actions),
            "Settings": SettingsPage(monitor, actions),
        }

        self._sidebar = QFrame(objectName="sidebar")
        side = QVBoxLayout(self._sidebar)
        side.setContentsMargins(10, 14, 10, 14)
        side.setSpacing(4)
        self._stack = QStackedWidget()
        self._nav = QButtonGroup(self)  # exclusive: one item selected
        for name, page in self._pages.items():
            button = QPushButton(checkable=True, iconSize=QSize(18, 18), toolTip=name)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _=False, name=name: self.show_page(name))
            self._nav.addButton(button)
            side.addWidget(button)
            scroll = QScrollArea(widgetResizable=True)
            scroll.setWidget(page)
            self._stack.addWidget(scroll)
        side.addStretch()

        pill = QFrame(objectName="pill")
        row = QHBoxLayout(pill)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)
        self._dot = QLabel()
        self._dot.setFixedSize(10, 10)
        self._status = QLabel()
        row.addWidget(self._dot)
        row.addWidget(self._status, 1)
        self._pill = pill
        side.addWidget(pill)

        central = QWidget()
        body = QHBoxLayout(central)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._sidebar)
        body.addWidget(self._stack, 1)
        self.setCentralWidget(central)

        self._compact: bool | None = None
        self._set_compact(False)
        self._apply_theme()
        QGuiApplication.styleHints().colorSchemeChanged.connect(self._apply_theme)
        self.show_page("Today")

    def present(self) -> None:
        """Show, restore and bring to the front (tray left-click and "Open Holdup")."""
        self.showNormal() if self.isMinimized() else self.show()
        self.raise_()
        self.activateWindow()

    def show_page(self, name: str) -> None:
        names = list(self._pages)
        self._nav.buttons()[names.index(name)].setChecked(True)
        self._stack.setCurrentIndex(names.index(name))
        self._pages[name].refresh()

    def show_calibration(self) -> None:
        """Show Calibration; the caller has already begun it on the Posture Monitor."""
        self.calibration.show()
        self.calibration.raise_()
        self.calibration.activateWindow()

    def refresh(self) -> None:
        """Re-read the Posture Monitor into the status pill and the showing page. Called on the tray tick while visible."""
        label, color = status(self._monitor.state, self._monitor.paused)
        self._status.setText(label)
        self._pill.setToolTip(label)
        self._dot.setStyleSheet(f"background: {color}; border-radius: 5px;")
        self._stack.currentWidget().widget().refresh()

    def showEvent(self, event) -> None:
        self.refresh()
        super().showEvent(event)

    def closeEvent(self, event) -> None:
        if event.spontaneous():  # the User's close button hides to the tray; Quit still closes
            event.ignore()
            self.hide()

    def resizeEvent(self, event) -> None:
        self._set_compact(self.width() < COMPACT_BELOW)
        super().resizeEvent(event)

    def _set_compact(self, compact: bool) -> None:
        if compact == self._compact:
            return
        self._compact = compact
        self._sidebar.setFixedWidth(SIDEBAR_WIDTH[compact])
        for name, button in zip(self._pages, self._nav.buttons()):
            button.setText("" if compact else f"  {name}")  # the spaces stand in for the design's 12 px icon gap
        self._status.setVisible(not compact)

    def _apply_theme(self) -> None:
        dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        tokens = THEMES["dark" if dark else "light"]
        self.setStyleSheet(stylesheet(tokens))
        for name, button in zip(self._pages, self._nav.buttons()):
            button.setIcon(_nav_icon(_NAV_ICONS[name], tokens["ink"]))
