import pandas as pd
import random
import numpy as np

# --- KONFIGURASI ---
# Nama file input dari Kaggle
FILE_KAGGLE = r"data_klien_1\fashion_products.csv"
# Nama file output yang siap di-ingest RAG
FILE_OUTPUT = r"data_klien_1\data_fashion_final.csv"
# Rate Konversi Mata Uang
RATE_INR_TO_IDR = 183.86
# Batas jumlah produk yang akan diproses (Untuk menghindari laptop berat)
MAX_PRODUCTS = 1000

# --- FUNGSI UTAMA KONVERSI ---
def convert_and_enrich_data():
    
    print(f"[{'='*10} START KONVERSI DATA {'='*10}]")
    
    # 1. Load Data Kaggle
    try:
        # Cek kolom yang ada di file Kaggle Anda (ProductID, ProductName, Gender, Price (INR), Description)
        df = pd.read_csv(FILE_KAGGLE)
        # Ambil hanya jumlah maksimal produk yang ditentukan
        df = df.head(MAX_PRODUCTS) 
        print(f"✅ Berhasil load {len(df)} data produk dari Kaggle.")
    except Exception as e:
        print(f"❌ Error saat load file: {e}")
        return

    # 2. Konversi Harga INR ke IDR
    # Pastikan kolom 'Price (INR)' ada dan diisi numerik
    df['Price (INR)'] = pd.to_numeric(df['Price (INR)'], errors='coerce')
    df['Price (IDR)'] = (df['Price (INR)'] * RATE_INR_TO_IDR).round(-3) # Bulatkan ke ribuan terdekat
    df = df.dropna(subset=['Price (IDR)'])
    print(f"✅ Harga berhasil dikonversi ke IDR dengan rate {RATE_INR_TO_IDR}.")
    
    # 3. Siapkan List untuk Data Baru (Format RAG: Topik, Detail)
    new_data = []

    # --- A. MASUKKAN DATA SOP MANUAL (PENTING!) ---
    sop_list = [
        {"Topik": "Jam Operasional Toko", "Detail": "Senin-Sabtu 09.00-17.00 WIB. Minggu dan Hari Libur Nasional tutup."},
        {"Topik": "Kebijakan Retur Produk", "Detail": "Retur diterima jika ada video unboxing, cacat pabrik, atau salah kirim ukuran. Batas waktu klaim retur adalah 2x24 jam setelah barang diterima."},
        {"Topik": "Lokasi dan Pengiriman", "Detail": "Toko fisik berlokasi di Jl. Buah Batu No 45, Bandung. Kami melayani pengiriman ke seluruh Indonesia via JNE, TIKI, dan SiCepat."},
        {"Topik": "Kontak Admin", "Detail": "WA Official: 0812-3456-7890. Email: support@arjunstore.id."},
    ]
    new_data.extend(sop_list)

    # --- B. KONVERSI & ENRICHMENT DATA PRODUK KAGGLE ---
    for index, row in df.iterrows():
        # Ambil data esensial
        product_id = row['ProductID']
        nama_produk = row['ProductName']
        deskripsi = row['Description'].replace('\n', ' ') if pd.notna(row['Description']) else "Tidak ada deskripsi rinci."
        gender = row.get('Gender', 'Unisex')
        harga_idr = int(row['Price (IDR)'])
        primary_color = row.get('PrimaryColor', 'Multi Warna')
        
        # --- LOGIKA STOK DUMMY & UKURAN ---
        stok_s = random.randint(1, 15)
        stok_m = random.randint(5, 30) # Stok M paling banyak
        stok_l = random.randint(5, 20)
        stok_xl = random.randint(0, 5)
        total_stok = stok_s + stok_m + stok_l + stok_xl
        
        # --- LOGIKA KATEGORI HANGAT/ADEM (Untuk membantu RAG) ---
        # Kita pakai heuristik sederhana dari deskripsi
        if any(keyword in deskripsi.lower() for keyword in ['wool', 'sweater', 'jacket', 'coat', 'hoodie']):
            nuansa = "HANGAT dan TEBAL"
        elif any(keyword in deskripsi.lower() for keyword in ['cotton', 'breathable', 'summer', 't-shirt', 'tank']):
            nuansa = "ADEM dan RINGAN"
        else:
            nuansa = "STANDAR (Casual/Medium)"
        
        # Rangkai menjadi kalimat yang kaya konteks untuk RAG
        detail_teks = (
            f"[ID Produk: {product_id}] {nama_produk} ({gender}). \n"
            f"Harga Jual: Rp {harga_idr:,.0f}. \n"
            f"Stok Tersedia: Total {total_stok} pcs. (S={stok_s}, M={stok_m}, L={stok_l}, XL={stok_xl}). \n"
            f"Warna Utama: {primary_color}. \n"
            f"Karakteristik Produk: Nuansa {nuansa}. \n"
            f"Deskripsi Lengkap: {deskripsi}"
        )
        
        new_data.append({
            "Topik": f"Stok dan Detail Produk - {nama_produk}",
            "Detail": detail_teks
        })

    # 4. Simpan ke CSV Baru (Format RAG)
    df_final = pd.DataFrame(new_data)
    df_final.to_csv(FILE_OUTPUT, index=False)

    print(f"\n[{'='*10} PROSES SELESAI {'='*10}]")
    print(f"✨ File '{FILE_OUTPUT}' siap di-ingest dengan {len(df_final)} baris data (termasuk SOP).")
    print("Langkah selanjutnya: Jalankan 01_build_index.py.")

if __name__ == "__main__":
    convert_and_enrich_data()