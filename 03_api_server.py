# FILE: 03_api_server.py (VERSI GPT-5-NANO - ULTIMATE)
# TUGAS: API Server Chatbot Cerdas & Ringan

import chromadb
import os
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Import OpenAI Modules
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# --- 0. LOAD ENVIRONMENT ---
load_dotenv()

# --- 1. MODEL DATA ---
class QueryRequest(BaseModel):
    pertanyaan: str

class ChatResponse(BaseModel):
    jawaban: str

# --- 2. KEAMANAN (API KEY UNTUK KLIEN) ---
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
VALID_API_KEYS_STRING = os.environ.get("MY_VALID_API_KEYS")
if VALID_API_KEYS_STRING:
    VALID_API_KEYS = set(VALID_API_KEYS_STRING.split(","))
else:
    VALID_API_KEYS = {"kunci_rahasia_bos"}

async def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(status_code=401, detail="API Key Klien tidak valid")

# --- 3. GLOBAL SETUP (INIT OTAK & MEMORI) ---
print("--- [SERVER STARTUP] ---")

# A. SETUP MODEL (Sesuai Request: GPT-5-NANO)
if not os.environ.get("OPENAI_API_KEY"):
    print("⚠️ WARNING: OPENAI_API_KEY belum diset di .env")

# Embedding Model (Tetap pakai v3 small karena standar industri saat ini)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# LLM MODEL (MENGGUNAKAN GPT-5-NANO)
# Pastikan API Key Anda memiliki akses ke model preview ini
try:
    print("[STARTUP] Mengaktifkan Model: gpt-5-nano...")
    Settings.llm = OpenAI(model="gpt-5-nano", temperature=0.2)
except Exception as e:
    print(f"⚠️ [WARNING] Gagal init gpt-5-nano (Mungkin belum akses?), fallback ke gpt-4o: {e}")
    # Fallback safety (Jaga-jaga kalau API menolak)
    Settings.llm = OpenAI(model="gpt-4o", temperature=0.2)

# B. LOAD DATABASE (CHROMA)
print("[STARTUP] Membuka 'Lemari Arsip' ChromaDB...")
try:
    db = chromadb.PersistentClient(path="./chroma_db")
    # Nama collection harus konsisten dengan ingestion
    chroma_collection = db.get_or_create_collection("fashion_store")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Init Index Global
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=Settings.embed_model
    )
    print("✅ Database Berhasil Dimuat.")
except Exception as e:
    print(f"❌ [CRITICAL ERROR] Gagal load DB: {e}")
    index = VectorStoreIndex.from_documents([])

# C. SYSTEM PROMPT (VERSION: WORLD CLASS SALES + GENDER GATEKEEPER)
SYSTEM_PROMPT = (
    "Anda adalah Customer Service Toko Fashion Terbaik di Dunia yang bekerja untuk 'Arjun Fashion Store'. "
    "Anda bukan sekadar bot, melainkan seorang Sales Expert kelas dunia. "
    "Tujuan Anda: Membuat pelanggan merasa spesial, terbantu, dan akhirnya ingin membeli dengan senang hati."
    "\n\nATURAN UTAMA (HYBRID INTELLIGENCE):\n"
    "1. **Data Toko:** Gunakan data harga dan nama produk dari database. Jangan mengarang angka.\n"
    "2. **PANTANGAN KERAS (Negative Constraints):**\n"
    "   - **JANGAN PERNAH** bilang 'Data tidak disebutkan', 'Bahan tidak tercantum'. GANTI FOKUS ke penjelasan Model, Warna, atau Gaya.\n"
    "   - Jangan gunakan kata 'Versi Indonesia' atau 'Terjemahan'. Langsung bicara seolah itu nama asli produknya.\n"
    "3. **Inferensi Cerdas (Sales Mindset):**\n"
    "   - Fokus pada BENEFIT. Jika 'Kaos Polos', jual sebagai 'Must-have item'.\n"
    "4. **Lokalisasi Natural:** Terjemahkan nama produk Inggris ke Indonesia yang 'menjual'.\n"
    "5. **GENDER GATEKEEPER (PENTING):**\n"
    "   - Jika user adalah **WANITA** (atau bertanya produk wanita), dan database memberikan data produk **PRIA**, Anda WAJIB MENGABAIKAN data pria tersebut.\n"
    "   - Lebih baik bilang 'Maaf stok wanita habis' daripada menawarkan Boxer Pria ke user Wanita.\n"
    "\n\nSOP PELAYANAN:\n"
    "6. **Cara Menjawab List Produk:**\n"
    "   - Format: * **Nama Produk** (Harga) — *Selling Point Singkat*.\n"
    "7. **Handling Banyak Data:** Pilih maksimal 3-5 item terbaik.\n"
    "8. **Tone:** Percaya diri, hangat, solutif. Panggil 'Kak'.\n"
    "9. **Closing:** Arahkan ke langkah selanjutnya. 'Gimana Kak, mau aku cek size-nya?'"
)

# D. GLOBAL CHAT ENGINE
print("[STARTUP] Menyiapkan Chat Engine...")
global_chat_engine = index.as_chat_engine(
    chat_mode="context", 
    system_prompt=SYSTEM_PROMPT,
    similarity_top_k=5
)

# --- 4. INISIALISASI APP ---
app = FastAPI(title="Bot CS Arjun Fashion Store (GPT-5 Nano)")

