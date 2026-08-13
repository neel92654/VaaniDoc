import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

from modules.session_manager import init_session_state, end_session_and_wipe_data
from modules.speech import transcribe_audio
from modules.clinical_extraction import extract_clinical_intake
from modules.validation import run_validation_suite

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="VaaniDoc - Multilingual AI Health Intake",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
init_session_state()

# ---------------------------------------------------------
# CRITICAL FIX #1: ROBUST ZERO-CRASH NAVIGATION STATE
# ---------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

def go_to_page(page_name: str):
    """Safely updates navigation state and triggers clean rerun."""
    st.session_state["current_page"] = page_name
    st.rerun()

def on_nav_radio_change():
    """Callback for sidebar navigation radio."""
    if "nav_radio" in st.session_state:
        st.session_state["current_page"] = st.session_state["nav_radio"]

# ---------------------------------------------------------
# DESIGN SYSTEM: HEALTHCARE PALETTE (#F6F8FB BACKGROUND)
# SCOPED CSS (NO GLOBAL WILDCARD OVERRIDES)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Design System Variables */
    :root {
        --bg-main: #F6F8FB;
        --card-bg: #FFFFFF;
        --text-primary: #172033;
        --text-secondary: #5B667A;
        --accent-blue: #2563EB;
        --accent-teal: #0EA5A4;
        --success: #15803D;
        --warning: #B45309;
        --error: #B91C1C;
        --border: #E2E8F0;
        --sidebar-bg: #0F172A;
    }

    /* Base Body Styling */
    .stApp {
        background-color: #F6F8FB !important;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #172033 !important;
    }

    /* Streamlit Top Header & Toolbar Contrast Fix */
    header[data-testid="stHeader"] {
        background-color: #F6F8FB !important;
        color: #172033 !important;
    }
    header[data-testid="stHeader"] *, div[data-testid="stToolbar"] * {
        color: #172033 !important;
    }
    div[data-testid="stDecoration"] {
        background-image: none !important;
        background-color: #2563EB !important;
    }

    /* Scoped Container Typography */
    .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown label,
    div[data-testid="stMarkdownContainer"] > p, label[data-testid="stWidgetLabel"] {
        color: #172033 !important;
        font-size: 1rem;
        line-height: 1.5;
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #F8FAFC !important;
    }

    /* Navigation Radio Text Visibility */
    div[data-testid="stRadio"] label p, div[data-testid="stRadio"] label span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }

    /* Sidebar Status Cards */
    .vaani-status-card {
        background-color: #1E293B;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.75rem;
    }
    .vaani-status-title {
        font-size: 0.75rem;
        color: #CBD5E1 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }
    .vaani-status-value {
        font-size: 1.2rem;
        font-weight: 800;
        color: #38BDF8 !important;
        margin-top: 0.2rem;
    }

    /* Streamlit Bordered Container Custom Card Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 1.4rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
    }

    /* Scoped White Card Component for standalone HTML */
    .vaani-card-box {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 1.6rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }

    /* Hero Section */
    .vaani-hero {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .vaani-eyebrow {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #2563EB !important;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .vaani-hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #172033 !important;
        line-height: 1.25;
        margin-bottom: 1rem;
    }
    .vaani-hero-desc {
        font-size: 1.1rem;
        color: #5B667A !important;
        max-width: 700px;
        margin-bottom: 1.5rem;
    }

    /* Feature Cards */
    .vaani-feature-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.4rem;
        height: 100%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .vaani-feature-card h4 {
        color: #172033 !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.4rem !important;
    }
    .vaani-feature-card p {
        color: #5B667A !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }

    /* Process Flow Steps */
    .vaani-step-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .vaani-step-num {
        font-size: 1.2rem;
        font-weight: 800;
        color: #2563EB !important;
    }

    /* High-Contrast Button Styling */
    .stButton button, div.stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.65rem 1.25rem !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    .stButton button:hover, div.stButton > button:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }

    /* Secondary Light Buttons */
    .secondary-btn button, div.secondary-btn > button {
        background-color: #FFFFFF !important;
        color: #172033 !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
    }
    .secondary-btn button:hover, div.secondary-btn > button:hover {
        background-color: #F1F5F9 !important;
    }

    /* Destructive Red Button */
    .destructive-btn button, div.destructive-btn > button {
        background-color: #FFF1F1 !important;
        color: #B91C1C !important;
        border: 1px solid #FCA5A5 !important;
        font-weight: 700 !important;
    }
    .destructive-btn button:hover, div.destructive-btn > button:hover {
        background-color: #FEE2E2 !important;
    }

    /* Input & Select Box Text Visibility */
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] span {
        color: #172033 !important;
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    /* Triage Badges */
    .badge-routine-v2 {
        background-color: #DCFCE7 !important;
        color: #15803D !important;
        border: 1px solid #86EFAC !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        display: inline-block !important;
    }
    .badge-priority-v2 {
        background-color: #FEF3C7 !important;
        color: #B45309 !important;
        border: 1px solid #FDE047 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        display: inline-block !important;
    }
    .badge-high-v2 {
        background-color: #FEE2E2 !important;
        color: #B91C1C !important;
        border: 1px solid #FCA5A5 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        display: inline-block !important;
    }

    /* Transcript Highlight Box */
    .transcript-box-v3 {
        background-color: #F1F5F9 !important;
        border-left: 4px solid #2563EB !important;
        border-radius: 8px !important;
        padding: 1.2rem !important;
        color: #172033 !important;
        font-size: 1.05rem !important;
        font-style: italic !important;
    }
</style>
""", unsafe_allow_html=True)

# Target Languages Definition with Native Names
LANGUAGES = [
    "🇮🇳 Hindi (हिंदी)",
    "🇮🇳 Gujarati (ગુજરાતી)",
    "🇮🇳 Marathi (मराठी)",
    "🇮🇳 Bengali (বাংলা)",
    "🇮🇳 Tamil (தமிழ்)",
    "🇮🇳 Telugu (తెలుగు)",
    "🇮🇳 Kannada (ಕನ್ನಡ)",
    "🇮🇳 Malayalam (മലയാളം)",
    "🇮🇳 Punjabi (ਪੰਜਾਬੀ)",
    "🇮🇳 Odia (ଓଡ଼ିଆ)",
    "🇬🇧 English"
]

LANG_MAP = {
    "🇮🇳 Hindi (हिंदी)": "Hindi",
    "🇮🇳 Gujarati (ગુજરાતી)": "Gujarati",
    "🇮🇳 Marathi (मराठी)": "Marathi",
    "🇮🇳 Bengali (বাংলা)": "Bengali",
    "🇮🇳 Tamil (தமிழ்)": "Tamil",
    "🇮🇳 Telugu (తెలుగు)": "Telugu",
    "🇮🇳 Kannada (ಕನ್ನಡ)": "Kannada",
    "🇮🇳 Malayalam (മലയാളം)": "Malayalam",
    "🇮🇳 Punjabi (ਪੰਜਾਬੀ)": "Punjabi",
    "🇮🇳 Odia (ଓଡ଼ିଆ)": "Odia",
    "🇬🇧 English": "English"
}

# Language-aware placeholder hints
PLACEHOLDER_MAP = {
    "Hindi": "उदाहरण: मुझे दो दिनों से बुखार है और सिर दर्द है।",
    "Gujarati": "ઉદાહરણ: મને બે દિવસથી તાવ છે અને છાતીમાં દુખાવો થાય છે.",
    "English": "Example: I've had fever for two days and a severe headache.",
    "Marathi": "उदाहरण: मला दोन दिवसांपासून ताप आहे आणि डोकेदुखी आहे.",
    "Bengali": "উদাহরণ: আমার দুই দিন ধরে জ্বর এবং মাথা ব্যথা করছে।"
}

# ---------------------------------------------------------
# SIDEBAR DESIGN & HONEST SYSTEM STATUS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🩺 **VaaniDoc**")
    st.markdown("<p style='color:#CBD5E1; font-size:0.85rem; margin-top:-0.5rem;'>Multilingual AI Health Intake</p>", unsafe_allow_html=True)

    # Active Session Badge
    st.markdown(f"""
    <div style="background:rgba(37, 99, 235, 0.15); border:1px solid #2563EB; border-radius:8px; padding:0.6rem 0.9rem; margin-bottom:1.2rem;">
        <div style="font-size:0.75rem; color:#93C5FD; text-transform:uppercase; font-weight:700;">Active Session</div>
        <div style="font-weight:800; color:#FFFFFF; font-size:1.1rem; margin-top:0.1rem;">Session: {st.session_state['session_id']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Synchronize widget state safely BEFORE radio rendering
    st.session_state["nav_radio"] = st.session_state["current_page"]

    st.radio(
        "Navigation",
        ["Home", "Patient Intake", "Doctor View", "Validation"],
        key="nav_radio",
        on_change=on_nav_radio_change
    )

    st.markdown("---")
    st.markdown("<h4 style='color:#F8FAFC; margin-bottom:0.8rem;'>SYSTEM STATUS</h4>", unsafe_allow_html=True)

    val_res = st.session_state.get("validation_results")
    if val_res:
        accuracy_display = f"{val_res['accuracy']}%"
        tests_display = f"{val_res['passed']} / {val_res['total']}"
    else:
        accuracy_display = "Pending validation"
        tests_display = "Pending validation"

    st.markdown(f"""
    <div class="vaani-status-card" style="border-left-color: #2563EB;">
        <div class="vaani-status-title">Language Coverage</div>
        <div class="vaani-status-value">10 Languages</div>
        <div style="font-size:0.7rem; color:#CBD5E1;">+ English</div>
    </div>
    <div class="vaani-status-card" style="border-left-color: #0EA5A4;">
        <div class="vaani-status-title">Extraction Accuracy</div>
        <div class="vaani-status-value">{accuracy_display}</div>
    </div>
    <div class="vaani-status-card" style="border-left-color: #7C3AED;">
        <div class="vaani-status-title">Test Cases Passed</div>
        <div class="vaani-status-value">{tests_display}</div>
    </div>
    <div class="vaani-status-card" style="border-left-color: #B45309;">
        <div class="vaani-status-title">Connectivity Mode</div>
        <div class="vaani-status-value">Low-Bandwidth Ready</div>
    </div>
    <div class="vaani-status-card" style="border-left-color: #15803D;">
        <div class="vaani-status-title">Privacy Architecture</div>
        <div class="vaani-status-value">Session-Only</div>
        <div style="font-size:0.7rem; color:#CBD5E1;">Auto delete on end</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Hack Orbit 2026 • Track 2 PS-03")


# ---------------------------------------------------------
# PAGE 1: HOME PAGE
# ---------------------------------------------------------
def show_home_page():
    st.markdown("""
    <div class="vaani-hero">
        <div class="vaani-eyebrow">Multilingual Clinical Intake</div>
        <div class="vaani-hero-title">Speak naturally.<br>Let the doctor see the important details.</div>
        <div class="vaani-hero-desc">
            VaaniDoc converts patient-reported symptoms from Indian regional languages into structured clinical information for faster review.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Start Patient Intake CTA Button - Clean Callback Execution
    if st.button("✨ **Start Patient Intake**", key="home_cta_start", use_container_width=True):
        go_to_page("Patient Intake")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 3 Feature Cards
    fcol1, fcol2, fcol3 = st.columns(3, gap="medium")
    with fcol1:
        st.markdown("""
        <div class="vaani-feature-card">
            <div style="font-size:2rem; color:#2563EB;">🌐</div>
            <h4>Multilingual</h4>
            <p>10 Indian languages + English supported with native voice recognition.</p>
        </div>
        """, unsafe_allow_html=True)
    with fcol2:
        st.markdown("""
        <div class="vaani-feature-card">
            <div style="font-size:2rem; color:#0EA5A4;">⚡</div>
            <h4>Low Connectivity</h4>
            <p>Engineered for low-bandwidth rural clinic environments (&lt;100 KB/s).</p>
        </div>
        """, unsafe_allow_html=True)
    with fcol3:
        st.markdown("""
        <div class="vaani-feature-card">
            <div style="font-size:2rem; color:#15803D;">🔒</div>
            <h4>Privacy First</h4>
            <p>Temporary session-based processing. All records are purged after session ends.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # How It Works Workflow
    st.markdown("### **How It Works**")
    wcol1, wcol2, wcol3, wcol4 = st.columns(4)
    with wcol1:
        st.markdown("""
        <div class="vaani-step-card">
            <div class="vaani-step-num">01</div>
            <strong style="color:#172033;">Speak or type</strong>
            <p style="margin:0; font-size:0.85rem; color:#5B667A;">Patient describes symptoms in their own language.</p>
        </div>
        """, unsafe_allow_html=True)
    with wcol2:
        st.markdown("""
        <div class="vaani-step-card">
            <div class="vaani-step-num">02</div>
            <strong style="color:#172033;">VaaniDoc understands</strong>
            <p style="margin:0; font-size:0.85rem; color:#5B667A;">Speech is transcribed preserving original transcript.</p>
        </div>
        """, unsafe_allow_html=True)
    with wcol3:
        st.markdown("""
        <div class="vaani-step-card">
            <div class="vaani-step-num">03</div>
            <strong style="color:#172033;">Clinical intake structured</strong>
            <p style="margin:0; font-size:0.85rem; color:#5B667A;">Key clinical parameters are extracted into English.</p>
        </div>
        """, unsafe_allow_html=True)
    with wcol4:
        st.markdown("""
        <div class="vaani-step-card">
            <div class="vaani-step-num">04</div>
            <strong style="color:#172033;">Doctor reviews</strong>
            <p style="margin:0; font-size:0.85rem; color:#5B667A;">Attending doctor sees organized form & triage level.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 1rem 1.2rem; border-radius: 8px; margin-top: 2.5rem;">
        <strong style="color: #172033;">⚠️ Medical Safety Disclaimer:</strong> 
        <span style="color: #5B667A;">VaaniDoc is a clinical intake and prioritization support prototype. 
        It does not diagnose conditions or replace a healthcare professional.</span>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 2: PATIENT INTAKE PAGE
# ---------------------------------------------------------
def show_patient_intake_page():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="margin:0; color:#172033; font-weight:800;">PATIENT INTAKE</h2>
        <p style="color:#5B667A; margin-top:0.2rem; font-size:1.05rem;">Tell us what you're experiencing.</p>
    </div>
    """, unsafe_allow_html=True)

    # Low-Bandwidth Mode UX Status Indicator
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; border:1px solid #E2E8F0; padding:0.6rem 1rem; border-radius:8px; margin-bottom:1.5rem;">
        <span style="color:#15803D; font-weight:700; font-size:0.9rem;">● Connection: Low bandwidth mode active</span>
        <span style="color:#5B667A; font-size:0.85rem;">Connection is slow. Text input uses less data.</span>
    </div>
    """, unsafe_allow_html=True)

    # Desktop Responsive 40%/60% Split
    col_input, col_output = st.columns([2, 3], gap="large")

    with col_input:
        with st.container(border=True):
            st.markdown("### **STEP 1 — LANGUAGE**")
            
            selected_lang_display = st.selectbox(
                "Select your language:",
                LANGUAGES,
                index=1 # Default Gujarati
            )
            selected_lang = LANG_MAP[selected_lang_display]
            st.session_state["selected_language"] = selected_lang

            st.markdown("---")
            st.markdown("### **STEP 2 — VOICE INPUT**")
            st.markdown("<p style='color:#5B667A; font-size:0.9rem;'>Speak naturally in your preferred language. You don't need to use medical terms.</p>", unsafe_allow_html=True)

            audio_val = st.audio_input("Record symptom description:")

            if audio_val:
                st.success("✓ Recording captured")
                if st.button("⚡ **Process Voice**", key="proc_voice_action", use_container_width=True):
                    with st.spinner("Understanding your response..."):
                        try:
                            audio_bytes = audio_val.read()
                            transcript = transcribe_audio(audio_bytes, language_name=selected_lang)
                            st.session_state["original_transcript"] = transcript

                            intake = extract_clinical_intake(transcript, selected_language=selected_lang)
                            st.session_state["current_intake"] = intake
                            st.success("✓ Clinical intake ready")
                            st.rerun()
                        except Exception as e:
                            st.error("We couldn't process the recording. Please check your connection and try again.")
                            st.caption(f"Error details: {str(e)}")

            st.markdown("---")
            st.markdown("### **OR — PREFER TYPING?**")
            
            placeholder_text = PLACEHOLDER_MAP.get(selected_lang, "Type your symptoms here...")
            text_input = st.text_area(
                "Type your symptoms here:",
                placeholder=placeholder_text,
                height=100
            )

            if st.button("📄 **Process Text**", key="proc_text_action", use_container_width=True):
                if not text_input.strip():
                    st.warning("Please enter your symptoms before processing.")
                else:
                    with st.spinner("Understanding your response..."):
                        try:
                            st.session_state["original_transcript"] = text_input.strip()
                            intake = extract_clinical_intake(text_input.strip(), selected_language=selected_lang)
                            st.session_state["current_intake"] = intake
                            st.success("✓ Clinical intake ready")
                            st.rerun()
                        except Exception as e:
                            st.error(f"We couldn't process your response: {str(e)}")

    with col_output:
        with st.container(border=True):
            st.markdown("### 🩺 **Structured Clinical Intake Output**")

            current_intake = st.session_state.get("current_intake")

            if not current_intake:
                st.info("🎙️ Speak or type your symptoms on the left to generate the structured doctor intake form.")
            else:
                urgency_info = current_intake.get("urgency_info", {})
                urgency_level = urgency_info.get("urgency", "ROUTINE")
                reasons = urgency_info.get("reasons", [])

                # High Contrast Triage Banner
                if urgency_level == "HIGH PRIORITY":
                    st.markdown('<div class="badge-high-v2">🚩 HIGH PRIORITY</div>', unsafe_allow_html=True)
                elif urgency_level == "PRIORITY":
                    st.markdown('<div class="badge-priority-v2">🟡 PRIORITY</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-routine-v2">🟢 ROUTINE</div>', unsafe_allow_html=True)

                if reasons:
                    st.markdown(f"<p style='color:#172033; font-weight:700; margin-top:0.4rem;'>Reasons: {', '.join(reasons)}</p>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # High Contrast Clinical Intake Table
                st.markdown(f"""
                <table style="width:100%; border-collapse:collapse; color:#172033;">
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700; width:35%;">Language</td>
                        <td style="padding:0.6rem 0;">{current_intake.get('language', 'Not specified')}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Chief Complaint</td>
                        <td style="padding:0.6rem 0; font-weight:600; color:#2563EB;">{current_intake.get('chief_complaint', 'Not mentioned')}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">English Summary</td>
                        <td style="padding:0.6rem 0;">{current_intake.get('english_summary', 'Not mentioned')}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Symptoms</td>
                        <td style="padding:0.6rem 0;">{', '.join(current_intake.get('symptoms', [])) or 'None mentioned'}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Duration</td>
                        <td style="padding:0.6rem 0;">{', '.join(current_intake.get('duration', [])) or 'Not specified'}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Severity</td>
                        <td style="padding:0.6rem 0;">{', '.join(current_intake.get('severity', [])) or 'Not specified'}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Medical History</td>
                        <td style="padding:0.6rem 0;">{', '.join(current_intake.get('medical_history', [])) or 'None mentioned'}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Medications</td>
                        <td style="padding:0.6rem 0;">{', '.join(current_intake.get('medications', [])) or 'None mentioned'}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E8F0;">
                        <td style="padding:0.6rem 0; font-weight:700;">Allergies</td>
                        <td style="padding:0.6rem 0;">{', '.join(current_intake.get('allergies', [])) or 'None mentioned'}</td>
                    </tr>
                    <tr>
                        <td style="padding:0.6rem 0; font-weight:700; color:#B91C1C;">Red Flags</td>
                        <td style="padding:0.6rem 0; font-weight:700; color:#B91C1C;">{', '.join(current_intake.get('red_flags', [])) or 'None detected'}</td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### **Original Patient Statement**")
                st.markdown(f"""
                <div class="transcript-box-v3">
                    "{current_intake.get('original_text', '')}"
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="destructive-btn">', unsafe_allow_html=True)
    if st.button("🗑️ **End Session & Delete Data**", key="end_intake_session", use_container_width=True):
        end_session_and_wipe_data()
        go_to_page("Home")
    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 3: DOCTOR VIEW PAGE
# ---------------------------------------------------------
def show_doctor_view_page():
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
        <div>
            <h2 style="margin:0; color:#172033; font-weight:800;">DOCTOR VIEW</h2>
            <p style="color:#5B667A; margin-top:0.2rem; font-size:1rem;">Structured clinical review interface</p>
        </div>
        <span style="background:#0F172A; color:#38BDF8; padding:0.5rem 1.2rem; border-radius:20px; font-weight:800;">
            Session ID: {st.session_state['session_id']} <span style="color:#15803D;">● Live Session</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    current_intake = st.session_state.get("current_intake")

    # Empty State for Doctor View
    if not current_intake:
        st.markdown("""
        <div class="vaani-card-box" style="text-align:center; padding:3rem 2rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🩺</div>
            <h3 style="color:#172033; font-weight:800;">No active clinical intake</h3>
            <p style="color:#5B667A; max-width:500px; margin:0 auto 1.5rem auto;">
                Start a patient intake session to generate the structured clinical intake form for doctor review.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✨ **Start Patient Intake**", key="doctor_empty_start", use_container_width=True):
            go_to_page("Patient Intake")
    else:
        urgency_info = current_intake.get("urgency_info", {})
        urgency = urgency_info.get("urgency", "ROUTINE")

        if urgency == "HIGH PRIORITY":
            st.markdown("""
            <div style="background-color:#FEE2E2; border-left:6px solid #B91C1C; padding:1.2rem; border-radius:10px; margin-bottom:1.5rem;">
                <h3 style="margin:0; color:#991B1B; font-weight:800;">🚩 HIGH PRIORITY — CLINICIAN ATTENTION RECOMMENDED</h3>
                <p style="margin:0.3rem 0 0 0; color:#991B1B;">Potential red-flag symptoms detected in patient statement.</p>
            </div>
            """, unsafe_allow_html=True)

        dcol1, dcol2 = st.columns([2, 1], gap="large")

        with dcol1:
            with st.container(border=True):
                st.markdown("<h3 style='margin-top:0; color:#172033;'>📋 Structured Clinical Intake</h3>", unsafe_allow_html=True)

                kcol1, kcol2 = st.columns(2)
                with kcol1:
                    st.markdown(f"<p><strong>Language:</strong> {current_intake.get('language', 'Not specified')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Chief Complaint:</strong><br><span style='color:#2563EB; font-weight:700;'>{current_intake.get('chief_complaint', 'Not mentioned')}</span></p>", unsafe_allow_html=True)
                    
                    symptoms = current_intake.get("symptoms", [])
                    sym_str = "<br>• ".join(symptoms) if symptoms else "None mentioned"
                    st.markdown(f"<p><strong>Symptoms:</strong><br>• {sym_str}</p>", unsafe_allow_html=True)
                with kcol2:
                    st.markdown(f"<p><strong>Duration:</strong> {', '.join(current_intake.get('duration', [])) or 'Not specified'}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Severity:</strong> {', '.join(current_intake.get('severity', [])) or 'Not specified'}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Medical History:</strong> {', '.join(current_intake.get('medical_history', [])) or 'None mentioned'}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Medications:</strong> {', '.join(current_intake.get('medications', [])) or 'None mentioned'}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Allergies:</strong> {', '.join(current_intake.get('allergies', [])) or 'None mentioned'}</p>", unsafe_allow_html=True)

                st.markdown("<hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#B91C1C; font-weight:800;'><strong>Red Flags Identified:</strong> {', '.join(current_intake.get('red_flags', [])) or 'None detected'}</p>", unsafe_allow_html=True)

        with dcol2:
            with st.container(border=True):
                st.markdown("#### **Triage Screening**")
                if urgency == "HIGH PRIORITY":
                    st.markdown('<div class="badge-high-v2">🚩 HIGH PRIORITY</div>', unsafe_allow_html=True)
                elif urgency == "PRIORITY":
                    st.markdown('<div class="badge-priority-v2">🟡 PRIORITY</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-routine-v2">🟢 ROUTINE</div>', unsafe_allow_html=True)

                reasons = urgency_info.get("reasons", [])
                if reasons:
                    st.markdown("<p style='color:#172033; font-weight:700; margin-top:0.8rem;'>Rationale:</p>", unsafe_allow_html=True)
                    for r in reasons:
                        st.markdown(f"<p style='color:#5B667A; margin-bottom:0.2rem;'>• {r}</p>", unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("#### **Original Patient Statement**")
                st.markdown(f"<p style='color:#5B667A; font-size:0.85rem;'>Language: {current_intake.get('language')}</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="transcript-box-v3">
                    "{current_intake.get('original_text')}"
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="destructive-btn">', unsafe_allow_html=True)
        if st.button("🗑️ **End Session & Delete Data**", key="end_doctor_session", use_container_width=True):
            end_session_and_wipe_data()
            go_to_page("Home")
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# PAGE 4: VALIDATION PAGE
# ---------------------------------------------------------
def show_validation_page():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="margin:0; color:#172033; font-weight:800;">MODEL VALIDATION</h2>
        <p style="color:#5B667A; margin-top:0.2rem; font-size:1.05rem;">
            Evaluate VaaniDoc's clinical information extraction across 20 multilingual test cases.
        </p>
    </div>
    """, unsafe_allow_html=True)

    vcol1, vcol2 = st.columns([1, 1], gap="medium")
    with vcol1:
        run_live = st.button("⚡ **Run Live Groq API Validation**", key="run_val_live_btn", use_container_width=True)
    with vcol2:
        run_fast = st.button("🏃 **Run Fast Rule Engine Check**", key="run_val_fast_btn", use_container_width=True)

    if run_live or run_fast:
        use_api = True if run_live else False
        with st.spinner("Running validation cases..."):
            results_dict = run_validation_suite(use_live_api=use_api)
            st.session_state["validation_results"] = results_dict
            st.success("✓ Validation suite completed successfully!")

    val_res = st.session_state.get("validation_results")

    if val_res:
        st.markdown("### **Summary Metrics**")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Total Test Cases", val_res["total"])
        mcol2.metric("Passed", val_res["passed"])
        mcol3.metric("Failed", val_res["failed"])
        mcol4.metric("Extraction Accuracy", f"{val_res['accuracy']}%")

        st.progress(val_res["accuracy"] / 100.0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### **Test Case Results**")

        table_data = []
        for r in val_res["results"]:
            table_data.append({
                "ID": r["id"],
                "Language": r["language"],
                "Input Statement": r["input"],
                "Expected Urgency": r["expected_urgency"],
                "Actual Urgency": r["actual_urgency"],
                "Status": "✅ PASS" if r["status"] == "PASSED" else "❌ FAIL",
                "Details": r["details"]
            })
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("Click 'Run Live Groq API Validation' or 'Run Fast Rule Engine Check' above to execute the test suite.")


# ---------------------------------------------------------
# TOP-LEVEL PAGE ROUTER
# ---------------------------------------------------------
if st.session_state.get("session_just_ended", False):
    st.session_state["session_just_ended"] = False
    st.markdown("""
    <div class="vaani-card-box" style="border-left:5px solid #15803D; margin-bottom:2rem;">
        <h3 style="color:#15803D; margin-top:0;">✓ SESSION ENDED</h3>
        <ul style="color:#172033; font-weight:600;">
            <li>✓ Audio removed</li>
            <li>✓ Transcript removed</li>
            <li>✓ Clinical intake removed</li>
            <li>✓ Temporary session cleared</li>
        </ul>
        <p style="color:#5B667A;">Your session has ended and no patient information is retained.</p>
    </div>
    """, unsafe_allow_html=True)

if st.session_state["current_page"] == "Home":
    show_home_page()
elif st.session_state["current_page"] == "Patient Intake":
    show_patient_intake_page()
elif st.session_state["current_page"] == "Doctor View":
    show_doctor_view_page()
elif st.session_state["current_page"] == "Validation":
    show_validation_page()
