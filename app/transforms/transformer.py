from app.models.graphic_object import GraphicObject 

class Transformer:

    @staticmethod
    def translate(obj: GraphicObject, dx: float, dy: float) -> None:
        obj.move_by(dx, dy) 
    
    @staticmethod
    def rotate(obj: GraphicObject, angle: float) -> None:
        """Tambahkan sudut rotasi ke objek (derajat)."""
        obj.rotation += angle 

    @staticmethod
    def scale(obj: GraphicObject, sx: float, sy: float) -> None:
        """Kalikan faktor skala objek."""
        obj.scale_x *= sx
        obj.scale_y *= sy 
    
    @staticmethod
    def reset(obj: GraphicObject) -> None:
        """Reset transformasi ke nilai awal."""
        obj.rotation = 0.0
        obj.scale_x = 1.0
        obj.scale_y = 1.0 
    
    @staticmethod
    def grayscale(obj: GraphicObject) -> None:
        """
        Konversi warna stroke dan fill ke grayscale.
        Menggunakan bobot luminansi ITU-R BT.601:
        gray = 0.299*R + 0.587*G + 0.114*B
        """
        for attr in ["stroke", "fill"]:
            col = getattr(obj, attr)
            gray = int(0.299 * col.red() + 0.587 * col.green() + 0.114 * col.blue())
            from PySide6.QtGui import QColor
            setattr(obj, attr, QColor(gray, gray, gray, col.alpha()))