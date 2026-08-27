import json
from pathlib import Path


# ============================================================
# NetSage AI - Report Generator
# ============================================================

def load_ai_results():
    """
    Load AI diagnosis results from logs/ai_diagnosis_results.json.
    """

    project_root = Path(__file__).resolve().parent.parent

    results_path = (
        project_root
        / "logs"
        / "ai_diagnosis_results.json"
    )

    if not results_path.exists():
        raise FileNotFoundError(
            f"Could not find AI diagnosis results:\n{results_path}\n\n"
            "Run ai_engine.py first."
        )

    with open(
        results_path,
        "r",
        encoding="utf-8"
    ) as file:

        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError(
            "ai_diagnosis_results.json must contain a list."
        )

    return results


# ============================================================
# Generate Summary
# ============================================================

def generate_summary(results):

    total_cases = len(results)

    high = 0
    medium = 0
    low = 0

    for case in results:

        for diagnosis in case.get("diagnoses", []):

            severity = diagnosis.get(
                "severity",
                "Info"
            ).lower()

            if severity == "high":
                high += 1

            elif severity == "medium":
                medium += 1

            elif severity == "low":
                low += 1

    if high > 0:
        status = "CRITICAL - Immediate attention required"

    elif medium > 0:
        status = "WARNING - Review required"

    else:
        status = "HEALTHY"

    return {
        "total_cases": total_cases,
        "high": high,
        "medium": medium,
        "low": low,
        "status": status
    }


# ============================================================
# Generate Report
# ============================================================

def generate_report(results):

    summary = generate_summary(results)

    report = []

    report.append("=" * 70)
    report.append("NETSAGE AI - NETWORK DIAGNOSTIC REPORT")
    report.append("=" * 70)

    report.append("")

    report.append(
        f"Total Cases      : {summary['total_cases']}"
    )

    report.append(
        f"High Severity    : {summary['high']}"
    )

    report.append(
        f"Medium Severity  : {summary['medium']}"
    )

    report.append(
        f"Low Severity     : {summary['low']}"
    )

    report.append(
        f"Overall Status   : {summary['status']}"
    )

    report.append("")
    report.append("=" * 70)

    for case in results:

        report.append("")

        report.append(
            f"Case ID : {case.get('case_id', '')}"
        )

        report.append(
            f"Symptom : {case.get('symptom', '')}"
        )

        report.append("-" * 70)

        for diagnosis in case.get(
            "diagnoses",
            []
        ):

            report.append(
                f"Rule           : {diagnosis.get('rule', '')}"
            )

            report.append(
                f"Severity       : {diagnosis.get('severity', '')}"
            )

            report.append(
                f"Diagnosis      : {diagnosis.get('diagnosis', '')}"
            )

            report.append(
                f"Root Cause     : {diagnosis.get('root_cause', '')}"
            )

            report.append(
                f"Recommendation : {diagnosis.get('recommendation', '')}"
            )

            report.append(
                f"Confidence     : {diagnosis.get('confidence', '')}"
            )

            report.append("")

    report.append("=" * 70)
    report.append("NETSAGE AI REPORT GENERATION COMPLETED")
    report.append("=" * 70)

    return "\n".join(report)


# ============================================================
# Save Report
# ============================================================

def save_report(report):

    project_root = Path(__file__).resolve().parent.parent

    logs_folder = (
        project_root
        / "logs"
    )

    logs_folder.mkdir(
        exist_ok=True
    )

    report_path = (
        logs_folder
        / "final_network_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    return report_path


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    try:

        results = load_ai_results()

        report = generate_report(
            results
        )

        print(report)

        output_file = save_report(
            report
        )

        print()
        print(
            f"Report saved to : {output_file}"
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)

        print(error)

        print("=" * 70)