"""
SelectTool - tool untuk memilih dan memindahkan objek di canvas.
"""
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QMouseEvent

from app.tools.base_tools import BaseTool
from app.models.graphic_object import GraphicObject


class SelectTool(BaseTool):
    """
    Tool untuk memilih objek dengan klik, drag objek untuk memindahkan,
    dan drag area kosong untuk membuat kotak seleksi bergaris putus-putus.
    """

    def __init__(self, canvas):
        super().__init__(canvas)
        self._dragging = False
        self._selecting = False
        self._last_pos: QPointF | None = None
        self._selection_start: QPointF | None = None
        self._moved = False

    def on_press(self, pos: QPointF, event: QMouseEvent) -> None:
        hit = self._hit_test(pos)

        if hit is not None:
            if not hit.selected:
                self._deselect_all()
                hit.selected = True
                self.canvas.selected_objects = [hit]
            self._dragging = True
            self._last_pos = pos
            self._moved = False
        else:
            self._deselect_all()
            self._selecting = True
            self._selection_start = pos
            self.canvas.selection_rect_preview = QRectF(pos, pos)

        self.canvas.update()

    def on_move(self, pos: QPointF, event: QMouseEvent) -> None:
        if self._dragging and self._last_pos is not None and self.canvas.selected_objects:
            dx = pos.x() - self._last_pos.x()
            dy = pos.y() - self._last_pos.y()
            for obj in self.canvas.selected_objects:
                obj.move_by(dx, dy)
            self._last_pos = pos
            self._moved = True
            self.canvas.update()
        elif self._selecting and self._selection_start is not None:
            self.canvas.selection_rect_preview = QRectF(self._selection_start, pos)
            self.canvas.update()

    def on_release(self, pos: QPointF, event: QMouseEvent) -> None:
        if self._dragging and self._moved:
            pass
        elif self._selecting and self._selection_start is not None:
            rect = QRectF(self._selection_start, pos).normalized()
            if rect.width() >= 4 or rect.height() >= 4:
                self._select_objects_in_rect(rect)
            self.canvas.selection_rect_preview = None
            self.canvas.update()

        self._dragging = False
        self._selecting = False
        self._last_pos = None
        self._selection_start = None

    def _hit_test(self, pos: QPointF) -> GraphicObject | None:
        """
        Cari objek yang berada di bawah posisi klik.
        Iterasi dimulai dari objek paling atas.
        """
        threshold = 8.0
        for obj in reversed(self.canvas.objects):
            if self._point_in_object(pos, obj, threshold):
                return obj
        return None

    def _point_in_object(self, pos: QPointF, obj: GraphicObject, threshold: float) -> bool:
        """Cek apakah posisi klik berada di dalam atau dekat bounding box objek."""
        if not obj.points:
            return False
        x0, y0, x1, y1 = obj.bounding_rect()
        return (
            x0 - threshold <= pos.x() <= x1 + threshold
            and y0 - threshold <= pos.y() <= y1 + threshold
        )

    def _select_objects_in_rect(self, rect: QRectF) -> None:
        """Pilih semua objek yang bounding box-nya bersinggungan dengan kotak seleksi."""
        selected = []
        for obj in self.canvas.objects:
            obj.selected = False
            obj_rect = self._object_rect(obj)
            if obj_rect is not None and rect.intersects(obj_rect):
                obj.selected = True
                selected.append(obj)
        self.canvas.selected_objects = selected

    def _object_rect(self, obj: GraphicObject) -> QRectF | None:
        if not obj.points:
            return None
        x0, y0, x1, y1 = obj.bounding_rect()
        return QRectF(QPointF(x0, y0), QPointF(x1, y1)).normalized()

    def _deselect_all(self) -> None:
        """Hapus seleksi dari semua objek."""
        for obj in self.canvas.objects:
            obj.selected = False
        self.canvas.selected_objects = []
