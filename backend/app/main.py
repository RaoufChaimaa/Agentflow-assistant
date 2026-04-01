from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import run_agent
from .models import AnalyzeRequest, AnalyzeResponse

load_dotenv()

app = FastAPI(title="AgentFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.page_text.strip():
        raise HTTPException(status_code=400, detail="page_text cannot be empty")

    if req.mode == "qa" and not req.question.strip():
        raise HTTPException(status_code=400, detail="question required for qa mode")

    try:
        result, latency_ms = run_agent(req.page_text, req.mode, req.question)
        return AnalyzeResponse(result=result, mode=req.mode, latency_ms=latency_ms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))