"""The History page: Good Posture per day as a chart, the Daily Stats table, and Clear statistics."""
from dataclasses import dataclass
from datetime import date, timedelta

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QToolTip,
    QVBoxLayout, QWidget,
)

from holdup.posture_monitor import DailyStats, PostureMonitor
from holdup.ui.actions import Actions
from holdup.ui.theme import CARD_MARGINS, PAGE_MARGINS, THEMES

STATS_COLUMNS = ("Good Posture", "Forward Lean", "Side Lean", "Mirror")
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")  # not strftime: that follows the locale
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


@dataclass(frozen=True)
class Row:
    day: str  # Today, Yesterday, then "Wed 14 Oct"
    watched_time: str  # "" without Watched Time
    cells: tuple[str, ...]  # one per STATS_COLUMNS; () without Watched Time


@dataclass(frozen=True)
class Bar:
    label: str  # under the bar; "" for most bars of the 30-day view
    good: int | None  # Good Posture %; None without Watched Time


@dataclass(frozen=True)
class History:
    rows: tuple[Row, ...]  # newest first
    bars: tuple[Bar, ...]  # oldest first
    average: int | None  # mean Good Posture % of the days with Watched Time
    active_days: int  # days with Watched Time


def _cells(stats: DailyStats) -> tuple[str, ...]:
    shares = (stats.good_posture, stats.forward_lean, stats.side_lean)
    return tuple(f"{round(100 * seconds / stats.watched_time)}%" for seconds in shares) + (str(stats.mirror_count),)


