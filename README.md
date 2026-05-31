# PBO Amazon Sales

Repositori ini digunakan untuk menyimpan data, kode, dan dokumentasi terkait pengolahan data Amazon dalam konteks **PBO (Pemrograman Berorientasi Objek)**.

## Anggota

1. Dwiki Aprilian Aryanda (2409106001)
2. M Tedy Azhari (2409106003)
3. Zeydan Fazle Mawla (2409106010)
4. Muhammad Faiz Lazuardi (2409106031)

## Tujuan Repositori

1. Menyediakan dataset yang relevan untuk analisis.
2. Mengimplementasikan pengolahan data dengan pendekatan OOP/PBO.
3. Menjadi referensi tugas, eksperimen, atau pengembangan proyek lanjutan.

## Isi Utama Repositori

Secara umum, repositori ini mencakup:

- **Data mentah**: file awal sebelum dibersihkan.
- **Data hasil olahan**: data yang sudah diproses untuk analisis/modeling.
- **Kode program**: script/class untuk membaca, memproses, dan menganalisis data.
- **Dokumentasi**: penjelasan alur kerja, struktur, dan cara penggunaan.

## Alur Kerja (Workflow)

1. **Pengumpulan data**
   - Data diambil dari sumber yang tersedia.
2. **Pembersihan data**
   - Menangani nilai kosong, duplikat, dan format tidak konsisten.
3. **Transformasi data**
   - Konversi tipe data, normalisasi kolom, dan feature engineering sederhana.
4. **Analisis/implementasi PBO**
   - Pemrosesan dilakukan melalui class dan method agar modular.
5. **Output**
   - Hasil berupa data siap pakai, ringkasan, atau laporan.

## Struktur Kode Berbasis PBO

Pendekatan yang digunakan menekankan:

- **Enkapsulasi**: logika dipisah dalam class sesuai tanggung jawab.
- **Abstraksi**: antarmuka method dibuat sederhana untuk pemakaian ulang.
- **Modularitas**: tiap komponen (loader, cleaner, analyzer) dapat dikembangkan terpisah.

Contoh komponen class yang biasanya digunakan:

- `DataLoader` untuk membaca data.
- `DataCleaner` untuk pembersihan.
- `DataProcessor` untuk transformasi.
- `DataAnalyzer` untuk analisis/ringkasan.

## Cara Menggunakan

1. Clone repositori ini.
2. Siapkan environment Python dan dependensi yang dibutuhkan.
3. Jalankan script utama sesuai alur proyek.
4. Cek folder output/hasil untuk melihat data akhir.

## Catatan

- Pastikan format data input sesuai dengan yang diharapkan script.
- Jika menambah fitur baru, ikuti pola class yang sudah ada agar konsisten.
- Dokumentasikan perubahan penting agar mudah dipahami kolaborator lain.

## Kontribusi

Kontribusi diperbolehkan melalui:

1. Fork repositori.
2. Buat branch fitur/perbaikan.
3. Commit perubahan dengan pesan yang jelas.
4. Ajukan pull request.
