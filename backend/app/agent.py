import os
import time
import requests
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class AgentState(TypedDict):
    page_text: str
    mode: Literal["summary", "qa", "tasks"]
    question: str
    result: str


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


def summarize_node(state: AgentState) -> AgentState:
    prompt = f"""Summarize the following web page content in 3-5 concise bullet points.
Focus on the most important information.

PAGE CONTENT:
{state["page_text"][:3000]}
"""
    result = ask_ollama(prompt)
    return {**state, "result": result}


def qa_node(state: AgentState) -> AgentState:
    prompt = f"""Answer the following question using ONLY the information from the page content below.
If the answer is not in the content, say: "I couldn't find that information on this page."

QUESTION:
{state["question"]}

PAGE CONTENT:
{state["page_text"][:3000]}
"""
    result = ask_ollama(prompt)
    return {**state, "result": result}


def tasks_node(state: AgentState) -> AgentState:
    prompt = f"""Extract all action items, tasks, to-dos, and deadlines from the page content below.
Format as a numbered list. If none are found, say: "No action items found."

PAGE CONTENT:
{state["page_text"][:3000]}
"""
    result = ask_ollama(prompt)
    return {**state, "result": result}


def router(state: AgentState) -> Literal["summarize", "qa", "tasks"]:
    if state["mode"] == "summary":
        return "summarize"
    if state["mode"] == "qa":
        return "qa"
    return "tasks"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("summarize", summarize_node)
    graph.add_node("qa", qa_node)
    graph.add_node("tasks", tasks_node)

    graph.set_conditional_entry_point(
        router,
        {
            "summarize": "summarize",
            "qa": "qa",
            "tasks": "tasks",
        },
    )

    graph.add_edge("summarize", END)
    graph.add_edge("qa", END)
    graph.add_edge("tasks", END)

    return graph.compile()


agent_graph = build_graph()


def run_agent(page_text: str, mode: str, question: str = "") -> tuple[str, int]:
    start = time.time()

    result = agent_graph.invoke(
        {
            "page_text": page_text,
            "mode": mode,
            "question": question,
            "result": ""
        }
    )

    latency_ms = int((time.time() - start) * 1000)
    return result["result"], latency_ms