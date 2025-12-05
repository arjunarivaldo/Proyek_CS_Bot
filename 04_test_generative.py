# FILE: 04_test_generative.py
# TUGAS: Menguji 'Pustakawan' (Retriever) + 'Juru Bicara' (LLM)

import chromadb
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama # <-- IMPORT BARU
import time

print("--- Memulai Uji Coba 'Generatif' ---")
start_time = time.time()

# --- 1. Tentukan 'Ilmu' (Pustakawan) ---
print("Memuat 'Ilmu' (Embedding Model)...")
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

# --- 2. Tentukan 'Juru Bicara' (LLM) ---
print("Menghubungkan ke 'Juru Bicara' (Ollama - Llama 3)...")
# Pastikan aplikasi Ollama berjalan di komputer
try:
    # Set timeout 120 detik (2 menit) untuk respons LLM
    Settings.llm = Ollama(
        model="llama3",
        request_timeout=120.0
    )
except Exception as e:
    print(f"GAGAL terhubung ke Ollama: {e}")
    exit()
    
# --- 3. Hubungkan ke 'Lemari Arsip' ---
print("Menghubungkan ke 'Lemari Arsip' (ChromaDB)...")
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_collection("klien_dokter_qna")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# --- 4. Muat Indeks ---
print("Memuat Indeks dari storage...")
index_dari_storage = VectorStoreIndex.from_vector_store(vector_store)

# --- 5. BUAT "QUERY ENGINE" (Tim Pustakawan + Juru Bicara) ---
# Inilah 'tim' lengkap yang menggabungkan Retrieval & Generation
# Kita tidak lagi pakai 'as_retriever', kita pakai 'as_query_engine'
print("Membuat 'Query Engine' (Tim Pustakawan + Juru Bicara)...")

# # Ini adalah 'perintah' atau 'aturan' untuk si "Juru Bicara"
SYSTEM_PROMPT_STR = ( # <-- Saya ganti nama ke _STR agar lebih jelas
    "Anda adalah asisten AI yang menjawab pertanyaan medis.\n"
    "Gunakan HANYA informasi dari 'Konteks' yang diberikan di bawah ini.\n"
    "JANGAN PERNAH menambahkan informasi apa pun dari pengetahuan Anda sendiri.\n"
    "JANGAN mengarang jawaban. Jika 'Konteks' tidak relevan atau tidak cukup "
    "untuk menjawab pertanyaan, katakan HANYA: "
    "'Maaf, saya tidak menemukan informasi spesifik tentang itu di database saya.'\n"
    "Selalu jawab dalam bahasa Indonesia.\n\n"
    "--- Konteks yang Diberikan ---\n"
    "{context_str}\n"
    "--- Pertanyaan User ---\n"
    "{query_str}\n"
    "--- Jawaban Anda ---\n"
)

# Kita "cetak" lirik mentah kita ke "buku partitur" (Objek PromptTemplate)
qa_template = PromptTemplate(SYSTEM_PROMPT_STR)

query_engine = index_dari_storage.as_query_engine(
    # 'text_qa_template' adalah cara kita 'menyuntikkan' aturan kita ke LLM
    text_qa_template=qa_template
)

end_time = time.time()
print(f"--- Setup selesai dalam {end_time - start_time:.2f} detik. ---")
print("=" * 50)
print("SIAP MENERIMA PERTANYAAN! (Mode Generatif)")
print("Ketik 'exit' atau tekan Ctrl+C untuk keluar.")
print("=" * 50)

# --- 6. BAGIAN INTERAKTIF ---
while True:
    try:
        pertanyaan = input("\nMasukkan pertanyaan Anda: ")
        if pertanyaan.lower() == "exit":
            print("Terima kasih. Sampai jumpa!")
            break
        if not pertanyaan:
            continue
        
        query_start = time.time()
        
        # --- PERUBAHAN UTAMA: PANGGIL 'QUERY' ---
        # 'query' akan otomatis melakukan RAG (Retrieve + Generate)
        response = query_engine.query(pertanyaan)
        
        query_end = time.time()
        
        print(f"\n--- JAWABAN BOT (dihasilkan dalam {query_end - query_start:.2f} detik) ---")
        print(response)
        print("-" * 50)
        
    except KeyboardInterrupt:
        print("\nTerima kasih. Sampai jumpa!")
        break
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")