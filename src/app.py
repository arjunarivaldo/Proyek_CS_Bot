import streamlit as st
import os
from datetime import datetime

LOGO_PATH = "assets/logo.png"
HEADER_PATH = "assets/header.jpg"
AVATAR_PATH = "assets/avatar.jpg"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from setup_database import build_index
import shutil

# Reset dan rebuild ChromaDB setiap kali app dijalankan
if "db_initialized" not in st.session_state:
    # Hapus database lama
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
    
    # Rebuild database
    build_index()
    
    st.session_state.db_initialized = True

st.set_page_config(
    page_title="Fasha - Personal Fashion Advisor",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "👗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --primary-brown: #8B5A2B;
        --dark-brown: #5D3A1A;
        --light-brown: #A67C52;
        --cream: #FFF8F0;
        --beige: #F5E6D3;
        --beige-dark: #E8D5C4;
        --white: #FFFFFF;
        --text-dark: #3D2314;
        --text-light: #6B5344;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: var(--white);
    }
    
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        max-width: 900px;
    }
    
    [data-testid="stChatMessageContent"] {
        background: var(--white) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-dark) !important;
        box-shadow: 0 2px 8px rgba(93, 58, 26, 0.06);
    }
    
    [data-testid="stChatMessageContent"] p {
        color: var(--text-dark) !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stChatMessage[data-testid="user-message"] [data-testid="stChatMessageContent"] {
        background: var(--primary-brown) !important;
        color: var(--white) !important;
    }
    
    .stChatMessage[data-testid="user-message"] [data-testid="stChatMessageContent"] p {
        color: var(--white) !important;
    }
    
    /* INPUT CHAT - BACKGROUND PUTIH */
    [data-testid="stChatInput"] {
        max-width: 900px !important;
        margin: 0 auto !important;
    }
    
    [data-testid="stChatInput"] > div {
        background: #FFFFFF !important;
        border: 2px solid var(--beige-dark) !important;
        border-radius: 25px !important;
    }
    
    [data-testid="stChatInput"] > div > div {
        background: #FFFFFF !important;
    }
    
    [data-testid="stChatInput"] input,
    [data-testid="stChatInput"] textarea {
        font-family: 'Inter', sans-serif !important;
        background: #FFFFFF !important;
        color: var(--text-dark) !important;
    }
    
    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--primary-brown) !important;
        box-shadow: 0 0 0 2px rgba(139, 90, 43, 0.2) !important;
    }
    
    [data-testid="stBottomBlockContainer"] {
        background: var(--white) !important;
        max-width: 900px !important;
        margin: 0 auto !important;
        padding: 0.5rem 2rem !important;
    }
    
    .feature-card {
        background: var(--beige);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid var(--beige-dark);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        box-shadow: 0 5px 15px rgba(93, 58, 26, 0.1);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }
    
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-dark);
        font-size: 0.8rem;
    }
    
    .info-card {
        background: var(--beige);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid var(--beige-dark);
        margin-bottom: 0.8rem;
    }
    
    .info-card h4 {
        font-family: 'Playfair Display', serif;
        color: var(--text-dark);
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .info-card p {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: var(--text-light);
        line-height: 1.5;
        margin: 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-brown) 0%, var(--dark-brown) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.4rem 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(93, 58, 26, 0.3) !important;
    }
    
    /* TOMBOL LIHAT - FONT PUTIH */
    .stLinkButton > a {
        background: linear-gradient(135deg, var(--primary-brown) 0%, var(--dark-brown) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 15px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.3rem 0.8rem !important;
        font-size: 0.8rem !important;
        text-decoration: none !important;
    }
    
    .stLinkButton > a:hover {
        color: #FFFFFF !important;
        text-decoration: none !important;
    }
    
    .stLinkButton > a span {
        color: #FFFFFF !important;
    }
    
    hr {
        border: none;
        height: 1px;
        background: var(--beige-dark);
        margin: 0.8rem 0;
    }
    
    .stImage {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .powered-by {
        text-align: center;
        padding: 0.8rem;
        color: var(--text-light);
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--beige);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--light-brown);
        border-radius: 3px;
    }
    
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 35px !important;
        height: 35px !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
