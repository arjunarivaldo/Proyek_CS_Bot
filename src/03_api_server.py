# ======================================================
# FILE: 03_api_server.py
# FASHA AI — LLM-Orchestrated Commerce Assistant
# INTENT by LLM | MODE by LLM | DATA by PYTHON
# ======================================================

import os
import csv
import re
from datetime import datetime
from dotenv import load_dotenv

import chromadb
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from src.prompts import EMPLOYEE_PROMPT, AFFILIATE_PROMPT, ADVISOR_PROMPT, SEARCH_PROMPT

import logging

# ================== LOGGING SETUP ==================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("FASHA_AI")
# ===================================================

def log_ai_flow(intent: str, state: str, user_msg: str):
    icon_map = {
        "SEARCH": "🔍",
        "ORDER": "🛒",
        "CHAT": "💬",
    }

    state_icon_map = {
        "IDLE": "🟢",
        "AWAITING_CONFIRMATION": "🟡",
        "COLLECTING_DATA": "📝",
        "WAITING_PAYMENT": "💰",
    }

    intent_icon = icon_map.get(intent, "🤖")
    state_icon = state_icon_map.get(state, "⚪")

    logger.info(
        "%s %s AI_FLOW | intent=%s | state=%s | user=\"%s\"",
        intent_icon,
        state_icon,
        intent,
        state,
        user_msg
    )


# ======================================================
# 0. LOAD ENV
# ======================================================
load_dotenv()

# ======================================================
# 1. API MODELS
# ======================================================
class QueryRequest(BaseModel):
    pertanyaan: str

class ChatResponse(BaseModel):
    jawaban: str

# ======================================================
# 2. API SECURITY
# ======================================================
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
VALID_API_KEYS = set(
    os.environ.get("MY_VALID_API_KEYS", "kunci_rahasia_bos").split(",")
)

async def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="API Key tidak valid")
    return api_key

# ======================================================
# 3. INIT LLM & VECTOR DB
# ======================================================
if not os.environ.get("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY belum diset")

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

try:
    Settings.llm = OpenAI(model="gpt-5-nano", temperature=0.2)
except:
    Settings.llm = OpenAI(model="gpt-4o", temperature=0.2)

db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("fashion_store")
vector_store = ChromaVectorStore(chroma_collection=collection)
index = VectorStoreIndex.from_vector_store(vector_store)

# ======================================================
# 4. FASTAPI INIT
# ======================================================
app = FastAPI(title="Fasha AI — Role Based Fashion Assistant")

# ======================================================
# 5. MEMORY & ORDER STATE
# ======================================================
CHAT_HISTORY = []
ORDER_STATE = "IDLE"
# IDLE | AWAITING_CONFIRMATION | COLLECTING_DATA | WAITING_PAYMENT


# ======================================================
# 6. TRANSACTION STORAGE
# ======================================================
FILE_TRANSAKSI = "data_transaksi.csv"

def simpan_pesanan(nama, item, alamat, harga):
    try:
        file_exists = os.path.isfile(FILE_TRANSAKSI)
        with open(FILE_TRANSAKSI, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Tanggal", "Nama", "Item", "Harga", "Alamat", "Status"])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                nama, item, harga, alamat, "PENDING"
            ])
        return True
    except:
        return False

