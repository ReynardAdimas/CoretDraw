import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF

from app.models.graphic_object import GraphicObject
from app.algorithms.line import bresenham_line, dda_line
from app.algorithms.circle import midpoint_circle, bresenham_circle
from app.algorithms.ellipse import midpoint_ellipse, bresenham_ellipse


class Renderer:
    """
    Bertanggung jawab menggambar satu GraphicObject ke QPainter.
    Pemisahan ini memastikan logika rendering tidak bercampur dengan
    logika event handling di CanvasWidget.
    """

    def draw(self, painter: QPainter, obj: GraphicObject, preview: bool = False) -> None:
        if obj.image is not None:
            painter.drawImage(0, 0, obj.image)
            if obj.selected and obj.points:
                self._draw_selection_box(painter, obj)
            return

        painter.save()
        c = obj.center()
        painter.translate(c)
        painter.rotate(obj.rotation)
        painter.scale(obj.scale_x, obj.scale_y)
        painter.translate(-c)

        color = QColor(obj.stroke)
        if preview:
            color.setAlpha(150)

        pen = QPen(color, obj.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(obj.fill) if obj.fill.alpha() > 0 else Qt.NoBrush)

        if obj.kind == "point":
            self._draw_point(painter, obj)
        elif obj.kind == "line":
            self._draw_line(painter, obj)
        elif obj.kind == "circle":
            self._draw_circle(painter, obj)
        elif obj.kind == "ellipse":
            self._draw_ellipse(painter, obj)
        elif obj.kind == "rectangle":
            self._draw_rectangle(painter, obj)
        elif obj.kind == "triangle":
            self._draw_triangle(painter, obj)
        elif obj.kind == "trapezoid":
            self._draw_trapezoid(painter, obj)
        elif obj.kind in {"brush", "eraser"}:
            self._draw_brush(painter, obj)

        painter.restore()

    # ← dipindah ke sini, di luar save/restore
        if obj.selected and obj.points:
            self._draw_selection_box(painter, obj)
    # ── Shape renderers ─────────────────────────────────────────────────────

    def _draw_point(self, painter: QPainter, obj: GraphicObject) -> None:
        p = obj.points[0]
        r = max(3, obj.width)
        painter.drawEllipse(p, r, r)

    def _draw_line(self, painter: QPainter, obj: GraphicObject) -> None:
        x0, y0 = int(obj.points[0].x()), int(obj.points[0].y())
        x1, y1 = int(obj.points[1].x()), int(obj.points[1].y())

        if obj.line_algo == "dda":
            pixels = dda_line(x0, y0, x1, y1)
        else:
            pixels = bresenham_line(x0, y0, x1, y1)

        for x, y in pixels:
            painter.drawPoint(x, y)

    def _draw_circle(self, painter: QPainter, obj: GraphicObject) -> None:
        if len(obj.points) < 2:
            return
        center = obj.points[0]
        edge = obj.points[1]
        r = int(math.hypot(edge.x() - center.x(), edge.y() - center.y()))
        cx, cy = int(center.x()), int(center.y())

        # Gambar fill dulu dengan Qt jika ada fill color
        if obj.fill.alpha() > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(obj.fill))
            painter.drawEllipse(center, float(r), float(r))

        # Kembalikan pen untuk outline
        pen = QPen(obj.stroke, obj.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # BUG FIX: loop drawPoint yang sebelumnya hilang
        if obj.circle_algo == "bresenham":
            pixels = bresenham_circle(cx, cy, r)
        else:
            pixels = midpoint_circle(cx, cy, r)

        for x, y in pixels:
            painter.drawPoint(x, y)

    def _draw_ellipse(self, painter: QPainter, obj: GraphicObject) -> None:
        if len(obj.points) < 2:
            return
        rect = QRectF(obj.points[0], obj.points[1]).normalized()
        cx = int(rect.center().x())
        cy = int(rect.center().y())
        rx = int(rect.width() / 2)
        ry = int(rect.height() / 2)

        # Fill
        if obj.fill.alpha() > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(obj.fill))
            painter.drawEllipse(rect)

        pen = QPen(obj.stroke, obj.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # BUG FIX: loop drawPoint yang sebelumnya hilang
        if obj.ellipse_algo == "bresenham":
            pixels = bresenham_ellipse(cx, cy, rx, ry)
        else:
            pixels = midpoint_ellipse(cx, cy, rx, ry)

        for x, y in pixels:
            painter.drawPoint(x, y)

    def _draw_rectangle(self, painter: QPainter, obj: GraphicObject) -> None:
        if len(obj.points) < 2:
            return
        rect = QRectF(obj.points[0], obj.points[1]).normalized()
        painter.drawRect(rect)

    def _draw_triangle(self, painter: QPainter, obj: GraphicObject) -> None:
        if len(obj.points) < 2:
            return
        rect = QRectF(obj.points[0], obj.points[1]).normalized()
        points = [
            QPointF(rect.center().x(), rect.top()),
            QPointF(rect.left(), rect.bottom()),
            QPointF(rect.right(), rect.bottom()),
        ]
        self._draw_algorithm_polygon(painter, obj, points)

    def _draw_trapezoid(self, painter: QPainter, obj: GraphicObject) -> None:
        if len(obj.points) < 2:
            return
        rect = QRectF(obj.points[0], obj.points[1]).normalized()
        inset = rect.width() * 0.25
        points = [
            QPointF(rect.left() + inset, rect.top()),
            QPointF(rect.right() - inset, rect.top()),
            QPointF(rect.right(), rect.bottom()),
            QPointF(rect.left(), rect.bottom()),
        ]
        self._draw_algorithm_polygon(painter, obj, points)

    def _draw_algorithm_polygon(
        self, painter: QPainter, obj: GraphicObject, points: list[QPointF]
    ) -> None:
        if obj.fill.alpha() > 0:
            current_pen = painter.pen()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(obj.fill))
            painter.drawPolygon(QPolygonF(points))
            painter.setPen(current_pen)
            painter.setBrush(Qt.NoBrush)

        for start, end in zip(points, points[1:] + points[:1]):
            x0, y0 = int(start.x()), int(start.y())
            x1, y1 = int(end.x()), int(end.y())
            if obj.line_algo == "dda":
                pixels = dda_line(x0, y0, x1, y1)
            else:
                pixels = bresenham_line(x0, y0, x1, y1)
            for x, y in pixels:
                painter.drawPoint(x, y)

    def _draw_brush(self, painter: QPainter, obj: GraphicObject) -> None:
        if obj.path is not None:
            painter.drawPath(obj.path)

    def _draw_selection_box(self, painter: QPainter, obj: GraphicObject) -> None:
        import math
        if obj.kind == "circle" and len(obj.points) >= 2:
            cx, cy = obj.points[0].x(), obj.points[0].y()
            r = math.hypot(obj.points[1].x() - cx, obj.points[1].y() - cy)
            x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
        else:
            x0, y0, x1, y1 = obj.bounding_rect()
    
        sel_pen = QPen(QColor("#2563eb"), 1, Qt.DashLine)
        painter.setPen(sel_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(x0 - 6, y0 - 6, x1 - x0 + 12, y1 - y0 + 12))
