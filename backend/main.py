from agents.analyzer import LogTriageAgent
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="CI/CD Triage Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Welcome to the CI/CD Triage Agent Backend Server!",
        "hackathon": "Microsoft Hackathon 2026"
    }

@app.post("/api/triage")
async def triage_log(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    try:
        log_bytes = await file.read()
        log_text = log_bytes.decode("utf-8", errors="ignore")
        line_count = len(log_text.splitlines())
        return {
            "filename": file.filename,
            "lines_processed": line_count,
            "status": "success",
            "analysis": {
                "root_cause": "Mock analysis: Server connection successful!",
                "confidence_score": 95,
                "retry_recommended": True,
                "error_severity": "HIGH"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main.py:app", host="127.0.0.1", port=8000, reload=True)
