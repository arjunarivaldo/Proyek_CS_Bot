# FILE: 01_build_index.py
# TUGAS: Ingest Dataset Role-Based (CS / Affiliator / Advisor)

import pandas as pd
import chromadb
import os
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding

# --- LOAD ENV ---
load_dotenv()

# --- KONFIGURASI ---
NAMA_FILE_CSV = "data_klien_1/products_role_based.csv"  # ⬅️ FILE BARU
NAMA_COLLECTION = "fashion_store"
DB_PATH = "./chroma_db"

def build_index():
    print(f"🚀 Memulai Ingestion Data dari {NAMA_FILE_CSV}...")

    if not os.path.exists(NAMA_FILE_CSV):
        print(f"❌ File {NAMA_FILE_CSV} tidak ditemukan!")
        return

    df = pd.read_csv(NAMA_FILE_CSV)
    print(f"📊 Ditemukan {len(df)} produk.")

    documents = []

    for _, row in df.iterrows():
        # --- TEXT UTAMA UNTUK VECTOR SEARCH ---
        text_content = f"""
        Nama Produk: {row['nama_produk']}
        Kategori: {row['kategori']} - {row['sub_kategori']}
        Gender: {row['gender']}
        Occasion: {row['occasion']}
        Harga: Rp {int(row['harga']):,}
        Deskripsi: {row['deskripsi']}
        Warna: {row['warna_tersedia']}
        Body Type: {row['body_type']}
        Skin Tone: {row['skin_tone']}
        """

        # --- METADATA (UNTUK LOGIC, BUKAN SEMANTIC SEARCH) ---
        metadata = {
            "product_id": int(row["id"]),
            "nama_produk": row["nama_produk"],
            "kategori": row["kategori"],
            "sub_kategori": row["sub_kategori"],
            "gender": row["gender"],
            "occasion": row["occasion"],
            "harga": int(row["harga"]),
            "tier": row["tier"],  # 🔥 KUNCI PIVOT
            "product_link": row.get("product_link", ""),
            "affiliate_link": row.get("affiliate_link", ""),
            "image_url": row.get("image_url", "")
        }

        doc = Document(
            text=text_content.strip(),
            metadata=metadata
        )
        documents.append(doc)

    print(f"📦 Total dokumen siap di-ingest: {len(documents)}")

    # --- SETUP EMBEDDING ---
    print("⚙️ Menyiapkan Embedding Model...")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    # --- SETUP CHROMADB ---
    db = chromadb.PersistentClient(path=DB_PATH)

    try:
        db.delete_collection(NAMA_COLLECTION)
        print("🧹 Koleksi lama dihapus.")
    except:
        print("ℹ️ Tidak ada koleksi lama, lanjut membuat baru.")

    chroma_collection = db.get_or_create_collection(NAMA_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    # --- BUILD INDEX ---
    print("🧠 Memasukkan data ke Vector Store...")
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    print("✅ INGEST SELESAI")
    print("📁 DB Path:", DB_PATH)
    print("📚 Collection:", NAMA_COLLECTION)

if __name__ == "__main__":
    build_index()
