# FILE: 01_build_index.py
# TUGAS: HANYA MEMBANGUN DATABASE. JALANKAN INI SEKALI SAJA.

import pandas as pd
import chromadb
from llama_index.core import (
    VectorStoreIndex, 
    Document, 
    StorageContext, 
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

print("Memulai proses 'Ingesti Data' (Membangun Perpustakaan)...")

# --- 1. TENTUKAN "LEMARI ARSIP" (Vector Database) ---
print("Menyiapkan 'Lemari Arsip' (ChromaDB)...")
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("klien_dokter_qna")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# --- 2. TENTUKAN "ILMU" & "MESIN" (CARA BARU) ---
print("Memuat dan Mengatur 'Ilmu' (Embedding Model) secara Global...")
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
Settings.llm = None
Settings.chunk_size = 512 

# --- 3. BACA "BAHAN BAKU" (Loader dari CSV) ---
print("Membaca 'Bahan Baku' (File CSV)...")
try:
    df = pd.read_csv("Doctor_QnA_Indonesia_Cleaned.csv")
except FileNotFoundError:
    print("Error: File 'Doctor_QnA_Indonesia_Cleaned.csv' tidak ditemukan.")
    exit()

documents = []
for index, row in df.iterrows():
    text_content = f"Pertanyaan: {row['question']}\n\nJawaban: {row['answer']}"
    documents.append(Document(text=text_content))
print(f"Berhasil membaca {len(documents)} baris Q&A.")

# --- 4. JALANKAN "LINI PERAKITAN"! ---
print("Menjalankan 'Lini Perakitan' (Membuat Indeks)... Ini mungkin butuh beberapa menit...")
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

print("-" * 50)
print("SELAMAT! 'Perpustakaan Dokter' telah berhasil dibuat/diperbarui.")
print(f"Indeks Vektor disimpan di folder ./chroma_db")
print("-" * 50)