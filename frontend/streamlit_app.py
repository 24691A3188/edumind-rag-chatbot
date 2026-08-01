# -*- coding: utf-8 -*-
"""
EduMind AI — Premium Glassmorphic AI SaaS Frontend
Compatible with Streamlit 1.30+ and FastAPI Backend (Phases 1-5)
Inspired by ChatGPT, Perplexity, and Notion AI.
"""
import streamlit as st
import requests
import uuid
import time
import os
import pandas as pd

# ----------------------------------------------------------------------
# 1. API CONFIGURATION & PAGE CONFIG
# ----------------------------------------------------------------------
def discover_backend_url() -> str:
    env_url = os.getenv("BACKEND_URL", "").strip()
    if not env_url:
        try:
            if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
                env_url = str(st.secrets["BACKEND_URL"]).strip()
        except Exception:
            pass

    if env_url:
        env_url = env_url.rstrip("/")
        # If it's a remote production URL (e.g., Render), return directly
        if not ("127.0.0.1" in env_url or "localhost" in env_url):
            return env_url

    # Fallback local discovery
    default_url = env_url if env_url else "http://127.0.0.1:8001"
    candidates = [default_url, "http://127.0.0.1:8001", "http://127.0.0.1:8000", "http://127.0.0.1:8002"]
    seen = set()
    for url in candidates:
        if url and url not in seen:
            seen.add(url)
            try:
                r = requests.get(f"{url}/", timeout=1.0)
                if r.status_code == 200:
                    return url
            except Exception:
                continue
    return default_url

BACKEND_URL = discover_backend_url()

st.set_page_config(
    page_title="EduMind AI — Premium RAG Knowledge Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------------
# 2. PREMIUM GLASSMORPHISM DESIGN SYSTEM & CUSTOM CSS
# ----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
  --bg-deep:        #030712;
  --bg-surface:     #090d16;
  --bg-card:        rgba(15, 23, 42, 0.65);
  --bg-card-hover:  rgba(30, 41, 59, 0.75);
  --glass-border:   rgba(255, 255, 255, 0.08);
  --glass-glow:     rgba(139, 92, 246, 0.15);
  
  --accent-purple:  #8b5cf6;
  --accent-indigo:  #6366f1;
  --accent-cyan:    #06b6d4;
  --accent-pink:    #ec4899;
  --accent-emerald: #10b981;
  
  --text-primary:   #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted:     #64748b;
  
  --radius-sm:      8px;
  --radius-md:      14px;
  --radius-lg:      20px;
  --radius-xl:      24px;
}

/* Global Reset & Typography */
html, body, [class*="css"] {
    font-family: 'Inter', 'Poppins', 'Outfit', system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.22) 0px, transparent 45%),
        radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.20) 0px, transparent 45%),
        radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.10) 0px, transparent 40%) !important;
    background-attachment: fixed !important;
}

/* Hide Streamlit Default UI Noise & Fix Padding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent !important;}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1320px !important;
}

/* Keyframe Animations */
@keyframes floatAnim {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
    100% { transform: translateY(0px); }
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: rgba(3, 7, 18, 0.88) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary);
}

/* Sidebar Radio Buttons Styling */
div[data-testid="stSidebar"] .stRadio > label {
    display: none !important;
}

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 8px !important;
}

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
    background: rgba(15, 23, 42, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: var(--radius-md) !important;
    padding: 12px 16px !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
    background: rgba(30, 41, 59, 0.7) !important;
    color: #ffffff !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
    transform: translateX(4px);
}

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%) !important;
    border: 1px solid rgba(139, 92, 246, 0.5) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2) !important;
}

/* Glass Containers & Headers */
.glass-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.80) 0%, rgba(30, 41, 59, 0.60) 100%) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: var(--radius-xl) !important;
    padding: 28px 36px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

.glass-card {
    background: var(--bg-card) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 22px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.glass-card:hover {
    border-color: rgba(139, 92, 246, 0.45) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4), 0 0 25px rgba(139, 92, 246, 0.25) !important;
}

