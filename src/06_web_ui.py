# FILE: 06_web_ui.py
# TUGAS: Website Chatbot Fashion Store (Frontend)
# BRAND AI: Fasha AI
# ROLE:
# - CS utama untuk Zaneva Store (tier: premium)
# - Affiliator cerdas untuk produk non-premium
# - Advisor fashion jika user hanya bertanya

import streamlit as st
import requests

# --- KONFIGURASI ---
# Ganti ke URL Render Anda jika sudah deploy backend baru
# API_URL = "https://final-project-fasha-ai.onrender.com" 
API_URL = "http://127.0.0.1:8000" # Kita pakai Local dulu untuk tes sekarang
API_KEY = "kunci_rahasia_bos"

# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="Fasha AI | Fashion Advisor & Smart CS",
    page_icon="👗",
    layout="centered"
)

# ==============================
# SIDEBAR (BRANDING & INFO)
# ==============================
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/892/892458.png",
        width=100
    )
    st.title("Fasha AI 🤍")
    st.caption("Fashion Advisor & Smart Commerce AI")

    st.markdown("""
**Peran Fasha AI:**
- 🛍️ CS utama produk **Zaneva Store**
- 🤝 Rekomendasi produk mitra (affiliate)
- 🎓 Advisor fashion & style

**Jam Operasional CS:**
Senin – Sabtu  
09.00 – 20.00 WIB

**Catatan:**
Fasha AI akan selalu **memprioritaskan Zaneva Store**.  
Jika produk tidak tersedia, Fasha AI akan membantu mencarikan alternatif terbaik.
""")

    st.divider()
    st.caption("© 2026 Fasha AI System")

# ==============================
# HEADER UTAMA
# ==============================
st.title("👋 Halo, selamat datang!")
st.subheader("Saya **Fasha AI**, asisten fashion kamu 👗")
st.info(
    "Kamu bisa tanya stok Zaneva, minta rekomendasi outfit, "
    "atau sekadar minta saran style. Aku bantu dari niat sampai deal ✨"
)

# ==============================
# INISIALISASI CHAT MEMORY
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Halo Kak! 👋 Aku **Fasha AI**.\n\n"
                "Aku bisa bantu:\n"
                "- Cek & pesan produk **Zaneva Store**\n"
                "- Rekomendasi produk alternatif (affiliate)\n"
                "- Kasih saran outfit & style\n\n"
                "Lagi cari apa hari ini? 😊"
            )
        }
    ]

# ==============================
# TAMPILKAN RIWAYAT CHAT
# ==============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================
# INPUT CHAT USER
# ==============================
if prompt := st.chat_input(
    "Tulis pesan... (contoh: Hoodie buat padel ada?)"
):
    # Tampilkan pesan user
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    # Placeholder jawaban AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Fasha sedang mengetik... 🤍")

        try:
            payload = {"pertanyaan": prompt}
            headers = {"X-API-Key": API_KEY}

            response = requests.post(
                f"{API_URL}/chat",
                json=payload,
                headers=headers,
                timeout=120
            )

            if response.status_code == 200:
                ai_answer = response.json().get(
                    "jawaban",
                    "Maaf Kak, ada sedikit kendala di sistem."
                )
            else:
                ai_answer = (
                    f"⚠️ Server error ({response.status_code}). "
                    "Coba beberapa saat lagi ya Kak."
                )

        except Exception as e:
            ai_answer = (
                "🔌 Fasha AI belum bisa terhubung ke server.\n\n"
                f"Detail error: `{e}`"
            )

        placeholder.markdown(ai_answer)
        st.session_state.messages.append(
            {"role": "assistant", "content": ai_answer}
        )
