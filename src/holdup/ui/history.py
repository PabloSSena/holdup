"""The History page. Placeholder until issue 03 builds it."""
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from holdup.posture_monitor import PostureMonitor
from holdup.ui.actions import Actions
from holdup.ui.theme import PAGE_MARGINS


class HistoryPage(QWidget):
    def __init__(self, monitor: PostureMonitor, actions: Actions):
        super().__init__()
        self._monitor = monitor
        self._actions = actions
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*PAGE_MARGINS)
        title = QLabel("History")
        title.setProperty("role", "title")
        layout.addWidget(title)
        layout.addStretch()

    def refresh(self) -> None:
        """Re-read the Posture Monitor. Called on show and on the tray tick while this page is showing."""