.metric-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.65)) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px 24px !important;
    text-align: center !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}

.metric-card:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(6, 182, 212, 0.4) !important;
    box-shadow: 0 12px 35px rgba(6, 182, 212, 0.2) !important;
}

/* Gradient Typography */
.gradient-text {
    background: linear-gradient(135deg, #a78bfa 0%, #38bdf8 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

.gradient-title {
    background: linear-gradient(135deg, #ffffff 30%, #a78bfa 70%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* Badges */
.badge-purple {
    background: rgba(139, 92, 246, 0.18) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    color: #c084fc !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    display: inline-block !important;
}

.badge-cyan {
    background: rgba(6, 182, 212, 0.18) !important;
    border: 1px solid rgba(6, 182, 212, 0.4) !important;
    color: #38bdf8 !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    display: inline-block !important;
}

.badge-emerald {
    background: rgba(16, 185, 129, 0.18) !important;
    border: 1px solid rgba(16, 185, 129, 0.4) !important;
    color: #34d399 !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    display: inline-block !important;
}

/* Citation Box */
.citation-box {
    background: rgba(15, 23, 42, 0.85) !important;
    border-left: 4px solid #38bdf8 !important;
    border-radius: 4px 12px 12px 4px !important;
    padding: 14px 18px !important;
    margin-top: 12px !important;
    font-size: 0.88rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
}

/* Streamlit Button Restyling */
.stButton>button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35) !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.55) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
}

/* Streamlit Input & Text Area Restyling */
div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
    background-color: rgba(15, 23, 42, 0.75) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px !important;
    color: #f8fafc !important;
}

div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.3) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px !important;
    background: rgba(15, 23, 42, 0.6) !important;
    padding: 6px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.stTabs [data-baseweb="tab"] {
    height: 44px !important;
    border-radius: 12px !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0 20px !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35) !important;
}

/* Typing Indicator Animation */
.typing-loader {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    background: rgba(15, 23, 42, 0.8);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
}
.typing-dot {
    width: 7px;
    height: 7px;
    background: #38bdf8;
    border-radius: 50%;
    animation: typingPulse 1.4s infinite ease-in-out both;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0s; }

@keyframes typingPulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

/* File Uploader Drag and Drop Customization */
div[data-testid="stFileUploader"] section {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 2px dashed rgba(139, 92, 246, 0.4) !important;
    border-radius: 18px !important;
    padding: 24px !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFileUploader"] section:hover {
    border-color: rgba(6, 182, 212, 0.7) !important;
    background: rgba(30, 41, 59, 0.6) !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: rgba(3, 7, 18, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.35); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.65); }