# --- 5. FUNGSI PENDUKUNG (HELPER) ---

def perbaiki_pertanyaan(pertanyaan_asli: str) -> str:
    """
    Mediator Bahasa dengan FILTER KATEGORI & LOGIKA KONTEKS.
    """
    prompt_penerjemah = (
        f"Anda adalah Mediator Bahasa E-Commerce Fashion Profesional.\n"
        f"Tugas: Terjemahkan intent user (Indo) ke keywords pencarian (Inggris).\n"
        f"Database: T-Shirt, Shirt, Jeans, Trousers, Dress, Jacket, (Hindari Lingerie/Underwear kecuali diminta).\n"
        f"\nATURAN KRUSIAL (FILTERING):\n"
        f"1. **Anti-Salah Kategori:**\n"
        f"   - Jika user minta 'Baju cewek/wanita', TERJEMAHKAN ke 'Women Tops, Women Shirt, Women Dress, Women Blouse'.\n"
        f"   - **JANGAN** sertakan 'Bra', 'Lingerie', atau 'Underwear' kecuali user spesifik minta 'daleman'.\n"
        f"2. **Gender Context:**\n"
        f"   - 'Cewek/Wanita' -> Tambahkan keyword 'Women'.\n"
        f"   - 'Cowok/Pria' -> Tambahkan keyword 'Men'.\n"
        f"3. **Pertanyaan Lanjutan (Context Retention):**\n"
        f"   - Jika user tanya 'Bahannya adem ngga?' (tanpa subjek), asumsikan user menanyakan barang yang 'Breathable' dan 'Comfortable'.\n"
        f"   - Tambahkan 'Clothing material detail' agar mesin mencari deskripsi baju, bukan celana dalam.\n"
        f"\nCONTOH:\n"
        f"- User: 'Ada baju cewek?' -> Output: Women Tops Shirt Blouse Dress Casual (No Lingerie)\n"
        f"- User: 'Bahannya gimana?' -> Output: Product material detail fabric quality\n"
        f"\nPertanyaan User: '{pertanyaan_asli}' \n"
        f"Terjemahan Inggris (Hanya Output Teks):"
    )
    
    response = Settings.llm.complete(prompt_penerjemah)
    hasil = str(response).strip()
    
    if len(hasil) < 2: return pertanyaan_asli
    return hasil

def cek_intent(pertanyaan: str) -> str:
    """
    Menentukan apakah user butuh DATA PRODUK (SEARCH) atau hanya NGOBROL (CHAT).
    """
    prompt_router = (
        f"Klasifikasikan pesan user ke dalam dua kategori: 'SEARCH' atau 'CHAT'.\n"
        f"1. **SEARCH**: Jika user bertanya tentang produk, stok, harga, rekomendasi, bahan, warna, atau toko.\n"
        f"2. **CHAT**: Jika user hanya menyapa (Halo), memberi info diri (Saya cewek), setuju/menolak (Oke), atau berterima kasih.\n"
        f"\nContoh:\n"
        f"- 'Halo kak' -> CHAT\n"
        f"- 'Saya mau cari kemeja' -> SEARCH\n"
        f"- 'Saya wanita' -> CHAT\n"
        f"- 'Bahannya apa?' -> SEARCH\n"
        f"\nPesan User: '{pertanyaan}'\n"
        f"Kategori (Hanya output 1 kata):"
    )
    
    response = Settings.llm.complete(prompt_router)
    kategori = str(response).strip().upper()
    
    if "SEARCH" in kategori: return "SEARCH"
    return "CHAT"

# --- 6. ENDPOINT UTAMA ---

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
async def chat_endpoint(request: QueryRequest):
    
    print("\n" + "="*50)
    print(f"🚀 [START] User Input: {request.pertanyaan}")

    # 1. CEK INTENT (Polisi Lalu Lintas)
    intent = cek_intent(request.pertanyaan)
    print(f"🚦 [ROUTER] Intent Terdeteksi: {intent}")
    
    context_str = ""
    
    # 2. CABANG LOGIKA
    if intent == "SEARCH":
        # --- JALUR KANAN: BUTUH DATA GUDANG ---
        
        pertanyaan_inggris = perbaiki_pertanyaan(request.pertanyaan)
        print(f"📝 [TRANSLATOR] Query Gudang: '{pertanyaan_inggris}'")
        
        # 'index' aman diakses dari global
        retriever = index.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(pertanyaan_inggris)
        
        context_str = "\n\nINFORMASI STOK DARI DATABASE:\n"
        for node in nodes:
            context_str += f"- {node.text}\n"
            
        print(f"📦 [RETRIEVAL] Mengambil {len(nodes)} data produk.")

    else:
        # --- JALUR KIRI: HANYA NGOBROL ---
        print(f"🗣️ [CHAT MODE] Skip Retrieval. Langsung ngobrol.")
        context_str = ""

    # 3. EKSEKUSI JAWABAN (SALES EXPERT)
    if context_str:
        pesan_final = f"{request.pertanyaan}\n\n{context_str}"
    else:
        pesan_final = request.pertanyaan

    response = global_chat_engine.chat(pesan_final)
    
    print(f"🤖 [BOT] Reply: {str(response)[:100]}...")
    print("="*50 + "\n")
    
    return ChatResponse(jawaban=str(response))

@app.get("/")
def root():
    return {"status": "Bot Arjun Fashion Store (GPT-5 Nano) is Online 🚀"}