# app.py
"""Streamlit front-end for the AI-supported LMS (Turkish UI)."""

import os
import hashlib
import requests
import asyncio
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# ── Load environment ───────────────────────────────────────────────────────────
print("DEBUG: [app.py] Starting execution...")
_project_dir = Path(__file__).resolve().parent
_env_path = _project_dir / ".env"
if _env_path.exists():
    print("DEBUG: [app.py] Loading .env file...")
    load_dotenv(dotenv_path=_env_path)

# Also load Streamlit Cloud secrets into env vars (if available)
print("DEBUG: [app.py] Accessing st.secrets...")
try:
    for key in ["GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "MODEL_NAME",
                 "FASTAPI_URL", "DATABASE_URL", "JWT_SECRET"]:
        if key in st.secrets:
            print(f"DEBUG: [app.py] Loading secret key: {key}")
            os.environ[key] = st.secrets[key]
except Exception as e:
    print(f"DEBUG: [app.py] Secrets loading failed or skipped: {e}")

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").strip()
print(f"DEBUG: [app.py] FASTAPI_URL is set to: {FASTAPI_URL}")

# ── Page config ────────────────────────────────────────────────────────────────
print("DEBUG: [app.py] Configuring page...")
st.set_page_config(
    page_title="AI Destekli LMS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
print("DEBUG: [app.py] Page configured successfully.")

# ── Premium dark-theme CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e) !important;
    color: #e2e8f0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.3) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.5) !important;
}

/* ── Input fields ── */
.stTextInput > div > input,
.stTextArea > div > textarea {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(129,140,248,0.8) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04) !important;
    padding: 0.45rem 0.7rem !important;
}

.stTextInput > div > input::placeholder,
.stTextArea > div > textarea::placeholder {
    color: #cbd5e1 !important;
}

/* ── Selectbox styling (for course select on content page) ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(129,140,248,0.8) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}
.stSelectbox [data-baseweb="select"] * {
    color: #f8fafc !important;
}
.stSelectbox svg {
    fill: #e2e8f0 !important;
}
/* Selectbox dropdown popup */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[role="listbox"] {
    background: #1e1e2e !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 10px !important;
}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
ul[role="listbox"] li,
[role="option"] {
    color: #e2e8f0 !important;
    background: transparent !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
ul[role="listbox"] li:hover,
[role="option"]:hover {
    background: rgba(99,102,241,0.25) !important;
    color: #ffffff !important;
}

/* ── Sidebar: ALL text elements ── */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p {
    color: #e2e8f0 !important;
}

/* ── Radio buttons (used for menu) ── */
.stRadio > div {
    gap: 4px !important;
}
.stRadio > div > label {
    color: #e2e8f0 !important;
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.8rem !important;
    margin-bottom: 2px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
.stRadio > div > label:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.5) !important;
}
/* Active/selected radio */
.stRadio > div > label[data-checked="true"],
.stRadio > div > label:has(input:checked) {
    background: rgba(99,102,241,0.2) !important;
    border-color: #6366f1 !important;
}
.stRadio > div > label > div,
.stRadio > div > label > div > p,
.stRadio > div > label > div > div,
.stRadio > div > label span,
.stRadio > div > label p {
    color: #e2e8f0 !important;
}
/* Hide radio circle */
[data-testid="stSidebar"] .stRadio input[type="radio"] {
    accent-color: #6366f1 !important;
}

