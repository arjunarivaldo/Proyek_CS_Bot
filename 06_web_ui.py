# FILE: 06_web_ui.py
# TUGAS: Website Chatbot Fashion Store (Frontend)

import streamlit as st
import requests

# --- KONFIGURASI ---
# Ganti ke URL Render Anda jika sudah deploy backend baru
API_URL = "https://api-bot-arjun.onrender.com" 
# API_URL = "http://127.0.0.1:8000" # Kita pakai Local dulu untuk tes sekarang

# API Key Klien (Salah satu dari MY_VALID_API_KEYS)
API_KEY = "kunci_rahasia_bos"

# --- 1. KONFIGURASI HALAMAN (TAB BROWSER) ---
st.set_page_config(
    page_title="Arjun Fashion Store",
    page_icon="🛍️",
    layout="centered"
)

# --- 2. SIDEBAR (INFO TOKO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3159/3159066.png", width=100) # Logo Dummy
    st.title("Arjun Fashion")
    st.markdown("""
    **Jam Operasional:**
    Senin - Sabtu: 09.00 - 20.00 WIB
    Minggu: Libur
    
    **Alamat:**
    Jl. Buah Batu No. 45, Bandung.
    
    **Kontak Admin:**
    WA: 0812-3456-7890
    """)
    st.divider()
    st.caption("© 2025 Arjun Fashion AI System")

# --- 3. JUDUL UTAMA ---
st.title("👋 Halo! Selamat Datang.")
st.subheader("Asisten Virtual Arjun Fashion Store 👕")
st.info("Tanyakan stok, cek harga, atau lacak pesanan Anda di sini. Saya siap membantu 24/7!")

# --- 4. INISIALISASI MEMORI CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Pesan pembuka otomatis dari Bot
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Halo Kak! 👋 Ada yang bisa saya bantu?"
    })

# --- 5. TAMPILKAN RIWAYAT CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. LOGIKA CHAT ---
if prompt := st.chat_input("Ketik pesan... (Misal: Kemeja merah ukuran L ada?)"):
    
    # Tampilkan pesan user
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Pikirkan jawaban (Loading state)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Typing...") # Efek mengetik
        
        try:
            # Kirim ke API (Render/Local)
            payload = {"pertanyaan": prompt}
            headers = {"X-API-Key": API_KEY}
            
            # Timeout kita perpanjang jadi 120 detik (aman buat server tidur)
            response = requests.post(
                f"{API_URL}/chat", 
                json=payload, 
                headers=headers,
                timeout=120 
            )
            
            if response.status_code == 200:
                ai_answer = response.json().get("jawaban", "Maaf, format error.")
            else:
                ai_answer = f"⚠️ Error Server: {response.status_code}. Cek apakah server nyala?"
                
        except Exception as e:
            ai_answer = f"🔌 Gagal terhubung ke server. Pastikan server (Uvicorn/Render) menyala. Error: {e}"

        # Tampilkan jawaban final
        message_placeholder.markdown(ai_answer)
        st.session_state.messages.append({"role": "assistant", "content": ai_answer})