import math 
from PySide6.QtCore import QTimer
from app.models.graphic_object import GraphicObject 

class Animator:
    
    def __init__(self, canvas_ref, interval_ms: int = 30):
        self._canvas = canvas_ref
        self._timer = QTimer()
        self._timer.timeout.connect(self._step)
        self._interval = interval_ms
        self._mode = None
        self._angle = 0.0  
    
    def start(self, mode: str) -> None:
        self._mode = mode 
        self._angle = 0.0 
        self._timer.start(self._interval) 
    
    def stop(self) -> None:
        self._mode = None 
        self._timer.stop() 
    
    @property 
    def is_running(self) -> bool:
        return self._timer.isActive() 
    
    def _step(self) -> None: 
        obj: GraphicObject = self._canvas.selected_object
        if obj is None:
            self.stop()
            return
        w = self._canvas.width()
        h = self._canvas.height()
        if self._mode == "move":
            obj.move_by(2, 0)
            if obj.bounding_rect()[2] > w:
                obj.move_by(-w + 50, 0)
        elif self._mode == "rotate":
            obj.rotation += 3
        elif self._mode == "scale":
            self._angle += 5
            s = 1 + 0.01 * math.sin(math.radians(self._angle))
            obj.scale_x *= s
            obj.scale_y *= s
        elif self._mode == "bounce":
            obj.move_by(3, 2)
            x0, y0, x1, y1 = obj.bounding_rect()
            if x1 > w or y1 > h:
                obj.move_by(-80, -60)
                
        self._canvas.update() 
        