# FILE: 01_build_index.py
# TUGAS: Membaca Data Fashion dan menyimpannya ke ChromaDB

import pandas as pd
import chromadb
import os
import time
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding

# --- KONFIGURASI ---
NAMA_FILE_CSV = r"data_klien_1\data_fashion.csv"  # <-- NAMA FILE BARU

# --- CEK API KEY ---
if not os.environ.get("OPENAI_API_KEY"):
    print("[ERROR] OPENAI_API_KEY tidak ditemukan!")
    exit()

def main():
    print("--- Memulai Proses Ingestion (Toko Fashion Arjun) ---")
    start_time = time.time()

    # 1. SETUP "OTAK" EMBEDDING
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.llm = None 

    # 2. BACA DATA
    print(f"Membaca file CSV: {NAMA_FILE_CSV}...")
    try:
        df = pd.read_csv(NAMA_FILE_CSV)
        print(f"Berhasil membaca {len(df)} baris data.")
    except Exception as e:
        print(f"Error membaca CSV: {e}")
        return

    # 3. KONVERSI KE DOKUMEN (FORMAT BARU)
    print("Mengkonversi data ke format LlamaIndex Document...")
    documents = []
    for index, row in df.iterrows():
        # Kita gabungkan Topik dan Detail jadi satu teks utuh
        text_content = f"Topik: {row['Topik']}\nInformasi Detail: {row['Detail']}"
        
        # Metadata membantu pencarian lebih spesifik (opsional tapi bagus)
        doc = Document(
            text=text_content,
            metadata={"topik": row['Topik']}
        )
        documents.append(doc)

    # 4. SIAPKAN DATABASE (CHROMA)
    # Hapus DB lama dulu biar bersih (Manual di terminal lebih aman, tapi kode ini akan menimpa/menambah)
    print("Menyiapkan Vector Database...")
    db = chromadb.PersistentClient(path="./chroma_db")
    # Ganti nama collection biar tidak campur dengan data medis
    chroma_collection = db.get_or_create_collection("toko_fashion_arjun") 
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 5. PROSES EMBEDDING
    print("Mulai proses indexing ke OpenAI...")
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    end_time = time.time()
    print(f"--- SELESAI! Database Fashion siap dalam {end_time - start_time:.2f} detik. ---")

if __name__ == "__main__":
    main()