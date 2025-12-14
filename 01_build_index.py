# FILE: 01_build_index.py
import pandas as pd
import chromadb
from llama_index.core import VectorStoreIndex, Document, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import os
from dotenv import load_dotenv

load_dotenv()

# --- KONFIGURASI ---
NAMA_FILE_CSV = "data_klien_1/data_fashion_final.csv" # Pastikan file ini ada
NAMA_COLLECTION = "fashion_store" # <--- KITA KUNCI NAMANYA DISINI
DB_PATH = "./chroma_db"

def build_index():
    print(f"🚀 Memulai Ingestion Data dari {NAMA_FILE_CSV}...")
    
    # 1. Baca Data
    if not os.path.exists(NAMA_FILE_CSV):
        print(f"❌ File {NAMA_FILE_CSV} tidak ditemukan!")
        return

    df = pd.read_csv(NAMA_FILE_CSV)
    print(f"📊 Ditemukan {len(df)} baris data.")

    # 2. Buat Dokumen LlamaIndex
    documents = []
    for idx, row in df.iterrows():
        # Kita gabungkan Topik dan Detail agar pencarian lebih kaya
        text_content = f"{row['Topik']}\n{row['Detail']}"
        
        doc = Document(
            text=text_content,
            metadata={
                "row_id": idx,
                "topik": row['Topik']
            }
        )
        documents.append(doc)

    # 3. Setup ChromaDB & Embedding
    print("⚙️  Menyiapkan ChromaDB & Embedding...")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    # Init Client
    db = chromadb.PersistentClient(path=DB_PATH)
    
    # Hapus koleksi lama jika ada (biar bersih)
    try:
        db.delete_collection(NAMA_COLLECTION)
        print("🧹 Koleksi lama dihapus, membuat yang baru...")
    except:
        pass

    chroma_collection = db.get_or_create_collection(NAMA_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. Build Index (Memasukkan Data ke Otak)
    print("🧠 Sedang memasukkan data ke Vector Store (Ini butuh waktu)...")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        show_progress=True
    )

    print("✅ SUKSES! Index tersimpan di folder:", DB_PATH)
    print("Nama Collection:", NAMA_COLLECTION)

if __name__ == "__main__":
    build_index()