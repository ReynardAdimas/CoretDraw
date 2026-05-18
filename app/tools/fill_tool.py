"""
FillTool — tool untuk mengisi area tertutup menggunakan BFS Flood Fill.
"""
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent, QImage, QColor, QPainter

from app.tools.base_tools import BaseTool
from app.models.graphic_object import GraphicObject
from app.algorithms.fill import bfs


class FillTool(BaseTool):
    """
    Tool flood fill — klik pada area tertutup untuk mengisinya dengan warna stroke aktif.

    Cara kerja:
    1. Saat mouse ditekan, render semua objek ke QImage sementara (off-screen)
    2. Ambil warna pixel di titik klik sebagai target_color
    3. Jalankan BFS flood fill dari titik tersebut
    4. Hasilnya disimpan sebagai GraphicObject bertipe 'fill' dengan QImage overlay
    """

    def on_press(self, pos: QPointF, event: QMouseEvent) -> None:
        canvas = self.canvas
        w = canvas.width()
        h = canvas.height()

        # ── 1. Render scene ke off-screen image ──────────────────────────────
        snapshot = QImage(canvas.size(), QImage.Format_ARGB32)
        snapshot.fill(QColor("#ffffff"))
        painter = QPainter(snapshot)
        painter.setRenderHint(QPainter.Antialiasing, False)  # non-AA agar warna pixel tepat
        for obj in canvas.objects:
            canvas._renderer.draw(painter, obj)
        painter.end()

        # ── 2. Ambil target color di titik klik ───────────────────────────────
        x, y = int(pos.x()), int(pos.y())
        if x < 0 or y < 0 or x >= w or y >= h:
            return

        target_color = snapshot.pixel(x, y)
        fill_color_int = QColor(canvas.stroke_color).rgba()

        if target_color == fill_color_int:
            return  # sudah berwarna sama, tidak perlu diisi

        # ── 3. Jalankan BFS flood fill ────────────────────────────────────────
        filled_pixels = bfs(
            pixels=snapshot.pixel,   # callable: pixel(x, y) -> int ARGB
            width=w,
            height=h,
            x=x,
            y=y,
            target_color=target_color,
            fill_color=fill_color_int,
        )

        if not filled_pixels:
            return

        # ── 4. Gambar hasil fill ke overlay QImage ────────────────────────────
        fill_img = QImage(canvas.size(), QImage.Format_ARGB32)
        fill_img.fill(QColor(0, 0, 0, 0))  # transparan

        for fx, fy in filled_pixels:
            fill_img.setPixel(fx, fy, fill_color_int)

        # ── 5. Simpan ke history dan tambahkan ke canvas ──────────────────────
        canvas.history.push(canvas.clone_state())
        obj = GraphicObject(
            kind="fill",
            points=[pos],
            stroke=QColor(canvas.stroke_color),
            image=fill_img,
        )
        canvas.objects.append(obj)
        canvas.update()

    def on_move(self, pos: QPointF, event: QMouseEvent) -> None:
        pass  # fill tidak butuh drag

    def on_release(self, pos: QPointF, event: QMouseEvent) -> None:
        pass  # semua logika ada di on_press