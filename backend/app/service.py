import os
import time
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def ask_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def summarize(page_text: str) -> str:
    prompt = f"""Summarize the following web page content in 3-5 concise bullet points.
Focus on the most important information.

PAGE CONTENT:
{page_text[:3000]}
"""
    return ask_ollama(prompt)


def answer_question(page_text: str, question: str) -> str:
    prompt = f"""Answer the following question using ONLY the information from the page content below.
If the answer is not in the content, say: "I couldn't find that information on this page."

QUESTION:
{question}

PAGE CONTENT:
{page_text[:3000]}
"""
    return ask_ollama(prompt)


def extract_tasks(page_text: str) -> str:
    prompt = f"""Extract all action items, tasks, to-dos, and deadlines from the page content below.
Format as a numbered list. If none are found, say: "No action items found."

PAGE CONTENT:
{page_text[:3000]}
"""
    return ask_ollama(prompt)


def run_analysis(page_text: str, mode: str, question: str = "") -> tuple[str, int]:
    start = time.time()

    if mode == "summary":
        result = summarize(page_text)
    elif mode == "qa":
        result = answer_question(page_text, question)
    elif mode == "tasks":
        result = extract_tasks(page_text)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    latency_ms = int((time.time() - start) * 1000)
    return result, latency_ms