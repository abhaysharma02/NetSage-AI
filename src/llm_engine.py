import os
import json
import urllib.request
import urllib.error

from dotenv import load_dotenv


# ============================================================
# NetSage AI - LLM Engine
# ============================================================

load_dotenv()


# ============================================================
# Configuration
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama3.2:3b"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)


# ============================================================
# Build Prompt
# ============================================================

def build_prompt(case):

    case_id = case.get(
        "case_id",
        ""
    )

    symptom = case.get(
        "symptom",
        ""
    )

    findings = case.get(
        "findings",
        []
    )

    prompt = []

    prompt.append(
        "You are NetSage AI, a network troubleshooting assistant."
    )

    prompt.append(
        "Analyze the supplied network diagnostic evidence."
    )

    prompt.append(
        "Identify the most likely diagnosis and root cause."
    )

    prompt.append(
        "Give a practical recommendation for fixing the issue."
    )

    prompt.append(
        "Do not invent network evidence."
    )

    prompt.append("")

    prompt.append(
        f"Case ID: {case_id}"
    )

    prompt.append(
        f"Symptom: {symptom}"
    )

    prompt.append("")

    prompt.append(
        "Network Findings:"
    )

    for finding in findings:

        prompt.append(
            f"- Rule: {finding.get('rule', '')}"
        )

        prompt.append(
            f"- Finding: {finding.get('finding', '')}"
        )

        prompt.append(
            f"- Severity: {finding.get('severity', '')}"
        )

    prompt.append("")

    prompt.append(
        "Return ONLY valid JSON."
    )

    prompt.append(
        "Do not add markdown."
    )

    prompt.append(
        "Do not add explanations outside the JSON."
    )

    prompt.append(
        "Use exactly these fields:"
    )

    prompt.append(
        "diagnosis, root_cause, recommendation, confidence"
    )

    return "\n".join(prompt)


# ============================================================
# Call Ollama
# ============================================================

def call_ollama(prompt):

    payload = {

        "model": LLM_MODEL,

        "prompt": prompt,

        "stream": False,

        "format": "json"
    }

    data = json.dumps(
        payload
    ).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            response_data = response.read().decode(
                "utf-8"
            )

    except urllib.error.URLError as error:

        raise RuntimeError(
            "Could not connect to Ollama.\n"
            "Make sure Ollama is running on your computer.\n"
            f"Details: {error}"
        )

    result = json.loads(
        response_data
    )

    return result.get(
        "response",
        ""
    ).strip()


# ============================================================
# Analyze Case
# ============================================================

def analyze_case(case):

    prompt = build_prompt(
        case
    )

    text = call_ollama(
        prompt
    )

    try:

        result = json.loads(
            text
        )

    except json.JSONDecodeError:

        result = {

            "diagnosis": text,

            "root_cause":
                "Not returned as structured JSON.",

            "recommendation":
                "Review the model response manually.",

            "confidence":
                "Unknown"
        }

    return result


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("NETSAGE AI - LLM ENGINE")
    print("=" * 70)

    print()
    print(
        f"Provider           : {LLM_PROVIDER}"
    )

    print(
        f"Model              : {LLM_MODEL}"
    )

    print(
        f"Ollama URL         : {OLLAMA_URL}"
    )

    try:

        test_case = {

            "case_id":
                "NET-001",

            "symptom":
                "PC1 cannot reach Server1 in VLAN 30",

            "findings": [

                {
                    "rule":
                        "INTERFACE_DOWN",

                    "finding":
                        "gigabitethernet0/0.10 is administratively down.",

                    "severity":
                        "High"
                }
            ]
        }

        print()
        print(
            "Sending test case to local AI model..."
        )

        result = analyze_case(
            test_case
        )

        print()
        print(
            "AI RESPONSE"
        )

        print(
            "-" * 70
        )

        print(
            json.dumps(
                result,
                indent=4
            )
        )

        print(
            "-" * 70
        )

        print()
        print(
            "LLM test completed successfully."
        )

    except Exception as error:

        print()
        print(
            "=" * 70
        )

        print(
            "LLM ERROR"
        )

        print(
            "=" * 70
        )

        print(
            error
        )

        print(
            "=" * 70
        )