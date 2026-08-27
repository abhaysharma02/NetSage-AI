from checker import (
    run_dataset,
    save_results as save_checker_results
)

from ai_engine import (
    run_ai_engine,
    save_results as save_ai_results
)

from report_generator import (
    generate_report,
    save_report
)


def main():

    print()
    print("=" * 70)
    print("NETSAGE AI - NETWORK DIAGNOSTIC SYSTEM")
    print("=" * 70)

    # --------------------------------------------------------
    # Step 1: Run Deterministic Checker
    # --------------------------------------------------------

    print()
    print("[1] Running deterministic rule checker...")

    checker_results = run_dataset()

    save_checker_results(
        checker_results
    )

    print(
        f"Checker completed: "
        f"{len(checker_results)} cases processed."
    )

    # --------------------------------------------------------
    # Step 2: Run AI Diagnosis Engine
    # --------------------------------------------------------

    print()
    print("[2] Running AI diagnosis engine...")

    ai_results = run_ai_engine()

    save_ai_results(
        ai_results
    )

    print(
        f"AI diagnosis completed: "
        f"{len(ai_results)} cases processed."
    )

    # --------------------------------------------------------
    # Step 3: Generate Final Report
    # --------------------------------------------------------

    print()
    print("[3] Generating final network report...")

    report = generate_report(
        ai_results
    )

    report_path = save_report(
        report
    )

    print(
        "Report generated successfully."
    )

    print(
        f"Report saved to: {report_path}"
    )

    # --------------------------------------------------------
    # Step 4: Completion
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("NETSAGE AI COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(
        f"Total cases processed : {len(ai_results)}"
    )

    print(
        "Checker output        : logs/checker_results.json"
    )

    print(
        "AI output             : logs/ai_diagnosis_results.json"
    )

    print(
        "Final report          : logs/final_network_report.txt"
    )

    print("=" * 70)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 70)
        print("NETSAGE AI ERROR")
        print("=" * 70)

        print(error)

        print("=" * 70)