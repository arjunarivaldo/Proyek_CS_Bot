import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# 1. Load Data
df = pd.read_csv('data_klien_1/data_fashion_final.csv')

# 2. LOGIKA PARSING (NLP Extraction)
# Karena data kita berbentuk teks panjang, kita harus 'mancing' angkanya keluar
# menggunakan Regex (Regular Expression).

def extract_info(text):
    # Cari pola "Harga Jual: Rp (angka)"
    price_match = re.search(r'Harga Jual: Rp ([\d,]+)', str(text))
    # Cari pola "Total (angka) pcs"
    stock_match = re.search(r'Total (\d+) pcs', str(text))
    
    # Ambil nilainya jika ketemu
    price = int(price_match.group(1).replace(',', '')) if price_match else None
    stock = int(stock_match.group(1)) if stock_match else None
    
    # Cari kategori Nuansa (Logic sederhana string matching)
    nuance = "Standar"
    if "Nuansa HANGAT" in str(text): nuance = "Hangat"
    if "Nuansa ADEM" in str(text): nuance = "Adem"
    
    return pd.Series([price, stock, nuance])

# Terapkan fungsi ke kolom 'Detail' (Abaikan baris SOP 4 teratas)
products = df[df['Detail'].str.contains("Harga Jual", na=False)].copy()
products[['Price', 'Stock', 'Nuance']] = products['Detail'].apply(extract_info)

# 3. VISUALISASI DATA
plt.figure(figsize=(15, 5))

# Plot 1: Sebaran Harga (Apakah toko kita kemahalan?)
plt.subplot(1, 3, 1)
sns.histplot(products['Price'], kde=True, color='green')
plt.title('Distribusi Harga Produk (IDR)')
plt.xlabel('Harga (Rupiah)')
plt.ylabel('Jumlah Produk')

# Plot 2: Ketersediaan Stok
plt.subplot(1, 3, 2)
sns.histplot(products['Stock'], kde=True, color='blue')
plt.title('Distribusi Stok per Barang')
plt.xlabel('Jumlah Stok (Pcs)')

# Plot 3: Kategori Nuansa (Adem vs Hangat)
plt.subplot(1, 3, 3)
sns.countplot(x='Nuance', data=products, palette='viridis')
plt.title('Jumlah Produk per Kategori Nuansa')

plt.tight_layout()
plt.show()

print("✅ EDA Selesai. Tutup jendela grafik untuk kembali ke terminal.")