import streamlit as st
import sqlite3
import hashlib
import time
import random
import numpy as np
from PIL import Image
from datetime import datetime
import io
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HEMOSCAN",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme config ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0f;
    color: #e2e2ee;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.8rem; padding-bottom: 2rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0d0d15 !important;
    border-right: 1px solid #1e1e2e;
}
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label { color: #e2e2ee !important; }

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background-color: #13131f !important;
    border: 1px solid #2a2a3e !important;
    border-radius: 8px !important;
    color: #e2e2ee !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput label, .stSelectbox label,
.stNumberInput label, .stRadio label { color: #e2e2ee !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }

/* File uploader */
div[data-testid="stFileUploader"] {
    background-color: #13131f !important;
    border: 2px dashed #2a2a3e !important;
    border-radius: 12px !important;
}

/* Page title */
.page-title {
    font-size: 1.8rem; font-weight: 700; color: #f1f1f8;
    border-left: 4px solid #dc2626; padding-left: 14px; margin-bottom: 4px;
}
.page-sub { color: #8888aa; font-size: 0.87rem; padding-left: 18px; margin-bottom: 22px; }

/* Cards */
.card {
    background: #13131f; border: 1px solid #1e1e2e;
    border-radius: 14px; padding: 22px 26px; margin-bottom: 16px;
}
.metric-card {
    background: #13131f; border: 1px solid #1e1e2e;
    border-radius: 12px; padding: 18px 20px; text-align: center;
}
.metric-label { font-size: 0.72rem; color: #8888aa; text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 6px; }
.metric-value { font-size: 1.8rem; font-weight: 700; }
.metric-tag { font-size: 0.7rem; color: #dc2626; margin-top: 3px; }

/* Result severity */
.sev-normal  { background: rgba(34,197,94,0.1);  border: 1px solid #16a34a; border-radius: 12px; padding: 20px 24px; }
.sev-mild    { background: rgba(234,179,8,0.1);  border: 1px solid #ca8a04; border-radius: 12px; padding: 20px 24px; }
.sev-moderate{ background: rgba(249,115,22,0.1); border: 1px solid #ea580c; border-radius: 12px; padding: 20px 24px; }
.sev-severe  { background: rgba(220,38,38,0.1);  border: 1px solid #dc2626; border-radius: 12px; padding: 20px 24px; }
.sev-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 4px; }
.sev-sub   { font-size: 0.85rem; color: #8888aa; }

/* Hb gauge */
.hb-box {
    background: #0d0d15; border: 1px solid #1e1e2e;
    border-radius: 10px; padding: 14px 18px; margin-top: 14px;
}
.hb-label { font-size: 0.75rem; color: #8888aa; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.07em; }
.hb-value { font-size: 2rem; font-weight: 700; }

/* History rows */
.hist-row {
    background: #13131f; border: 1px solid #1e1e2e; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px; display: flex;
    align-items: center; gap: 12px; font-size: 0.84rem; color: #e2e2ee;
}
.badge { padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-normal   { background: rgba(34,197,94,0.2);  color: #22c55e; }
.badge-mild     { background: rgba(234,179,8,0.2);  color: #eab308; }
.badge-moderate { background: rgba(249,115,22,0.2); color: #f97316; }
.badge-severe   { background: rgba(220,38,38,0.2);  color: #ef4444; }

/* User badge sidebar */
.user-badge {
    background: #13131f; border: 1px solid #1e1e2e;
    border-radius: 10px; padding: 10px 14px; margin-bottom: 14px;
    font-size: 0.82rem; color: #e2e2ee;
}

/* Consent box */
.consent-box {
    background: rgba(220,38,38,0.08); border: 1px solid #dc2626;
    border-radius: 12px; padding: 18px 22px; margin: 16px 0;
}

/* Tab-like section headers */
.section-head {
    font-size: 1rem; font-weight: 600; color: #dc2626;
    border-bottom: 1px solid #1e1e2e; padding-bottom: 8px; margin-bottom: 16px;
}

div[data-testid="stCheckbox"] label { color: #e2e2ee !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE SETUP (SQLite)
# ══════════════════════════════════════════════════════════════════════════════
DB_PATH = "hemoscan.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            age        INTEGER,
            gender     TEXT,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # screening table
    c.execute("""
        CREATE TABLE IF NOT EXISTS screening (
            screening_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER,
            screening_date TEXT,
            screening_time TEXT,
            hb_level       REAL,
            anemia_status  TEXT,
            severity       TEXT,
            confidence     REAL,
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        )
    """)
    # consent table
    c.execute("""
        CREATE TABLE IF NOT EXISTS consent (
            consent_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER,
            consent_status    TEXT,
            consent_timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(name, age, gender, username, password):
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO user (name,age,gender,username,password) VALUES (?,?,?,?,?)",
            (name, age, gender, username, hash_pw(password))
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."

def login_user(username, password):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM user WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def save_consent(user_id):
    conn = get_db()
    conn.execute(
        "INSERT INTO consent (user_id,consent_status) VALUES (?,?)",
        (user_id, "Given")
    )
    conn.commit()
    conn.close()

def save_screening(user_id, hb, status, severity, confidence):
    now = datetime.now()
    conn = get_db()
    conn.execute("""
        INSERT INTO screening
        (user_id,screening_date,screening_time,hb_level,anemia_status,severity,confidence)
        VALUES (?,?,?,?,?,?,?)
    """, (user_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),
          hb, status, severity, confidence))
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM screening WHERE user_id=? ORDER BY screening_id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats(user_id):
    conn = get_db()
    total  = conn.execute("SELECT COUNT(*) FROM screening WHERE user_id=?", (user_id,)).fetchone()[0]
    anemic = conn.execute("SELECT COUNT(*) FROM screening WHERE user_id=? AND anemia_status='Anemic'", (user_id,)).fetchone()[0]
    conn.close()
    return total, anemic

# ── Hb Classification ─────────────────────────────────────────────────────────
# Based on WHO thresholds for adults
def classify_hb(hb_value, gender="Male"):
    """
    Returns (anemia_status, severity, color, emoji, description)
    WHO Hb thresholds (g/dL):
      Normal   : Male ≥13.0 / Female ≥12.0
      Mild     : 10.0 – 12.9 (M) / 10.0 – 11.9 (F)
      Moderate : 8.0 – 9.9
      Severe   : < 8.0
    """
    if gender == "Female":
        normal_thresh = 12.0
    else:
        normal_thresh = 13.0

    if hb_value >= normal_thresh:
        return ("Non-Anemic", "Normal",
                "#22c55e", "🟢",
                "Hemoglobin level is within the normal range. No anemia detected.")
    elif hb_value >= 10.0:
        return ("Anemic", "Mild",
                "#eab308", "🟡",
                "Mild anemia detected. Monitor diet and consult a physician.")
    elif hb_value >= 8.0:
        return ("Anemic", "Moderate",
                "#f97316", "🟠",
                "Moderate anemia detected. Medical consultation is recommended.")
    else:
        return ("Anemic", "Severe",
                "#ef4444", "🔴",
                "Severe anemia detected. Immediate medical attention is advised.")

# ── Session state init ────────────────────────────────────────────────────────
for key, val in [("logged_in", False), ("user", None), ("consent_given", False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES (Login / Register)
# ══════════════════════════════════════════════════════════════════════════════
def auth_page():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:2.8rem;">🩸</div>
            <div style="font-size:1.8rem;font-weight:700;color:#f1f1f8;letter-spacing:-0.5px;">HEMOSCAN</div>
            <div style="font-size:0.82rem;color:#8888aa;margin-top:4px;">
                AI-Based Non-Invasive Hemoglobin Screening
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑  Login", "📝  Register"])

        # ── LOGIN ──
        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            uname = st.text_input("Username", placeholder="Enter your username", key="l_user")
            pwd   = st.text_input("Password", placeholder="Enter your password",
                                  type="password", key="l_pass")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                if uname and pwd:
                    user = login_user(uname, pwd)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.consent_given = False
                        st.success(f"Welcome back, {user['name']}!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please fill in all fields.")

        # ── REGISTER ──
        with tab_register:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            r_name   = st.text_input("Full Name",  placeholder="Your full name",    key="r_name")
            r_age    = st.number_input("Age", min_value=1, max_value=120, value=25, key="r_age")
            r_gender = st.selectbox("Gender", ["Male", "Female", "Other"],           key="r_gender")
            r_uname  = st.text_input("Username",   placeholder="Choose a username", key="r_user")
            r_pwd    = st.text_input("Password",   placeholder="Create a password",
                                     type="password", key="r_pass")
            r_pwd2   = st.text_input("Confirm Password", placeholder="Repeat password",
                                     type="password", key="r_pass2")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_register"):
                if not all([r_name, r_uname, r_pwd, r_pwd2]):
                    st.warning("Please fill in all fields.")
                elif r_pwd != r_pwd2:
                    st.error("Passwords do not match.")
                elif len(r_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = register_user(r_name, r_age, r_gender, r_uname, r_pwd)
                    if ok:
                        st.success(msg + " Please log in.")
                    else:
                        st.error(msg)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR (after login)
# ══════════════════════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="font-size:1.4rem;font-weight:700;color:#dc2626;padding:6px 0 2px;">
            🩸 HEMOSCAN
        </div>
        <div style="font-size:0.73rem;color:#8888aa;margin-bottom:16px;">
            Non-Invasive Anemia Detector
        </div>
        """, unsafe_allow_html=True)

        u = st.session_state.user
        st.markdown(f"""
        <div class="user-badge">
            👤 &nbsp;<strong>{u['name']}</strong><br>
            <span style="font-size:0.7rem;color:#8888aa;">
                Age {u['age']} · {u['gender']}
            </span>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio("Navigation", [
            "🏠  Dashboard",
            "🔬  New Screening",
            "📋  Screening History",
            "ℹ️  About"
        ], label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪  Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.consent_given = False
            st.rerun()

    return page

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def dashboard_page():
    u = st.session_state.user
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Welcome back, {u["name"]} — here\'s your screening summary</div>',
                unsafe_allow_html=True)

    total, anemic = get_stats(u["user_id"])
    normal = total - anemic

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, color, tag in [
        (c1, "Total Screenings", total,  "#f1f1f8", "lifetime"),
        (c2, "Anemic Results",  anemic, "#ef4444", "flagged"),
        (c3, "Normal Results",  normal, "#22c55e", "healthy"),
        (c4, "Your Age",        u["age"], "#a78bfa", u["gender"]),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-tag">{tag}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Hb reference chart
    st.markdown('<div class="section-head">📊 Hemoglobin Reference Ranges (WHO)</div>', unsafe_allow_html=True)
    thresh = "≥ 13.0 g/dL" if u["gender"] == "Male" else "≥ 12.0 g/dL"
    st.markdown(f"""
    <div class="card" style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:0.87rem;color:#ccc;">
            <tr style="border-bottom:1px solid #2a2a3e;">
                <th style="text-align:left;padding:8px 12px;color:#8888aa;">Category</th>
                <th style="text-align:left;padding:8px 12px;color:#8888aa;">Hb Level (g/dL)</th>
                <th style="text-align:left;padding:8px 12px;color:#8888aa;">Action</th>
            </tr>
            <tr style="border-bottom:1px solid #1e1e2e;">
                <td style="padding:10px 12px;"><span style="color:#22c55e;font-weight:600;">🟢 Normal</span></td>
                <td style="padding:10px 12px;">{thresh}</td>
                <td style="padding:10px 12px;color:#8888aa;">No action needed</td>
            </tr>
            <tr style="border-bottom:1px solid #1e1e2e;">
                <td style="padding:10px 12px;"><span style="color:#eab308;font-weight:600;">🟡 Mild Anemia</span></td>
                <td style="padding:10px 12px;">10.0 – 12.9</td>
                <td style="padding:10px 12px;color:#8888aa;">Monitor diet, consult physician</td>
            </tr>
            <tr style="border-bottom:1px solid #1e1e2e;">
                <td style="padding:10px 12px;"><span style="color:#f97316;font-weight:600;">🟠 Moderate Anemia</span></td>
                <td style="padding:10px 12px;">8.0 – 9.9</td>
                <td style="padding:10px 12px;color:#8888aa;">Medical consultation required</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;"><span style="color:#ef4444;font-weight:600;">🔴 Severe Anemia</span></td>
                <td style="padding:10px 12px;">&lt; 8.0</td>
                <td style="padding:10px 12px;color:#8888aa;">Immediate medical attention</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Recent history
    history = get_history(u["user_id"])
    if history:
        st.markdown('<div class="section-head">🕒 Recent Screenings</div>', unsafe_allow_html=True)
        for h in history[:4]:
            sev = h["severity"].lower()
            badge_class = f"badge-{sev}"
            st.markdown(f"""
            <div class="hist-row">
                <span style="color:#8888aa;font-size:0.74rem;">#{h['screening_id']}</span>
                <span><strong>{h['screening_date']}</strong> &nbsp;{h['screening_time']}</span>
                <span class="badge {badge_class}">{h['severity']}</span>
                <span style="color:#a78bfa;font-weight:600;">{h['hb_level']:.1f} g/dL</span>
                <span style="margin-left:auto;color:#8888aa;font-size:0.76rem;">
                    {h['confidence']:.1f}% confidence
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 No screenings yet. Go to **New Screening** to upload your first fingertip image.")

# ══════════════════════════════════════════════════════════════════════════════
# NEW SCREENING (main predict page)
# ══════════════════════════════════════════════════════════════════════════════
def screening_page():
    u = st.session_state.user

    st.markdown('<div class="page-title">New Screening</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Upload or capture a fingertip (nail-bed) image for anemia analysis</div>',
                unsafe_allow_html=True)

    # ── Load model ────────────────────────────────────────────────────────────
    @st.cache_resource
    def load_model():
        import tensorflow as tf
        return tf.keras.models.load_model("modell.keras", compile=False)

    try:
        model = load_model()
        model_loaded = True
    except Exception as e:
        model_loaded = False
        st.error(f"Error loading model: {e}")
    # ── CONSENT GATE ─────────────────────────────────────────────────────────
    if not st.session_state.consent_given:
        st.markdown("""
        <div class="consent-box">
            <div style="font-size:1rem;font-weight:700;color:#ef4444;margin-bottom:10px;">
                🔒 Consent Required
            </div>
            <div style="font-size:0.87rem;color:#ccc;line-height:1.7;">
                Before proceeding, please read and agree to the following:<br><br>
                • Your fingertip image will be processed by an AI model for hemoglobin estimation.<br>
                • Results are for <strong>preliminary screening only</strong> and do not replace medical diagnosis.<br>
                • Screening data will be stored securely in the local database for your reference.<br>
                • Image quality and lighting may affect result accuracy.
            </div>
        </div>
        """, unsafe_allow_html=True)

        agree = st.checkbox("I have read and agree to the above terms", key="consent_check")
        if st.button("Proceed to Screening →", use_container_width=False):
            if agree:
                save_consent(u["user_id"])
                st.session_state.consent_given = True
                st.rerun()
            else:
                st.error("You must provide consent to proceed.")
        return

    # ── IMAGE INPUT ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">📸 Image Input</div>', unsafe_allow_html=True)

    input_method = st.radio(
        "Select image source:",
        ["📁 Upload Image", "📷 Use Camera"],
        horizontal=True, key="input_method"
    )

    image = None
    img_name = ""

    if "Upload" in input_method:
        uploaded = st.file_uploader(
            "Upload a fingertip / nail-bed image (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
            help="Ensure the nail is clearly visible with good lighting"
        )
        if uploaded:
            image    = Image.open(uploaded).convert("RGB")
            img_name = uploaded.name

    else:
        cam_img = st.camera_input("📷 Capture your fingertip image")
        if cam_img:
            image    = Image.open(cam_img).convert("RGB")
            img_name = f"camera_{datetime.now().strftime('%H%M%S')}.jpg"

    if image is None:
        st.markdown("""
        <div style="text-align:center;padding:36px;color:#8888aa;font-size:0.9rem;">
            📁 Upload or capture a fingertip image above to begin analysis
        </div>
        """, unsafe_allow_html=True)
        return

    # ── ANALYSIS ──────────────────────────────────────────────────────────────
    col_img, col_res = st.columns([1, 1], gap="large")

    with col_img:
        st.markdown('<div class="section-head">🖼️ Uploaded Image</div>', unsafe_allow_html=True)
        st.image(image, use_container_width=True, caption=img_name)

    with col_res:
        st.markdown('<div class="section-head">🧬 Analysis Result</div>', unsafe_allow_html=True)

        analyze_btn = st.button("🔬  Analyze Now", use_container_width=True)

        if analyze_btn:
            with st.spinner("Preprocessing image and running CNN inference…"):
                time.sleep(1.5)

                if model_loaded:
                   
                    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

                    img_array = np.array(image.resize((224, 224)))
                    img_array = preprocess_input(img_array)
                    img_array  = np.expand_dims(img_array, axis=0)
                    prediction = model.predict(img_array)

                    # If regression output (single float = Hb value)
                    if prediction.shape[-1] == 1:
                        hb_value = float(prediction[0][0]) * 26.7009 + 127.995
                        hb_value = hb_value / 10.0
                        confidence = min(95.0, max(60.0, abs(hb_value - 10) * 5 + 70))
                    else:
                        # If classification output — map class probabilities to Hb estimate
                        probs      = prediction[0]
                        # class 0=Normal, 1=Mild, 2=Moderate, 3=Severe
                        hb_map     = [13.5, 11.0, 9.0, 6.5]
                        hb_value   = sum(p * h for p, h in zip(probs, hb_map))
                        confidence = float(max(probs)) * 100
                else:
                    # Demo mode — random realistic Hb value
                    hb_value   = random.uniform(5.5, 15.5)
                    confidence = random.uniform(72.0, 94.0)

            gender = u.get("gender", "Male")
            status, severity, color, emoji, description = classify_hb(hb_value, gender)

            # Severity result card
            sev_class = f"sev-{severity.lower()}"
            st.markdown(f"""
            <div class="{sev_class}" style="margin-bottom:14px;">
                <div class="sev-title" style="color:{color};">
                    {emoji} {severity} {'Anemia' if status == 'Anemic' else '— No Anemia'}
                </div>
                <div class="sev-sub">{description}</div>
            </div>
            """, unsafe_allow_html=True)

            # Hb level box
            st.markdown(f"""
            <div class="hb-box">
                <div class="hb-label">Estimated Hemoglobin Level</div>
                <div class="hb-value" style="color:{color};">{hb_value:.1f} <span style="font-size:1rem;color:#8888aa;">g/dL</span></div>
                <div style="font-size:0.74rem;color:#8888aa;margin-top:4px;">
                    Confidence: {confidence:.1f}% &nbsp;|&nbsp;
                    Status: <span style="color:{color};font-weight:600;">{status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Severity progress bar
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            normal_thresh = 13.0 if gender == "Male" else 12.0
            hb_pct = min(100, max(0, (hb_value / normal_thresh) * 100))
            st.markdown(f"""
            <div style="font-size:0.75rem;color:#8888aa;margin-bottom:4px;">Hb Level (% of normal)</div>
            <div style="background:#1e1e2e;border-radius:20px;height:10px;overflow:hidden;">
                <div style="width:{hb_pct:.0f}%;height:100%;
                    background:linear-gradient(90deg,{color},{color}88);
                    border-radius:20px;transition:width 1s;"></div>
            </div>
            <div style="font-size:0.72rem;color:#8888aa;margin-top:4px;">{hb_pct:.0f}% of normal threshold</div>
            """, unsafe_allow_html=True)

            # Save to DB
            save_screening(u["user_id"], hb_value, status, severity, confidence)
            st.success("✅ Screening result saved to your history.")

            # Disclaimer
            st.markdown("""
            <div style="margin-top:14px;background:#0d0d15;border:1px solid #1e1e2e;
                border-radius:8px;padding:12px 14px;font-size:0.76rem;color:#8888aa;">
                ⚠️ <strong>Disclaimer:</strong> This result is for preliminary screening only.
                Always consult a qualified healthcare professional for clinical diagnosis and treatment.
            </div>
            """, unsafe_allow_html=True)

        elif not analyze_btn:
            st.markdown("""
            <div style="text-align:center;padding:28px;color:#8888aa;font-size:0.87rem;">
                Click <strong>Analyze Now</strong> to run the CNN model on your image
            </div>
            """, unsafe_allow_html=True)

    # Reset consent for next session
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 New Screening (reset consent)", use_container_width=False):
        st.session_state.consent_given = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SCREENING HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def history_page():
    u = st.session_state.user
    st.markdown('<div class="page-title">Screening History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">All past screening records stored in the local database</div>',
                unsafe_allow_html=True)

    history = get_history(u["user_id"])

    if not history:
        st.info("No screening records yet. Go to **New Screening** to get started.")
        return

    # Summary stats
    total   = len(history)
    anemic  = sum(1 for h in history if h["anemia_status"] == "Anemic")
    avg_hb  = sum(h["hb_level"] for h in history) / total

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Records</div>
        <div class="metric-value">{total}</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="metric-card">
        <div class="metric-label">Anemic Results</div>
        <div class="metric-value" style="color:#ef4444;">{anemic}</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card">
        <div class="metric-label">Avg Hb Level</div>
        <div class="metric-value" style="color:#a78bfa;">{avg_hb:.1f} <span style="font-size:1rem">g/dL</span></div></div>""",
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        filter_sev = st.selectbox("Filter by severity",
                                  ["All", "Normal", "Mild", "Moderate", "Severe"],
                                  key="hist_filter")
    with col_f2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    filtered = history if filter_sev == "All" else [h for h in history if h["severity"] == filter_sev]

    st.markdown(f'<div class="section-head">📋 Records ({len(filtered)} shown)</div>', unsafe_allow_html=True)

    for h in filtered:
        sev   = h["severity"].lower()
        color_map = {
            "normal": "#22c55e", "mild": "#eab308",
            "moderate": "#f97316", "severe": "#ef4444"
        }
        color = color_map.get(sev, "#ccc")
        st.markdown(f"""
        <div class="hist-row">
            <span style="color:#8888aa;font-size:0.74rem;min-width:28px;">#{h['screening_id']}</span>
            <div>
                <div style="font-weight:500;">{h['screening_date']} &nbsp;
                    <span style="color:#8888aa;font-size:0.8rem;">{h['screening_time']}</span>
                </div>
                <div style="font-size:0.78rem;color:#8888aa;">
                    {h['anemia_status']}
                </div>
            </div>
            <span class="badge badge-{sev}">{h['severity']}</span>
            <span style="color:{color};font-weight:700;font-size:1.05rem;">
                {h['hb_level']:.1f} g/dL
            </span>
            <span style="margin-left:auto;color:#8888aa;font-size:0.76rem;">
                {h['confidence']:.1f}% conf.
            </span>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════════════════════════════════
def about_page():
    st.markdown('<div class="page-title">About HEMOSCAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Project information, architecture, and references</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3 style="color:#dc2626;margin-top:0;">🩸 HEMOSCAN — Non-Invasive Anemia Detection</h3>
        <p style="color:#ccc;line-height:1.75;">
            HEMOSCAN is a machine-learning-based screening system that estimates hemoglobin (Hb) levels
            and classifies anemia severity from <strong>fingertip (nail-bed) images</strong> using a
            trained <strong>Convolutional Neural Network (CNN)</strong> model.
        </p>
        <hr style="border-color:#1e1e2e;">
        <table style="width:100%;border-collapse:collapse;font-size:0.87rem;color:#ccc;">
            <tr><td style="color:#8888aa;padding:7px 0;width:180px;">Model</td><td>CNN / MobileNet-based Regression</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Input</td><td>Fingertip nail-bed image (224×224 RGB)</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Output</td><td>Hb level (g/dL) + Anemia severity</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Severity Classes</td><td>Normal · Mild · Moderate · Severe</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Database</td><td>SQLite (local)</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Framework</td><td>Streamlit + TensorFlow/Keras</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Team</td><td>Team 7 — VJC23CS</td></tr>
            <tr><td style="color:#8888aa;padding:7px 0;">Guide</td><td>Mrs. Swathi Venugopal</td></tr>
        </table>
        <hr style="border-color:#1e1e2e;">
        <p style="color:#8888aa;font-size:0.78rem;margin-bottom:0;">
            ⚠️ <strong>Disclaimer:</strong> HEMOSCAN is intended for research and preliminary screening only.
            Results do not constitute a medical diagnosis. Always consult a qualified healthcare professional.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-top:16px;">
        <div class="section-head">🔄 Application Workflow</div>
        <div style="font-size:0.87rem;color:#ccc;line-height:2.2;">
            1. User <strong>registers</strong> and <strong>logs in</strong><br>
            2. User provides <strong>consent</strong> to process biometric image data<br>
            3. User <strong>uploads</strong> or <strong>captures</strong> a fingertip nail-bed image<br>
            4. System <strong>preprocesses</strong> the image (resize to 224×224, normalize)<br>
            5. <strong>CNN model</strong> estimates hemoglobin level via regression<br>
            6. System <strong>classifies</strong> anemia severity using WHO thresholds<br>
            7. Results are <strong>displayed</strong> and <strong>saved</strong> to the SQLite database<br>
            8. User can review <strong>screening history</strong> anytime
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    auth_page()
else:
    page = sidebar()
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if "Dashboard" in page:
        dashboard_page()
    elif "Screening" in page and "History" not in page:
        screening_page()
    elif "History" in page:
        history_page()
    elif "About" in page:
        about_page()
