import json
from pathlib import Path

from llm_engine import analyze_case


# ============================================================
# NetSage AI - AI Diagnosis Engine
# ============================================================


# ============================================================
# Load Checker Results
# ============================================================

def load_checker_results():
    """
    Load deterministic checker results from:
    logs/checker_results.json
    """

    project_root = Path(__file__).resolve().parent.parent

    results_path = (
        project_root
        / "logs"
        / "checker_results.json"
    )

    if not results_path.exists():
        raise FileNotFoundError(
            f"Could not find checker results:\n"
            f"{results_path}\n\n"
            f"Run checker.py first."
        )

    with open(
        results_path,
        "r",
        encoding="utf-8"
    ) as file:

        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError(
            "checker_results.json must contain a list of results."
        )

    return results


# ============================================================
# Normalize Confidence
# ============================================================

def normalize_confidence(value):
    """
    Convert different confidence formats into
    a standard numeric value between 0 and 1.

    Supported examples:

        0.90  -> 0.90
        0.8   -> 0.80
        9     -> 0.90
        8     -> 0.80
        90    -> 0.90
        "90"  -> 0.90
        "High"   -> 0.90
        "Medium" -> 0.70
        "Low"    -> 0.40
    """

    # --------------------------------------------------------
    # String values
    # --------------------------------------------------------

    if isinstance(value, str):

        value = value.strip()

        # Handle words
        if value.lower() == "high":
            return 0.90

        if value.lower() == "medium":
            return 0.70

        if value.lower() == "low":
            return 0.40

        # Try numeric string
        try:
            value = float(value)

        except ValueError:
            return 0.50

    # --------------------------------------------------------
    # Numeric values
    # --------------------------------------------------------

    if isinstance(value, (int, float)):

        # Already in 0-1 format
        if 0 <= value <= 1:
            return round(value, 2)

        # 1-10 format
        # Example:
        # 9 -> 0.90
        # 8 -> 0.80
        if 1 < value <= 10:
            value = value / 10

        # Percentage format
        # Example:
        # 90 -> 0.90
        elif 10 < value <= 100:
            value = value / 100

        else:
            return 0.50

        return round(
            max(0.0, min(1.0, value)),
            2
        )

    return 0.50


# ============================================================
# Clean Text
# ============================================================

def clean_text(value, default):
    """
    Convert AI output into clean string values.
    """

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


# ============================================================
# Normalize AI Response
# ============================================================

