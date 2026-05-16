from dataclasses import dataclass, field 
from typing import List, Optional 
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QImage, QPainterPath 

@dataclass 
class GraphicObject: 
    kind: str
    points: List[QPointF] = field(default_factory=list)
    stroke: QColor = field(default_factory=lambda: QColor("#111827"))
    fill: QColor = field(default_factory=lambda: QColor(0, 0, 0, 0))
    width: int = 2
    line_algo: str = "bresenham"
    circle_algo: str = "midpoint"
    ellipse_algo: str = "midpoint"
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    selected: bool = False
    image: Optional[QImage] = None
    path: Optional[QPainterPath] = None 

    def center(self) -> QPointF:
        """Hitung titik tengah bounding box objek."""
        if not self.points:
            return QPointF(0, 0)
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        return QPointF((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)

    def bounding_rect(self):
        """Kembalikan (x_min, y_min, x_max, y_max) dari semua titik."""
        if not self.points:
            return (0, 0, 0, 0)
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys)) 
    
    def move_by(self, dx: float, dy: float) -> None:
        """Translasikan objek sejauh (dx, dy)."""
        self.points = [QPointF(p.x() + dx, p.y() + dy) for p in self.points]
        # Untuk objek bitmap (brush/fill), translasikan juga isi imagenya
        if self.image is not None and not self.image.isNull():
            from PySide6.QtGui import QPainter
            moved = QImage(self.image.size(), self.image.format())
            moved.setDevicePixelRatio(self.image.devicePixelRatio())
            moved.fill(QColor(0, 0, 0, 0))
            painter = QPainter(moved)
            painter.drawImage(QPointF(dx, dy), self.image)
            painter.end()
            self.image = moved
    
    def clone(self) -> "GraphicObject":
        """Buat salinan dalam (deep copy) objek ini untuk keperluan undo/redo."""
        from PySide6.QtGui import QPainterPath
        return GraphicObject(
            kind=self.kind,
            points=[QPointF(p) for p in self.points],
            stroke=QColor(self.stroke),
            fill=QColor(self.fill),
            width=self.width,
            line_algo=self.line_algo,
            circle_algo=self.circle_algo,
            ellipse_algo=self.ellipse_algo,
            rotation=self.rotation,
            scale_x=self.scale_x,
            scale_y=self.scale_y,
            selected=self.selected,
            image=self.image.copy() if self.image is not None else None,
            path=QPainterPath(self.path) if self.path is not None else None,
        )