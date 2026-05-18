from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.analyzer import LogTriageAgent

app = FastAPI(title="CI/CD Triage Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

triage_agent = LogTriageAgent()

@app.get("/")
def read_root():
    return {"status": "Online", "agent": "Hindsight Triage Core"}

@app.post("/api/triage")
async def triage_log(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    try:
        log_bytes = await file.read()
        log_text = log_bytes.decode("utf-8", errors="ignore")
        analysis_results = triage_agent.analyze_log(log_text, file.filename)
        return analysis_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error processing file: {str(e)}")
