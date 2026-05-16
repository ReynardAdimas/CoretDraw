from abc import ABC, abstractmethod
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent 

class BaseTool(ABC):

    def __init__(self, canvas):
        self.canvas = canvas 
    
    @abstractmethod
    def on_press(self, pos: QPointF, event: QMouseEvent) -> None:
        """Dipanggil saat tombol mouse ditekan."""
        pass
    @abstractmethod
    def on_move(self, pos: QPointF, event: QMouseEvent) -> None:
        """Dipanggil saat mouse digerakkan (dengan atau tanpa tombol ditekan)."""
        pass
    @abstractmethod
    def on_release(self, pos: QPointF, event: QMouseEvent) -> None:
        """Dipanggil saat tombol mouse dilepas."""
        pass
    def on_double_click(self, pos: QPointF, event: QMouseEvent) -> None:
        """Opsional — untuk tool seperti Polygon yang perlu double-click."""
        pass