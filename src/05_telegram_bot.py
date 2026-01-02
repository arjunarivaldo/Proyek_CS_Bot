# FILE: 05_telegram_bot.py
# TUGAS: Menghubungkan Telegram dengan API AI Render Anda

import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- KONFIGURASI (WAJIB DIISI) ---
# 1. Token dari BotFather (Langkah 1 tadi)
TELEGRAM_TOKEN = "GANTI_DENGAN_TOKEN_BOTFATHER_ANDA"

# 2. URL API Render Anda (Cek di Dashboard Render)
# Pastikan tidak ada garis miring '/' di paling belakang
API_URL = "https://api-bot-arjun.onrender.com" 

# 3. API Key Klien (Salah satu dari MY_VALID_API_KEYS yang Anda set di Render)
# Ingat, Telegram ini bertindak sebagai "Klien" bagi server Anda.
API_KEY_KLIEN = "kunci_rahasia_bos" 

# --- SETUP LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pesan sambutan saat user mengetik /start"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Halo! Saya adalah Asisten Medis AI.\nSilakan tanya keluhan Anda, saya akan mencoba menjawab berdasarkan data dokter."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fungsi ini dipanggil setiap kali ada pesan masuk"""
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    print(f"[TELEGRAM] Pesan dari User: {user_text}")

    # Beri tahu user kalau bot sedang mengetik (biar gak dikira mati)
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # --- MENGHUBUNGI OTAK (RENDER API) ---
    try:
        # Kirim surat ke API Server
        response = requests.post(
            f"{API_URL}/chat",
            json={"pertanyaan": user_text},
            headers={"X-API-Key": API_KEY_KLIEN},
            timeout=30 # Tunggu maksimal 30 detik
        )
        
        # Cek balasan
        if response.status_code == 200:
            ai_reply = response.json().get("jawaban", "Maaf, format error.")
        else:
            ai_reply = f"Error dari Server: {response.status_code} - {response.text}"

    except Exception as e:
        ai_reply = f"Gagal menghubungi server: {e}"
        print(f"[ERROR] {e}")

    # --- KIRIM JAWABAN KE TELEGRAM ---
    await context.bot.send_message(
        chat_id=chat_id,
        text=ai_reply
    )

if __name__ == '__main__':
    print("--- BOT TELEGRAM BERJALAN ---")
    print("Tekan Ctrl+C untuk berhenti.")
    
    # Membangun Aplikasi Bot
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Menambahkan Handler
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    # Jalankan Bot (Polling Mode)
    application.run_polling()