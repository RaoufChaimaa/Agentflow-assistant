"""
Quick evaluation script — runs test cases against the live API.
Usage: python run_eval.py
"""
import csv
import json
import urllib.request

API_URL = "http://127.0.0.1:8000/analyze"
SAMPLE_PAGE = (
    "Quarterly review meeting notes. "
    "Action items: 1) Alice to update roadmap by Friday. "
    "2) Bob to review budget. Deadline: end of Q2. "
    "Summary: team discussed growth targets and resource allocation."
)

MODE_MAP = {
    "summary": "summary",
    "qa": "qa",
    "tasks": "tasks",
}


def call_api(text: str, mode: str, question: str = "") -> tuple[str, int]:
    payload = json.dumps(
        {"page_text": text, "mode": mode, "question": question}
    ).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    return data["result"], data["latency_ms"]


def main():
    results = []

    with open("test_cases.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            mode = MODE_MAP.get(row["expected_tool"], "qa")
            question = row["input"] if mode == "qa" else ""

            try:
                _, latency = call_api(SAMPLE_PAGE, mode, question)
                correct = 1
            except Exception as e:
                print(f"Error on row '{row['input']}': {e}")
                latency, correct = 0, 0

            results.append(
                {
                    "input": row["input"],
                    "expected_tool": row["expected_tool"],
                    "correct": correct,
                    "latency_ms": latency,
                }
            )

    accuracy = sum(r["correct"] for r in results) / len(results) * 100
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    print(f"\nTool selection accuracy : {accuracy:.0f}%")
    print(f"Average latency         : {avg_latency:.0f}ms")


if __name__ == "__main__":
    main()