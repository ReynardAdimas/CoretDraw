# CoretDraw

CoretDraw adalah aplikasi grafika 2D interaktif berbasis Python dan PySide6. Project ini dibuat untuk kebutuhan pembelajaran Grafika Komputer, terutama untuk mencoba algoritma menggambar objek 2D, transformasi, animasi sederhana, dan manipulasi objek pada canvas.

## Fitur

- Canvas gambar interaktif berbasis Qt.
- Tool utama: Select, Brush, Eraser, dan Fill.
- Shape: Point, Line, Circle, Ellipse, Rectangle, Triangle, dan Trapezoid.
- Pilihan algoritma:
  - Garis: Bresenham dan DDA.
  - Lingkaran: Midpoint dan Bresenham.
  - Elips: Midpoint dan Bresenham.
- Pengaturan warna stroke dan fill.
- Pengaturan ketebalan garis atau ukuran brush.
- Transformasi objek: translate, rotate, scale, grayscale, dan reset transform.
- Pengaturan urutan objek: bring to front dan send to back.
- Undo dan redo.
- Animasi sederhana: move, rotate, scale, dan bounce.
- Export canvas ke file PNG.

## Kebutuhan

- Python 3.10 atau lebih baru.
- PySide6.

Dependency project tersedia di file `requirements.txt`.

## Instalasi

Masuk ke folder project:

```powershell
cd "\CoretDraw"
```

Opsional, buat virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependency:

```powershell
python -m pip install -r requirements.txt
```

## Menjalankan Aplikasi

Jalankan file utama:

```powershell
python main.py
```

Setelah dijalankan, window aplikasi akan terbuka dengan sidebar di sebelah kiri dan canvas di sebelah kanan.

## Cara Penggunaan Singkat

1. Pilih tool dari sidebar.
2. Untuk menggambar shape, pilih jenis shape dari dropdown `SHAPES`.
3. Pilih algoritma garis, lingkaran, atau elips dari bagian `ALGORITMA`.
4. Atur warna stroke, fill, dan ukuran garis dari sidebar.
5. Klik dan drag pada canvas untuk membuat objek.
6. Gunakan tool `Select` untuk memilih objek.
7. Setelah objek dipilih, gunakan tombol transformasi untuk translate, rotate, scale, grayscale, atau reset.
8. Gunakan menu `Edit` untuk undo, redo, atau delete.
9. Gunakan menu `File > Export PNG` untuk menyimpan hasil gambar.

## Shortcut

- `Ctrl + Z`: Undo.
- `Ctrl + Shift + Z`: Redo.
- `Delete`: Hapus objek terpilih.
- `Ctrl + Scroll`: Zoom canvas.
- `Shift + Scroll`: Geser canvas secara horizontal.

## Struktur Project

```text
CoretDraw/
+-- main.py
+-- requirements.txt
+-- app/
    +-- algorithms/     # Implementasi algoritma garis, lingkaran, elips, dan fill
    +-- animation/      # Logika animasi objek
    +-- canvas/         # Widget canvas dan renderer objek
    +-- history/        # Undo dan redo
    +-- models/         # Model data objek grafis
    +-- tools/          # Tool interaksi pengguna
    +-- transforms/     # Operasi transformasi objek
    +-- ui/             # Main window dan sidebar
```

## Entry Point

File utama project adalah:

```text
main.py
```

File ini membuat `QApplication`, membuka `MainWindow`, lalu menjalankan event loop Qt.

## Catatan

Jika command `py` tidak tersedia di Windows, gunakan `python`:

```powershell
python main.py
```

Jika muncul error `No module named PySide6`, pastikan dependency sudah diinstall dengan:

```powershell
python -m pip install -r requirements.txt
```
