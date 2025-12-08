# FILE: 03_api_server.py (VERSI OPENAI - LEVEL 3 CHAT)
# TUGAS: API Server Chatbot Cerdas & Ringan

import chromadb
import os
import time
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional

# Import OpenAI Modules
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


# --- 1. MODEL DATA ---
class QueryRequest(BaseModel):
    pertanyaan: str
    # Kita tidak butuh top_k di request chat biasa, tapi boleh disisakan

class ChatResponse(BaseModel):
    jawaban: str
    # Kita kembalikan string jawaban langsung, bukan node raw

# --- 2. KEAMANAN (API KEY UNTUK KLIEN) ---
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
VALID_API_KEYS_STRING = os.environ.get("MY_VALID_API_KEYS")
if VALID_API_KEYS_STRING:
    VALID_API_KEYS = set(VALID_API_KEYS_STRING.split(","))
else:
    VALID_API_KEYS = set()

async def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(status_code=401, detail="API Key Klien tidak valid")

# --- 3. FUNGSI SETUP (LOAD OTAK CLOUD) ---
def load_chat_engine():
    print("--- [SERVER STARTUP] ---")
    
    # Cek Kunci OpenAI (Kunci 'Dapur')
    if not os.environ.get("OPENAI_API_KEY"):
        print("[CRITICAL] OPENAI_API_KEY belum diset! Server tidak bisa jalan.")
        # Di production, kita biarkan error biar ketahuan
    
    # 1. SETUP MODEL (Sangat Ringan di RAM)
    print("[STARTUP] Menghubungkan ke OpenAI API...")
    
    # Otak Kiri (Pustakawan)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    # Otak Kanan (Juru Bicara - GPT-5-nano)
    # temperature=0.2 biar tidak terlalu kreatif/halu
    Settings.llm = OpenAI(model="gpt-5-nano", temperature=0.2) 

    # 2. LOAD DATABASE
    print("[STARTUP] Membuka 'Lemari Arsip' ChromaDB...")
    db = chromadb.PersistentClient(path="./chroma_db")
    try:
        # PERUBAHAN DISINI:
        chroma_collection = db.get_collection("toko_fashion_arjun") 
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store)
    except Exception as e:
        print(f"[ERROR] Gagal load DB Fashion: {e}")
        raise e

    # 3. BUAT CHAT ENGINE (MEMORI + RAG)
    print("[STARTUP] Menyiapkan Chat Engine Fashion...")
    
    SYSTEM_PROMPT = (
        "Anda adalah Customer Service AI untuk 'Arjun Fashion Store'. "
        "Tugas Anda adalah melayani pelanggan dengan ramah dan persuasif agar mereka segera membeli. "
        "\nATURAN PENTING:\n"
        "1. Gunakan data 'Konteks' sebagai referensi stok dan kebijakan. "
        "2. SAAT DITANYA STOK: Jangan sebutkan rincian angka (misal 'Total 30 pcs') kecuali user bertanya spesifik jumlahnya. "
        "Cukup jawab 'Ada Kak' atau 'Ready Kak' dan sebutkan ukuran yang tersedia jika perlu. "
        "3. Langsung arahkan ke pemesanan. Contoh: 'Masih ada Kak. Mau ukuran apa?' atau 'Ready Kak, mau dibungkus berapa pcs?'.\n"
        "4. Gaya bahasa: Santai, ramah, gunakan sapaan 'Kak', dan hindari bahasa robot yang kaku.\n"
        "5. Jika stok ukuran tertentu habis, tawarkan ukuran lain atau warna lain yang tersedia.\n"
    )
    
    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context", # Mode Pintar (Memori + RAG)
        system_prompt=SYSTEM_PROMPT,
        verbose=True
    )
    
    print("--- [SERVER SIAP] ---")
    return chat_engine

# --- 4. INISIALISASI ---
app = FastAPI(title="Bot CS AI (OpenAI Version)")

# Load Engine Global
# Perhatikan: ChatEngine di LlamaIndex menyimpan state/memori per sesi.
# Untuk MVP sederhana ini, kita pakai satu engine global. 
# (Untuk production nyata multi-user, nanti kita butuh session_id, tapi ini cukup untuk MVP).
global_chat_engine = load_chat_engine()

# --- 5. ENDPOINT ---
@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
async def chat_endpoint(request: QueryRequest):
    """
    Endpoint Chatbot Cerdas (Level 3).
    Bisa mengingat konteks percakapan pendek.
    """
    # Panggil OpenAI (GPT-5-nano)
    # Ini akan memakan waktu 1-3 detik (tergantung OpenAI), tapi RAM aman.
    response = global_chat_engine.chat(request.pertanyaan)
    
    return ChatResponse(jawaban=str(response))

@app.get("/")
def root():
    return {"status": "Bot AI (OpenAI) Online & Ready"}