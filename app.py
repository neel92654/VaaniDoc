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

# Native UI Localization Dictionary for Patient Intake Page
PATIENT_UI_TRANSLATIONS = {
    "Hindi": {
        "title": "👨‍🌾 मरीज पंजीकरण (Patient Intake)",
        "subtitle": "अपनी भाषा में स्वास्थ्य संबंधी समस्याएं बताएं।",
        "step1": "चरण 1 — भाषा चुनें",
        "step2": "चरण 2 — आवाज रिकॉर्ड करें",
        "step2_desc": "अपनी पसंदीदा भाषा में स्पष्ट बोलें। चिकित्सा शब्दों का प्रयोग आवश्यक नहीं है।",
        "record_label": "अपनी समस्या रिकॉर्ड करें (अधिकतम 30 सेकंड):",
        "captured": "✓ आवाज रिकॉर्ड हो गई",
        "process_voice": "⚡ जानकारी प्रोसेस करें",
        "or_type": "या — लिखकर बताएं",
        "type_label": "अपनी समस्या यहां लिखें:",
        "placeholder": "उदाहरण: मुझे दो दिनों से बुखार है और सिर दर्द है।",
        "process_text": "📄 जानकारी प्रोसेस करें",
        "tip": "💡 सलाह: बेहतर सटीकता के लिए शांत स्थान पर स्पष्ट बोलें।",
        "demo_title": "🧪 त्वरित परीक्षण इनपुट",
        "output_title": "🩺 क्लिनिकल इनटेक परिणाम",
        "output_empty": "👈 क्लिनिकल फॉर्म तैयार करने के लिए बाईं ओर आवाज रिकॉर्ड करें या लिखकर बताएं।"
    },
    "Gujarati": {
        "title": "👨‍🌾 દર્દી નોંધણી (Patient Intake)",
        "subtitle": "તમારી તકલીફ તમારી પોતાની ભાષામાં જણાવો.",
        "step1": "પગલું ૧ — ભાષા પસંદ કરો",
        "step2": "પગલું ૨ — અવાજ રેકોર્ડ કરો",
        "step2_desc": "તમારી ભાષામાં સ્પષ્ટ બોલો. તબીબી શબ્દો વાપરવા જરૂરી નથી.",
        "record_label": "તમારી તકલીફ રેકોર્ડ કરો (મહત્તમ ૩૦ સેકન્ડ):",
        "captured": "✓ અવાજ રેકોર્ડ થઈ ગયો",
        "process_voice": "⚡ માહિતી પ્રોસેસ કરો",
        "or_type": "અથવા — લખીને જણાવો",
        "type_label": "તમારી તકલીફ અહીં લખો:",
        "placeholder": "ઉદાહરણ: મને બે દિવસથી તાવ છે અને છાતીમાં દુખાવો થાય છે.",
        "process_text": "📄 માહિતી પ્રોસેસ કરો",
        "tip": "💡 સલાહ: સચોટ પરિણામ માટે શાંત જગ્યાએ સ્પષ્ટ બોલો.",
        "demo_title": "🧪 ઝડપી ડેમો ઇનપુટ",
        "output_title": "🩺 ક્લિનિકલ ઇન્ટેક આઉટપુટ",
        "output_empty": "👈 ડોક્ટર માટે ફોર્મ બનાવવા ડાબી બાજુ અવાજ રેકોર્ડ કરો અથવા લખીને જણાવો."
    },
    "Marathi": {
        "title": "👨‍🌾 रुग्ण नोंदणी (Patient Intake)",
        "subtitle": "तुमच्या भाषेत तुमच्या आरोग्याच्या समस्या सांगा.",
        "step1": "पायरी १ — भाषा निवडा",
        "step2": "पायरी २ — आवाज रेकॉर्ड करा",
        "step2_desc": "तुमच्या भाषेत स्पष्ट बोला. वैद्यकीय शब्द वापरण्याची गरज नाही.",
        "record_label": "तुमची समस्या रेकॉर्ड करा (जास्तीत जास्त ३० सेकंद):",
        "captured": "✓ आवाज रेकॉर्ड झाला",
        "process_voice": "⚡ माहिती प्रोसेस करा",
        "or_type": "किंवा — लिहून सांगा",
        "type_label": "तुमची समस्या येथे लिहा:",
        "placeholder": "उदाहरण: मला दोन दिवसांपासून ताप आहे आणि डोकेदुखी आहे.",
        "process_text": "📄 माहिती प्रोसेस करा",
        "tip": "💡 टीप: चांगल्या अचूकतेसाठी शांत ठिकाणी स्पष्ट बोला.",
        "demo_title": "🧪 जलद चाचणी इनपुट",
        "output_title": "🩺 क्लिनिकल इनटेक आउटपुट",
        "output_empty": "👈 डॉक्टरांसाठी फॉर्म तयार करण्यासाठी डावीकडे आवाज रेकॉर्ड करा किंवा लिहा."
    },
    "Bengali": {
        "title": "👨‍🌾 রোগী নিবন্ধন (Patient Intake)",
        "subtitle": "আপনার নিজের ভাষায় স্বাস্থ্য সমস্যা বলুন।",
        "step1": "ধাপ ১ — ভাষা নির্বাচন করুন",
        "step2": "ধাপ ২ — ভয়েস রেকর্ড করুন",
        "step2_desc": "আপনার ভাষায় স্পষ্টভাবে কথা বলুন। ডাক্তারি শব্দ ব্যবহার করার প্রয়োজন নেই।",
        "record_label": "আপনার লক্ষণ রেকর্ড করুন (সর্বোচ্চ ৩০ সেকেন্ড):",
        "captured": "✓ ভয়েস রেকর্ড করা হয়েছে",
        "process_voice": "⚡ তথ্য প্রসেস করুন",
        "or_type": "অথবা — লিখে জানান",
        "type_label": "আপনার লক্ষণ এখানে লিখুন:",
        "placeholder": "উদাহরণ: আমার দুই দিন ধরে জ্বর এবং মাথা ব্যথা করছে।",
        "process_text": "📄 তথ্য প্রসেস করুন",
        "tip": "💡 পরামর্শ: সঠিক ফলাফলের জন্য স্পষ্টভাবে কথা বলুন।",
        "demo_title": "🧪 দ্রুত ডেমো ইনপুট",
        "output_title": "🩺 ক্লিনিক্যাল ইনটেক আউটপুট",
        "output_empty": "👈 ডাক্তারের ফর্ম তৈরি করতে বাম দিকে ভয়েস রেকর্ড করুন বা লিখুন।"
    },
    "Tamil": {
        "title": "👨‍🌾 நோயாளி சேர்க்கை (Patient Intake)",
        "subtitle": "உங்கள் சொந்த மொழியில் உங்கள் அறிகுறிகளைப் பேசுங்கள்.",
        "step1": "படி 1 — மொழியைத் தேர்ந்தெடுக்கவும்",
        "step2": "படி 2 — குரலைப் பதிவுசெய்க",
        "step2_desc": "தெளிவாகப் பேசுங்கள். மருத்துவச் சொற்களைப் பயன்படுத்த வேண்டிய அவசியமில்லை.",
        "record_label": "உங்கள் அறிகுறிகளைப் பதிவுசெய்யவும் (அதிகபட்சம் 30 வினாடிகள்):",
        "captured": "✓ குரல் பதிவு செய்யப்பட்டது",
        "process_voice": "⚡ செயலாக்கு",
        "or_type": "அல்லது — தட்டச்சு செய்க",
        "type_label": "உங்கள் அறிகுறிகளை இங்கே தட்டச்சு செய்க:",
        "placeholder": "உதாரணம்: எனக்கு இரண்டு நாட்களாக காய்ச்சல் மற்றும் தலைவலி உள்ளது.",
        "process_text": "📄 செயலாக்கு",
        "tip": "💡 உதவிக்குறிப்பு: துல்லியமான முடிவுகளுக்கு தெளிவாகப் பேசுங்கள்.",
        "demo_title": "🧪 மாதிரி உள்ளீடு",
        "output_title": "🩺 மருத்துவ அறிக்கை",
        "output_empty": "👈 இடதுபுறத்தில் குரலைப் பதிவுசெய்யவும் அல்லது தட்டச்சு செய்யவும்."
    },
    "Telugu": {
        "title": "👨‍🌾 రోగి వివరాలు (Patient Intake)",
        "subtitle": "మీ స్వంత భాషలో మీ ఆరోగ్య సమస్యలను చెప్పండి.",
        "step1": "దశ 1 — భాషను ఎంచుకోండి",
        "step2": "దశ 2 — వాయిస్ రికార్డ్ చేయండి",
        "step2_desc": "స్పష్టంగా మాట్లాడండి. వైద్య పదాలను ఉపయోగించాల్సిన అవసరం లేదు.",
        "record_label": "మీ లక్షణాలను రికార్డ్ చేయండి (గరిష్టంగా 30 సెకన్లు):",
        "captured": "✓ వాయిస్ రికార్డ్ చేయబడింది",
        "process_voice": "⚡ వివరాలను ప్రాసెస్ చేయండి",
        "or_type": "లేదా — టైప్ చేయండి",
        "type_label": "మీ లక్షణాలను ఇక్కడ టైప్ చేయండి:",
        "placeholder": "ఉదాహరణ: నాకు రెండు రోజులుగా జ్వరం మరియు తలనొప్పి ఉంది.",
        "process_text": "📄 వివరాలను ప్రాసెస్ చేయండి",
        "tip": "💡 చిట్కా: మెరుగైన కచ్చితత్వం కోసం స్పష్టంగా మాట్లాడండి.",
        "demo_title": "🧪 శీఘ్ర డెమో",
        "output_title": "🩺 క్లినికల్ అవుట్‌పుట్",
        "output_empty": "👈 డాక్టర్ ఫారమ్ కోసం ఎడమ వైపున రికార్డ్ చేయండి లేదా టైప్ చేయండి."
    },
    "Kannada": {
        "title": "👨‍🌾 ರೋಗಿ ನೋಂದಣಿ (Patient Intake)",
        "subtitle": "ನಿಮ್ಮ ಸ್ವಂತ ಭಾಷೆಯಲ್ಲಿ ನಿಮ್ಮ ಆರೋಗ್ಯ ತೊಂದರೆಗಳನ್ನು ತಿಳಿಸಿ.",
        "step1": "ಹಂತ 1 — ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "step2": "ಹಂತ 2 — ಧ್ವನಿ ಧ್ವನಿಮುದ್ರಿಸಿ",
        "step2_desc": "ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ. ವೈದ್ಯಕೀಯ ಪದಗಳನ್ನು ಬಳಸುವ ಅಗತ್ಯವಿಲ್ಲ.",
        "record_label": "ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ಧ್ವನಿಮುದ್ರಿಸಿ (ಗರಿಷ್ಠ 30 ಸೆಕೆಂಡುಗಳು):",
        "captured": "✓ ಧ್ವನಿಮುದ್ರಣ ಯಶಸ್ವಿಯಾಗಿದೆ",
        "process_voice": "⚡ ಮಾಹಿತಿ ಸಂಸ್ಕರಿಸಿ",
        "or_type": "ಅಥವಾ — ಟೈಪ್ ಮಾಡಿ",
        "type_label": "ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ:",
        "placeholder": "ಉದಾಹರಣೆಗೆ: ನನಗೆ ಎರಡು ದಿನಗಳಿಂದ ಜ್ವರ ಮತ್ತು ತಲೆನೋವು ಇದೆ.",
        "process_text": "📄 ಮಾಹಿತಿ ಸಂಸ್ಕರಿಸಿ",
        "tip": "💡 ಸಲಹೆ: ನಿಖರ ಫಲಿತಾಂಶಗಳಿಗಾಗಿ ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ.",
        "demo_title": "🧪 ತ್ವರಿತ ಡೆಮೊ",
        "output_title": "🩺 ಕ್ಲಿನಿಕಲ್ ಔಟ್‌ಪುಟ್",
        "output_empty": "👈 ವೈದ್ಯರ ಫಾರ್ಮ್‌ಗಾಗಿ ಎಡಭಾಗದಲ್ಲಿ ಧ್ವನಿಮುದ್ರಿಸಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ."
    },
    "Malayalam": {
        "title": "👨‍🌾 രോഗി വിവരങ്ങൾ (Patient Intake)",
        "subtitle": "നിങ്ങളുടെ സ്വന്തം ഭാഷയിൽ ആരോഗ്യ പ്രശ്നങ്ങൾ പറയുക.",
        "step1": "ഘട്ടം 1 — ഭാഷ തിരഞ്ഞെടുക്കുക",
        "step2": "ഘട്ടം 2 — ശബ്ദം റെക്കോർഡ് ചെയ്യുക",
        "step2_desc": "വ്യക്തമായി സംസാരിക്കുക. മെഡിക്കൽ വാക്കുകൾ ഉപയോഗിക്കേണ്ടതില്ല.",
        "record_label": "ലക്ഷണങ്ങൾ റെക്കോർഡ് ചെയ്യുക (പരമാവധി 30 സെക്കൻഡ്):",
        "captured": "✓ ശബ്ദം റെക്കോർഡ് ചെയ്തു",
        "process_voice": "⚡ പ്രോസസ്സ് ചെയ്യുക",
        "or_type": "അല്ലെങ്കിൽ — ടൈപ്പ് ചെയ്യുക",
        "type_label": "ലക്ഷണങ്ങൾ ഇവിടെ ടൈപ്പ് ചെയ്യുക:",
        "placeholder": "ഉദാഹരണം: എനിക്ക് രണ്ടു ദിവസമായി പനിയും തലവേദനയും ഉണ്ട്.",
        "process_text": "📄 പ്രോസസ്സ് ചെയ്യുക",
        "tip": "💡 കുറിപ്പ്: മികച്ച ഫലത്തിനായി വ്യക്തമായി സംസാരിക്കുക.",
        "demo_title": "🧪 ഡെമോ ഇൻപുട്ട്",
        "output_title": "🩺 ക്ലിനിക്കൽ റിപ്പോർട്ട്",
        "output_empty": "👈 ഡോക്ടർ ഫോമിനായി ഇടതുവശത്ത് റെക്കോർഡ് ചെയ്യുക അല്ലെങ്കിൽ ടൈപ്പ് ചെയ്യുക."
    },
    "Punjabi": {
        "title": "👨‍🌾 ਮਰੀਜ਼ ਰਜਿਸਟ੍ਰੇਸ਼ਨ (Patient Intake)",
        "subtitle": "ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਆਪਣੀਆਂ ਸਿਹਤ ਸਮੱਸਿਆਵਾਂ ਦੱਸੋ।",
        "step1": "ਕਦਮ 1 — ਭਾਸ਼ਾ ਚੁਣੋ",
        "step2": "ਕਦਮ 2 — ਆਵਾਜ਼ ਰਿਕਾਰਡ ਕਰੋ",
        "step2_desc": "ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਸਾਫ਼ ਬੋਲੋ। ਡਾਕਟਰੀ ਸ਼ਬਦਾਂ ਦੀ ਲੋੜ ਨਹੀਂ ਹੈ।",
        "record_label": "ਆਪਣੇ ਲੱਛਣ ਰਿਕਾਰਡ ਕਰੋ (ਵੱਧ ਤੋਂ ਵੱਧ 30 ਸਕਿੰਟ):",
        "captured": "✓ ਆਵਾਜ਼ ਰਿਕਾਰਡ ਹੋ ਗਈ",
        "process_voice": "⚡ ਜਾਣਕਾਰੀ ਪ੍ਰੋਸੈਸ ਕਰੋ",
        "or_type": "ਜਾਂ — ਲਿਖ ਕੇ ਦੱਸੋ",
        "type_label": "ਆਪਣੇ ਲੱਛਣ ਇੱਥੇ ਲਿਖੋ:",
        "placeholder": "ਉਦਾਹਰਨ: ਮੈਨੂੰ ਦੋ ਦਿਨਾਂ ਤੋਂ ਬੁਖਾਰ ਅਤੇ ਸਿਰ ਦਰਦ ਹੈ।",
        "process_text": "📄 ਜਾਣਕਾਰੀ ਪ੍ਰੋਸੈਸ ਕਰੋ",
        "tip": "💡 ਸੁਝਾਅ: ਵਧੀਆ ਨਤੀਜਿਆਂ ਲਈ ਸਾਫ਼ ਬੋਲੋ।",
        "demo_title": "🧪 ਤੁਰੰਤ ਟੈਸਟ ਇਨਪੁਟ",
        "output_title": "🩺 ਕਲੀਨਿਕਲ ਇਨਟੇਕ",
        "output_empty": "👈 ਡਾਕਟਰ ਦੇ ਫਾਰਮ ਲਈ ਖੱਬੇ ਪਾਸੇ ਆਵਾਜ਼ ਰਿਕਾਰਡ ਕਰੋ ਜਾਂ ਲਿਖੋ।"
    },
    "Odia": {
        "title": "👨‍🌾 ରୋଗୀ ପଞ୍ଜୀକରଣ (Patient Intake)",
        "subtitle": "ଆପଣଙ୍କ ନିଜ ଭାଷାରେ ସ୍ୱାସ୍ଥ୍ୟ ସମସ୍ୟା କୁହନ୍ତୁ।",
        "step1": "ପଦକ୍ଷେପ ୧ — ଭାଷା ବାଛନ୍ତୁ",
        "step2": "ପଦକ୍ଷେପ ୨ — ସ୍ୱର ରେକର୍ଡ କରନ୍ତୁ",
        "step2_desc": "ସ୍ପଷ୍ଟ ଭାବରେ କୁହନ୍ତୁ। ଡାକ୍ତରୀ ଶବ୍ଦ ବ୍ୟବହାର କରିବା ଆବଶ୍ୟକ ନାହିଁ।",
        "record_label": "ଆପଣଙ୍କ ଲକ୍ଷଣ ରେକର୍ଡ କରନ୍ତୁ (ସର୍ବାଧିକ ୩୦ ସେକେଣ୍ଡ):",
        "captured": "✓ ସ୍ୱର ରେକର୍ଡ ହେଲା",
        "process_voice": "⚡ ସୂଚନା ପ୍ରୋସେସ୍ କରନ୍ତୁ",
        "or_type": "କିମ୍ବା — ଲେଖି ଜଣାନ୍ତୁ",
        "type_label": "ଆପଣଙ୍କ ଲକ୍ଷଣ ଏଠାରେ ଲେଖନ୍ତୁ:",
        "placeholder": "ଉଦାହରଣ: ମୋତେ ଦୁଇ ଦିନ ହେବ ଜ୍ୱର ଏବଂ ମୁଣ୍ଡ ବିନ୍ଧା ହେଉଛି।",
        "process_text": "📄 ସୂଚନା ପ୍ରୋସେସ୍ କରନ୍ତୁ",
        "tip": "💡 ପରାମର୍ଶ: ସଠିକ୍ ଫଳାଫଳ ପାଇଁ ସ୍ପଷ୍ଟ ଭାବରେ କୁହନ୍ତୁ।",
        "demo_title": "🧪 ଡେମୋ ଇନପୁଟ୍",
        "output_title": "🩺 କ୍ଲିନିକାଲ୍ ଫର୍ମ",
        "output_empty": "👈 ଡାକ୍ତର ଫର୍ମ ପାଇଁ ବାମ ପାଖରେ ସ୍ୱର ରେକର୍ଡ କରନ୍ତୁ କିମ୍ବା ଲେଖନ୍ତୁ।"
    },
    "English": {
        "title": "👨‍🌾 Patient Intake",
        "subtitle": "Describe your symptoms naturally in your language.",
        "step1": "STEP 1 — LANGUAGE",
        "step2": "STEP 2 — VOICE INPUT",
        "step2_desc": "Speak naturally in your preferred language. Medical terms are not required.",
        "record_label": "Record symptom description (max 30 sec):",
        "captured": "✓ Recording captured",
        "process_voice": "⚡ Process Input",
        "or_type": "OR — PREFER TYPING?",
        "type_label": "Type your symptoms here:",
        "placeholder": "Example: I've had fever for two days and a severe headache.",
        "process_text": "📄 Process Input",
        "tip": "💡 Tip: Speak clearly in a quiet area for better accuracy.",
        "demo_title": "🧪 Quick Demo Test Inputs",
        "output_title": "🩺 Structured Clinical Intake Output",
        "output_empty": "👈 Record voice or enter text on the left to generate structured clinical intake."
    }
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
# PAGE 2: PATIENT INTAKE PAGE (NATIVE REGIONAL LOCALIZATION)
# ---------------------------------------------------------
def show_patient_intake_page():
    # Step 1: Detect selected language first to localize entire page
    current_selected_display = st.session_state.get("selected_lang_display", LANGUAGES[1])
    current_lang = LANG_MAP.get(current_selected_display, "Gujarati")
    
    # Retrieve Regional UI Translations
    t = PATIENT_UI_TRANSLATIONS.get(current_lang, PATIENT_UI_TRANSLATIONS["English"])

    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <h2 style="margin:0; color:#172033; font-weight:800;">{t['title']}</h2>
        <p style="color:#5B667A; margin-top:0.2rem; font-size:1.05rem;">{t['subtitle']}</p>
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
            st.markdown(f"### **{t['step1']}**")
            
            selected_lang_display = st.selectbox(
                "Select language / ભાષા પસંદ કરો / भाषा चुनें:",
                LANGUAGES,
                index=LANGUAGES.index(current_selected_display) if current_selected_display in LANGUAGES else 1,
                key="selected_lang_display"
            )
            selected_lang = LANG_MAP[selected_lang_display]
            st.session_state["selected_language"] = selected_lang

            # Update localized text if user changes language dropdown
            t = PATIENT_UI_TRANSLATIONS.get(selected_lang, PATIENT_UI_TRANSLATIONS["English"])

            st.markdown("---")
            st.markdown(f"### **{t['step2']}**")
            st.markdown(f"<p style='color:#5B667A; font-size:0.9rem;'>{t['step2_desc']}</p>", unsafe_allow_html=True)

            audio_val = st.audio_input(t['record_label'])

            if audio_val:
                st.success(t['captured'])
                if st.button(t['process_voice'], key="proc_voice_action", use_container_width=True):
                    with st.spinner("Processing audio with Groq Whisper..."):
                        try:
                            audio_bytes = audio_val.read()
                            transcript = transcribe_audio(audio_bytes, language_name=selected_lang)
                            st.session_state["original_transcript"] = transcript

                            intake = extract_clinical_intake(transcript, selected_language=selected_lang)
                            st.session_state["current_intake"] = intake
                            
                            # REQUIREMENT 2: Auto-navigate to Doctor View on successful processing
                            go_to_page("Doctor View")
                        except Exception as e:
                            st.error("We couldn't process the recording. Please check your connection and try again.")
                            st.caption(f"Error details: {str(e)}")

            st.markdown("---")
            st.markdown(f"### **{t['or_type']}**")
            
            text_input = st.text_area(
                t['type_label'],
                placeholder=t['placeholder'],
                height=100
            )

            if st.button(t['process_text'], key="proc_text_action", use_container_width=True):
                if not text_input.strip():
                    st.warning("Please enter your symptoms before processing.")
                else:
                    with st.spinner("Processing symptoms..."):
                        try:
                            st.session_state["original_transcript"] = text_input.strip()
                            intake = extract_clinical_intake(text_input.strip(), selected_language=selected_lang)
                            st.session_state["current_intake"] = intake
                            
                            # REQUIREMENT 2: Auto-navigate to Doctor View on successful processing
                            go_to_page("Doctor View")
                        except Exception as e:
                            st.error(f"We couldn't process your response: {str(e)}")

            st.markdown("---")
            st.markdown(f"#### **{t['demo_title']}**")
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                if st.button("Gujarati Demo (Chest Pain)", key="guj_demo_btn", use_container_width=True):
                    sample = "મને બે દિવસથી તાવ છે અને છાતીમાં દુખાવો થાય છે."
                    st.session_state["original_transcript"] = sample
                    with st.spinner("Processing Gujarati demo..."):
                        intake = extract_clinical_intake(sample, selected_language="Gujarati")
                        st.session_state["current_intake"] = intake
                        go_to_page("Doctor View")
            with dcol2:
                if st.button("Hindi Demo (Stomach Pain)", key="hin_demo_btn", use_container_width=True):
                    sample = "मुझे कल से पेट में बहुत दर्द हो रहा है।"
                    st.session_state["original_transcript"] = sample
                    with st.spinner("Processing Hindi demo..."):
                        intake = extract_clinical_intake(sample, selected_language="Hindi")
                        st.session_state["current_intake"] = intake
                        go_to_page("Doctor View")

    with col_output:
        with st.container(border=True):
            st.markdown(f"### **{t['output_title']}**")

            current_intake = st.session_state.get("current_intake")

            if not current_intake:
                st.info(t['output_empty'])
            else:
                urgency_info = current_intake.get("urgency_info", {})
                urgency_level = urgency_info.get("urgency", "ROUTINE")
                reasons = urgency_info.get("reasons", [])

                if urgency_level == "HIGH PRIORITY":
                    st.markdown('<div class="badge-high-v2">🚩 HIGH PRIORITY</div>', unsafe_allow_html=True)
                elif urgency_level == "PRIORITY":
                    st.markdown('<div class="badge-priority-v2">🟡 PRIORITY</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-routine-v2">🟢 ROUTINE</div>', unsafe_allow_html=True)

                if reasons:
                    st.markdown(f"<p style='color:#172033; font-weight:700; margin-top:0.4rem;'>Reasons: {', '.join(reasons)}</p>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

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
