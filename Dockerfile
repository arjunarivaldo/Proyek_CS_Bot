# 1. Gunakan "Base Image" (OS Linux ringan yang sudah ada Python-nya)
FROM python:3.11-slim

# 2. Buat folder kerja di dalam kontainer
WORKDIR /app

# 3. Salin "Daftar Isi Koper" (requirements.txt) ke dalam kontainer
COPY requirements.txt .

# 4. Instal "Perkakas" (Library) di dalam kontainer
# Kita tambah --no-cache-dir agar ukuran kontainer lebih kecil
RUN pip install --no-cache-dir -r requirements.txt

# 5. Salin SELURUH kode dan database (chroma_db) Anda ke dalam kontainer
COPY . .

# 6. Buka "Port" 8000 (agar bisa diakses dari luar)
EXPOSE 8000

# 7. Tentukan Perintah Utama saat kontainer menyala
# PENTING: Kita pakai --host 0.0.0.0 agar bisa diakses dari luar kontainer
CMD ["uvicorn", "03_api_server:app", "--host", "0.0.0.0", "--port", "8000"]