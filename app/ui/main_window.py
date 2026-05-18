# from PySide6.QtWidgets import (
# QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
# QStatusBar, QAction, QKeySequence, QFileDialog, QMessageBox
# )
from PySide6.QtGui import QKeySequence, QImage, QPainter, QColor
from PySide6.QtCore import Qt 

from app.canvas.canvas_widget import CanvasWidget
from app.ui.sidebar import Sidebar
from app.animation.animator import Animator
from PySide6.QtWidgets import (
QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
QStatusBar, QFileDialog, QMessageBox
)
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grafika 2D — Tugas Kelompok")
        self.resize(1200, 760)
        # Canvas & komponen utama
        self.canvas = CanvasWidget(self)
        self.animator = Animator(self.canvas)
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._build_ui()
        self._build_menu()
        self._apply_style()
        self.status.showMessage("Siap. Pilih tool dari sidebar untuk mulai menggambar.")
    def _build_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.sidebar = Sidebar(self.canvas, self)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.canvas, 1)
        self.setCentralWidget(central) 
    
    def _build_menu(self):
        mb = self.menuBar()
        # File
        file_m = mb.addMenu("File")
        new_a = QAction("New", self); new_a.triggered.connect(self.canvas.clear)
        exp_a = QAction("Export PNG", self); 
        exp_a.triggered.connect(self._export_png)
        exit_a = QAction("Exit", self); exit_a.triggered.connect(self.close)
        file_m.addActions([new_a, exp_a, exit_a])
        # Edit
        edit_m = mb.addMenu("Edit")
        undo_a = QAction("Undo", self)
        undo_a.setShortcut(QKeySequence("Ctrl+Z"))
        undo_a.triggered.connect(self.canvas.undo)
        redo_a = QAction("Redo", self)
        redo_a.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        redo_a.triggered.connect(self.canvas.redo)
        del_a = QAction("Delete", self)
        del_a.setShortcut(QKeySequence("Delete")) 
        del_a.triggered.connect(self.sidebar.delete_selected)
        edit_m.addActions([undo_a, redo_a, del_a])
        # Animation
        anim_m = mb.addMenu("Animation")
        for label, mode in [("Move", "move"), ("Rotate", "rotate"),("Scale", "scale"), ("Bounce", "bounce")]:
            a = QAction(label, self)
            a.triggered.connect(lambda _, m=mode: self.animator.start(m))
            anim_m.addAction(a)
        stop_a = QAction("Stop", self); 
        stop_a.triggered.connect(self.animator.stop)
        anim_m.addAction(stop_a)
        # Help
        help_m = mb.addMenu("Help")
        about_a = QAction("About", self); about_a.triggered.connect(self._about)
        formula_a = QAction("Formula Transformasi", self)
        formula_a.triggered.connect(self._show_formula)
        help_m.addActions([about_a, formula_a]) 
    
    def update_coords(self, x:int, y:int):
        self.status.showMessage(f"x={x}, y={y}")
    
    def _export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export PNG", "output.png", "PNG (*.png)")
        if path:
            img = QImage(self.canvas.size(), QImage.Format_ARGB32)
            img.fill(QColor("#ffffff"))
            p = QPainter(img)
            self.canvas.render(p)
            p.end()
            img.save(path)
            self.status.showMessage(f"Tersimpan: {path}") 
    
    def _about(self):
        QMessageBox.information(self, "Tentang Aplikasi",
        "Aplikasi Grafika 2D Interaktif\n"
        "Tugas Kelompok — Grafika Komputer\n\n"
        "Algoritma: Bresenham, DDA, Midpoint Circle/Ellipse, BFS Flood Fill") 
    
    def _show_formula(self):
        QMessageBox.information(self, "Formula Transformasi",
        "Translasi:\n  x' = x + tx\n  y' = y + ty\n\n"
        "Rotasi:\n  x' = x cos θ - y sin θ\n  y' = x sin θ + y cos θ\n\n"
        "Skala:\n  x' = x × sx\n  y' = y × sy") 
    
    def _apply_style(self):
        self.setStyleSheet("""
        QMainWindow { background: #f5f6f8; }
        QMenuBar { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 
        4px; }
        QMenuBar::item { padding: 6px 10px; border-radius: 4px; }
                                   QMenuBar::item:selected { background: #e0ecff; }
        QMenu { background: #fff; border: 1px solid #e2e8f0; }
        QMenu::item { padding: 6px 20px; }
        QMenu::item:selected { background: #e0ecff; }
        QStatusBar { background: #fff; border-top: 1px solid #e2e8f0; color: 
        #374151; }
        """)