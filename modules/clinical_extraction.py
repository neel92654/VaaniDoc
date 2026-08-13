import os
import json
import re
import streamlit as st
from groq import Groq
from modules.urgency import evaluate_urgency

SYSTEM_PROMPT = """You are a multilingual clinical intake processing AI for rural health clinics in India.
Your task is to convert patient symptom descriptions provided in any Indian regional language or English into a structured English clinical intake form for an attending doctor.

STRICT SAFETY & CLINICAL RULES:
1. NEVER diagnose diseases or conditions (e.g. DO NOT say 'patient has typhoid', 'likely COVID-19', 'suffering from malaria').
2. NEVER recommend treatments, suggest tests, or prescribe medications.
3. NEVER invent or assume symptoms, duration, medical history, medications, or allergies that the patient did NOT mention. If absent, set field to empty list [] or "Not specified".
4. Extract ONLY information explicitly stated or directly supported by the patient's statement.
5. Translate the clinical concepts into clear, professional English.
6. Identify potentially urgent / red-flag symptoms explicitly stated by the patient (e.g., chest pain, breathing difficulty, severe bleeding, sudden weakness, unconsciousness).
7. Return output strictly as valid JSON adhering to the target schema. No conversational filler, no markdown intros.

TARGET JSON SCHEMA:
{
  "language": "Language of the patient input",
  "original_text": "Exact original patient transcript",
  "english_summary": "Concise 1-2 sentence English translation/summary of patient statement",
  "chief_complaint": "Main reason for intake in English (e.g. Fever with chest pain)",
  "symptoms": ["List of extracted symptoms in English"],
  "duration": ["List of duration indicators mentioned, e.g. '2 days', 'since yesterday'"],
  "severity": ["List of severity descriptors if mentioned, e.g. 'severe', 'mild', 'unbearable'"],
  "body_locations": ["Body parts affected if mentioned, e.g. 'chest', 'stomach', 'leg'"],
  "medical_history": ["Past medical conditions explicitly mentioned"],
  "medications": ["Current medications explicitly mentioned"],
  "allergies": ["Allergies explicitly mentioned"],
  "red_flags": ["List of urgent red-flag symptoms identified from the statement"],
  "missing_information": ["Key intake details not mentioned, e.g. 'duration not specified'"]
}
"""

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Set GROQ_API_KEY in .env or Streamlit Secrets.")
        
    return Groq(api_key=api_key)

def clean_json_response(raw_response: str) -> str:
    """Removes markdown code fence blocks from LLM output."""
    raw = raw_response.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()

def extract_clinical_intake(patient_text: str, selected_language: str = "Hindi") -> dict:
    """
    Sends patient description to Groq LLM and retrieves structured English clinical intake JSON.
    Augments the extracted intake with rule-based urgency screening.
    """
    if not patient_text or not patient_text.strip():
        raise ValueError("Patient text is empty. Please provide a symptom description.")

    client = get_groq_client()
    
    user_prompt = f"""
    Selected Language Context: {selected_language}
    Patient Statement: "{patient_text}"
    
    Extract structured clinical intake JSON strictly adhering to instructions and schema.
    """

    # We try llama-3.3-70b-versatile first, with fallback to llama-3.1-8b-instant
    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    last_error = None
    extracted_json = None

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            cleaned = clean_json_response(content)
            extracted_json = json.loads(cleaned)
            break
        except Exception as e:
            last_error = e
            continue

    if not extracted_json:
        raise RuntimeError(f"Clinical extraction failed: {str(last_error)}")

    # Ensure required default keys exist
    extracted_json["original_text"] = patient_text
    if "language" not in extracted_json or not extracted_json["language"]:
        extracted_json["language"] = selected_language
        
    for key in ["symptoms", "duration", "severity", "body_locations", "medical_history", "medications", "allergies", "red_flags", "missing_information"]:
        if key not in extracted_json or extracted_json[key] is None:
            extracted_json[key] = []
        elif isinstance(extracted_json[key], str):
            extracted_json[key] = [extracted_json[key]]

    # 4. Integrate transparent Rule-based Urgency Engine
    urgency_info = evaluate_urgency(extracted_json)
    extracted_json["urgency_info"] = urgency_info

    return extracted_json
