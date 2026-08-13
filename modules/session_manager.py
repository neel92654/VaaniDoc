import random
import streamlit as st

def generate_session_id() -> str:
    """Generate a clean temporary session ID like VD-A7F21C."""
    chars = "ABCDEF0123456789"
    suffix = "".join(random.choices(chars, k=6))
    return f"VD-{suffix}"

def init_session_state():
    """Ensure all required session state variables exist cleanly."""
    if "session_id" not in st.session_state or not st.session_state["session_id"]:
        st.session_state["session_id"] = generate_session_id()

    if "current_intake" not in st.session_state:
        st.session_state["current_intake"] = None

    if "original_transcript" not in st.session_state:
        st.session_state["original_transcript"] = None

    if "selected_language" not in st.session_state:
        st.session_state["selected_language"] = "Hindi"

    if "low_bandwidth_mode" not in st.session_state:
        st.session_state["low_bandwidth_mode"] = False

    if "validation_results" not in st.session_state:
        st.session_state["validation_results"] = None

    if "session_just_ended" not in st.session_state:
        st.session_state["session_just_ended"] = False

def end_session_and_wipe_data():
    """
    Privacy-first session deletion:
    1. Delete audio from session state / memory.
    2. Delete original transcript.
    3. Delete extracted clinical data.
    4. Delete temporary session information.
    5. Return clean session state and mark deletion confirmation.
    """
    keys_to_delete = [
        "current_intake",
        "original_transcript",
        "session_id",
        "audio_buffer",
        "processed_text"
    ]
    
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
            
    # Reset session ID to a fresh clean ID
    st.session_state["session_id"] = generate_session_id()
    st.session_state["current_intake"] = None
    st.session_state["original_transcript"] = None
    st.session_state["session_just_ended"] = True