def normalize_diagnosis(
    finding,
    ai_response
):
    """
    Convert the Ollama response into a consistent
    NetSage diagnosis format.
    """

    rule = finding.get(
        "rule",
        "NO_MATCH"
    )

    severity = finding.get(
        "severity",
        "Info"
    )

    # --------------------------------------------------------
    # Validate AI response
    # --------------------------------------------------------

    if not isinstance(ai_response, dict):
        ai_response = {}

    # --------------------------------------------------------
    # Diagnosis
    # --------------------------------------------------------

    diagnosis = clean_text(
        ai_response.get("diagnosis"),
        "No detailed diagnosis returned."
    )

    # --------------------------------------------------------
    # Root Cause
    # --------------------------------------------------------

    root_cause = clean_text(
        ai_response.get("root_cause"),
        finding.get(
            "finding",
            "Unknown root cause."
        )
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    recommendation = clean_text(
        ai_response.get("recommendation"),
        "Review the supplied network evidence manually."
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = normalize_confidence(
        ai_response.get(
            "confidence",
            0.50
        )
    )

    return {
        "rule": rule,

        "severity": severity,

        "diagnosis": diagnosis,

        "root_cause": root_cause,

        "recommendation": recommendation,

        "confidence": confidence
    }


# ============================================================
# Generate AI Diagnosis
# ============================================================

def generate_diagnosis(case):
    """
    Send deterministic checker findings to the
    local Ollama AI model and generate diagnosis.
    """

    findings = case.get(
        "findings",
        []
    )

    diagnoses = []

    # --------------------------------------------------------
    # No findings
    # --------------------------------------------------------

    if not findings:

        return [{
            "rule": "NO_MATCH",

            "severity": "Info",

            "diagnosis":
                "No network fault was detected by the deterministic checker.",

            "root_cause":
                "No matching diagnostic rule was triggered.",

            "recommendation":
                "No immediate corrective action is required.",

            "confidence": 0.50
        }]

    # --------------------------------------------------------
    # Process every finding
    # --------------------------------------------------------

    for finding in findings:

        try:

            ai_response = analyze_case({

                "case_id":
                    case.get(
                        "case_id",
                        ""
                    ),

                "symptom":
                    case.get(
                        "symptom",
                        ""
                    ),

                "findings": [
                    finding
                ]
            })

            diagnosis = normalize_diagnosis(
                finding,
                ai_response
            )

            diagnoses.append(
                diagnosis
            )

        except Exception as error:

            # ------------------------------------------------
            # AI failure fallback
            # ------------------------------------------------

            print(
                f"Warning: AI analysis failed for "
                f"{case.get('case_id', '')}"
            )

            print(
                f"Reason: {error}"
            )

            diagnoses.append({

                "rule":
                    finding.get(
                        "rule",
                        "NO_MATCH"
                    ),

                "severity":
                    finding.get(
                        "severity",
                        "Info"
                    ),

                "diagnosis":
                    "AI diagnosis unavailable.",

                "root_cause":
                    finding.get(
                        "finding",
                        "Unknown root cause."
                    ),

                "recommendation":
                    "Review the deterministic checker finding manually.",

                "confidence": 0.00
            })

    return diagnoses


# ============================================================
# Run AI Engine
# ============================================================

def run_ai_engine():

    checker_results = load_checker_results()

    ai_results = []

    total_cases = len(
        checker_results
    )

    print()

    print("=" * 70)
    print("NETSAGE AI - AI DIAGNOSIS ENGINE")
    print("=" * 70)

    print()

    print(
        "Using local Ollama AI model..."
    )

    print()

    # --------------------------------------------------------
    # Process every case
    # --------------------------------------------------------

    for index, case in enumerate(
        checker_results,
        start=1
    ):

        print(
            f"Processing case {index}/{total_cases}..."
        )

        diagnoses = generate_diagnosis(
            case
        )

        ai_results.append({

            "case_id":
                case.get(
                    "case_id",
                    ""
                ),

            "symptom":
                case.get(
                    "symptom",
                    ""
                ),

            "diagnoses":
                diagnoses
        })

    return ai_results


# ============================================================
# Print Results
# ============================================================

def print_results(results):

    print()

    print("=" * 70)
    print("NETSAGE AI - AI DIAGNOSIS RESULTS")
    print("=" * 70)

    for result in results:

        print()

        print(
            f"Case ID : {result.get('case_id', '')}"
        )

        print(
            f"Symptom : {result.get('symptom', '')}"
        )

        print("-" * 70)

        for diagnosis in result.get(
            "diagnoses",
            []
        ):

            print(
                f"Rule           : "
                f"{diagnosis.get('rule', '')}"
            )

            print(
                f"Severity       : "
                f"{diagnosis.get('severity', '')}"
            )

            print(
                f"Diagnosis      : "
                f"{diagnosis.get('diagnosis', '')}"
            )

            print(
                f"Root Cause     : "
                f"{diagnosis.get('root_cause', '')}"
            )

            print(
                f"Recommendation : "
                f"{diagnosis.get('recommendation', '')}"
            )

            print(
                f"Confidence     : "
                f"{diagnosis.get('confidence', 0):.2f}"
            )

            print()


# ============================================================
# Save AI Results
# ============================================================

def save_results(results):

    project_root = Path(__file__).resolve().parent.parent

    logs_folder = (
        project_root
        / "logs"
    )

    logs_folder.mkdir(
        exist_ok=True
    )

    output_path = (
        logs_folder
        / "ai_diagnosis_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_path


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    try:

        results = run_ai_engine()

        print_results(
            results
        )

        output_file = save_results(
            results
        )

        print()

        print("=" * 70)

        print(
            f"Total cases processed : "
            f"{len(results)}"
        )

        print(
            f"Results saved to      : "
            f"{output_file}"
        )

        print("=" * 70)

    except Exception as error:

        print()

        print("=" * 70)
        print("NETSAGE AI ERROR")
        print("=" * 70)

        print(error)

        print("=" * 70)