"""
Sidebar — panel kontrol di sebelah kiri canvas.

Berisi:
  - Tombol tool (Select, Brush, Eraser, Fill)
  - Dropdown shape (Point, Line, Circle, Ellipse, Rectangle, Triangle, Trapezoid)
  - Pilihan algoritma garis, lingkaran, dan elips
  - Picker warna Stroke dan Fill
  - Slider ukuran brush / ketebalan garis
  - Tombol transformasi (Translate, Rotate, Scale, Grayscale)
  - Tombol Z-order (Bring to Front, Send to Back)
  - Tombol Delete
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider, QComboBox,
    QColorDialog, QWidget, QDoubleSpinBox,
    QDialog, QFormLayout, QSizePolicy
)

from app.tools.select_tool import SelectTool
from app.tools.shape_tool import ShapeTool
from app.tools.brush_tool import BrushTool
from app.tools.eraser_tool import EraserTool
from app.tools.fill_tool import FillTool


# ── Helper Dialog Transformasi ────────────────────────────────────────────────

class TransformDialog(QDialog):
    """Dialog input nilai transformasi (Translate / Rotate / Scale)."""

    def __init__(self, title: str, fields: list, parent=None):
        """
        Args:
            title  : judul dialog
            fields : list of (label, default, min, max)
        """
        super().__init__(parent)
        self.setStyleSheet("""
            QDialog { background: #ffffff; }
            QLabel { color: #111827; background: transparent; }
            QDoubleSpinBox { color: #111827; background: #ffffff; border: 1px solid #d1d5db; border-radius: 4px; padding: 3px; }
            QPushButton { color: #111827; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 5px 8px; }
            QPushButton:hover { background: #e0ecff; }
        """)
        self.setWindowTitle(title)
        self.setWindowTitle(title)
        self._spins = []
        layout = QFormLayout(self)

        for label, default, vmin, vmax in fields:
            spin = QDoubleSpinBox()
            spin.setRange(vmin, vmax)
            spin.setValue(default)
            spin.setDecimals(2)
            spin.setSingleStep(1.0)
            layout.addRow(label, spin)
            self._spins.append(spin)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("Terapkan")
        cancel_btn = QPushButton("Batal")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addRow(btn_row)

    def values(self) -> list:
        return [s.value() for s in self._spins]


# ── Sidebar Utama ─────────────────────────────────────────────────────────────

class Sidebar(QFrame):
    """
    Panel sidebar kiri aplikasi.

    Semua perubahan setting (warna, algoritma, ukuran) langsung
    diupdate ke canvas melalui referensi self._canvas.
    """

    def __init__(self, canvas, parent_window):
        super().__init__(parent_window)
        self.setObjectName("sidebar")
        self.setFixedWidth(200)

        self._canvas = canvas
        self._parent = parent_window
        self._tool_buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(10)

        self._build_tools_section(layout)
        self._build_shapes_section(layout)
        self._build_algorithm_section(layout)
        self._build_style_section(layout)
        self._build_size_section(layout)
        self._build_transform_section(layout)
        self._build_object_section(layout)

        layout.addStretch()

        self._apply_style()

        # Set tool default: Select
        self._canvas.set_tool(SelectTool(self._canvas))
        self._set_active_tool_btn("select")

    # ── Section builders ──────────────────────────────────────────────────────

    def _build_tools_section(self, layout: QVBoxLayout):
        """Tombol tool utama: Select, Brush, Eraser, Fill."""
        layout.addWidget(self._section_label("TOOLS"))

        grid = QGridLayout()
        grid.setSpacing(5)

        tools = [
            ("Select", "select"),
            ("Brush",  "brush"),
            ("Eraser", "eraser"),
            ("Fill",   "fill"),
        ]

        for i, (text, key) in enumerate(tools):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("toolBtn")
            btn.clicked.connect(lambda _, k=key: self._on_tool_clicked(k))
            self._tool_buttons[key] = btn
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)

    def _build_shapes_section(self, layout: QVBoxLayout):
        """Dropdown pilihan shape."""
        layout.addWidget(self._section_label("SHAPES"))

        self._shape_combo = QComboBox()
        self._shape_combo.setObjectName("combo")
        self._shape_combo.addItem("— Pilih Shape —", "")
        for text, kind in [
            ("Point",     "point"),
            ("Line",      "line"),
            ("Circle",    "circle"),
            ("Ellipse",   "ellipse"),
            ("Rectangle", "rectangle"),
            ("Triangle",  "triangle"),
            ("Trapezoid", "trapezoid"),
        ]:
            self._shape_combo.addItem(text, kind)

        self._shape_combo.currentIndexChanged.connect(self._on_shape_selected)
        layout.addWidget(self._shape_combo)

    def _build_algorithm_section(self, layout: QVBoxLayout):
        """Dropdown pilihan algoritma untuk garis, lingkaran, dan elips."""
        layout.addWidget(self._section_label("ALGORITMA"))

        # Garis
        row_line = QHBoxLayout()
        row_line.addWidget(QLabel("Garis"))
        self._line_algo_combo = QComboBox()
        self._line_algo_combo.setObjectName("combo")
        self._line_algo_combo.addItem("Bresenham", "bresenham")
        self._line_algo_combo.addItem("DDA", "dda")
        self._line_algo_combo.currentIndexChanged.connect(self._on_line_algo_changed)
        row_line.addWidget(self._line_algo_combo)
        layout.addLayout(row_line)

        # Lingkaran
        row_circle = QHBoxLayout()
        row_circle.addWidget(QLabel("Lingkaran"))
        self._circle_algo_combo = QComboBox()
        self._circle_algo_combo.setObjectName("combo")
        self._circle_algo_combo.addItem("Midpoint", "midpoint")
        self._circle_algo_combo.addItem("Bresenham", "bresenham")
        self._circle_algo_combo.currentIndexChanged.connect(self._on_circle_algo_changed)
        row_circle.addWidget(self._circle_algo_combo)
        layout.addLayout(row_circle)

        # Elips
        row_ellipse = QHBoxLayout()
        row_ellipse.addWidget(QLabel("Elips"))
        self._ellipse_algo_combo = QComboBox()
        self._ellipse_algo_combo.setObjectName("combo")
        self._ellipse_algo_combo.addItem("Midpoint", "midpoint")
        self._ellipse_algo_combo.addItem("Bresenham", "bresenham")
        self._ellipse_algo_combo.currentIndexChanged.connect(self._on_ellipse_algo_changed)
        row_ellipse.addWidget(self._ellipse_algo_combo)
        layout.addLayout(row_ellipse)

    def _build_style_section(self, layout: QVBoxLayout):
        """Picker warna Stroke dan Fill."""
        layout.addWidget(self._section_label("WARNA"))

        # Stroke
        stroke_btn = QPushButton("Stroke Color")
        stroke_btn.clicked.connect(self._pick_stroke)
        layout.addWidget(stroke_btn)

        self._stroke_chip = QLabel()
        self._stroke_chip.setObjectName("colorChip")
        self._stroke_label = QLabel("─")
        stroke_row = QHBoxLayout()
        stroke_row.addWidget(self._stroke_chip)
        stroke_row.addWidget(self._stroke_label, 1)
        layout.addLayout(stroke_row)

        # Fill
        fill_btn = QPushButton("Fill Color")
        fill_btn.clicked.connect(self._pick_fill)
        layout.addWidget(fill_btn)

        self._fill_chip = QLabel()
        self._fill_chip.setObjectName("colorChip")
        self._fill_label = QLabel("None")
        fill_row = QHBoxLayout()
        fill_row.addWidget(self._fill_chip)
        fill_row.addWidget(self._fill_label, 1)
        layout.addLayout(fill_row)

        self._refresh_color_indicators()

    def _build_size_section(self, layout: QVBoxLayout):
        """Slider ketebalan garis / ukuran brush."""
        size_row = QHBoxLayout()
        size_row.addWidget(self._section_label("UKURAN"))
        self._size_label = QLabel(f"{self._canvas.line_width} px")
        self._size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        size_row.addWidget(self._size_label)
        layout.addLayout(size_row)

        self._size_slider = QSlider(Qt.Horizontal)
        self._size_slider.setRange(1, 30)
        self._size_slider.setValue(self._canvas.line_width)
        self._size_slider.valueChanged.connect(self._on_size_changed)
        layout.addWidget(self._size_slider)

    def _build_transform_section(self, layout: QVBoxLayout):
        """Tombol transformasi: Translate, Rotate, Scale, Grayscale, Reset."""
        layout.addWidget(self._section_label("TRANSFORMASI"))

        grid = QGridLayout()
        grid.setSpacing(5)

        actions = [
            ("Translate", self._do_translate),
            ("Rotate",    self._do_rotate),
            ("Scale",     self._do_scale),
            ("Grayscale", self._do_grayscale),
        ]

        for i, (text, slot) in enumerate(actions):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)

    def _build_object_section(self, layout: QVBoxLayout):
        """Tombol Z-order dan Delete."""
        layout.addWidget(self._section_label("OBJEK"))

        grid = QGridLayout()
        grid.setSpacing(5)

        front_btn = QPushButton("Bring Front")
        back_btn  = QPushButton("Send Back")
        del_btn   = QPushButton("Delete")
        del_btn.setObjectName("deleteBtn")

        front_btn.clicked.connect(self._do_bring_front)
        back_btn.clicked.connect(self._do_send_back)
        del_btn.clicked.connect(self.delete_selected)

        grid.addWidget(front_btn, 0, 0)
        grid.addWidget(back_btn,  0, 1)
        grid.addWidget(del_btn,   1, 0, 1, 2)  # span 2 kolom
        layout.addLayout(grid)

    # ── Slot: Tool ────────────────────────────────────────────────────────────

    def _on_tool_clicked(self, key: str):
        """Ganti tool aktif di canvas sesuai tombol yang diklik."""
        tool_map = {
            "select": lambda: SelectTool(self._canvas),
            "brush":  lambda: BrushTool(self._canvas),
            "eraser": lambda: EraserTool(self._canvas),
            "fill":   lambda: FillTool(self._canvas),
        }
        if key in tool_map:
            self._canvas.set_tool(tool_map[key]())
            self._set_active_tool_btn(key)
            # Reset shape combo ke placeholder saat tool non-shape dipilih
            self._shape_combo.blockSignals(True)
            self._shape_combo.setCurrentIndex(0)
            self._shape_combo.blockSignals(False)

    def _on_shape_selected(self):
        """Ganti ke ShapeTool sesuai shape yang dipilih dari dropdown."""
        kind = self._shape_combo.currentData()
        if not kind:
            return
        self._canvas.set_tool(ShapeTool(self._canvas, kind))
        # Hapus highlight semua tombol tool (shape dipilih via combo)
        self._set_active_tool_btn(None)

    def _set_active_tool_btn(self, active_key: str | None):
        """Update tampilan checked pada tombol tool."""
        for key, btn in self._tool_buttons.items():
            btn.setChecked(key == active_key)

    # ── Slot: Algoritma ───────────────────────────────────────────────────────

    def _on_line_algo_changed(self):
        self._canvas.line_algo = self._line_algo_combo.currentData()
        self._update_status()

    def _on_circle_algo_changed(self):
        self._canvas.circle_algo = self._circle_algo_combo.currentData()
        self._update_status()

    def _on_ellipse_algo_changed(self):
        self._canvas.ellipse_algo = self._ellipse_algo_combo.currentData()
        self._update_status()

    # ── Slot: Warna ───────────────────────────────────────────────────────────

    def _pick_stroke(self):
        col = QColorDialog.getColor(self._canvas.stroke_color, self, "Pilih Warna Stroke")
        if col.isValid():
            self._canvas.stroke_color = col
            # Jika ada objek terpilih, ubah warna stroke-nya juga
            if self._canvas.selected_objects:
                self._canvas.history.push(self._canvas.clone_state())
                for obj in self._canvas.selected_objects:
                    obj.stroke = QColor(col)
                self._canvas.update()
            self._refresh_color_indicators()

    def _pick_fill(self):
        col = QColorDialog.getColor(self._canvas.fill_color, self, "Pilih Warna Fill")
        if col.isValid():
            self._canvas.fill_color = col
            if self._canvas.selected_objects:
                self._canvas.history.push(self._canvas.clone_state())
                for obj in self._canvas.selected_objects:
                    obj.fill = QColor(col)
                self._canvas.update()
            self._refresh_color_indicators()

    def _refresh_color_indicators(self):
        """Update chip warna dan label teks sesuai warna aktif canvas."""
        stroke = self._canvas.stroke_color
        fill   = self._canvas.fill_color

        # Stroke chip
        self._stroke_chip.setStyleSheet(
            f"background:{stroke.name()}; border:1px solid #94a3b8; border-radius:4px;"
        )
        self._stroke_label.setText(stroke.name().upper())

        # Fill chip
        if fill.alpha() == 0:
            self._fill_chip.setStyleSheet(
                "background:transparent; border:1px dashed #94a3b8; border-radius:4px;"
            )
            self._fill_label.setText("None")
        else:
            self._fill_chip.setStyleSheet(
                f"background:{fill.name()}; border:1px solid #94a3b8; border-radius:4px;"
            )
            self._fill_label.setText(fill.name().upper())

    # ── Slot: Ukuran ──────────────────────────────────────────────────────────

    def _on_size_changed(self, value: int):
        self._canvas.line_width = value
        self._size_label.setText(f"{value} px")
        # Update ketebalan objek terpilih secara langsung
        if self._canvas.selected_objects:
            self._canvas.history.push(self._canvas.clone_state())
            for obj in self._canvas.selected_objects:
                obj.width = value
            self._canvas.update()

    # ── Slot: Transformasi ────────────────────────────────────────────────────

    def _do_translate(self):
        if not self._canvas.selected_objects:
            return
        d = TransformDialog(
            "Translate",
            [("dx (pixel)", 50, -2000, 2000), ("dy (pixel)", 20, -2000, 2000)],
            self
        )
        if d.exec():
            dx, dy = d.values()
            self._canvas.history.push(self._canvas.clone_state())
            from app.transforms.transformer import Transformer
            for obj in self._canvas.selected_objects:
                Transformer.translate(obj, dx, dy)
            self._canvas.update()

    def _do_rotate(self):
        if not self._canvas.selected_objects:
            return
        d = TransformDialog(
            "Rotate",
            [("Sudut (derajat)", 45, -360, 360)],
            self
        )
        if d.exec():
            angle = d.values()[0]
            self._canvas.history.push(self._canvas.clone_state())
            from app.transforms.transformer import Transformer
            for obj in self._canvas.selected_objects:
                Transformer.rotate(obj, angle)
            self._canvas.update()

    def _do_scale(self):
        if not self._canvas.selected_objects:
            return
        d = TransformDialog(
            "Scale",
            [("Skala X", 1.5, 0.1, 10.0), ("Skala Y", 1.5, 0.1, 10.0)],
            self
        )
        if d.exec():
            sx, sy = d.values()
            self._canvas.history.push(self._canvas.clone_state())
            from app.transforms.transformer import Transformer
            for obj in self._canvas.selected_objects:
                Transformer.scale(obj, sx, sy)
            self._canvas.update()

    def _do_grayscale(self):
        if not self._canvas.selected_objects:
            return
        self._canvas.history.push(self._canvas.clone_state())
        from app.transforms.transformer import Transformer
        for obj in self._canvas.selected_objects:
            Transformer.grayscale(obj)
        self._canvas.update()

    def _do_reset_transform(self):
        if not self._canvas.selected_objects:
            return
        self._canvas.history.push(self._canvas.clone_state())
        from app.transforms.transformer import Transformer
        for obj in self._canvas.selected_objects:
            Transformer.reset(obj)
        self._canvas.update()

    # ── Slot: Objek / Z-order ─────────────────────────────────────────────────

    def _do_bring_front(self):
        if not self._canvas.selected_objects:
            return
        self._canvas.history.push(self._canvas.clone_state())
        sel = [o for o in self._canvas.objects if o.selected]
        rest = [o for o in self._canvas.objects if not o.selected]
        self._canvas.objects = rest + sel
        self._canvas.update()

    def _do_send_back(self):
        if not self._canvas.selected_objects:
            return
        self._canvas.history.push(self._canvas.clone_state())
        sel = [o for o in self._canvas.objects if o.selected]
        rest = [o for o in self._canvas.objects if not o.selected]
        self._canvas.objects = sel + rest
        self._canvas.update()

    def delete_selected(self):
        """Hapus semua objek yang sedang dipilih. Dipanggil juga dari MainWindow (menu Edit > Delete)."""
        if not self._canvas.selected_objects:
            return
        self._canvas.history.push(self._canvas.clone_state())
        for obj in list(self._canvas.selected_objects):
            if obj in self._canvas.objects:
                self._canvas.objects.remove(obj)
        self._canvas.selected_objects = []
        self._canvas.update()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("sectionLabel")
        return lbl

    def _update_status(self):
        algo_info = (
            f"Garis: {self._canvas.line_algo.upper()} | "
            f"Circle: {self._canvas.circle_algo.capitalize()} | "
            f"Ellipse: {self._canvas.ellipse_algo.capitalize()}"
        )
        if hasattr(self._parent, "status"):
            self._parent.status.showMessage(algo_info)

    def _apply_style(self):
        self.setStyleSheet("""
        #sidebar {
            background: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        QLabel {
            color: #1f2937;
            font-size: 12px;
        }
        QLabel#sectionLabel {
            font-weight: 600;
            font-size: 11px;
            color: #6b7280;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }
        QLabel#colorChip {
            min-width: 20px;
            max-width: 20px;
            min-height: 16px;
            max-height: 16px;
            border-radius: 4px;
        }
        QPushButton {
            background: #f8fafc;
            color: #111827;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 5px 8px;
            font-size: 12px;
        }
        QPushButton:hover {
            background: #e0ecff;
        }
        QPushButton:pressed {
            background: #bfdbfe;
        }
        QPushButton#toolBtn:checked {
            background: #2563eb;
            color: #ffffff;
            border-color: #1d4ed8;
        }
        QPushButton#deleteBtn {
            background: #fef2f2;
            color: #dc2626;
            border-color: #fecaca;
        }
        QPushButton#deleteBtn:hover {
            background: #fee2e2;
        }
        QComboBox {
            background: #f8fafc;
            color: #111827;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 12px;
        }
        QComboBox QAbstractItemView {
            background: #ffffff;
            color: #111827;
            selection-background-color: #e0ecff;
        }
        QSlider::groove:horizontal {
            height: 4px;
            background: #e2e8f0;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #2563eb;
            border: 1px solid #1d4ed8;
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        """)
