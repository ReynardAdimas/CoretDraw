# CoretDraw

CoretDraw adalah aplikasi grafika komputer 2D interaktif berbasis desktop. Aplikasi ini dibuat untuk tugas kelompok mata kuliah Grafika Komputer.

## Fitur Utama

- Canvas besar dan responsif mengikuti ukuran window
- Menu atas: File, Edit, View, Object, Transform, Animation, Help
- Sidebar tools: Select, Brush, Eraser, Fill
- Shape tools: Point, Line, Circle, Ellipse, Rectangle, Polygon
- Pengaturan warna stroke dan fill
- Indikator warna aktif di sidebar dan status bar
- Pengaturan ukuran brush / ketebalan garis
- Koordinat mouse di status bar
- Select object dan multi-select
- Translasi dengan klik-drag pada tool Select
- Transformasi: Translate, Rotate, Scale
- Animasi: Move, Rotate, Scale, Bounce
- Undo, Redo, Clear Canvas
- Export gambar ke PNG
- Panel rumus transformasi

## Multi-Select dan Drag

Tool **Move** sudah dihapus agar toolbar lebih sederhana. Semua pemilihan dan pemindahan objek dilakukan lewat tool **Select**.

Cara pakai:

- Klik objek untuk memilih satu objek.
- Klik lalu drag objek untuk memindahkannya.
- `Shift + Klik` untuk menambah atau melepas objek dari pilihan.
- `Ctrl + Klik` juga bisa dipakai untuk menambah atau melepas objek dari pilihan.
- Jika beberapa objek sudah dipilih, drag salah satu objek terpilih untuk memindahkan semuanya sekaligus.

Fitur transformasi seperti Translate, Rotate, Scale, Grayscale, Bring to Front, Send to Back, Delete, Stroke Color, Fill Color, dan Size/Width berlaku untuk semua objek yang sedang dipilih.

## Fitur Fill Tool

Tool **Fill** digunakan untuk mengisi ruang kosong/area tertutup berdasarkan titik yang diklik.

Terdapat dua mode:

1. **Area ini saja**  
   Mengisi hanya area yang tersambung dengan titik klik. Cocok untuk mengisi satu ruang tertutup saja.

2. **Semua area serupa**  
   Mengisi semua area yang memiliki warna/sifat pixel yang sama dengan titik klik. Cocok jika ingin mengisi beberapa daerah kosong yang sejenis sekaligus.

Catatan: Fill Tool memakai **Fill Color**. Jika Fill Color masih `None`, aplikasi memakai Stroke Color sebagai warna pengisi agar tetap bisa langsung dicoba.

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

## Shortcut

- `Ctrl+Z` untuk Undo.
- `Ctrl+Shift+Z` untuk Redo.

## Catatan

Build `.exe` sebaiknya dilakukan di Windows agar menghasilkan file executable Windows. Grid dan Snap to Grid sudah dihapus agar canvas terlihat lebih bersih.


## Catatan Optimasi Brush
Versi ini mengoptimalkan brush dengan menyimpan path secara bertahap, membatasi titik yang terlalu rapat, dan hanya me-refresh area kecil saat menggambar. Hal ini mengurangi lag saat coretan semakin banyak.

## Update Brush Super Halus
Versi ini memakai quadratic smoothing untuk brush, menyaring titik yang terlalu rapat, dan hanya me-refresh area kecil yang berubah. Hasil brush menjadi lebih halus dan tetap ringan walaupun coretan semakin banyak.


## Catatan versi Brush Stable
- Brush diperbaiki agar tidak ada dot besar di awal stroke.
- Brush memakai cap datar dan join halus agar ukuran stroke konsisten.
- Repaint brush dibuat full-canvas untuk mencegah garis hilang saat mouse bergerak jauh/cepat, tetapi tetap ringan karena stroke disimpan sebagai bitmap layer.


## Update UI

Bagian **SHAPES** pada sidebar sekarang memakai dropdown agar tampilan lebih ringkas dan area sidebar lebih tertata. Pilih shape dari dropdown, lalu gambar di canvas seperti biasa.

- Hasil Brush dapat dipilih dengan Select, lalu digeser bersama objek lain.


## Shortcut

- `Ctrl + Z`: Undo
- `Ctrl + Shift + Z`: Redo
- `Delete`: Hapus objek yang sedang dipilih