/* Mobile Responsive Tweaks */
@media (max-width: 768px) {
    .glass-header { padding: 18px 20px !important; }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# 3. SESSION STATE INITIALIZATION
# ----------------------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ----------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & BRANDING
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 16px 0 24px 0;">
        <div style="display: inline-block; background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 12px; border-radius: 18px; box-shadow: 0 0 25px rgba(139, 92, 246, 0.5); margin-bottom: 12px; animation: floatAnim 4s ease-in-out infinite;">
            <span style="font-size: 2.2rem; display: block; line-height: 1;">⚡</span>
        </div>
        <h2 class="gradient-text" style="margin:0; font-size: 1.75rem; font-weight:800; letter-spacing: -0.5px;">EduMind AI</h2>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px; font-weight: 500;">Contextual RAG SaaS Engine</p>
        <span class="badge-purple" style="margin-top: 6px;">v1.0 • Enterprise SaaS Edition</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    navigation = st.sidebar.radio(
        "Navigation",
        ["💬 Chat Assistant", "📚 Knowledge Documents", "⚙️ Admin Control", "🏠 Home & Overview"],
        index=0
    )
    
    st.markdown("---")
    
    # Live System Status Dashboard Widget
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px; margin-bottom: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
            <span style="font-size: 0.85rem; font-weight: 700; color: #f8fafc;">System Operational</span>
            <div style="display:flex; align-items:center; gap:6px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981;"></div>
                <span style="font-size:0.75rem; color:#34d399; font-weight:600;">ACTIVE</span>
            </div>
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; display: flex; flex-direction: column; gap: 6px;">
            <div style="display:flex; justify-content:space-between;"><span>• Vector Index:</span> <strong style="color:#38bdf8;">Pinecone 384d</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>• Memory Engine:</span> <strong style="color:#a78bfa;">Active</strong></div>
            <div style="display:flex; justify-content:space-between;"><span>• LLM Synthesis:</span> <strong style="color:#f472b6;">Online</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Session ID:**")
    st.code(f"{st.session_state.user_id[:18]}...", language="text")
    
    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        try:
            res = requests.delete(f"{BACKEND_URL}/history?user_id={st.session_state.user_id}", timeout=5)
            st.session_state.messages = []
            st.sidebar.success("Clear Chat History complete.")
            time.sleep(0.4)
            st.rerun()
        except Exception:
            st.session_state.messages = []
            st.sidebar.info("Session reset locally.")
            st.rerun()

# ----------------------------------------------------------------------
# 5. PAGE 1: 💬 CHAT ASSISTANT (CHATGPT / PERPLEXITY STYLE)
# ----------------------------------------------------------------------
if navigation == "💬 Chat Assistant":
    st.markdown("""
    <div class="glass-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <h1 style="margin:0; font-weight:800; color:#f8fafc; font-size:2.2rem; letter-spacing:-0.5px;">🧠 AI Contextual Website Chatbot</h1>
                <p style="margin:6px 0 0 0; color:#94a3b8; font-size:1.05rem;">Ask questions grounded strictly in your uploaded course materials, policies, and FAQs.</p>
            </div>
            <div>
                <span class="badge-emerald" style="box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);">🟢 RAG Engine Online</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render Empty State & Suggested Prompts Grid if no messages
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0 16px 0;">
            <h3 style="font-weight: 700; color: #f8fafc; font-size: 1.35rem; margin-bottom: 6px;">💡 Suggested Questions</h3>
            <p style="color: #94a3b8; font-size: 0.92rem;">Select a sample prompt below or ask your own question.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📚 What AI courses are offered?", use_container_width=True, key="btn_suggest_1"):
                st.session_state.pending_prompt = "What AI courses are offered?"
                st.rerun()
        with col2:
            if st.button("💳 What is the tuition fee policy?", use_container_width=True, key="btn_suggest_2"):
                st.session_state.pending_prompt = "What is the tuition fee policy?"
                st.rerun()
        with col3:
            if st.button("🕒 What are submission deadlines?", use_container_width=True, key="btn_suggest_3"):
                st.session_state.pending_prompt = "What are submission deadlines?"
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # Render Conversation Message History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"🔍 View Retrieved Sources ({len(msg['sources'])} chunks)"):
                    for idx, src in enumerate(msg["sources"]):
                        score_val = src.get('score', 0.0)
                        score_pct = int(score_val * 100) if score_val <= 1.0 else 95
                        st.markdown(f"""
                        <div class="citation-box">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <strong style="color:#38bdf8; font-size:0.95rem;">📄 {src.get('file_name', 'Document')}</strong>
                                <span class="badge-purple">Similarity Score: {score_val}</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); height: 5px; border-radius: 10px; margin-bottom: 10px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #6366f1, #38bdf8); width: {min(score_pct, 100)}%; height: 100%;"></div>
                            </div>
                            <div style="color:#cbd5e1; font-style:italic; font-size:0.85rem; line-height: 1.5;">"{src.get('chunk', '')}"</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Prompt Input Handler
    prompt = st.chat_input("Ask any question about your documents...")
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        # User message UI update
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response synthesis via backend RAG API (/chat)
        with st.chat_message("assistant"):
            # Typing Animation Loader Placeholder
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class="typing-loader">
                <span style="font-size:0.85rem; color:#94a3b8; font-weight:500;">Searching vector database & synthesizing answer</span>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            """, unsafe_allow_html=True)

            t0 = time.time()
            try:
                payload = {
                    "user_id": st.session_state.user_id,
                    "question": prompt
                }
                response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=45)
                elapsed = time.time() - t0
                
                typing_placeholder.empty()

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer generated.")
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander(f"🔍 View Retrieved Sources ({len(sources)} chunks)"):
                            for src in sources:
                                score_val = src.get('score', 0.0)
                                score_pct = int(score_val * 100) if score_val <= 1.0 else 95
                                st.markdown(f"""
                                <div class="citation-box">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                        <strong style="color:#38bdf8; font-size:0.95rem;">📄 {src.get('file_name', 'Document')}</strong>
                                        <span class="badge-purple">Similarity Score: {score_val}</span>
                                    </div>
                                    <div style="background: rgba(255,255,255,0.05); height: 5px; border-radius: 10px; margin-bottom: 10px; overflow: hidden;">
                                        <div style="background: linear-gradient(90deg, #6366f1, #38bdf8); width: {min(score_pct, 100)}%; height: 100%;"></div>
                                    </div>
                                    <div style="color:#cbd5e1; font-style:italic; font-size:0.85rem; line-height: 1.5;">"{src.get('chunk', '')}"</div>
                                </div>
                                """, unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Backend API Error ({response.status_code}): {response.text}")
            except Exception as e:
                typing_placeholder.empty()
                st.error(f"Failed to connect to RAG server at {BACKEND_URL}: {str(e)}")

# ----------------------------------------------------------------------
# 6. PAGE 2: 📚 KNOWLEDGE DOCUMENTS MANAGEMENT
# ----------------------------------------------------------------------
elif navigation == "📚 Knowledge Documents":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin:0; color:#f9fafb; font-size: 2.2rem; font-weight:800; letter-spacing:-0.5px;">📚 Active Knowledge Base Documents</h1>
        <p style="margin:6px 0 0 0; color:#94a3b8; font-size:1.05rem;">Browse and manage documents currently indexed in Pinecone vector store and Supabase database.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        res = requests.get(f"{BACKEND_URL}/documents", timeout=10)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            if docs:
                st.markdown(f"##### 📑 Currently Indexed Files (`{len(docs)}`)")
                
                cols = st.columns(2)
                for idx, doc in enumerate(docs):
                    col = cols[idx % 2]
                    with col:
                        doc_id = doc.get("id", "")
                        title = doc.get("title", "Untitled Document")
                        file_name = doc.get("file_name", "unknown")
                        file_type = doc.get("file_type", "txt").upper()
                        chunk_count = doc.get("chunk_count", 0)
                        uploaded_at = str(doc.get("uploaded_at", ""))[:10]

                        with st.container():
                            st.markdown(f"""
                            <div class="glass-card">
                                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                                    <h3 style="margin:0; color:#f8fafc; font-size:1.2rem; font-weight:700;">📄 {title}</h3>
                                    <span class="badge-cyan">{file_type}</span>
                                </div>
                                <div style="font-size:0.88rem; color:#94a3b8; margin-bottom:14px; display:flex; flex-direction:column; gap:6px;">
                                    <div>• <strong style="color:#e2e8f0;">File Name:</strong> {file_name}</div>
                                    <div>• <strong style="color:#e2e8f0;">Chunks Indexed:</strong> <span style="color:#a78bfa; font-weight:600;">{chunk_count}</span></div>
                                    <div>• <strong style="color:#e2e8f0;">Index Date:</strong> {uploaded_at}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"🗑️ Delete Document", key=f"kb_del_{doc_id}_{idx}", use_container_width=True):
                                try:
                                    del_res = requests.delete(f"{BACKEND_URL}/document/{doc_id}", timeout=10)
                                    if del_res.status_code == 200:
                                        st.success(f"Purged document '{title}' and associated vectors.")
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error(f"Deletion failed: {del_res.text}")
                                except Exception as err:
                                    st.error(f"Deletion error: {err}")
            else:
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 40px 20px;">
                    <div style="font-size: 3rem; margin-bottom: 12px;">📂</div>
                    <h3 style="color: #f8fafc; margin-bottom: 6px;">No Knowledge Documents Found</h3>
                    <p style="color: #94a3b8; max-width: 500px; margin: 0 auto 20px auto;">Upload PDF, DOCX, TXT, or FAQ files in the Admin Control panel to power your RAG engine.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"Error fetching documents ({res.status_code}): {res.text}")
    except Exception as e:
        st.error(f"Could not connect to backend server: {str(e)}")

