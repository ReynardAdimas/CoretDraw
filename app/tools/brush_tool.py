"""
BrushTool — tool untuk menggambar bebas (freehand brush).
"""
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent, QPainterPath, QImage, QPainter, QPen, QColor

from app.tools.base_tools import BaseTool
from app.models.graphic_object import GraphicObject


class BrushTool(BaseTool):
    """
    Tool brush freehand.

    Saat mouse ditekan → buat GraphicObject baru bertipe 'brush' dengan QPainterPath
    Saat mouse digerak → tambahkan titik ke path dan update preview
    Saat mouse dilepas → commit ke canvas
    """

    def __init__(self, canvas):
        super().__init__(canvas)
        self._current_obj: GraphicObject | None = None

    def on_press(self, pos: QPointF, event: QMouseEvent) -> None:
        # Simpan state untuk undo sebelum mulai menggambar
        self.canvas.history.push(self.canvas.clone_state())

        path = QPainterPath()
        path.moveTo(pos)

        self._current_obj = GraphicObject(
            kind="brush",
            points=[pos],
            stroke=self.canvas.stroke_color,
            fill=QColor(0, 0, 0, 0),
            width=self.canvas.line_width,
            path=path,
        )
        self.canvas.objects.append(self._current_obj)
        self.canvas.update()

    def on_move(self, pos: QPointF, event: QMouseEvent) -> None:
        if self._current_obj is not None and event.buttons() & Qt.LeftButton:
            self._current_obj.path.lineTo(pos)
            self._current_obj.points.append(pos)
            self.canvas.update()

    def on_release(self, pos: QPointF, event: QMouseEvent) -> None:
        if self._current_obj is not None:
            self._current_obj.path.lineTo(pos)
            self._current_obj.points.append(pos)
            self._current_obj = None
            self.canvas.update()