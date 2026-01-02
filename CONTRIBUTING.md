# Contributing Guide – Gemini Fashion AI Project

Dokumen ini berisi **aturan inti** agar tim bisa bekerja rapi, aman, dan tanpa konflik.  
Aturan sedikit, tapi **WAJIB dipatuhi** oleh semua anggota.

---

## 1. Aturan Dasar

- Repository ini menggunakan **Git + GitHub workflow**
- Semua perubahan **WAJIB tercatat melalui commit**
- Tidak ada perubahan langsung ke branch utama tanpa proses review.

---

## 2. Cara Memulai Kontribusi

1. Clone repository (JANGAN download ZIP):
   ```bash
   git clone https://github.com/arjunarivaldo/Proyek_CS_Bot.git
   ```
2. Masuk ke folder project:
   ```bash
   cd Proyek_CS_Bot
   ```
3. Pastikan menggunakan branch yang benar:
   ```bash
   git branch
   ```

Branch main dan dev **sudah disediakan dan tidak untuk development langsung**.

--- 

## 3. Struktur Branch (WAJIB)

Branch utama:

- main → versi stabil / siap demo / presentasi
- dev → gabungan seluruh hasil kerja tim

Setiap anggota WAJIB membuat branch sendiri dengan format:
   ```text
   feature/nama-atau-fitur
   ```
Contoh:
- feature/arjun-backend
- feature/bintang-data
- feature/abdul-ui
- feature/krisna-testing

❌ DILARANG:
- Bekerja langsung di main
- Bekerja langsung di dev

--- 

## 4. Workflow Harian (WAJIB DIIKUTI)

Saat mulai bekerja
   ```bash
   git checkout dev
   git pull origin dev
   git checkout feature/nama-branch
   git merge dev
   ```

Tujuan:
- Selalu bekerja dari versi terbaru tim
- Menghindari konflik antar anggota

---

Saat menyelesaikan 1 task kecil
   ```bash
   git add .
   git commit -m "feat: deskripsi perubahan singkat dan jelas"
   git push origin feature/nama-branch
   ```
Catatan:
- Commit kecil lebih baik daripada commit besar
- Jangan menunda commit terlalu lama

---
## 5. Aturan Commit Message
Gunakan format berikut:
   ```text
   feat: menambah fitur baru
   fix: memperbaiki bug
   refactor: merapikan kode tanpa mengubah behavior
   docs: update dokumentasi
   test: menambah atau memperbaiki testing
   chore: perubahan kecil non-fungsional
   ```

Contoh commit yang BENAR:
- feat: tambah validasi input order
- fix: perbaiki error intent detection
- refactor: rapikan struktur fungsi API

❌ Commit yang TIDAK BOLEH:
- update
- fix bug
- perubahan
- coba-coba
Commit message adalah **alat komunikasi tim**, bukan formalitas.

---

## 6. Pull Request (PR)

- Push ke branch sendiri
- Buat Pull Request ke dev
- Minimal 1 orang lain review
❌ Tidak boleh merge PR sendiri.

---

## 7. Jangan Commit File Sensitif atau Besar

❌ Dilarang commit:
- .env
- API key / secret
- chroma_db, venv
- File data besar tanpa izin tim

---

## Penutup

Dokumen ini dibuat untuk menjaga kualitas kerja tim dan kelancaran kolaborasi.  
Jika terjadi kebingungan atau perbedaan pendapat, **aturan dalam dokumen ini menjadi acuan utama**.

Terima kasih atas komitmen dan kontribusinya. 🚀
