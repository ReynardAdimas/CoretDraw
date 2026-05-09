import math
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QPainter, QPainterPath, QPen, QBrush, QPixmap, QImage, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QColorDialog, QDialog, QDoubleSpinBox, QFileDialog, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QSlider, QSpinBox, QStatusBar, QVBoxLayout, QWidget, QInputDialog
)


@dataclass
class GraphicObject:
    kind: str
    points: List[QPointF] = field(default_factory=list)
    stroke: QColor = field(default_factory=lambda: QColor("#111827"))
    fill: QColor = field(default_factory=lambda: QColor(0, 0, 0, 0))
    width: int = 3
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    selected: bool = False

    def center(self) -> QPointF:
        if not self.points:
            return QPointF(0, 0)
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        return QPointF((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)

    def move_by(self, dx: float, dy: float) -> None:
        self.points = [QPointF(p.x() + dx, p.y() + dy) for p in self.points]

    def rect(self) -> QRectF:
        if not self.points:
            return QRectF()
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        return QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)).normalized()

    def contains(self, point: QPointF) -> bool:
        r = self.rect().adjusted(-8, -8, 8, 8)
        if self.kind in {"line", "brush", "polygon"}:
            return r.contains(point)
        return r.contains(point)


class TransformDialog(QDialog):
    def __init__(self, title: str, fields: List[Tuple[str, float, float, float]], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.values = []
        layout = QFormLayout(self)
        for label, default, minimum, maximum in fields:
            spin = QDoubleSpinBox()
            spin.setRange(minimum, maximum)
            spin.setValue(default)
            spin.setDecimals(2)
            spin.setSingleStep(1.0)
            layout.addRow(label, spin)
            self.values.append(spin)
        buttons = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        cancel_btn = QPushButton("Cancel")
        apply_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(apply_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

    def get_values(self):
        return [s.value() for s in self.values]


class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 350)
        self.setMouseTracking(True)
        self.objects: List[GraphicObject] = []
        self.undo_stack: List[List[GraphicObject]] = []
        self.redo_stack: List[List[GraphicObject]] = []
        self.current_tool = "select"
        self.stroke = QColor("#111827")
        self.fill = QColor(0, 0, 0, 0)
        self.line_width = 3
        self.grid_size = 25
        self.start: Optional[QPointF] = None
        self.preview: Optional[GraphicObject] = None
        self.selected: Optional[GraphicObject] = None
        self.dragging_selected = False
        self.last_pos: Optional[QPointF] = None
        self.current_brush: Optional[GraphicObject] = None
        self.poly_points: List[QPointF] = []
        self.animation_mode: Optional[str] = None
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.step_animation)
        self.anim_angle = 0
        self.parent_window = parent

    def clone_state(self):
        import copy
        return copy.deepcopy(self.objects)

    def push_undo(self):
        self.undo_stack.append(self.clone_state())
        self.redo_stack.clear()
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def set_tool(self, tool: str):
        self.current_tool = tool
        self.preview = None
        self.current_brush = None
        self.poly_points = [] if tool != "polygon" else self.poly_points
        self.update_status(self.status_text())
        if self.parent_window and hasattr(self.parent_window, "update_tool_buttons"):
            self.parent_window.update_tool_buttons(tool)
        self.update()

    def color_label(self, color: QColor) -> str:
        if color.alpha() == 0:
            return "None"
        return color.name().upper()

    def status_text(self, prefix: str = "") -> str:
        parts = []
        if prefix:
            parts.append(prefix)
        parts.append(f"Mode: {self.current_tool.title()}")
        parts.append(f"Stroke: {self.color_label(self.stroke)}")
        parts.append(f"Fill: {self.color_label(self.fill)}")
        parts.append(f"Size: {self.line_width}")
        return " | ".join(parts)

    def update_status(self, text: str = ""):
        if self.parent_window and hasattr(self.parent_window, "status"):
            self.parent_window.status.showMessage(text if text else self.status_text())

    def snap(self, p: QPointF) -> QPointF:
        return p

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        for obj in self.objects:
            self.draw_object(painter, obj)
        if self.preview:
            self.draw_object(painter, self.preview, preview=True)
        if self.poly_points:
            pen = QPen(QColor("#2563eb"), 2, Qt.DashLine)
            painter.setPen(pen)
            for i in range(len(self.poly_points) - 1):
                painter.drawLine(self.poly_points[i], self.poly_points[i + 1])
            for p in self.poly_points:
                painter.drawEllipse(p, 3, 3)


    def draw_object(self, painter: QPainter, obj: GraphicObject, preview=False):
        painter.save()
        c = obj.center()
        painter.translate(c)
        painter.rotate(obj.rotation)
        painter.scale(obj.scale_x, obj.scale_y)
        painter.translate(-c)
        color = QColor(obj.stroke)
        if preview:
            color.setAlpha(140)
        pen = QPen(color, obj.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        if obj.selected:
            pen = QPen(QColor("#2563eb"), max(2, obj.width), Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(obj.fill))
        if obj.kind == "point":
            p = obj.points[0]
            painter.drawEllipse(p, max(3, obj.width), max(3, obj.width))
        elif obj.kind == "line":
            painter.drawLine(obj.points[0], obj.points[1])
        elif obj.kind == "circle":
            center, edge = obj.points[0], obj.points[1]
            r = math.hypot(edge.x() - center.x(), edge.y() - center.y())
            painter.drawEllipse(center, r, r)
        elif obj.kind == "ellipse":
            painter.drawEllipse(QRectF(obj.points[0], obj.points[1]).normalized())
        elif obj.kind == "rectangle":
            painter.drawRect(QRectF(obj.points[0], obj.points[1]).normalized())
        elif obj.kind == "polygon":
            if len(obj.points) > 1:
                painter.drawPolygon(obj.points)
        elif obj.kind in {"brush", "eraser"}:
            path = QPainterPath(obj.points[0])
            for p in obj.points[1:]:
                path.lineTo(p)
            painter.drawPath(path)
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        p = self.snap(QPointF(event.position()))
        self.start = p
        self.last_pos = p
        if self.current_tool == "select":
            self.select_at(p)
        elif self.current_tool == "move":
            self.select_at(p)
            self.dragging_selected = self.selected is not None
            if self.dragging_selected:
                self.push_undo()
        elif self.current_tool == "point":
            self.push_undo()
            self.objects.append(GraphicObject("point", [p], self.stroke, self.fill, self.line_width))
            self.update()
        elif self.current_tool in {"brush", "eraser"}:
            self.push_undo()
            stroke = QColor("#ffffff") if self.current_tool == "eraser" else self.stroke
            self.current_brush = GraphicObject(self.current_tool, [p], stroke, QColor(0,0,0,0), self.line_width)
            self.objects.append(self.current_brush)
        elif self.current_tool == "polygon":
            self.poly_points.append(p)
            self.update()
        else:
            self.preview = GraphicObject(self.current_tool, [p, p], self.stroke, self.fill, self.line_width)

    def mouseMoveEvent(self, event):
        p = self.snap(QPointF(event.position()))
        self.update_status(self.status_text(f"Coordinate: x={int(p.x())}, y={int(p.y())}"))
        if self.dragging_selected and self.selected and self.last_pos:
            dx, dy = p.x() - self.last_pos.x(), p.y() - self.last_pos.y()
            self.selected.move_by(dx, dy)
            self.last_pos = p
            self.update()
        elif self.current_brush:
            self.current_brush.points.append(p)
            self.update()
        elif self.preview and self.start:
            self.preview.points = [self.start, p]
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        p = self.snap(QPointF(event.position()))
        if self.preview:
            self.push_undo()
            self.preview.points = [self.start, p]
            self.objects.append(self.preview)
            self.preview = None
            self.update()
        self.dragging_selected = False
        self.current_brush = None

    def mouseDoubleClickEvent(self, event):
        if self.current_tool == "polygon" and len(self.poly_points) >= 3:
            self.push_undo()
            self.objects.append(GraphicObject("polygon", list(self.poly_points), self.stroke, self.fill, self.line_width))
            self.poly_points.clear()
            self.update()

    def select_at(self, p: QPointF):
        for obj in self.objects:
            obj.selected = False
        self.selected = None
        for obj in reversed(self.objects):
            if obj.contains(p):
                obj.selected = True
                self.selected = obj
                break
        self.update()
        if self.selected:
            self.update_status(
                f"Selected: {self.selected.kind.title()} | "
                f"X={int(self.selected.center().x())}, Y={int(self.selected.center().y())} | "
                f"Stroke: {self.color_label(self.selected.stroke)} | "
                f"Fill: {self.color_label(self.selected.fill)} | "
                f"Size: {self.selected.width}"
            )
        else:
            self.update_status(self.status_text("Selected: None"))

    def clear(self):
        self.push_undo()
        self.objects.clear()
        self.selected = None
        self.update()

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self.clone_state())
        self.objects = self.undo_stack.pop()
        self.selected = None
        self.update()

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self.clone_state())
        self.objects = self.redo_stack.pop()
        self.selected = None
        self.update()

    def export_png(self, filename: str):
        image = QImage(self.size(), QImage.Format_ARGB32)
        image.fill(QColor("#ffffff"))
        painter = QPainter(image)
        self.render(painter)
        painter.end()
        image.save(filename)

    def grayscale_selected(self):
        if not self.selected:
            return
        self.push_undo()
        for attr in ["stroke", "fill"]:
            col = getattr(self.selected, attr)
            gray = int(0.299 * col.red() + 0.587 * col.green() + 0.114 * col.blue())
            setattr(self.selected, attr, QColor(gray, gray, gray, col.alpha()))
        self.update()

    def bring_front(self):
        if self.selected and self.selected in self.objects:
            self.push_undo()
            self.objects.remove(self.selected)
            self.objects.append(self.selected)
            self.update()

    def send_back(self):
        if self.selected and self.selected in self.objects:
            self.push_undo()
            self.objects.remove(self.selected)
            self.objects.insert(0, self.selected)
            self.update()

    def translate_selected(self, dx: float, dy: float):
        if self.selected:
            self.push_undo()
            self.selected.move_by(dx, dy)
            self.update()

    def rotate_selected(self, angle: float):
        if self.selected:
            self.push_undo()
            self.selected.rotation += angle
            self.update()

    def scale_selected(self, sx: float, sy: float):
        if self.selected:
            self.push_undo()
            self.selected.scale_x *= sx
            self.selected.scale_y *= sy
            self.update()

    def reset_transform(self):
        if self.selected:
            self.push_undo()
            self.selected.rotation = 0
            self.selected.scale_x = 1
            self.selected.scale_y = 1
            self.update()

    def start_animation(self, mode: str):
        if not self.selected:
            QMessageBox.information(self, "CoretDraw", "Pilih objek terlebih dahulu dengan tool Select.")
            return
        self.animation_mode = mode
        self.anim_timer.start(30)

    def stop_animation(self):
        self.animation_mode = None
        self.anim_timer.stop()

    def step_animation(self):
        obj = self.selected
        if not obj:
            self.stop_animation(); return
        if self.animation_mode == "move":
            obj.move_by(2, 0)
            if obj.rect().right() > self.width():
                obj.move_by(-self.width() + 50, 0)
        elif self.animation_mode == "rotate":
            obj.rotation += 3
        elif self.animation_mode == "scale":
            self.anim_angle += 5
            s = 1 + 0.01 * math.sin(math.radians(self.anim_angle))
            obj.scale_x *= s
            obj.scale_y *= s
        elif self.animation_mode == "bounce":
            obj.move_by(3, 2)
            r = obj.rect()
            if r.right() > self.width() or r.bottom() > self.height():
                obj.move_by(-80, -60)
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoretDraw - Aplikasi Grafika 2D Interaktif")
        self.resize(1200, 760)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.canvas = Canvas(self)
        self.tool_buttons = {}
        self.build_ui()
        self.build_menu()
        self.apply_style()
        self.status.showMessage("CoretDraw siap digunakan. Pilih tool di sidebar.")

    def build_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(190)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(12, 12, 12, 12)
        side.setSpacing(8)
        self.add_section(side, "TOOLS", [("Select", "select"), ("Move", "move"), ("Brush", "brush"), ("Eraser", "eraser")])
        self.add_section(side, "SHAPES", [("Point", "point"), ("Line", "line"), ("Circle", "circle"), ("Ellipse", "ellipse"), ("Rectangle", "rectangle"), ("Polygon", "polygon")])
        side.addWidget(QLabel("STYLE"))
        stroke_btn = QPushButton("Stroke Color")
        fill_btn = QPushButton("Fill Color")
        stroke_btn.clicked.connect(self.pick_stroke)
        fill_btn.clicked.connect(self.pick_fill)

        self.stroke_chip = QLabel()
        self.stroke_chip.setObjectName("colorChip")
        self.stroke_text = QLabel("Stroke: #111827")
        stroke_row = QHBoxLayout()
        stroke_row.addWidget(self.stroke_chip)
        stroke_row.addWidget(self.stroke_text, 1)

        self.fill_chip = QLabel()
        self.fill_chip.setObjectName("colorChip")
        self.fill_text = QLabel("Fill: None")
        fill_row = QHBoxLayout()
        fill_row.addWidget(self.fill_chip)
        fill_row.addWidget(self.fill_text, 1)

        side.addWidget(stroke_btn)
        side.addLayout(stroke_row)
        side.addWidget(fill_btn)
        side.addLayout(fill_row)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size / Width"))
        self.size_text = QLabel("3 px")
        self.size_text.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        size_row.addWidget(self.size_text, 1)
        side.addLayout(size_row)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(1, 30)
        slider.setValue(3)
        self.size_slider = slider
        slider.valueChanged.connect(self.change_line_width)
        side.addWidget(slider)
        self.update_style_indicators()
        side.addStretch()
        layout.addWidget(sidebar)
        canvas_wrap = QFrame()
        canvas_wrap.setObjectName("canvasWrap")
        wrap = QVBoxLayout(canvas_wrap)
        wrap.setContentsMargins(14, 14, 14, 14)
        wrap.addWidget(self.canvas)
        layout.addWidget(canvas_wrap, 1)
        self.setCentralWidget(central)

    def add_section(self, layout, title, buttons):
        label = QLabel(title)
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        grid = QGridLayout()
        grid.setSpacing(6)
        for i, (text, tool) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, t=tool: self.canvas.set_tool(t))
            self.tool_buttons[tool] = btn
            grid.addWidget(btn, i // 2, i % 2)
        layout.addLayout(grid)

    def update_tool_buttons(self, active_tool: str):
        for tool, button in self.tool_buttons.items():
            button.setChecked(tool == active_tool)

    def color_name(self, color: QColor) -> str:
        if color.alpha() == 0:
            return "None"
        return color.name().upper()

    def chip_style(self, color: QColor) -> str:
        if color.alpha() == 0:
            return "background: transparent; border: 1px dashed #64748b; border-radius: 5px;"
        return f"background: {color.name()}; border: 1px solid #64748b; border-radius: 5px;"

    def update_style_indicators(self):
        if hasattr(self, "stroke_chip"):
            self.stroke_chip.setStyleSheet(self.chip_style(self.canvas.stroke))
            self.stroke_text.setText(f"Stroke: {self.color_name(self.canvas.stroke)}")
        if hasattr(self, "fill_chip"):
            self.fill_chip.setStyleSheet(self.chip_style(self.canvas.fill))
            self.fill_text.setText(f"Fill: {self.color_name(self.canvas.fill)}")
        if hasattr(self, "size_text"):
            self.size_text.setText(f"{self.canvas.line_width} px")
        if hasattr(self, "status"):
            self.status.showMessage(self.canvas.status_text())

    def change_line_width(self, value: int):
        self.canvas.line_width = value
        if self.canvas.selected:
            self.canvas.push_undo()
            self.canvas.selected.width = value
            self.canvas.update()
        self.update_style_indicators()

    def build_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        new_act = QAction("New Canvas", self); new_act.triggered.connect(self.canvas.clear)
        export_act = QAction("Export PNG", self); export_act.triggered.connect(self.export_png)
        exit_act = QAction("Exit", self); exit_act.triggered.connect(self.close)
        file_menu.addActions([new_act, export_act, exit_act])
        edit_menu = menubar.addMenu("Edit")
        undo = QAction("Undo", self)
        undo.setShortcut(QKeySequence("Ctrl+Z"))
        undo.setStatusTip("Batalkan aksi terakhir (Ctrl+Z)")
        undo.triggered.connect(self.canvas.undo)
        redo = QAction("Redo", self)
        redo.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        redo.setStatusTip("Ulangi aksi yang dibatalkan (Ctrl+Shift+Z)")
        redo.triggered.connect(self.canvas.redo)
        clear = QAction("Clear Canvas", self); clear.triggered.connect(self.canvas.clear)
        delete = QAction("Delete Object", self); delete.triggered.connect(self.delete_selected)
        edit_menu.addActions([undo, redo, clear, delete])
        view = menubar.addMenu("View")
        coord_info = QAction("Coordinate is shown in status bar", self)
        coord_info.setEnabled(False)
        view.addAction(coord_info)
        obj = menubar.addMenu("Object")
        front = QAction("Bring to Front", self); front.triggered.connect(self.canvas.bring_front)
        back = QAction("Send to Back", self); back.triggered.connect(self.canvas.send_back)
        gray = QAction("Grayscale", self); gray.triggered.connect(self.canvas.grayscale_selected)
        obj.addActions([front, back, gray])
        trans = menubar.addMenu("Transform")
        t = QAction("Translate", self); t.triggered.connect(self.translate_dialog)
        r = QAction("Rotate", self); r.triggered.connect(self.rotate_dialog)
        s = QAction("Scale", self); s.triggered.connect(self.scale_dialog)
        reset = QAction("Reset Transform", self); reset.triggered.connect(self.canvas.reset_transform)
        trans.addActions([t, r, s, reset])
        anim = menubar.addMenu("Animation")
        for name, mode in [("Move Animation", "move"), ("Rotate Animation", "rotate"), ("Scale Animation", "scale"), ("Bounce Animation", "bounce")]:
            a = QAction(name, self); a.triggered.connect(lambda checked=False, m=mode: self.canvas.start_animation(m)); anim.addAction(a)
        stop = QAction("Stop Animation", self); stop.triggered.connect(self.canvas.stop_animation); anim.addAction(stop)
        helpm = menubar.addMenu("Help")
        about = QAction("About App", self); about.triggered.connect(self.about)
        formula = QAction("Formula / Matrix", self); formula.triggered.connect(self.formulas)
        helpm.addActions([about, formula])

    def pick_stroke(self):
        col = QColorDialog.getColor(self.canvas.stroke, self, "Stroke Color")
        if col.isValid():
            self.canvas.stroke = col
            if self.canvas.selected:
                self.canvas.push_undo()
                self.canvas.selected.stroke = col; self.canvas.update()
            self.update_style_indicators()

    def pick_fill(self):
        col = QColorDialog.getColor(self.canvas.fill, self, "Fill Color")
        if col.isValid():
            self.canvas.fill = col
            if self.canvas.selected:
                self.canvas.push_undo()
                self.canvas.selected.fill = col; self.canvas.update()
            self.update_style_indicators()


    def export_png(self):
        name, _ = QFileDialog.getSaveFileName(self, "Export PNG", "coretdraw.png", "PNG Images (*.png)")
        if name:
            self.canvas.export_png(name)
            self.status.showMessage(f"Export berhasil: {name}")

    def delete_selected(self):
        if self.canvas.selected:
            self.canvas.push_undo()
            self.canvas.objects.remove(self.canvas.selected)
            self.canvas.selected = None
            self.canvas.update()

    def translate_dialog(self):
        d = TransformDialog("Translate Object", [("X", 50, -1000, 1000), ("Y", 20, -1000, 1000)], self)
        if d.exec():
            dx, dy = d.get_values(); self.canvas.translate_selected(dx, dy)

    def rotate_dialog(self):
        d = TransformDialog("Rotate Object", [("Angle", 45, -360, 360)], self)
        if d.exec():
            self.canvas.rotate_selected(d.get_values()[0])

    def scale_dialog(self):
        d = TransformDialog("Scale Object", [("Scale X", 1.5, 0.1, 10), ("Scale Y", 1.5, 0.1, 10)], self)
        if d.exec():
            sx, sy = d.get_values(); self.canvas.scale_selected(sx, sy)

    def formulas(self):
        QMessageBox.information(self, "Formula / Matrix", "Translasi:\nx' = x + tx\ny' = y + ty\n\nRotasi:\nx' = x cos θ - y sin θ\ny' = x sin θ + y cos θ\n\nSkala:\nx' = x × sx\ny' = y × sy")

    def about(self):
        QMessageBox.information(self, "About CoretDraw", "CoretDraw adalah aplikasi grafika komputer 2D interaktif.\n\nFitur: brush, shape presisi, transformasi 2D, animasi, status warna, dan export PNG.")

    def apply_style(self):
        self.setStyleSheet("""
        QMainWindow { background: #f5f6f8; }
        QMenuBar { background: #ffffff; color: #111827; padding: 4px; border-bottom: 1px solid #d0d5dd; }
        QMenuBar::item { color: #111827; padding: 6px 10px; }
        QMenuBar::item:selected { background: #e0ecff; color: #111827; }
        QMenu { background: #ffffff; color: #111827; border: 1px solid #d0d5dd; }
        QMenu::item { color: #111827; padding: 6px 22px; }
        QMenu::item:selected { background: #e0ecff; color: #111827; }
        #sidebar { background: #ffffff; border-right: 1px solid #d0d5dd; }
        #canvasWrap { background: #e9ecf1; }
        Canvas { background: #ffffff; border: 1px solid #d0d5dd; }
        QPushButton { background: #f8fafc; color: #111827; border: 1px solid #d0d5dd; border-radius: 6px; padding: 6px; font-weight: 500; }
        QPushButton:hover { background: #e0ecff; color: #111827; }
        QPushButton:pressed { background: #bfdbfe; color: #111827; }
        QPushButton:checked { background: #2563eb; color: #ffffff; border-color: #1d4ed8; }
        QPushButton:disabled { background: #f1f5f9; color: #94a3b8; }
        QLabel#sectionLabel, QLabel { color: #1f2937; font-weight: 600; }
        QLabel#colorChip { min-width: 24px; max-width: 24px; min-height: 18px; max-height: 18px; }
        QStatusBar { background: #ffffff; color: #111827; border-top: 1px solid #d0d5dd; }
        QSlider::groove:horizontal { height: 4px; background: #cbd5e1; border-radius: 2px; }
        QSlider::handle:horizontal { background: #2563eb; border: 1px solid #1d4ed8; width: 14px; margin: -5px 0; border-radius: 7px; }
        """)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()