def _watched_time(seconds: float) -> str:
    hours, minutes = divmod(int(seconds // 60), 60)
    return f"{hours} h {minutes} min" if hours else f"{minutes} min"


def _day(day: date, today: date) -> str:
    return {0: "Today", 1: "Yesterday"}.get((today - day).days, f"{WEEKDAYS[day.weekday()]} {_date(day)}")


def _date(day: date) -> str:
    return f"{day.day} {MONTHS[day.month - 1]}"


def _bar_label(ago: int, day: date, days: int) -> str:
    if ago == 0:
        return "Today"
    if days <= 7:
        return WEEKDAYS[day.weekday()]
    return _date(day) if ago % 5 == 0 else ""


def history(stats: dict[date, DailyStats], today: date, days: int) -> History:
    """What the page shows for the last `days` days up to today, from monitor.daily_stats()."""
    rows, bars = [], []
    for ago in range(days):
        day = today - timedelta(days=ago)
        day_stats = stats.get(day)
        watched = day_stats.watched_time if day_stats else 0
        rows.append(Row(_day(day, today), _watched_time(watched) if watched else "",
                        _cells(day_stats) if watched else ()))
        bars.append(Bar(_bar_label(ago, day, days), round(100 * day_stats.good_posture / watched) if watched else None))
    goods = [bar.good for bar in bars if bar.good is not None]
    average = round(sum(goods) / len(goods)) if goods else None  # of the shown (rounded) bars, so it adds up on screen
    return History(tuple(rows), tuple(reversed(bars)), average, len(goods))


def _tokens() -> dict[str, str]:
    dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    return THEMES["dark" if dark else "light"]


def _label(text: str = "", role: str | None = None, align=Qt.AlignLeft) -> QLabel:
    label = QLabel(text, alignment=align | Qt.AlignVCenter)
    if role:
        label.setProperty("role", role)
    return label


def _card(margins=CARD_MARGINS, spacing: int = 14) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setProperty("role", "card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return card, layout


_COLUMN_STRETCH = (15, 11, 10, 10, 10, 7)  # Day, Watched Time, the three shares, Mirror (the design's grid)


def _table_row(cells: list[QWidget], margins: tuple[int, int, int, int], stretches=_COLUMN_STRETCH) -> QFrame:
    row = QFrame()
    row.setProperty("role", "row")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(*margins)
    layout.setSpacing(8)
    for cell, stretch in zip(cells, stretches):
        cell.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)  # columns share the width by stretch alone
        layout.addWidget(cell, stretch)
    return row


class _Chart(QWidget):
    """Good Posture per day: one bar per day, oldest first; a day without Watched Time is a thin stub."""

    AXIS, TOP, PLOT, BELOW = 44, 18, 150, 22  # axis column + gap, room for % labels, plot height, day labels

    def __init__(self):
        super().__init__()
        self.setFixedHeight(self.TOP + self.PLOT + self.BELOW)
        self._bars: tuple[Bar, ...] = ()

    def set_bars(self, bars: tuple[Bar, ...]) -> None:
        self._bars = bars
        self.update()

    def _slots(self) -> list[QRectF]:
        n, gap = len(self._bars), 14 if len(self._bars) <= 7 else 4
        width = (self.width() - self.AXIS - gap * (n - 1)) / n
        return [QRectF(self.AXIS + i * (width + gap), self.TOP, width, self.PLOT) for i in range(n)]

    def event(self, event) -> bool:
        if event.type() == QEvent.ToolTip:
            x = event.pos().x()
            bar = next((bar for bar, slot in zip(self._bars, self._slots()) if slot.left() <= x <= slot.right()), None)
            if bar:
                QToolTip.showText(event.globalPos(), "No Watched Time" if bar.good is None else f"Good Posture {bar.good}%")
            else:
                QToolTip.hideText()
            return True
        return super().event(event)

    def paintEvent(self, event) -> None:
        if not self._bars:
            return
        t = _tokens()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont(self.font())
        font.setPixelSize(11)
        painter.setFont(font)
        top, bottom, right = self.TOP, self.TOP + self.PLOT, self.width()

        painter.setPen(QColor(t["mu"]))
        for y, text in ((top, "100%"), (top + self.PLOT / 2, "50%"), (bottom, "0%")):
            painter.drawText(QRectF(0, y - 8, 34, 16), Qt.AlignRight | Qt.AlignVCenter, text)
        for y, style in ((top, Qt.DashLine), (top + self.PLOT / 2, Qt.DashLine), (bottom, Qt.SolidLine)):
            painter.setPen(QPen(QColor(t["ln"]), 1, style))
            painter.drawLine(QPointF(self.AXIS, y + 0.5), QPointF(right, y + 0.5))

        show_values = len(self._bars) <= 7
        for i, (bar, slot) in enumerate(zip(self._bars, self._slots())):
            width = min(slot.width(), 44)
            height = self.PLOT * (bar.good if bar.good is not None else 1.5) / 100
            rect = QRectF(slot.center().x() - width / 2, bottom - height, width, height)
            path = QPainterPath()
            path.addRoundedRect(rect.adjusted(0, 0, 0, 5), 5, 5)  # only the top corners round: the rest is clipped
            painter.save()
            painter.setClipRect(QRectF(0, 0, right, bottom))
            painter.fillPath(path, QColor(t["ln"] if bar.good is None else t["ac"]))
            painter.restore()
            painter.setPen(QColor(t["mu"]))
            if show_values and bar.good is not None:
                font.setWeight(QFont.DemiBold)
                painter.setFont(font)
                painter.drawText(QRectF(slot.left() - 10, rect.top() - 18, slot.width() + 20, 14),
                                 Qt.AlignHCenter | Qt.AlignBottom, f"{bar.good}%")
            font.setWeight(QFont.Bold if i == len(self._bars) - 1 else QFont.Normal)  # today's label stands out
            painter.setFont(font)
            label = painter.boundingRect(QRectF(slot.center().x(), bottom + 6, 0, 16), Qt.AlignHCenter, bar.label)
            label.moveRight(min(label.right(), right))  # the last label would spill past a thin 30-day bar
            painter.drawText(label, Qt.AlignHCenter | Qt.AlignTop, bar.label)
        painter.end()


class _EmptyIcon(QWidget):
    """The History icon on a soft accent circle."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(56, 56)

    def paintEvent(self, event) -> None:
        t = _tokens()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(t["acs"]))
        painter.drawEllipse(self.rect())
        painter.setPen(QPen(QColor(t["ac"]), 2.4, Qt.SolidLine, Qt.RoundCap))
        scale, origin = 24 / 18, 16  # the design's 18-unit icon drawn at 24 px, centred
        for x, y in ((3, 9), (7, 4), (11, 7), (15, 11)):
            painter.drawLine(QPointF(origin + x * scale, origin + 15 * scale), QPointF(origin + x * scale, origin + y * scale))
        painter.end()


class _Confirm(QFrame):
    """The in-window confirm dialog for Clear statistics: a scrim over the whole window."""

    def __init__(self, window: QWidget, on_delete):
        super().__init__(window, objectName="confirm")
        window.installEventFilter(self)  # follow the window's size
        self.setGeometry(window.rect())

        dialog, layout = _card((24, 24, 24, 24), 8)
        dialog.setFixedWidth(min(400, window.width() - 48))
        dialog.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=40, offset=QPointF(0, 16), color=QColor(0, 0, 0, 51)))
        layout.addWidget(_label("Delete all Daily Stats?", "dialog-title"))
        layout.addWidget(_label("Your Baseline and settings are kept.", "muted"))
        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 16, 0, 0)
        buttons.setSpacing(8)
        buttons.addStretch()
        cancel, delete = QPushButton("Cancel"), QPushButton("Delete Daily Stats")
        delete.setProperty("role", "danger")
        cancel.clicked.connect(self.close)
        delete.clicked.connect(lambda: (on_delete(), self.close()))
        for button in (cancel, delete):
            button.setCursor(Qt.PointingHandCursor)
            buttons.addWidget(button)
        layout.addLayout(buttons)

        outer = QHBoxLayout(self)
        outer.addWidget(dialog, 0, Qt.AlignCenter)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show()
        self.raise_()
        cancel.setFocus()

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Resize:
            self.setGeometry(watched.rect())
        return False

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()


_UNREAD = object()


class HistoryPage(QWidget):
    def __init__(self, monitor: PostureMonitor, actions: Actions):
        super().__init__(objectName="history")
        self._monitor = monitor
        self._actions = actions
        self._days = 7
        self._shown = _UNREAD  # the History last built, so a tick with unchanged Daily Stats changes nothing

        page = QVBoxLayout(self)
        page.setContentsMargins(*PAGE_MARGINS)
        content = QWidget(maximumWidth=820)
        row = QHBoxLayout()
        row.addWidget(content, 1)
        row.addStretch()  # takes the width past 820 px, keeping the content on the left as in the design
        page.addLayout(row)
        page.addStretch()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(12)
        header.addWidget(_label("History", "title"), 1)
        segment = QFrame()
        segment.setProperty("role", "segment")
        toggle = QHBoxLayout(segment)
        toggle.setContentsMargins(3, 3, 3, 3)
        toggle.setSpacing(2)
        self._range = QButtonGroup(self)
        for days in (7, 30):
            button = QPushButton(f"Last {days} days", checkable=True, checked=days == self._days)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _=False, days=days: self._set_days(days))
            self._range.addButton(button)
            toggle.addWidget(button)
        header.addWidget(segment)
        self._clear = QPushButton("Clear statistics", objectName="clear")
        self._clear.setCursor(Qt.PointingHandCursor)
        self._clear.clicked.connect(lambda: _Confirm(self.window(), self._delete))
        header.addWidget(self._clear)
        layout.addLayout(header)

        self._empty, empty = _card((32, 56, 32, 56), 10)
        empty.addWidget(_EmptyIcon(), 0, Qt.AlignHCenter)
        empty.addSpacing(6)
        empty.addWidget(_label("No Daily Stats yet", "dialog-title", Qt.AlignHCenter))
        hint = _label("Once Holdup has watched you for a while, each day's Good Posture, Forward Lean and Side Lean "
                      "show up here.", "muted", Qt.AlignHCenter)
        hint.setWordWrap(True)
        hint.setMaximumWidth(360)
        centred = QHBoxLayout()  # not an alignment flag: that breaks the wrapped label's height
        centred.addStretch()
        centred.addWidget(hint, 1)
        centred.addStretch()
        empty.addLayout(centred)
        layout.addWidget(self._empty)

        self._chart_card, chart = _card()
        top = QHBoxLayout()
        top.setSpacing(4)
        top.addWidget(_label("Good Posture per day", "heading"), 1)
        self._average = [_label(role="small-muted"), _label(role="small-strong"), _label(role="small-muted")]
        for label in self._average:
            top.addWidget(label)
        chart.addLayout(top)
        self._chart = _Chart()
        chart.addWidget(self._chart)
        layout.addWidget(self._chart_card)

        self._table, table = _card((0, 8, 0, 8), 0)
        heading = _label("Daily Stats", "heading")
        heading.setContentsMargins(22, 10, 22, 12)
        table.addWidget(heading)
        columns: list[QWidget] = [_label("Day", "column"), _label("Watched Time", "column")]
        for name, swatch in zip(STATS_COLUMNS, ("good", "forward", "side")):
            cell = QWidget()
            row = QHBoxLayout(cell)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            row.addStretch()
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setProperty("role", f"swatch-{swatch}")
            row.addWidget(dot)
            row.addWidget(_label(name, "column"))
            columns.append(cell)
        columns.append(_label("Mirror", "column", Qt.AlignRight))
        table.addWidget(_table_row(columns, (22, 0, 22, 8)))
        self._rows = QVBoxLayout()
        self._rows.setSpacing(0)
        table.addLayout(self._rows)
        layout.addWidget(self._table)

    def _set_days(self, days: int) -> None:
        self._days = days
        self.refresh()

    def _delete(self) -> None:
        self._monitor.clear_stats()
        self.refresh()

    def refresh(self) -> None:
        """Re-read the Posture Monitor. Called on show and on the tray tick while this page is showing."""
        today = date.today()
        stats = self._monitor.daily_stats(today - timedelta(days=self._days - 1), today)
        any_stats = bool(stats) or bool(self._monitor.daily_stats(date.min, date.max))
        view = history(stats, today, self._days) if any_stats else None
        if view == self._shown:
            return
        self._shown = view
        self._clear.setEnabled(any_stats)
        self._empty.setVisible(view is None)
        self._chart_card.setVisible(view is not None)
        self._table.setVisible(view is not None)
        if view is None:
            return

        if view.average is None:
            texts = ("No Watched Time in these days", "", "")
        else:
            days = "day" if view.active_days == 1 else "days"
            texts = ("Average", f"{view.average}%", f"across {view.active_days} {days} with Watched Time")
        for label, text in zip(self._average, texts):
            label.setText(text)
            label.setVisible(bool(text))
        self._chart.set_bars(view.bars)

        while self._rows.count():
            old = self._rows.takeAt(0).widget()
            old.hide()  # deleteLater waits for the event loop; until then it would still paint
            old.deleteLater()
        for row in view.rows:
            cells = [_label(row.day, "day")]
            if row.cells:
                cells.append(_label(row.watched_time, "muted"))
                cells += [_label(text, "share-good" if i == 0 else "share", Qt.AlignRight) for i, text in enumerate(row.cells)]
                self._rows.addWidget(_table_row(cells, (22, 11, 22, 11)))
            else:
                cells.append(_label("No Watched Time", "small-muted"))
                # the 32 px right margin stands in for the 4 column gaps this row lacks, so the Day column lines up
                self._rows.addWidget(_table_row(cells, (22, 11, 54, 11), (15, 48)))
