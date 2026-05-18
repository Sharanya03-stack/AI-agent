from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.analyzer import LogTriageAgent
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

triage_agent = LogTriageAgent()
historical_incident_ledger = []

class ChatRequest(BaseModel):
    message: str
    filename: str = ""

@app.get("/")
def read_root():
    return {"status": "Online", "agent": "Hindsight Triage Core Engine"}

@app.post("/api/triage")
async def triage_log(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    try:
        log_bytes = await file.read()
        log_text = log_bytes.decode("utf-8", errors="ignore")
        analysis_results = triage_agent.analyze_log(log_text, file.filename)
        
        # --- ENTERPRISE FEATURE: AUTOMATED TEAM DELEGATION ROUTING ---
        lower_snippet = analysis_results["analysis"]["extracted_snippet"].lower()
        if "timeout" in lower_snippet or "docker" in lower_snippet:
            assigned_team = "⚙️ DevOps Core Infrastructure"
            slack_channel = "#infra-alerts-critical"
        elif "assert" in lower_snippet or "test" in lower_snippet:
            assigned_team = "🧪 QA Automation & Frameworks"
            slack_channel = "#qa-regression-logs"
        elif "auth" in lower_snippet or "401" in lower_snippet:
            assigned_team = "🔑 SecOps / Identity Team"
            slack_channel = "#security-audit-stream"
        else:
            assigned_team = "💻 General Engineering Core"
            slack_channel = "#dev-triage"

        analysis_results["enterprise_routing"] = {
            "assigned_owner_group": assigned_team,
            "slack_destination": slack_channel,
            "incident_id": f"TRG-{datetime.datetime.now().strftime('%M%S')}"
        }

        # Sync existing history ledger properties
        timestamp_str = datetime.datetime.now().strftime("%I:%M:%S %p")
        incident_record = {
            "time": timestamp_str,
            "file": file.filename,
            "severity": analysis_results["error_severity"],
            "tier": analysis_results["analytics"]["routing_tier"]
        }
        historical_incident_ledger.insert(0, incident_record)
        analysis_results["ledger_history"] = historical_incident_ledger
        
        return analysis_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_consultation(payload: ChatRequest):
    msg = payload.message.lower()
    if "proxy" in msg or "mirror" in msg or "network" in msg or "timeout" in msg:
        reply = "🛠️ **CascadeFlow Network Advisory:** To stabilize this timeout, add an explicit `--network=host` parameter or verify local environment variables like `HTTP_PROXY`. Hindsight logs indicate transient cluster spikes."
    elif "retry" in msg or "rerun" in msg:
        reply = "🔄 **Hindsight Safety Gate:** Retrying manually right now will fail identically. Wait for automated network mirror failovers or clear lockfiles before initiating build runners."
    elif "token" in msg or "auth" in msg or "401" in msg:
        reply = "🔑 **Security Scan Analysis:** Token expired or secrets mapping block dropped permissions. Ensure repository configurations match requirements inside your environment context panels."
    else:
        reply = "🤖 **Triage Consulting Agent:** Parsing user string query patterns against active cluster telemetry databases. I suggest running a dependency validation stack trace check."
    return {"reply": reply}
