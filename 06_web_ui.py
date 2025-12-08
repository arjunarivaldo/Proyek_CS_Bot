# FILE: 06_web_ui.py
# TUGAS: Membuat Website Chatbot Sederhana (Frontend)

import streamlit as st
import requests

# --- KONFIGURASI ---
# URL API Render Anda (Tanpa garis miring di belakang)
API_URL = "https://api-bot-arjun.onrender.com"
# API Key Klien (Salah satu dari MY_VALID_API_KEYS)
API_KEY = "kunci_rahasia_bos"

# --- TAMPILAN HALAMAN ---
st.set_page_config(page_title="Dokter AI Assistant", page_icon="🩺")

st.title("🩺 Dokter AI Arjuna Rivaldo - Virtual Assistant")
st.write("Tanyakan keluhan medis Anda, AI akan menjawab berdasarkan database dokter.")

# --- INISIALISASI SESSION STATE (MEMORI CHAT DI BROWSER) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TAMPILKAN RIWAYAT CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT USER ---
if prompt := st.chat_input("Ketik keluhan Anda (misal: dada sakit saat batuk)..."):
    # 1. Tampilkan pesan user di layar
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Kirim ke API Render (Loading...)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Sedang berpikir...")
        
        try:
            # Panggil API
            payload = {"pertanyaan": prompt}
            headers = {"X-API-Key": API_KEY}
            
            response = requests.post(
                f"{API_URL}/chat", 
                json=payload, 
                headers=headers,
                timeout=300
            )
            
            if response.status_code == 200:
                ai_answer = response.json().get("jawaban", "Error: Format jawaban salah.")
            else:
                ai_answer = f"Error Server: {response.status_code}"
                
        except Exception as e:
            ai_answer = f"Gagal terhubung: {e}"

        # 3. Tampilkan jawaban AI
        message_placeholder.markdown(ai_answer)
        st.session_state.messages.append({"role": "assistant", "content": ai_answer})