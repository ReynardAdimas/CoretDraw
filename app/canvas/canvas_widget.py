from typing import List, Optional
from PySide6.QtCore import QPointF, Qt 
from PySide6.QtGui import QPainter, QColor, QImage 
from PySide6.QtWidgets import QWidget 

from app.models.graphic_object import GraphicObject
from app.canvas.renderer import Renderer
from app.history.history_manager import HistoryManager
from app.tools.base_tools import BaseTool 

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setMouseTracking(True)
        # State canvas
        self.objects: List[GraphicObject] = []
        self.preview_object: Optional[GraphicObject] = None
        self.selected_objects: List[GraphicObject] = []
        # Preferensi gambar
        self.stroke_color = QColor("#111827")
        self.fill_color = QColor(0, 0, 0, 0)
        self.line_width = 2
        self.line_algo = "bresenham"      
        # 'bresenham' atau 'dda'
        self.circle_algo = "midpoint"     
        self.ellipse_algo = "midpoint"
        # Komponen
        self._renderer = Renderer()
        self.history = HistoryManager()
        self._active_tool: Optional[BaseTool] = None
        # Referensi ke parent window (untuk update status bar)
        self.parent_window = parent 
    
    @property
    def selected_object(self) -> Optional[GraphicObject]:
        return self.selected_objects[0] if self.selected_objects else None 
    
    def set_tool(self, tool:BaseTool) -> None:
        self._active_tool = tool 
        self.preview_object = None 
        self.update() 
    
    def clone_state(self) -> List[GraphicObject]:
        """Buat deep copy seluruh scene untuk undo/redo."""
        return [obj.clone() for obj in self.objects] 
    
    def restore_state(self, state: List[GraphicObject]) -> None:
        """Kembalikan canvas ke state tertentu."""
        self.objects = state
        self.selected_objects = []
        self.update() 
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        clip = event.rect()
        for obj in self.objects:
            self._renderer.draw(painter, obj)
        if self.preview_object:
            self._renderer.draw(painter, self.preview_object, preview=True) 
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._active_tool:
            self._active_tool.on_press(QPointF(event.position()), event) 
    
    def mouseMoveEvent(self, event):
        pos = QPointF(event.position())
        if self._active_tool:
            self._active_tool.on_move(pos, event)
        if self.parent_window:
            self.parent_window.update_coords(int(pos.x()), int(pos.y())) 
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._active_tool:
            self._active_tool.on_release(QPointF(event.position()), event) 
    
    def mouseDoubleClickEvent(self, event):
        if self._active_tool:
            self._active_tool.on_double_click(QPointF(event.position()), event) 
    
    def undo(self):
        result = self.history.undo(self.clone_state())
        if result is not None:
            self.restore_state(result) 
    
    def redo(self):
        result = self.history.redo(self.clone_state())
        if result is not None:
            self.restore_state(result) 
    
    def clear(self):
        self.history.push(self.clone_state())
        self.objects.clear()
        self.selected_objects = []
        self.update()