# ======================================================
# 7. LLM — INTENT DETECTOR
# ======================================================
def llm_detect_intent(user_message: str) -> str:
    prompt = f"""
Tugas kamu adalah mengklasifikasikan NIAT UTAMA user ke SATU intent saja.

Kamu HARUS memilih salah satu dari:
SEARCH
ORDER
CHAT

────────────────────────
DEFINISI INTENT (WAJIB DIIKUTI)
────────────────────────

1️⃣ SEARCH  
Gunakan SEARCH jika user menunjukkan NIAT MENCARI atau MEMILIH PRODUK, termasuk:
- meminta rekomendasi produk
- menyebut kebutuhan atau aktivitas (kondangan, olahraga, padel, renang, kerja, dll)
- menyebut budget TANPA memilih item spesifik
- berkata:
  - "ada rekomendasi?"
  - "lagi cari..."
  - "yang cocok buat..."
  - "saya mau beli tapi belum tahu yang mana"
  - "ada produk yang sesuai...?"

CATATAN PENTING:
- Jika user ingin membeli TAPI BELUM menyebut produk yang jelas → tetap SEARCH
- SEARCH adalah fase eksplorasi, BELUM transaksi

Contoh SEARCH:
- "Saya mau cari baju batik buat kondangan"
- "Ada outfit yang cocok buat main padel?"
- "Budget 500 ribu, ada rekomendasi?"
- "Ada baju renang yang syar'i?"

────────────────────────

2️⃣ ORDER  
Gunakan ORDER HANYA JIKA user SUDAH MEMILIH PRODUK SECARA JELAS, ditandai oleh:
- menyebut NAMA PRODUK atau IDENTITAS ITEM
- menyebut ukuran / warna / jumlah
- mengkonfirmasi pilihan ("yang ini", "ambil yang A", "jadi pesan")
- mulai masuk ke proses transaksi

Kata kunci kuat ORDER:
- "saya pesan..."
- "ambil yang ini"
- "checkout"
- "order sekarang"
- "jadi beli..."
- "ukuran M 1 pcs"
- "kirim ke alamat..."

Contoh ORDER:
- "Saya pesan Aylee Set ukuran M"
- "Ambil hoodie Adrea warna hitam size L"
- "Jadi beli yang nomor 2"
- "Saya mau checkout yang ini"

JANGAN pilih ORDER jika:
- user baru bertanya "bagus nggak?"
- user belum menyebut produk spesifik
- user hanya menyebut budget atau kebutuhan

────────────────────────

3️⃣ CHAT  
Gunakan CHAT jika user:
- hanya ngobrol
- meminta saran umum TANPA fokus mencari produk
- bertanya edukasi / opini / tips
- bertanya di luar konteks belanja

Contoh CHAT:
- "Menurut kamu warna apa yang cocok buat kulit sawo matang?"
- "Apa bedanya katun dan linen?"
- "Baju syar'i itu seperti apa?"
- "Cuaca panas enaknya pakai apa?"

────────────────────────
ATURAN FINAL (WAJIB)
────────────────────────
- PILIH SATU intent SAJA
- JANGAN menjelaskan alasan
- JANGAN menambah teks lain
- JANGAN pakai huruf kecil

Balas dengan SALAH SATU dari:
SEARCH
ORDER
CHAT

────────────────────────
PESAN USER:
"{user_message}"
"""
    return Settings.llm.complete(prompt).text.strip().upper()



# ======================================================
# 8. LLM — MODE DETECTOR (AFTER SEARCH)
# ======================================================
def llm_detect_mode(user_message: str) -> str:
    prompt = f"""
Tentukan MODE respon AI yang PALING TEPAT untuk user.

Kamu HARUS memilih SATU dari:
EMPLOYEE
AFFILIATE
ADVISOR

────────────────────────
DEFINISI MODE (WAJIB DIIKUTI)
────────────────────────

EMPLOYEE:
- User sedang mencari atau ingin membeli PRODUK
- Produk tersebut secara wajar adalah PRODUK INTERNAL Zaneva Store
- Fokus ke rekomendasi produk yang ADA di toko

Contoh:
- "Ada baju renang?"
- "Rekomendasi outfit padel"
- "Baju syar'i buat olahraga ada?"
- "Yang cocok buat kondangan apa?"

────────────────────────

AFFILIATE:
- User mencari PRODUK
- Tapi kemungkinan produk TIDAK tersedia di Zaneva
- Perlu alternatif dari luar (affiliate)

Contoh:
- Produk sangat spesifik tapi tidak ada di Zaneva
- User mencari kategori yang jelas tidak dijual Zaneva

────────────────────────

ADVISOR:
- User hanya ingin saran, ide, atau edukasi
- Tidak fokus ke beli produk
- Tidak perlu rekomendasi item konkret

Contoh:
- "Outfit padel yang nyaman itu seperti apa?"
- "Tips berpakaian saat cuaca panas"
- "Baju syar'i yang nyaman kriterianya apa?"

────────────────────────
ATURAN FINAL (WAJIB)
────────────────────────
- PILIH SATU MODE SAJA
- JANGAN memberi penjelasan
- JANGAN menambah teks lain
- GUNAKAN HURUF BESAR

Balas dengan SALAH SATU dari:
EMPLOYEE
AFFILIATE
ADVISOR

────────────────────────
PESAN USER:
"{user_message}"
"""
    return Settings.llm.complete(prompt).text.strip().upper()


# ======================================================
# 9. DATA RETRIEVAL (PURE PYTHON)
# ======================================================
def retrieve_by_tier(query: str, tier: str, top_k: int = 5):
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)
    return [
        n for n in nodes
        if n.metadata.get("tier") == tier
    ]
    
def retrieve_neutral(query: str, top_k: int = 5):
    retriever = index.as_retriever(similarity_top_k=top_k)
    return retriever.retrieve(query)

