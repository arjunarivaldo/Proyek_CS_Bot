# FILE: 02_test_query.py
# TUGAS: HANYA BERTANYA KE DATABASE. (VERSI INTERAKTIF - OPENAI)

import chromadb
import os # <-- Tambahan untuk cek key
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
# PERBAIKAN DI SINI: Import dari module 'openai', bukan 'huggingface'
from llama_index.embeddings.openai import OpenAIEmbedding
import time

print("--- Memulai Ujicoba 'Dapur' (Mode Cepat - OpenAI) ---")

# --- CEK API KEY (PENTING) ---
if not os.environ.get("OPENAI_API_KEY"):
    print("[ERROR] OPENAI_API_KEY tidak ditemukan di environment variable!")
    print("Pastikan Anda sudah melakukan set key di terminal sebelum menjalankan script ini.")
    exit()

start_time = time.time()

# --- 1. TENTUKAN "ILMU" (HARUS SAMA DENGAN SAAT BUILD) ---
print("Memuat 'Ilmu' (Embedding Model OpenAI)...")
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-small" # PERBAIKAN: gunakan parameter 'model', bukan 'model_name'
)
Settings.llm = None

# --- 2. HUBUNGKAN KE "LEMARI ARSIP" YANG SUDAH ADA ---
print("Menghubungkan ke 'Lemari Arsip' (ChromaDB)...")
db = chromadb.PersistentClient(path="./chroma_db")
try:
    chroma_collection = db.get_collection("fashion_store")
except Exception as e:
    print("="*50)
    print("ERROR: Collection 'fashion_store' tidak ditemukan.")
    print("Pastikan Anda sudah menjalankan '01_build_index.py' (Versi OpenAI) setidaknya satu kali.")
    print("="*50)
    exit()
    
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# --- 3. MUAT INDEKS DARI 'LEMARI ARSIP' ---
print("Memuat Indeks dari storage...")
index_dari_storage = VectorStoreIndex.from_vector_store(
    vector_store
)

# --- 4. BUAT "PUSTAKAWAN" (RETRIEVER) ---
print("Menyiapkan 'Pustakawan' (Retriever)...")
# Kita tetap pakai top_k=3 agar bisa menganalisis hasil
retriever = index_dari_storage.as_retriever(similarity_top_k=3) #Mengambil 3 hasil teratas

end_time = time.time()
print(f"Setup selesai dalam {end_time - start_time:.2f} detik.")
print("=" * 50)
print("SIAP MENERIMA PERTANYAAN!")
print("Ketik 'exit' atau tekan Ctrl+C untuk keluar.")
print("=" * 50)

# --- 5. BAGIAN INTERAKTIF ---
while True:
    try:
        # Minta input dari user
        pertanyaan = input("\nKetik Pertanyaan Anda > ")

        # Cek jika user ingin keluar
        if pertanyaan.lower() == 'exit':
            print("[BOT]: Terima kasih, sampai jumpa!")
            break
        
        if not pertanyaan:
            continue

        # Waktu mulai query
        query_start = time.time()
        
        # Jalankan retrieval
        nodes = retriever.retrieve(pertanyaan)
        
        query_end = time.time()

        print(f"\n--- HASIL DARI PUSTAKAWAN (ditemukan dalam {query_end - query_start:.2f} detik) ---")
        
        if nodes:
            # Tampilkan 3 hasil teratas
            for i, node in enumerate(nodes):
                print(f"Hasil #{i+1} (Skor: {node.score:.4f}):")
                print(f"{node.get_content()}\n" + "-"*20)
        else:
            print("Maaf, saya tidak menemukan informasi yang relevan.")

    except KeyboardInterrupt:
        # Handle jika user menekan Ctrl+C
        print("\n[BOT]: Keluar dari program...")
        break
    except Exception as e:
        print(f"[ERROR]: Terjadi kesalahan: {e}")
        break