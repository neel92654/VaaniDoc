# VaaniDoc 🏥

**Multilingual AI Health Intake System for Rural & Semi-Urban Clinics**  
*Hack Orbit 2026 — Track 2, PS-03 Prototype*

---

## 📌 Problem Statement
In rural and semi-urban clinics across India, healthcare providers face severe linguistic and operational barriers:
- Patients describe complex health symptoms in diverse regional languages and dialects.
- Rural doctors often struggle with language translation delays, leading to inaccurate medical histories and missed red-flag symptoms.
- Network connectivity in rural primary health centers (PHCs) is unstable (<100 KB/s bandwidth).
- Strict patient privacy regulations demand zero permanent logging of sensitive health descriptions.

---

## 🚀 The Solution: VaaniDoc
**VaaniDoc** is a lightweight, mobile-first Streamlit web application that converts a patient's natural voice or text description in **10 Indian regional languages** into a structured, standardized **English clinical intake form** for attending doctors.

> **Voice / Text (Regional Language) ➡️ Groq STT & LLM ➡️ Structured Clinical Intake (English) ➡️ Urgency Triage ➡️ Doctor View**

*Note: VaaniDoc strictly functions as an intake & triage-support tool. It explicitly avoids medical diagnosis, disease predictions, treatment recommendations, or prescribing medication.*

---

## ✨ Key Features

1. **Multilingual Regional Voice Support**: Supports 10 Indian languages (Hindi, Gujarati, Marathi, Bengali, Tamil, Telugu, Kannada, Malayalam, Punjabi, Odia) plus English.
2. **Native Browser Audio Recording**: Built-in `st.audio_input()` for live voice recording directly from mobile or desktop browsers.
3. **Groq-Powered Whisper STT**: Fast speech-to-text using `whisper-large-v3-turbo` preserving the exact original regional transcript.
4. **Structured Clinical JSON Extraction**: Converts natural conversational statements into chief complaints, symptoms, duration, severity, body location, medical history, medications, allergies, and red flags.
5. **Rule-Based Urgency Engine**: Transparent 3-level triage screening (🟢 ROUTINE, 🟡 PRIORITY, 🔴 HIGH PRIORITY) detecting critical red-flag signals like chest pain, breathing difficulty, or severe bleeding.
6. **Low-Bandwidth (<100 KB/s) Optimization**: Payload optimization and low-bandwidth text input fallback for weak rural connections.
7. **Privacy-First Zero Retention**: One-click **"End Session & Delete Data"** completely wipes audio buffers, transcripts, and intake data from memory. Zero disk/database logging.
8. **Attending Doctor View**: Real-time structured summary view for clinicians displaying red flags and original patient statements.
9. **Automated 20-Test Validation Suite**: In-app evaluation page measuring accuracy against 20 benchmark Indian language symptom cases.

---

## 🏗️ Technology Stack

- **Frontend & App Framework**: Streamlit (Python)
- **Speech-to-Text (STT)**: Groq API — `whisper-large-v3-turbo`
- **Clinical Extraction (LLM)**: Groq API — `llama-3.3-70b-versatile` / `llama-3.1-8b-instant`
- **Triage Engine**: Python transparent rule-based screening engine
- **State Management**: Streamlit Ephemeral Session State (Zero DB)

---

## 📂 Project Structure

```
VaaniDoc/
├── app.py                      # Main Streamlit application & layout
├── requirements.txt            # Minimal dependencies
├── README.md                   # Complete documentation
├── .env.example                # Environment variable template
├── .gitignore                  # Git exclusion rules
│
├── modules/
│   ├── speech.py               # Groq Whisper speech-to-text module
│   ├── clinical_extraction.py # Groq LLM clinical JSON extraction module
│   ├── urgency.py              # Rule-based urgency & red-flag triage engine
│   ├── session_manager.py      # Session ID & zero-trace data deletion logic
│   └── validation.py           # 20 test case validation suite engine
│
└── data/
    └── test_cases.json         # 20 Indian language benchmark test cases
```

---

## 🌐 Supported Languages

| Language | Native Name | ISO Code | Voice STT | LLM Extraction |
| :--- | :--- | :---: | :---: | :---: |
| **Hindi** | हिंदी | `hi` | ✅ | ✅ |
| **Gujarati** | ગુજરાતી | `gu` | ✅ | ✅ |
| **Marathi** | मराठी | `mr` | ✅ | ✅ |
| **Bengali** | বাংলা | `bn` | ✅ | ✅ |
| **Tamil** | தமிழ் | `ta` | ✅ | ✅ |
| **Telugu** | తెలుగు | `te` | ✅ | ✅ |
| **Kannada** | ಕನ್ನಡ | `kn` | ✅ | ✅ |
| **Malayalam** | മലയാളം | `ml` | ✅ | ✅ |
| **Punjabi** | ਪੰਜਾਬੀ | `pa` | ✅ | ✅ |
| **Odia** | ଓଡ଼ିଆ | `or` | ✅ | ✅ |
| **English** | English | `en` | ✅ | ✅ |

---

## ⚡ Low-Bandwidth Strategy (<100 KB/s)

To guarantee operation in low-connectivity rural health centers:
1. **Short Audio Clips**: Micro-recordings under 30 seconds sampled at 16 kHz.
2. **Text Input Fallback**: Instant switch to lightweight text payload mode if audio uploads fail due to network instability.
3. **No Heavy JS/Assets**: Ultra-clean Streamlit UI without heavy video or external font frameworks.

---

## 🔒 Privacy Architecture

- **No Permanent Database**: VaaniDoc intentionally omits SQL/NoSQL databases.
- **In-Memory Session State Only**: All patient records exist temporarily in `st.session_state` tied to a short-lived Session ID (e.g. `VD-4821`).
- **One-Click Wipe**: Clicking `End Session & Delete Data` executes `session_manager.end_session_and_wipe_data()`, completely purging memory.
- **Zero Log Leakage**: Console logs record technical request status only, never patient transcript or symptom content.

---

## ⚙️ Local Setup Instructions

### 1. Prerequisites
- Python 3.11 or higher installed.
- A free **Groq API Key** from [Groq Console](https://console.groq.com/).

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/VaaniDoc.git
cd VaaniDoc

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Add your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 4. Run Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

1. Push your repository to GitHub.
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** and select your `VaaniDoc` repo and `app.py` as main file path.
4. Under **Advanced settings -> Secrets**, add your Groq key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
   ```
5. Click **Deploy!**

---

## 📊 Validation & Benchmark Suite

VaaniDoc includes an automated validation page testing 20 Indian language symptom statements against ground-truth clinical extractions:
- Measures symptom extraction recall and urgency triage accuracy.
- Dynamically updates sidebar metrics (e.g., **95% Accuracy, 19/20 Passed**).

To run validation within the app, navigate to **Validation** in the sidebar and click **Run Live Validation**.

---

## ⚠️ Medical Safety Disclaimer

> **VaaniDoc does NOT provide medical diagnosis, disease predictions, treatment advice, or drug prescriptions.**  
> It is strictly designed as an intake assistant and triage screening tool to help attending healthcare professionals understand patient descriptions faster.

---

## 📄 License
Licensed under the [MIT License](LICENSE). Developed for Hack Orbit 2026.
