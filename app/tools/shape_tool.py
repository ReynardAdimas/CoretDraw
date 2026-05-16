from PySide6.QtCore import QPointF 
from PySide6.QtGui import QMouseEvent 
from app.tools.base_tools import BaseTool 
from app.models.graphic_object import GraphicObject 

class ShapeTool(BaseTool):
    
    def __init__(self, canvas, kind: str):
        super().__init__(canvas)
        self.kind = kind           
        self._preview = None 

    def on_press(self, pos:QPointF, event:QMouseEvent) -> None:
        if self.kind == "point":
            self.canvas.history.push(self.canvas.clone_state())
            obj = GraphicObject(
            kind="point",
            points=[pos],
            stroke=self.canvas.stroke_color,
            fill=self.canvas.fill_color,
            width=self.canvas.line_width,
            line_algo=self.canvas.line_algo,
            circle_algo=self.canvas.circle_algo,
            ellipse_algo=self.canvas.ellipse_algo,
            )
            self.canvas.objects.append(obj)
            self.canvas.update()
            return 
        self._preview = GraphicObject(
            kind=self.kind,
            points=[pos, pos],
            stroke=self.canvas.stroke_color,
            fill=self.canvas.fill_color,
            width=self.canvas.line_width,
            line_algo=self.canvas.line_algo,
            circle_algo=self.canvas.circle_algo,
            ellipse_algo=self.canvas.ellipse_algo,
        ) 
        self.canvas.preview_object = self._preview 
    
    def on_move(self, pos:QPointF, event:QMouseEvent) -> None:
        if self._preview:
            self._preview.points = [self._preview.points[0], pos]
            self.canvas.update()
    
    def on_release(self, pos:QPointF, event:QMouseEvent) -> None:
        if self._preview:
            self.canvas.history.push(self.canvas.clone_state())
            self._preview.points = [self._preview.points[0], pos]
            self.canvas.objects.append(self._preview)
            self.canvas.preview_object = None
            self._preview = None
            self.canvas.update() 

            
        