# FILE: 03_api_server.py (VERSI 3 - FINAL DENGAN KEAMANAN)
# TUGAS: Menjalankan "Loket Pelayanan" (API) 24/7 dengan Penjaga Keamanan.

import chromadb
import time
import os
from fastapi import FastAPI, Depends, HTTPException, Security # <-- IMPORT TAMBAHAN
from fastapi.security import APIKeyHeader # <-- IMPORT TAMBAHAN
from pydantic import BaseModel
from typing import List, Optional
from starlette.status import HTTP_401_UNAUTHORIZED # <-- IMPORT TAMBAHAN

from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. Model Data (Struktur JSON untuk API) ---
# Ini tidak berubah
class QueryRequest(BaseModel):
    pertanyaan: str
    top_k: Optional[int] = 3

class NodeResponse(BaseModel):
    skor: float
    konten: str

class QueryResponse(BaseModel):
    hasil: List[NodeResponse]

# --- 2. Konfigurasi Keamanan (VERSI AMAN - Environment Variable) ---

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# Ambil 'Daftar Tamu' dari "luar".
# Kita akan menyimpan daftar kunci sebagai SATU string, dipisah koma.
# Contoh: "kunci_A,kunci_B,kunci_C"
VALID_API_KEYS_STRING = os.environ.get("MY_VALID_API_KEYS")

# Ubah string menjadi 'set' (daftar) yang bisa diperiksa
if VALID_API_KEYS_STRING:
    VALID_API_KEYS = set(VALID_API_KEYS_STRING.split(","))
else:
    print("PERINGATAN: Variabel 'MY_VALID_API_KEYS' tidak diatur!")
    VALID_API_KEYS = set() # Kosongkan jika tidak diatur

async def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    """
    Ini adalah "Penjaga Keamanan" Anda.
    Dia akan mengecek 'header' X-API-Key yang masuk.
    """
    if api_key in VALID_API_KEYS:
        return api_key  # Kunci valid, silakan masuk
    else:
        # Kunci salah atau tidak ada, usir!
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API Key tidak valid atau tidak ditemukan"
        )

# --- 3. Fungsi Setup (Load INDEKS 1x Saat Startup) ---
# Fungsi ini tidak berubah dari Versi 2
def load_index() -> VectorStoreIndex:
    print("--- [SERVER STARTUP] ---")
    start_time = time.time()
    print("[SERVER STARTUP] Memuat 'Ilmu' (Embedding Model)...")
    # Settings.embed_model = HuggingFaceEmbedding(
    #     model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    # )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Settings.llm = None
    print("[SERVER STARTUP] Menghubungkan ke 'Lemari Arsip' (ChromaDB)...")
    db = chromadb.PersistentClient(path="./chroma_db")
    try:
        chroma_collection = db.get_collection("klien_dokter_qna")
    except Exception as e:
        print(f"[SERVER STARTUP] GAGAL: {e}")
        raise e
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    print("[SERVER STARTUP] Memuat Indeks dari storage...")
    index_dari_storage = VectorStoreIndex.from_vector_store(vector_store)
    end_time = time.time()
    print(f"--- [SERVER STARTUP] Setup selesai dalam {end_time - start_time:.2f} detik. ---")
    return index_dari_storage

# --- 4. Inisialisasi API & "Indeks" ---
print("[SERVER STARTUP] Menginisialisasi FastAPI...")
app = FastAPI(
    title="API Bot CS (Dokter Q&A)",
    description="Endpoint untuk MVP Level 1 Bot CS (RAG Murni).",
    version="1.0.0"
)
global_index = load_index()
print("=" * 50)
print("API SIAP MENERIMA REQUEST di http://127.0.0.1:8000")
print("=" * 50)

# --- 5. API Endpoint ("Loket Pelayanan" YANG DIJAGA) ---
@app.post(
    "/tanya", 
    response_model=QueryResponse,
    dependencies=[Depends(get_api_key)] # <-- INI DIA PENJAGANYA!
)
async def tanya_bot(request: QueryRequest):
    """
    Endpoint utama untuk menerima pertanyaan dari klien.
    HANYA BISA DIAKSES DENGAN X-API-Key yang valid.
    """
    # KODE DI BAWAH INI HANYA AKAN DIJALANKAN JIKA 'get_api_key' SUKSES
    
    print(f"\n[REQUEST DITERIMA] Pertanyaan: '{request.pertanyaan}', Top K: {request.top_k}")
    
    retriever = global_index.as_retriever(
        similarity_top_k=request.top_k
    )
    
    query_start = time.time()
    nodes = retriever.retrieve(request.pertanyaan)
    query_end = time.time()
    
    print(f"[RETRIEVAL] Selesai dalam {query_end - query_start:.2f} detik.")

    hasil_json = []
    for node in nodes:
        hasil_json.append(
            NodeResponse(
                skor=node.score, 
                konten=node.get_content()
            )
        )
    
    return QueryResponse(hasil=hasil_json)

# --- 6. Endpoint 'Health Check' (Tidak berubah) ---
@app.get("/")
async def root():
    return {"message": "API Bot CS Anda 'Hidup'. Buka /docs untuk uji coba."}