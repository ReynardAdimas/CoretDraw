# CoretDraw

CoretDraw adalah aplikasi grafika komputer 2D interaktif berbasis desktop. Aplikasi ini dibuat untuk tugas kelompok mata kuliah Grafika Komputer.

## Fitur Utama

- Canvas besar dan responsif mengikuti ukuran window
- Menu atas: File, Edit, View, Object, Transform, Animation, Help
- Sidebar tools: Select, Move, Brush, Eraser
- Shape tools: Point, Line, Circle, Ellipse, Rectangle, Polygon
- Pengaturan warna stroke dan fill
- Pengaturan ukuran brush / ketebalan garis
- Koordinat mouse di status bar
- Select object
- Translasi dengan drag objek
- Transformasi: Translate, Rotate, Scale
- Animasi: Move, Rotate, Scale, Bounce
- Undo, Redo, Clear Canvas
- Export gambar ke PNG
- Panel rumus transformasi

## Cara Menjalankan

1. Install Python 3.10 atau lebih baru.
2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:

```bash
python main.py
```

## Cara Build Menjadi EXE

Jalankan perintah berikut di Windows:

```bash
pyinstaller --onefile --windowed --name CoretDraw main.py
```

Hasil build ada di folder:

```text
dist/CoretDraw.exe
```

## Catatan

Build `.exe` sebaiknya dilakukan di Windows agar menghasilkan file executable Windows.


## Shortcut

- `Ctrl+Z` untuk Undo.
- `Ctrl+Shift+Z` untuk Redo.


## Update UI Status Warna

Versi ini menambahkan indikator warna di sidebar:
- kotak warna Stroke dan kode warnanya,
- kotak warna Fill dan kode warnanya,
- ukuran brush/garis dalam px,
- status bar menampilkan mode, stroke, fill, size, dan koordinat mouse.

Shortcut:
- Undo: Ctrl+Z
- Redo: Ctrl+Shift+Z


## Update Tanpa Grid

Grid dan Snap to Grid sudah dihapus agar canvas terlihat lebih bersih dan tidak ada elemen latar yang mengganggu atau tertimpa saat memakai eraser.
