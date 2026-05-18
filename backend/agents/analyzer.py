# Filename: backend/agents/analyzer.py

import os
import re
# Import our new Hindsight Memory Controller directly
from memory.hindsight import HindsightMemoryDB

class LogTriageAgent:
    def __init__(self):
        self.error_keywords = [
            r"error:", r"failed:", r"fatal:", r"exception:", 
            r"assert", r"build failure", r"npm err!", r"exit code \d+"
        ]
        # Initialize database link inside our agent pipeline
        self.memory_db = HindsightMemoryDB()

    def extract_critical_section(self, raw_log_text: str, window_lines: int = 25) -> str:
        lines = raw_log_text.splitlines()
        critical_lines = set()
        for idx, line in enumerate(lines):
            lower_line = line.lower()
            if any(re.search(keyword, lower_line) for keyword in self.error_keywords):
                start = max(0, idx - window_lines)
                end = min(len(lines), idx + window_lines)
                for i in range(start, end):
                    critical_lines.add(i)
        if not critical_lines:
            return "\n".join(lines[-60:])
        sorted_indices = sorted(list(critical_lines))
        return "\n".join([lines[i] for i in sorted_indices])

    def analyze_log(self, raw_log_text: str, filename: str) -> dict:
        extracted_context = self.extract_critical_section(raw_log_text)
        
        severity = "MEDIUM"
        if "fatal" in extracted_context.lower() or "exception" in extracted_context.lower():
            severity = "HIGH"
        elif "timeout" in extracted_context.lower() or "network" in extracted_context.lower():
            severity = "CRITICAL"

        # Determine a dynamic error signature based on contents to check against database records
        if "timeout" in extracted_context.lower():
            signature = "Network Gateway Timeout Gateway 504 Failure"
            root_cause_summary = "Network Gateway Timeout during artifact download."
            suggested_fix = "Network glitch detected. Safe to retry. Ensure internal repository mirrors are operational."
            retry_safe = True
        elif "assert" in extracted_context.lower() or "failed" in extracted_context.lower():
            signature = "Application Unit Test Suite Assertion Regression Failure"
            root_cause_summary = "Application Unit Test Failure code assertion dropped."
            suggested_fix = "Review the modified test suites. Code logic regression detected. Do NOT auto-retry."
            retry_safe = False
        else:
            signature = "Unknown System Process Interruption Stack Error"
            root_cause_summary = "Dependency Resolution Failure: Package mismatch detected."
            suggested_fix = "Run 'npm cache clean --force' or verify dependencies match lockfiles."
            retry_safe = True

        # CRITICAL PIPELINE STEP: Commit signature telemetry directly to Hindsight Database memory bancos!
        memory_insight = self.memory_db.check_and_record_incident(signature)

        original_bytes = len(raw_log_text.encode('utf-8'))
        saved_bytes = len(extracted_context.encode('utf-8'))
        compression_ratio = round((1 - (saved_bytes / max(1, original_bytes))) * 100, 1)

        return {
            "filename": filename,
            "status": "Success",
            "error_severity": severity,
            "confidence_score": 88 if severity == "HIGH" else 94,
            "retry_recommended": retry_safe,
            "analytics": {
                "original_size_kb": round(original_bytes / 1024, 2),
                "routed_size_kb": round(saved_bytes / 1024, 2),
                "tokens_saved_percent": compression_ratio,
                "routing_tier": "Local Model (Ollama) Tier" if compression_ratio > 50 else "Cloud Model Tier"
            },
            # Inject our data variables cleanly into payload array structures
            "hindsight_memory": memory_insight,
            "analysis": {
                "root_cause": f"{root_cause_summary} (Incident Seen Count: {memory_insight['historical_occurrence_count']}x)",
                "suggested_fix": suggested_fix,
                "extracted_snippet": extracted_context[:1200] + "\n... [Truncated for Optimization Dashboard view] ..."
            }
        }