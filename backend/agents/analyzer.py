import os
import re
from memory.hindsight import HindsightMemoryDB

class LogTriageAgent:
    def __init__(self):
        self.error_keywords = [
            r"error:", r"failed:", r"fatal:", r"exception:", 
            r"assert", r"build failure", r"npm err!", r"exit code \d+"
        ]
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
        """
        Processes logs using a CascadeFlow Architecture:
        Layer 1: Deterministic Signature Matcher (Fast Execution)
        Layer 2: Semantic Heuristic Analysis (Deep Fallback Parsing)
        """
        extracted_context = self.extract_critical_section(raw_log_text)
        
        # --- CASCADEFLOW LAYER 1: DETERMINISTIC MATCHING (Fast Tier) ---
        flow_tier = "Layer 1: Deterministic Matcher"
        confidence = 98
        
        if "timeout" in extracted_context.lower():
            signature = "Network Gateway Timeout"
            root_cause_summary = "[CascadeFlow L1 Match] Network Gateway Timeout during artifact download download pipeline."
            suggested_fix = "Network glitch detected. Safe to retry. Ensure internal repository mirrors are operational."
            retry_safe = True
            severity = "CRITICAL"
            
        elif "assert" in extracted_context.lower():
            signature = "Application Unit Test Suite Assertion"
            root_cause_summary = "[CascadeFlow L1 Match] Application Unit Test Failure code assertion dropped."
            suggested_fix = "Review the modified test suites. Code logic regression detected. Do NOT auto-retry."
            retry_safe = False
            severity = "HIGH"
            
        # --- CASCADEFLOW LAYER 2: SEMANTIC HEURISTIC ANALYSIS (Fallback Tier) ---
        else:
            flow_tier = "Layer 2: Heuristic Semantic Fallback"
            confidence = 85
            severity = "MEDIUM"
            signature = "Unknown System Interruption Pattern"
            
            # Sub-parsing logic within Layer 2 fallback
            if "npm err!" in extracted_context.lower() or "missing" in extracted_context.lower():
                root_cause_summary = "[CascadeFlow L2 Fallback] Dependency Resolution Failure: Package mismatch detected."
                suggested_fix = "Run 'npm cache clean --force' or verify dependencies match lockfiles."
                retry_safe = True
            else:
                root_cause_summary = "[CascadeFlow L2 Fallback] General System Interruption: Unrecognized pipeline failure."
                suggested_fix = "Inspect verbose trace records. Review recently integrated pull request parameters."
                retry_safe = True

        # --- UNCHANGED DOWNSTREAM PIPELINES (Keeps UI and Database fully stable) ---
        memory_insight = self.memory_db.check_and_record_incident(signature)
        original_bytes = len(raw_log_text.encode('utf-8'))
        saved_bytes = len(extracted_context.encode('utf-8'))
        compression_ratio = round((1 - (saved_bytes / max(1, original_bytes))) * 100, 1)

        return {
            "filename": filename,
            "status": "Success",
            "error_severity": severity,
            "confidence_score": confidence,
            "retry_recommended": retry_safe,
            "analytics": {
                "original_size_kb": round(original_bytes / 1024, 2),
                "routed_size_kb": round(saved_bytes / 1024, 2),
                "tokens_saved_percent": compression_ratio,
                "routing_tier": flow_tier  # Displays CascadeFlow Layer name directly into your UI card!
            },
            "hindsight_memory": memory_insight,
            "analysis": {
                "root_cause": f"{root_cause_summary} (Incident Seen Count: {memory_insight['historical_occurrence_count']}x)",
                "suggested_fix": suggested_fix,
                "extracted_snippet": extracted_context[:1200]
            }
        }