# ======================================================
# 10. ORDER EXTRACTION
# ======================================================
def ekstrak_order(pesan: str, history: str):
    prompt = f"""
Ekstrak data order dari chat berikut.

Format JSON WAJIB:
{{"status":"","nama":"","alamat":"","item":"","qty":1,"unit_price":0}}

CHAT:
{history}

PESAN TERAKHIR:
{pesan}
"""
    try:
        import json
        data = json.loads(Settings.llm.complete(prompt).text)
        data["qty"] = int(data.get("qty", 1))
        data["unit_price"] = int(
            re.sub(r"[^\d]", "", str(data.get("unit_price", 0))) or 0
        )
        return data
    except:
        return {"status": "INCOMPLETE", "qty": 1, "unit_price": 0}

def ambil_harga(item: str) -> int:
    nodes = index.as_retriever(similarity_top_k=1).retrieve(item)
    if not nodes:
        return 0
    match = re.search(r"(\d{3,})", nodes[0].text)
    return int(match.group()) if match else 0

def is_order_commitment(text: str) -> bool:
    text = text.lower()

    commit_keywords = [
        "saya pesan",
        "jadi pesan",
        "jadi beli",
        "checkout",
        "order sekarang",
        "ambil yang ini",
        "saya mau pesan",
        "saya mau beli",
        "saya mau order",
    ]


    detail_keywords = [
        "size",
        "ukuran",
        "pcs",
        "buah",
        "qty"
    ]

    return any(k in text for k in commit_keywords) or any(k in text for k in detail_keywords)

