"""
Transparent, Python rule-based urgency & red-flag screening engine.
Does NOT diagnose diseases. Evaluates symptoms and red flags for clinical intake triage priority.
"""

# Red-flag keywords triggering HIGH PRIORITY (Red)
HIGH_PRIORITY_KEYWORDS = [
    "chest pain", "chest pressure", "radiating to left arm", "arm pain", 
    "breathing difficulty", "shortness of breath", "unable to breathe", "gasping",
    "unconscious", "unconsciousness", "fainted", "blackout", "passed out",
    "severe bleeding", "heavy bleeding", "coughing blood", "blood in vomit",
    "sudden weakness", "paralysis", "slurred speech", "stroke",
    "seizure", "convulsions", "fits",
    "anaphylaxis", "severe allergic reaction", "throat swelling",
    "stiff neck", "high fever with delirium"
]

# Symptoms triggering PRIORITY (Yellow)
PRIORITY_KEYWORDS = [
    "severe stomach pain", "severe abdominal pain", "intense abdominal pain", "abdominal pain", "stomach pain",
    "vomiting", "persistent vomiting", "cannot keep fluids down",
    "severe headache", "dizziness", "vertigo",
    "high fever", "fever for 3 days", "fever for 4 days", "fever for 5 days",
    "dehydration", "extreme fatigue", "unable to walk"
]

def evaluate_urgency(extracted_data: dict) -> dict:
    """
    Evaluates extracted clinical data against safety screening rules.
    Returns urgency level: ROUTINE (🟢), PRIORITY (🟡), or HIGH PRIORITY (🔴), along with reasons and exact palette color hexes.
    """
    reasons = []
    
    # 1. Check explicit red flags reported by LLM extraction or text match
    red_flags = extracted_data.get("red_flags", [])
    if isinstance(red_flags, list):
        for rf in red_flags:
            if rf and isinstance(rf, str):
                reasons.append(f"Red flag detected: {rf}")

    # Combine symptoms, chief complaint, and severity into searchable text
    chief_complaint = str(extracted_data.get("chief_complaint", "")).lower()
    symptoms_list = extracted_data.get("symptoms", [])
    symptoms_text = " ".join([str(s).lower() for s in symptoms_list]) if isinstance(symptoms_list, list) else str(symptoms_list).lower()
    severity_text = " ".join([str(s).lower() for s in extracted_data.get("severity", [])]) if isinstance(extracted_data.get("severity"), list) else str(extracted_data.get("severity", "")).lower()
    
    combined_text = f"{chief_complaint} {symptoms_text} {severity_text}"

    # 2. Check for High Priority (Red #EF4444) matches
    high_priority_detected = False
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in combined_text:
            high_priority_detected = True
            reasons.append(f"High-priority symptom detected: '{kw.title()}'")

    if high_priority_detected or len(red_flags) > 0:
        return {
            "urgency": "HIGH PRIORITY",
            "level_code": "HIGH",
            "icon": "🔴",
            "color_hex": "#EF4444",
            "bg_hex": "#FEE2E2",
            "reasons": list(set(reasons)) if reasons else ["High priority symptoms detected"]
        }

    # 3. Check for Priority (Yellow #F59E0B) matches
    priority_detected = False
    for kw in PRIORITY_KEYWORDS:
        if kw in combined_text:
            priority_detected = True
            reasons.append(f"Priority symptom detected: '{kw.title()}'")

    if priority_detected:
        return {
            "urgency": "PRIORITY",
            "level_code": "PRIORITY",
            "icon": "🟡",
            "color_hex": "#F59E0B",
            "bg_hex": "#FEF3C7",
            "reasons": list(set(reasons))
        }

    # 4. Default Routine (Green #10B981)
    return {
        "urgency": "ROUTINE",
        "level_code": "ROUTINE",
        "icon": "🟢",
        "color_hex": "#10B981",
        "bg_hex": "#D1FAE5",
        "reasons": ["Standard clinical intake - no red flags or high-priority symptoms detected"]
    }