/* ── Headers ── */
h1, h2, h3 { color: #e2e8f0 !important; }

/* ── Success / warning / info ── */
.stSuccess { background: rgba(16,185,129,0.15) !important; border-left: 4px solid #10b981 !important; }
.stWarning { background: rgba(245,158,11,0.15) !important; border-left: 4px solid #f59e0b !important; }
.stError   { background: rgba(239,68,68,0.15)  !important; border-left: 4px solid #ef4444  !important; }
.stInfo    { background: rgba(99,102,241,0.15)  !important; border-left: 4px solid #6366f1  !important; }

/* ── Alert text inside ── */
.stSuccess p, .stWarning p, .stError p, .stInfo p,
.stAlert p, [data-testid="stAlert"] p {
    color: #e2e8f0 !important;
}

/* ── Card-like containers ── */
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: rgba(99,102,241,0.55); }

.badge {
    display: inline-block;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 8px;
}

/* ── Sidebar menu button style ── */
.menu-item {
    display: block;
    width: 100%;
    padding: 0.6rem 1rem;
    margin-bottom: 4px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 10px;
    color: #e2e8f0;
    font-size: 0.95rem;
    text-decoration: none;
    transition: all 0.2s ease;
}
.menu-item:hover {
    background: rgba(99,102,241,0.15);
    border-color: rgba(99,102,241,0.4);
}

/* ── Metric labels ── */
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #e2e8f0 !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"] div,
[data-testid="stMetricDelta"] div {
    color: #e2e8f0 !important;
}

/* ── Divider ── */
hr { border-color: rgba(99,102,241,0.2) !important; }

/* ── JSON display ── */
.stJson { background: rgba(0,0,0,0.3) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "users_db" not in st.session_state:
    # In-memory user store (keyed by username → password_hash)
    st.session_state.users_db = {}
if "content_store" not in st.session_state:
    st.session_state.content_store = []  # list of dicts
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None
if "selected_course_detail" not in st.session_state:
    st.session_state.selected_course_detail = None

page = None

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ── FastAPI / Python Local Helper ─────────────────────────────────────────────
def api_post(endpoint: str, payload: dict):
    # 1. Try standard FastAPI endpoint
    url = f"{FASTAPI_URL}{endpoint}"
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # 2. Direct Python import fallback (No HTTP dependency)
    try:
        import ai_service
        
        # Propagate API keys manually to ensure they are up to date
        ai_service.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        ai_service.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        ai_service.GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
        ai_service.MODEL_NAME     = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        ai_service.PROVIDER       = ai_service._detect_provider()

        if endpoint == "/analyze_text":
            system_prompt = (
                "Sen bir eğitim asistanısın. Verilen öğrenci metnini analiz et; "
                "yapıcı geri bildirim, anahtar kavramlar ve geliştirme önerileri sun. "
                "Yanıtını Türkçe ver."
            )
            result = asyncio.run(ai_service.call_llm([
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": payload["text"]},
            ]))
            return {"analysis": result, "provider": ai_service.PROVIDER}

        elif endpoint == "/summarize_content":
            system_prompt = (
                "Sen özlü bir özetleyicisin. Verilen metni 2-3 cümleyle özetle; "
                "ana fikirleri koru. Türkçe yanıt ver."
            )
            result = asyncio.run(ai_service.call_llm([
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": payload["content"]},
            ]))
            return {"summary": result, "provider": ai_service.PROVIDER}
    except Exception as exc:
        st.error(f"AI Servis hatası: {exc}")
    return None

def check_api_health() -> dict:
    # 1. Try standard FastAPI health check
    urls_to_try = [
        f"{FASTAPI_URL}/health",
        "http://127.0.0.1:8000/health",
        "http://localhost:8000/health",
    ]
    for url in urls_to_try:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                data = r.json()
                data["internal"] = False
                return data
        except Exception:
            continue

    # 2. Try direct import fallback (If environment contains credentials)
    try:
        import ai_service
        # Re-detect provider based on active env variables
        ai_service.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        ai_service.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        ai_service.GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
        provider = ai_service._detect_provider()
        return {"status": "ok", "provider": provider, "internal": True}
    except Exception:
        pass
    return {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎓 AI Destekli LMS")
st.sidebar.markdown("---")

if st.session_state.user is None:
    login_tab = st.sidebar.radio(
        "İşlem Seçin",
        ["🔑 Giriş Yap", "📝 Kayıt Ol"],
        label_visibility="collapsed",
    )

    if login_tab == "🔑 Giriş Yap":
        st.sidebar.markdown("### Giriş")
        username = st.sidebar.text_input("Kullanıcı Adı", key="login_user")
        password = st.sidebar.text_input("Şifre", type="password", key="login_pass")
        if st.sidebar.button("Giriş Yap", key="btn_login"):
            stored = st.session_state.users_db.get(username)
            if stored and stored == _hash(password):
                st.session_state.user = {"name": username}
                st.rerun()
            elif not username or not password:
                st.sidebar.warning("Kullanıcı adı ve şifre giriniz.")
            else:
                st.sidebar.error("Kullanıcı adı veya şifre yanlış.")
    else:
        st.sidebar.markdown("### Kayıt Ol")
        new_user = st.sidebar.text_input("Yeni Kullanıcı Adı", key="reg_user")
        new_pass = st.sidebar.text_input("Yeni Şifre", type="password", key="reg_pass")
        new_pass2 = st.sidebar.text_input("Şifreyi Onayla", type="password", key="reg_pass2")
        if st.sidebar.button("Kayıt Ol", key="btn_register"):
            if not new_user or not new_pass:
                st.sidebar.warning("Tüm alanları doldurun.")
            elif new_pass != new_pass2:
                st.sidebar.error("Şifreler eşleşmiyor.")
            elif new_user in st.session_state.users_db:
                st.sidebar.error("Bu kullanıcı adı zaten alınmış.")
            else:
                st.session_state.users_db[new_user] = _hash(new_pass)
                st.sidebar.success("✅ Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
else:
    st.sidebar.markdown(f"### 👋 Hoş geldiniz,\n**{st.session_state.user['name']}**")
    st.sidebar.markdown("---")

    # API health badge
    health = check_api_health()
    if health.get("status") == "ok":
        provider = health.get("provider", "?").upper()
        if health.get("internal"):
            st.sidebar.success(f"✅ AI Servisi Aktif (Bulut) – {provider}")
        else:
            st.sidebar.success(f"✅ AI Servisi Aktif – {provider}")
    else:
        st.sidebar.warning("⚠️ AI Servisi bağlı değil – run_all.bat çalıştırın")

    st.sidebar.markdown("---")

    # ── MENÜ: Radio & Styling ──
    st.sidebar.markdown("### 📌 Menü")
    page = st.sidebar.radio(
        "Sayfa Seçin",
        ["🏠 Ana Sayfa", "📚 Kurslar", "📝 İçerik Yükle", "🔍 Metin Analizi", "🗂️ İçerik Özeti"],
        key="nav_menu",
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Çıkış Yap", key="btn_logout"):
        st.session_state.user = None
        st.rerun()

# ── Guard ─────────────────────────────────────────────────────────────────────
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 4rem 0;'>
            <div style='font-size:5rem;'>🎓</div>
            <h1 style='color:#e2e8f0; font-size:2.5rem; margin:0.5rem 0;'>AI Destekli LMS</h1>
            <p style='color:#94a3b8; font-size:1.1rem;'>Yapay Zeka ile Güçlendirilmiş Öğrenme Yönetim Sistemi</p>
            <p style='color:#6366f1; margin-top:2rem;'>← Sol menüden giriş yapın veya kayıt olun</p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ── Pages ─────────────────────────────────────────────────────────────────────

if page == "🏠 Ana Sayfa":
    st.markdown("# 🏠 Ana Sayfa")
    st.markdown(f"Hoş geldiniz, **{st.session_state.user['name']}**! Sisteme başarıyla giriş yaptınız.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("📚 Kurslar", "3", "Mevcut kurs"),
        ("📝 İçerikler", str(len(st.session_state.content_store)), "Yüklü içerik"),
        ("🤖 AI Durumu", "Aktif" if health.get("status") == "ok" else "Kapalı", ""),
        ("👤 Kullanıcı", st.session_state.user["name"], ""),
    ]
    for col, (icon_label, value, delta) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.metric(label=icon_label, value=value, delta=delta or None)

    st.markdown("---")
    st.markdown("### 🚀 Hızlı Erişim")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown("""<div class="card"><h4>🔍 Metin Analizi</h4><p style="color:#94a3b8">Öğrenci metinlerini AI ile analiz edin, geri bildirim alın.</p></div>""", unsafe_allow_html=True)
    with q2:
        st.markdown("""<div class="card"><h4>🗂️ İçerik Özeti</h4><p style="color:#94a3b8">Uzun içerikleri 2-3 cümleye sıkıştırın.</p></div>""", unsafe_allow_html=True)
    with q3:
        st.markdown("""<div class="card"><h4>📝 İçerik Yükle</h4><p style="color:#94a3b8">Yeni ders materyali ekleyin ve kaydedin.</p></div>""", unsafe_allow_html=True)

elif page == "📚 Kurslar":
    st.markdown("# 📚 Kurs Listesi")
    st.markdown("---")
    courses = [
        {"title": "Python Programlama", "desc": "Temel Python sözdizimi, veri yapıları ve nesne yönelimli programlama.", "icon": "🐍", "level": "Başlangıç", "detail": "Bu kurs, Python dilinin temellerini ve uygulamalı egzersizlerle öğrenmeyi sağlar."},
        {"title": "Derin Öğrenme", "desc": "Yapay sinir ağları, CNN, RNN ve modern derin öğrenme mimarileri.", "icon": "🧠", "level": "İleri", "detail": "Bu kurs, ileri düzey model mimarileri ve gerçek dünya uygulamaları üzerine odaklanır."},
        {"title": "Veri Bilimi", "desc": "Pandas, NumPy, Matplotlib ile veri analizi ve görselleştirme.", "icon": "📊", "level": "Orta", "detail": "Bu kurs, veri temizleme, keşif ve görselleştirme tekniklerini öğretir."},
    ]
    for c in courses:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"""
            <div class="card">
                <h3>{c['icon']} {c['title']} <span class="badge">{c['level']}</span></h3>
                <p style="color:#94a3b8; margin:0">{c['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Detay →", key=f"detail_{c['title']}"):
                st.session_state.selected_course = c['title']
                st.session_state.selected_course_detail = c['detail']
                st.rerun()

    if st.session_state.selected_course:
        st.markdown("---")
        st.markdown(f"### 📌 {st.session_state.selected_course} Detayları")
        st.info(st.session_state.selected_course_detail)
        if st.button("← Geri Dön", key="back_to_courses"):
            st.session_state.selected_course = None
            st.session_state.selected_course_detail = None
            st.rerun()

elif page == "📝 İçerik Yükle":
    st.markdown("# 📝 İçerik Yükle")
    st.markdown("---")
    course = st.selectbox("Kurs Seçiniz", ["Python Programlama", "Derin Öğrenme", "Veri Bilimi"])
    title  = st.text_input("İçerik Başlığı", placeholder="Ör: Değişkenler ve Veri Tipleri")
    body   = st.text_area("İçerik Metni", height=220, placeholder="Ders notlarını buraya yazın...")

    col_btn, col_clear = st.columns([1, 5])
    with col_btn:
        if st.button("⬆️ Yükle", key="btn_upload"):
            if title and body:
                st.session_state.content_store.append({"kurs": course, "başlık": title, "içerik": body[:100] + "..."})
                st.success(f"✅ **'{title}'** içeriği **{course}** kursuna eklendi!")
            else:
                st.warning("Başlık ve içerik zorunludur.")

    if st.session_state.content_store:
        st.markdown("---")
        st.markdown("### 📋 Yüklenen İçerikler")
        for i, item in enumerate(st.session_state.content_store):
            st.markdown(f"""
            <div class="card">
                <strong>{i+1}. {item['başlık']}</strong>
                <span class="badge">{item['kurs']}</span>
                <p style="color:#94a3b8; margin-top:0.5rem; font-size:0.85rem">{item['içerik']}</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "🔍 Metin Analizi":
    st.markdown("# 🔍 Öğrenci Metni Analizi")
    st.markdown("Öğrenci tarafından yazılan metni yapay zekâ ile analiz edin; anahtar kavramlar, geri bildirim ve öneriler alın.")
    st.markdown("---")

    student_text = st.text_area("Analiz edilecek metin", height=220,
                                placeholder="Öğrencinin ödevini veya metnini buraya yapıştırın...")

    if st.button("🔍 Analiz Et", key="btn_analyze"):
        if not student_text.strip():
            st.warning("Lütfen bir metin giriniz.")
        else:
            with st.spinner("AI analiz yapıyor..."):
                resp = api_post("/analyze_text", {"text": student_text})
            if resp:
                st.markdown("### 📊 Analiz Sonucu")
                provider_label = resp.get("provider", "").upper()
                st.markdown(f"<span class='badge'>{provider_label}</span>", unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(resp.get("analysis", ""))

elif page == "🗂️ İçerik Özeti":
    st.markdown("# 🗂️ İçerik Özeti")
    st.markdown("Uzun ders materyallerini veya makaleleri yapay zekâ ile 2-3 cümleye özetleyin.")
    st.markdown("---")

    raw_content = st.text_area("Özetlenecek içerik", height=220,
                               placeholder="Özetlemek istediğiniz metni buraya yapıştırın...")

    if st.button("🗂️ Özetle", key="btn_summarize"):
        if not raw_content.strip():
            st.warning("Lütfen özetlenecek metni giriniz.")
        else:
            with st.spinner("AI özetliyor..."):
                resp = api_post("/summarize_content", {"content": raw_content})
            if resp:
                st.markdown("### ✨ Özet")
                provider_label = resp.get("provider", "").upper()
                st.markdown(f"<span class='badge'>{provider_label}</span>", unsafe_allow_html=True)
                st.markdown("---")
                summary = resp.get("summary", "")
                st.info(summary)