# ======================================================
# 11. MAIN ENDPOINT
# ======================================================
@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
async def chat_endpoint(req: QueryRequest):
    global CHAT_HISTORY, ORDER_STATE

    CHAT_HISTORY.append(f"User: {req.pertanyaan}")
    CHAT_HISTORY = CHAT_HISTORY[-15:]
    history_text = "\n".join(CHAT_HISTORY)
    
    # 🔒 POST-ORDER GUARD (SETELAH PESANAN SELESAI)
    if ORDER_STATE == "WAITING_PAYMENT":

        pesan_lower = req.pertanyaan.lower()

        # ✅ USER KONFIRMASI PEMBAYARAN
        if any(k in pesan_lower for k in [
            "sudah transfer",
            "sudah bayar",
            "udah transfer",
            "udah bayar",
            "bukti transfer",
            "saya sudah transfer"
        ]):
            ORDER_STATE = "IDLE"

            jawaban = (
                "Terima kasih Kak 🙏\n\n"
                "Pembayaran sudah kami terima dan terkonfirmasi.\n"
                "Pesanan Kakak akan segera kami proses pengirimannya 📦\n\n"
                "Jika ada yang ingin ditanyakan lagi, silakan ya Kak 😊"
            )

            CHAT_HISTORY.append(f"Bot: {jawaban}")
            return ChatResponse(jawaban=jawaban)

        # ❗ BELUM ADA KONFIRMASI PEMBAYARAN
        jawaban = (
            "Siap Kak 🙏\n"
            "Kami masih menunggu pembayaran ya.\n\n"
            "💳 Silakan lakukan transfer sesuai total pesanan.\n"
            "Jika sudah, kirimkan bukti transfer di chat ini 😊"
        )

        CHAT_HISTORY.append(f"Bot: {jawaban}")
        return ChatResponse(jawaban=jawaban)



    # 🔐 INTENT LOCK (WAJIB)
    if ORDER_STATE in [
        "AWAITING_CONFIRMATION",
        "COLLECTING_DATA",
        "WAITING_PAYMENT"
    ]:
        intent = "ORDER"
    else:
        intent = llm_detect_intent(req.pertanyaan)

    log_ai_flow(intent, ORDER_STATE, req.pertanyaan)

    
    jawaban = ""

    # ================= ORDER =================
    if intent == "ORDER":
        data = ekstrak_order(req.pertanyaan, history_text)

        item_name = (data.get("item") or "").strip()
        qty = data.get("qty")
        size = data.get("size")
        nama = data.get("nama")
        alamat = data.get("alamat")

        # ==================================================
        # 1️⃣ ITEM BELUM JELAS → STOP
        # ==================================================
        if not item_name or len(item_name) < 3:
            ORDER_STATE = "COLLECTING_DATA"
            jawaban = (
                "Siap Kak 😊\n"
                "Produk yang mana ya?\n"
                "Tolong sebutkan **nama produk** agar tidak salah 🙏"
            )
            CHAT_HISTORY.append(f"Bot: {jawaban}")
            return ChatResponse(jawaban=jawaban)

        # ==================================================
        # 2️⃣ CEK APAKAH PRODUK INTERNAL / AFFILIATE
        # ==================================================
        nodes = index.as_retriever(similarity_top_k=1).retrieve(item_name)

        if not nodes:
            order_mode = "AFFILIATE"
        else:
            tier = nodes[0].metadata.get("tier")
            order_mode = "EMPLOYEE" if tier == "premium" else "AFFILIATE"

        # ==================================================
        # 3️⃣ AFFILIATE → STOP ORDER, KASIH LINK
        # ==================================================
        if order_mode == "AFFILIATE":
            link = nodes[0].metadata.get("affiliate_link") if nodes else None

            jawaban = (
                f"Siap Kak 😊\n\n"
                f"Produk **{item_name}** tersedia melalui partner kami.\n\n"
                f"🔗 {link if link else 'Maaf, link partner belum tersedia saat ini.'}\n\n"
                f"Aku bisa bantu:\n"
                f"- carikan alternatif sejenis\n"
                f"- bandingkan beberapa opsi\n"
                f"- bantu pilih ukuran / fit yang aman 🙌"
            )

            CHAT_HISTORY.append(f"Bot: {jawaban}")
            return ChatResponse(jawaban=jawaban)

        # ==================================================
        # 4️⃣ BELUM ADA KOMITMEN ORDER → MINTA KONFIRMASI
        # ==================================================
        if not is_order_commitment(req.pertanyaan):
            ORDER_STATE = "AWAITING_CONFIRMATION"
            jawaban = (
                "Siap Kak 😊\n\n"
                f"Kakak ingin memesan **{item_name}** ya?\n\n"
                "Silakan lanjut dengan salah satu cara berikut:\n"
                "1️⃣ Ketik: **Saya pesan …** + jumlah / size\n"
                "2️⃣ Atau langsung isi data pemesanan 🙌"
            )
            CHAT_HISTORY.append(f"Bot: {jawaban}")
            return ChatResponse(jawaban=jawaban)

        # ==================================================
        # 5️⃣ DATA BELUM LENGKAP → MINTA NAMA & ALAMAT
        # ==================================================
        if not (qty or size) or not nama or not alamat:
            ORDER_STATE = "COLLECTING_DATA"

            jawaban = f"""
                Siap Kak 😊  
                Sebelum lanjut ke pembayaran, mohon lengkapi data berikut ya:

                📦 DATA PEMESANAN
                Nama Produk: {item_name}\n
                Jumlah: {qty or "-"}\n
                Size: {size or "-"}\n\n

                👤 DATA PENERIMA\n
                Nama Lengkap:\n
                Alamat Lengkap:\n\n

                Silakan copas format di atas, lalu isi datanya 🙏
                """
            CHAT_HISTORY.append(f"Bot: {jawaban.strip()}")
            return ChatResponse(jawaban=jawaban.strip())

        # ==================================================
        # 6️⃣ SEMUA DATA LENGKAP → MASUK PAYMENT
        # ==================================================
        if data.get("unit_price") == 0:
            data["unit_price"] = ambil_harga(item_name)

        total = (qty or 1) * data["unit_price"]
        ORDER_STATE = "WAITING_PAYMENT"

        simpan_pesanan(
            nama,
            f"{item_name} (Qty {qty or 1})",
            alamat,
            f"Rp {total:,}".replace(",", ".")
        )

        jawaban = (
            f"Terima kasih Kak {nama} 🙏\n\n"
            f"Pesanan Kakak sudah kami terima.\n\n"
            f"🧾 Ringkasan Pesanan:\n"
            f"- Item  : {item_name}\n"
            f"- Jumlah: {qty or 1}\n"
            f"- Total : Rp {total:,}".replace(",", ".") + "\n\n"
            f"💳 Silakan lakukan transfer sesuai total di atas.\n"
            f"Pesanan akan dikirim setelah pembayaran terkonfirmasi 📦"
        )

        CHAT_HISTORY.append(f"Bot: {jawaban}")
        return ChatResponse(jawaban=jawaban)


    # ================= SEARCH =================
    elif intent == "SEARCH":
        nodes = retrieve_neutral(req.pertanyaan)

        ctx = "\n".join(n.text for n in nodes)

        jawaban = Settings.llm.complete(
            SEARCH_PROMPT.format(
                question=req.pertanyaan,
                ctx=ctx
            )
        ).text


    # ================= CHAT =================
    elif intent == "CHAT":
        jawaban = Settings.llm.complete(ADVISOR_PROMPT.format(
            question=req.pertanyaan
        )).text

    CHAT_HISTORY.append(f"Bot: {jawaban}")
    return ChatResponse(jawaban=jawaban)


@app.get("/")
def root():
    return {"status": "Fasha AI is Online 🚀"}
