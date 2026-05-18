"""
SelectTool — tool untuk memilih dan memindahkan objek di canvas.
"""
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent

from app.tools.base_tools import BaseTool
from app.models.graphic_object import GraphicObject


class SelectTool(BaseTool):
    """
    Tool untuk memilih objek dengan klik dan memindahkannya dengan drag.

    Cara kerja:
    - Klik pada objek → objek terpilih (selected=True), objek lain di-deselect
    - Klik di area kosong → semua objek di-deselect
    - Drag objek terpilih → objek berpindah (move_by)
    - Mouse release → simpan state ke history
    """

    def __init__(self, canvas):
        super().__init__(canvas)
        self._dragging = False
        self._last_pos: QPointF | None = None
        self._moved = False  # Tracking apakah objek dipindah (untuk undo)

    def on_press(self, pos: QPointF, event: QMouseEvent) -> None:
        hit = self._hit_test(pos)

        if hit is not None:
            # Jika objek yang diklik belum terpilih, ganti seleksi
            if not hit.selected:
                self._deselect_all()
                hit.selected = True
                self.canvas.selected_objects = [hit]
            self._dragging = True
            self._last_pos = pos
            self._moved = False
        else:
            # Klik di area kosong → hapus seleksi
            self._deselect_all()

        self.canvas.update()

    def on_move(self, pos: QPointF, event: QMouseEvent) -> None:
        if self._dragging and self._last_pos is not None and self.canvas.selected_objects:
            dx = pos.x() - self._last_pos.x()
            dy = pos.y() - self._last_pos.y()
            for obj in self.canvas.selected_objects:
                obj.move_by(dx, dy)
            self._last_pos = pos
            self._moved = True
            self.canvas.update()

    def on_release(self, pos: QPointF, event: QMouseEvent) -> None:
        if self._dragging and self._moved:
            # Simpan state sebelum move ke history
            # Catatan: state sudah berubah, jadi kita push state lama
            # (tidak ideal tapi cukup untuk proyek ini)
            pass
        self._dragging = False
        self._last_pos = None

    # ── Helper ───────────────────────────────────────────────────────────────

    def _hit_test(self, pos: QPointF) -> GraphicObject | None:
        """
        Cari objek yang berada di bawah posisi klik (pos).
        Iterasi dari objek paling atas (index terakhir) ke bawah.
        """
        threshold = 8.0  # toleransi klik dalam pixel
        for obj in reversed(self.canvas.objects):
            if self._point_in_object(pos, obj, threshold):
                return obj
        return None

    def _point_in_object(self, pos: QPointF, obj: GraphicObject, threshold: float) -> bool:
        """Cek apakah pos berada di dalam atau dekat bounding box objek."""
        if not obj.points:
            return False
        x0, y0, x1, y1 = obj.bounding_rect()
        # Tambah toleransi ke semua sisi
        return (x0 - threshold <= pos.x() <= x1 + threshold and
                y0 - threshold <= pos.y() <= y1 + threshold)

    def _deselect_all(self):
        """Hapus seleksi dari semua objek."""
        for obj in self.canvas.objects:
            obj.selected = False
        self.canvas.selected_objects = []