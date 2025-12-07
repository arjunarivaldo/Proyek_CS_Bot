# FILE: 01_build_index.py
# TUGAS: Membaca CSV dan menyimpannya ke ChromaDB (Versi OpenAI)

import pandas as pd
import chromadb
import os
import time
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding # <-- IMPORT BARU

# --- KONFIGURASI ---
# Ganti dengan nama file CSV Anda yang sebenarnya
NAMA_FILE_CSV = "Doctor_QnA_Indonesia_Cleaned.csv" 

# --- CEK API KEY ---
# Kita butuh kunci ini untuk menjalankan embedding
if not os.environ.get("OPENAI_API_KEY"):
    print("[ERROR] OPENAI_API_KEY tidak ditemukan di environment variable!")
    print("Cara pasang di PowerShell: $env:OPENAI_API_KEY='sk-proj-...'")
    exit()

def main():
    print("--- Memulai Proses Ingestion (Versi OpenAI) ---")
    start_time = time.time()

    # 1. SETUP "OTAK" EMBEDDING
    # Kita pakai model 'text-embedding-3-small' (Cepat, Murah, Cerdas)
    print("Menyiapkan model OpenAI Embedding...")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    # Kita tidak butuh LLM (Juru Bicara) untuk tahap ini, cuma butuh Embedding
    Settings.llm = None 

    # 2. BACA DATA
    print(f"Membaca file CSV: {NAMA_FILE_CSV}...")
    try:
        df = pd.read_csv(NAMA_FILE_CSV)
        print(f"Berhasil membaca {len(df)} baris data.")
    except Exception as e:
        print(f"Error membaca CSV: {e}")
        return

    # 3. KONVERSI KE DOKUMEN
    print("Mengkonversi data ke format LlamaIndex Document...")
    documents = []
    for index, row in df.iterrows():
        text_content = f"Pertanyaan: {row['question']}\n\nJawaban: {row['answer']}"
        doc = Document(text=text_content)
        documents.append(doc)

    # 4. SIAPKAN DATABASE (CHROMA)
    print("Menyiapkan Vector Database (ChromaDB)...")
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("klien_dokter_qna")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 5. PROSES EMBEDDING & PENYIMPANAN (YANG MAHAL DI SINI)
    # Ini akan mengirim data ke OpenAI, mengubahnya jadi angka, dan simpan.
    print("Mulai proses indexing (Mengirim ke OpenAI)... Mohon tunggu...")
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    end_time = time.time()
    print(f"--- SELESAI! Ingestion tuntas dalam {end_time - start_time:.2f} detik. ---")
    print("Database baru tersimpan di folder './chroma_db'")

if __name__ == "__main__":
    main()