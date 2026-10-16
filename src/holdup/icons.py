"""Tray icons (a coloured circle with a white glyph per state) and the app icon, painted with QPainter on the design's 32x32 grid."""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from holdup.posture_monitor import MonitorState

TRAY_COLORS = {
    "watching": "#3FA36B", "absent": "#8C948F", "unavailable": "#E07A2E",
    "stale": "#D9534F", "paused": "#E3B53B", "calibrating": "#4C8BD6",
}
_GLYPHS = {
    MonitorState.UNCALIBRATED: "calibrating", MonitorState.CALIBRATING: "calibrating",
    MonitorState.GOOD_POSTURE: "watching", MonitorState.FORWARD_LEAN: "watching", MonitorState.SIDE_LEAN: "watching",
    MonitorState.ABSENT: "absent", MonitorState.CAMERA_UNAVAILABLE: "unavailable", MonitorState.STALE_BASELINE: "stale",
}
WHITE = QColor("#FFFFFF")
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def tray_glyph(state: MonitorState, paused: bool) -> str:
    """The tray icon for a state; Paused wins over whatever the Posture Monitor last saw."""
    return "paused" if paused else _GLYPHS[state]


def _painter(pixmap: QPixmap) -> QPainter:
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.scale(pixmap.width() / 32, pixmap.height() / 32)
    painter.setPen(Qt.NoPen)
    return painter


def _dot(painter: QPainter, x: float, y: float, r: float) -> None:
    painter.drawEllipse(QPointF(x, y), r, r)


def _stroke(painter: QPainter, color: QColor, width: float) -> None:
    painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap))
    painter.setBrush(Qt.NoBrush)


def _paint_tray(pixmap: QPixmap, glyph: str) -> None:
    """The design's thicker 16 px shapes, used at every size so the glyph stays readable in the tray."""
    color = QColor(TRAY_COLORS[glyph])
    p = _painter(pixmap)
    p.setBrush(color)
    _dot(p, 16, 16, 15)
    p.setBrush(WHITE)
    if glyph in ("watching", "unavailable", "stale"):  # upright figure
        _dot(p, 16, 9.5, 3.8)
        p.drawRoundedRect(QRectF(12.5, 15, 7, 11), 3.5, 3.5)
    if glyph == "absent":  # outlined figure
        _stroke(p, WHITE, 3)
        _dot(p, 16, 9.5, 3.4)
        p.drawRoundedRect(QRectF(13, 15.5, 6, 10), 3, 3)
    if glyph == "unavailable":  # struck through, with a coloured gap around the white slash
        clip = QPainterPath()
        clip.addEllipse(QPointF(16, 16), 15, 15)
        p.setClipPath(clip)  # the gap's round caps would otherwise poke past the circle
        _stroke(p, color, 7)
        p.drawLine(QPointF(7, 26), QPointF(25, 6))
        _stroke(p, WHITE, 3.2)
        p.drawLine(QPointF(7, 26), QPointF(25, 6))
    if glyph == "stale":  # alert badge
        _dot(p, 24, 8, 7)
        p.setBrush(color)
        p.drawRoundedRect(QRectF(22.5, 3.5, 3, 6), 1.5, 1.5)
        _dot(p, 24, 12.2, 1.6)
    if glyph == "paused":
        p.drawRoundedRect(QRectF(10, 8.5, 4.5, 15), 1.5, 1.5)
        p.drawRoundedRect(QRectF(17.5, 8.5, 4.5, 15), 1.5, 1.5)
    if glyph == "calibrating":
        for x in (9, 16, 23):
            _dot(p, x, 16, 3.2)
    p.end()


def _paint_app(pixmap: QPixmap) -> None:
    """Rounded square with the upright figure; the design thickens the figure at small sizes."""
    size = pixmap.width()
    corner, head, body = ((7, 4, (12.5, 15, 7, 11)) if size <= 16 else
                          (7.5, 3.6, (12.8, 15, 6.4, 10.5)) if size <= 32 else
                          (7.5, 3.4, (13, 15, 6, 10.5)))
    p = _painter(pixmap)
    p.setBrush(QColor("#2F7D62"))
    p.drawRoundedRect(QRectF(0, 0, 32, 32), corner, corner)
    p.setBrush(QColor("#F4F1EB"))
    _dot(p, 16, 9.5, head)
    p.drawRoundedRect(QRectF(*body), body[2] / 2, body[2] / 2)
    p.end()


def _icon(paint, sizes: tuple[int, ...]) -> QIcon:
    icon = QIcon()
    for size in sizes:
        pixmap = QPixmap(size, size)
        paint(pixmap)
        icon.addPixmap(pixmap)
    return icon


def tray_icon(glyph: str) -> QIcon:
    return _icon(lambda pixmap: _paint_tray(pixmap, glyph), (16, 20, 24, 32, 48, 64))


def app_icon() -> QIcon:
    return _icon(_paint_app, ICO_SIZES)



def write_ico(path: str) -> None:
    """Writes the app icon as a multi-size .ico of PNG images (Qt's own ICO writer stores one size only)."""
    import struct
    from PySide6.QtCore import QBuffer, QByteArray

    images = []
    for size in ICO_SIZES:
        pixmap = QPixmap(size, size)
        _paint_app(pixmap)
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QBuffer.WriteOnly)
        pixmap.save(buffer, "PNG")
        images.append((size, bytes(data)))
    offset = 6 + 16 * len(images)
    with open(path, "wb") as ico:
        ico.write(struct.pack("<HHH", 0, 1, len(images)))
        for size, png in images:
            ico.write(struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png), offset))
            offset += len(png)
        for _, png in images:
            ico.write(png)


if __name__ == "__main__":  # regenerate the checked-in icon: python -m holdup.icons assets/holdup.ico
    import sys
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication(sys.argv)
    write_ico(sys.argv[1])