if os.path.exists(HEADER_PATH):
    st.image(HEADER_PATH, use_container_width=True)
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8B5A2B 0%, #5D3A1A 100%); 
                border-radius: 15px; padding: 2rem; text-align: center; margin-bottom: 1rem;">
        <h1 style="font-family: 'Playfair Display', serif; font-size: 2.5rem; color: #FFF8F0; margin: 0;">FASHA</h1>
        <p style="font-family: Georgia, serif; font-style: italic; font-size: 1rem; color: #F5E6D3;">Be Stylish, Be Outstanding</p>
    </div>
    """, unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card"><div class="feature-icon">👗</div><div class="feature-title">Outfit Ideas</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card"><div class="feature-icon">🎨</div><div class="feature-title">Color Match</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card"><div class="feature-icon">✨</div><div class="feature-title">Style Tips</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card"><div class="feature-icon">🛒</div><div class="feature-title">Shop Now</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout
chat_col, info_col = st.columns([3, 1])

# Init
if "chatbot" not in st.session_state:
    st.session_state.chatbot = FashionChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": st.session_state.chatbot.get_greeting(),
        "products": []
    }]

if "user_id" not in st.session_state:
    st.session_state.user_id = f"web_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Chat column
with chat_col:
    for message in st.session_state.messages:
        avatar = AVATAR_PATH if message["role"] == "assistant" and os.path.exists(AVATAR_PATH) else ("👗" if message["role"] == "assistant" else "👤")
        
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            
            if message.get("products"):
                st.markdown("---")
                st.markdown("**Rekomendasi Produk:**")
                
                for product in message["products"]:
                    col_img, col_info = st.columns([1, 2])
                    
                    with col_img:
                        try:
                            st.image(product["image_url"], use_container_width=True)
                        except:
                            st.image("https://via.placeholder.com/150?text=No+Image", use_container_width=True)
                    
                    with col_info:
                        tier_badge = "⭐ PREMIUM" if product.get('tier') == 'premium' else ""
                        st.markdown(f"**{product['nama_produk']}** {tier_badge}")
                        st.markdown(f"💰 Rp {product['harga']:,}")
                        st.markdown(f"🎨 {product['warna_tersedia']}")
                        st.link_button("🛒 Lihat", product["link"])
                    
                    st.markdown("---")

# Info column (TANPA info premium)
with info_col:
    st.markdown("""
    <div class="info-card">
        <h4>💡 Tips</h4>
        <p>Sebutkan acara, budget, dan warna untuk rekomendasi yang pas!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>📦 Kategori</h4>
        <p>👔 Kemeja & Kaos<br>👖 Celana<br>👗 Dress & Rok<br>🧥 Jaket & Hoodie<br>🎾 Sport Outfit</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload bukti transfer jika status waiting
    state = st.session_state.chatbot._get_state(st.session_state.user_id)
    if state.get("order_state") == "waiting_transfer":
        st.markdown("---")
        st.markdown("**📤 Upload Bukti Transfer**")
        uploaded = st.file_uploader("Pilih foto", type=['png', 'jpg', 'jpeg'], key="transfer_upload")
        
        if uploaded:
            path = os.path.join(UPLOAD_FOLDER, f"{st.session_state.user_id}_{uploaded.name}")
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())
            
            result = st.session_state.chatbot.handle_transfer_proof(st.session_state.user_id, path)
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["text"],
                "products": []
            })
            st.rerun()
    
    if st.button("🔄 Chat Baru", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": st.session_state.chatbot.get_greeting(),
            "products": []
        }]
        st.session_state.chatbot.clear_history(st.session_state.user_id)
        st.rerun()

# Input chat
if prompt := st.chat_input("Tanya Fasha tentang fashion..."):
    with chat_col:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
    
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "products": []
    })
    
    with chat_col:
        avatar = AVATAR_PATH if os.path.exists(AVATAR_PATH) else "👗"
        with st.chat_message("assistant", avatar=avatar):
            with st.spinner("Fasha sedang research saran dan rekomendasi terbaik buat kamu..."):
                result = st.session_state.chatbot.get_response(
                    st.session_state.user_id,
                    prompt
                )
            
            st.markdown(result["text"])
            
            if result.get("products"):
                st.markdown("---")
                st.markdown("**Rekomendasi Produk:**")
                
                for product in result["products"]:
                    col_img, col_info = st.columns([1, 2])
                    
                    with col_img:
                        try:
                            st.image(product["image_url"], use_container_width=True)
                        except:
                            st.image("https://via.placeholder.com/150?text=No+Image", use_container_width=True)
                    
                    with col_info:
                        tier_badge = "⭐ PREMIUM" if product.get('tier') == 'premium' else ""
                        st.markdown(f"**{product['nama_produk']}** {tier_badge}")
                        st.markdown(f"💰 Rp {product['harga']:,}")
                        st.markdown(f"🎨 {product['warna_tersedia']}")
                        st.link_button("🛒 Lihat", product["link"])
                    
                    st.markdown("---")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["text"],
        "products": result.get("products", [])
    })
    
    st.rerun()

# FOOTER di bawah input chat
st.markdown("""
<div class="powered-by">
    Made with ❤️ by GEMINI TEAMS | Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)