# ----------------------------------------------------------------------
# 7. PAGE 3: ⚙️ ADMIN CONTROL DASHBOARD
# ----------------------------------------------------------------------
elif navigation == "⚙️ Admin Control":
    st.markdown("""
    <div class="glass-header">
        <h1 style="margin:0; color:#f9fafb; font-size: 2.2rem; font-weight:800; letter-spacing:-0.5px;">⚙️ Administrator Knowledge Control Center</h1>
        <p style="margin:6px 0 0 0; color:#94a3b8; font-size:1.05rem;">Manage training data, monitor vector store index metrics, and purge outdated knowledge.</p>
    </div>
    """, unsafe_allow_html=True)

    # Analytics Metrics Dashboard Row
    try:
        stats_res = requests.get(f"{BACKEND_URL}/admin/stats", timeout=10)
        docs_res = requests.get(f"{BACKEND_URL}/documents", timeout=10)
        
        total_vectors = 0
        dimension_val = 384
        metric_val = "COSINE"
        status_val = "HEALTHY"
        doc_count = 0

        if stats_res.status_code == 200:
            stats = stats_res.json()
            total_vectors = stats.get('total_vector_count', 0)
            dimension_val = stats.get('dimension', 384)
            metric_val = str(stats.get('metric', 'cosine')).upper()
            status_val = str(stats.get('status', 'healthy')).upper()
            
        if docs_res.status_code == 200:
            doc_count = len(docs_res.json().get("documents", []))

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Total Vectors</div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #a78bfa; margin-top: 4px;">{total_vectors}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Pinecone Chunks</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Indexed Docs</div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #38bdf8; margin-top: 4px;">{doc_count}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Knowledge Files</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Embedding Dimension</div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #f472b6; margin-top: 4px;">{dimension_val}d</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">MiniLM Model</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Vector Engine</div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #34d399; margin-top: 4px;">{status_val}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Metric: {metric_val}</div>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📤 Upload Training Data", "📋 Manage Documents Table", "📊 Raw Vector Metrics"])

    # Tab 1: Upload & Ingest
    with tab1:
        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h3 style="font-weight:700; color:#f8fafc; margin-bottom:6px;">📤 Upload Training Documents or FAQ Files</h3>
            <p style="color:#94a3b8; font-size:0.92rem; margin:0;">Supported formats: <strong>PDF, DOCX, TXT, CSV (FAQs)</strong>. Uploaded documents are automatically chunked into 500-word sliding windows, embedded into 384-dim vectors, and indexed into Pinecone.</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Select file to upload",
            type=["pdf", "docx", "txt", "csv"],
            key="admin_file_uploader"
        )
        uploaded_by = st.text_input("Uploader Email / Identity", value="admin@edumind.ai")

        if uploaded_file is not None:
            st.info(f"📁 **Selected File:** `{uploaded_file.name}` ({round(uploaded_file.size/1024, 2)} KB)")
            if st.button("🚀 Process & Index Document", use_container_width=True, key="btn_ingest_tab1"):
                with st.spinner("Extracting text, chunking, generating 384-dim embeddings, and storing in Pinecone..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"uploaded_by": uploaded_by}
                        res = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=60)
                        if res.status_code == 200:
                            st.success(f"✅ Document `{uploaded_file.name}` successfully processed and indexed!")
                            st.json(res.json())
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"❌ Ingestion Failed ({res.status_code}): {res.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")

    # Tab 2: Manage Documents Table
    with tab2:
        st.markdown("### 📋 Active Knowledge Base Inventory")
        try:
            res = requests.get(f"{BACKEND_URL}/documents", timeout=10)
            if res.status_code == 200:
                docs = res.json().get("documents", [])
                if docs:
                    df = pd.DataFrame(docs)
                    cols_to_show = [c for c in ["id", "title", "file_type", "file_size", "chunk_count", "uploaded_at"] if c in df.columns]
                    st.dataframe(df[cols_to_show], use_container_width=True)

                    st.markdown("---")
                    st.markdown("### 🗑️ Purge Document & Vector Vectors")
                    doc_dict = {d["id"]: f"{d.get('title', 'Untitled')} ({d.get('file_type', 'unknown').upper()}) - ID: {d['id'][:8]}..." for d in docs}
                    selected_id = st.selectbox("Select document to purge:", options=list(doc_dict.keys()), format_func=lambda x: doc_dict[x])

                    if st.button("🗑️ Delete Selected Document & Vectors", type="primary", use_container_width=True):
                        try:
                            del_res = requests.delete(f"{BACKEND_URL}/document/{selected_id}", timeout=10)
                            if del_res.status_code == 200:
                                st.success("Document and vectors purged successfully.")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"Deletion failed: {del_res.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.info("No documents currently indexed.")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

    # Tab 3: Vector Index Analytics
    with tab3:
        st.markdown("### 📊 Pinecone Index Metrics & Namespace Breakdown")
        try:
            stats_res = requests.get(f"{BACKEND_URL}/admin/stats", timeout=10)
            if stats_res.status_code == 200:
                st.json(stats_res.json())
            else:
                st.warning("Could not fetch Pinecone stats.")
        except Exception as e:
            st.error(f"Error fetching stats: {e}")

