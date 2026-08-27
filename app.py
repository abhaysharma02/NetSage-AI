import streamlit as st
import sys
from pathlib import Path

# Add src folder to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from checker import load_cases, check_case
from ai_engine import generate_diagnosis


# ============================================================
# NetSage AI - Web Application
# ============================================================

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide"
)


# ============================================================
# Header
# ============================================================

st.title("🌐 NetSage AI")
st.subheader("Deterministic Network Diagnosis System")

st.write(
    "Analyze network evidence and identify possible configuration "
    "problems using deterministic rules and structured diagnosis."
)

st.divider()


# ============================================================
# Load Dataset
# ============================================================

try:
    cases = load_cases()

except Exception as error:

    st.error(f"Unable to load cases.csv: {error}")
    st.stop()


# ============================================================
# Sidebar
# ============================================================

st.sidebar.header("Case Selection")

case_options = [
    case.get("case_id", "")
    for case in cases
]

selected_case_id = st.sidebar.selectbox(
    "Select Case",
    case_options
)


# Find selected case
selected_case = next(
    (
        case
        for case in cases
        if case.get("case_id", "") == selected_case_id
    ),
    None
)


if selected_case is None:

    st.error("Selected case could not be found.")
    st.stop()


# ============================================================
# Case Information
# ============================================================

st.header(f"Case: {selected_case['case_id']}")

st.write(
    f"**Symptom:** {selected_case.get('symptom', '')}"
)


# ============================================================
# Evidence
# ============================================================

st.subheader("Network Evidence")

evidence = selected_case.get(
    "show_outputs",
    ""
)

st.code(
    evidence,
    language="text"
)


# ============================================================
# Run Diagnosis
# ============================================================

if st.button(
    "🔍 Analyze Network",
    type="primary"
):

    # --------------------------------------------------------
    # Step 1: Deterministic Checker
    # --------------------------------------------------------

    findings = check_case(
        selected_case
    )

    checker_case = {
        "case_id":
            selected_case.get("case_id", ""),

        "symptom":
            selected_case.get("symptom", ""),

        "findings":
            findings
    }

    # --------------------------------------------------------
    # Step 2: AI Diagnosis
    # --------------------------------------------------------

    diagnoses = generate_diagnosis(
        checker_case
    )

    st.divider()

    st.header("Diagnosis Results")


    # --------------------------------------------------------
    # Display Findings
    # --------------------------------------------------------

    for diagnosis in diagnoses:

        severity = diagnosis.get(
            "severity",
            "Info"
        )

        # Severity display
        if severity == "High":
            st.error(f"Severity: {severity}")

        elif severity == "Medium":
            st.warning(f"Severity: {severity}")

        elif severity == "Low":
            st.info(f"Severity: {severity}")

        else:
            st.success(f"Severity: {severity}")


        st.markdown(
            f"### Rule: `{diagnosis['rule']}`"
        )

        st.write(
            f"**Diagnosis:** {diagnosis['diagnosis']}"
        )

        st.write(
            f"**Root Cause:** {diagnosis['root_cause']}"
        )

        st.write(
            f"**Recommendation:** {diagnosis['recommendation']}"
        )

        st.write(
            f"**Confidence:** {diagnosis['confidence']}"
        )

        st.divider()


# ============================================================
# Footer
# ============================================================

st.caption(
    "NetSage AI • Deterministic Network Rule Checker + AI Diagnosis Engine"
)