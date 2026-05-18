"""
EraserTool — tool untuk menghapus dengan menggambar warna putih di atas canvas.
"""
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent, QPainterPath, QColor

from app.tools.base_tools import BaseTool
from app.models.graphic_object import GraphicObject


class EraserTool(BaseTool):
    """
    Tool eraser — menggambar path berwarna putih di atas canvas,
    efeknya seolah-olah menghapus gambar di bawahnya.
    """

    def __init__(self, canvas):
        super().__init__(canvas)
        self._current_obj: GraphicObject | None = None

    def on_press(self, pos: QPointF, event: QMouseEvent) -> None:
        self.canvas.history.push(self.canvas.clone_state())

        path = QPainterPath()
        path.moveTo(pos)

        self._current_obj = GraphicObject(
            kind="eraser",
            points=[pos],
            stroke=QColor("#ffffff"),   # warna putih = efek hapus
            fill=QColor(0, 0, 0, 0),
            width=max(self.canvas.line_width * 3, 12),  # eraser lebih tebal
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