# ----------------------------------------------------------------------
# 8. PAGE 4: 🏠 HOME & OVERVIEW (HERO LANDING PAGE)
# ----------------------------------------------------------------------
elif navigation == "🏠 Home & Overview":
    st.markdown("""
    <div class="glass-header" style="padding: 40px !important;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap:wrap; gap: 20px;">
            <div style="max-width: 800px;">
                <span class="badge-cyan" style="margin-bottom: 16px; box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);">Retrieval-Augmented Generation Platform</span>
                <h1 style="font-size: 3.1rem; margin: 12px 0 16px 0; font-weight: 800; line-height: 1.15;" class="gradient-title">
                    Turn Your Documents into an <span class="gradient-text">Interactive AI Assistant</span>
                </h1>
                <p style="color: #94a3b8; font-size: 1.15rem; max-width: 740px; margin-bottom: 28px; line-height: 1.65;">
                    EduMind AI indexes course materials, policies, and FAQs into a high-dimensional vector store, enabling instant, accurate, and context-grounded answers with zero hallucinations.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%; min-height: 200px; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size: 2.4rem; margin-bottom: 10px;">🎯</div>
            <h4 style="margin: 0 0 8px 0; color: #f8fafc; font-weight:700;">Zero Hallucination</h4>
            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; line-height:1.5;">Answers are strictly grounded in verified document chunks.</p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%; min-height: 200px; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size: 2.4rem; margin-bottom: 10px;">⚡</div>
            <h4 style="margin: 0 0 8px 0; color: #f8fafc; font-weight:700;">Sub-Second Search</h4>
            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; line-height:1.5;">Pinecone vector engine retrieves relevant context in milliseconds.</p>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%; min-height: 200px; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size: 2.4rem; margin-bottom: 10px;">🧠</div>
            <h4 style="margin: 0 0 8px 0; color: #f8fafc; font-weight:700;">Conversational Memory</h4>
            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; line-height:1.5;">Remembers previous context across follow-up user inquiries.</p>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 100%; min-height: 200px; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size: 2.4rem; margin-bottom: 10px;">📑</div>
            <h4 style="margin: 0 0 8px 0; color: #f8fafc; font-weight:700;">Multi-Format Support</h4>
            <p style="color: #94a3b8; font-size: 0.88rem; margin: 0; line-height:1.5;">Seamlessly processes PDF, DOCX, TXT, and FAQ CSV files.</p>
        </div>
        """, unsafe_allow_html=True)
