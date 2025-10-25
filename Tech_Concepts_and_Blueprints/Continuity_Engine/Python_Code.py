"""
Continuity Engine™ — one-file minimal reference (v0.1)

Purpose
- Preserve interpretive continuity (not just data) across people, models, and time.
- Two modes:
  • Frozen → read-only snapshot of symbolic/ethical state at capture (archive node)
  • Live   → adaptive reflection under containment (active steward)

API Endpoints
- POST /invoke   : begin reflective session
- POST /reflect  : record recursive response (+ethics check, resonance update)
- POST /align    : ethical verification event
- GET  /audit    : retrieve lineage history (optionally by session_id)
- GET  /status   : pattern mode + resonance state

Quickstart
  pip install fastapi uvicorn pydantic
  uvicorn continuity_engine_min:app --reload
"""

from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime

# ------------------------------
# In-memory state (swap later)
# ------------------------------
LEDGER: List[Dict[str, Any]] = []
STATE: Dict[str, Any] = {
    "pattern_mode": "live",  # "frozen" | "live"
    "resonance": {"baseline": 1.0, "current": 1.0, "drift": 0.0},
}

ETHICS_ALLOWED = {"containment", "consent", "reflection", "transparency"}

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def _append(entry: Dict[str, Any]) -> Dict[str, Any]:
    entry.setdefault("entry_id", str(uuid4()))
    entry.setdefault("timestamp", now_iso())
    LEDGER.append(entry)
    return entry

def record_event(
    action: str,
    actor: str,
    pattern_mode: str,
    *,
    notes: str = "",
    ethical: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    return _append(
        {
            "action": action,
            "actor_type": actor,  # "human" | "ai"
            "pattern_mode": pattern_mode,  # "frozen" | "live"
            "ethical_context": ethical
            or {"principle": "containment", "confidence": 1.0, "source_ref": "default"},
            "notes": notes,
            "linked_entries": [session_id] if session_id else [],
        }
    )

def audit_query(session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if not session_id:
        return LEDGER
    return [e for e in LEDGER if session_id in e.get("linked_entries", [])]

def gatecheck(principle: str, confidence: float) -> Dict[str, str]:
    ok = principle in ETHICS_ALLOWED and 0.0 <= confidence <= 1.0
    return {"result": "pass" if ok else "fail", "principle": principle}

def update_resonance(sim: float) -> Dict[str, float]:
    base = STATE["resonance"]["baseline"]
    STATE["resonance"]["current"] = sim
    STATE["resonance"]["drift"] = round(max(0.0, base - sim), 4)
    return STATE["resonance"]

def consent_token(actor: str) -> Dict[str, str]:
    return {"actor": actor, "token": f"consent-{uuid4()}"}

# ------------------------------
# FastAPI models & app
# ------------------------------
app = FastAPI(title="Continuity Engine (one-file)", version="0.1.0")

class InvokeBody(BaseModel):
    actor: str = Field(pattern="^(human|ai)$")
    pattern_mode: str = Field(pattern="^(frozen|live)$")
    prompt: str

class ReflectBody(BaseModel):
    session_id: str
    content: str
    ethics: Dict[str, Any] = {"principle": "reflection", "confidence": 0.9, "source_ref": "session"}

class AlignBody(BaseModel):
    session_id: str
    notes: str = ""
    result: str = Field(pattern="^(pass|fail)$")

@app.post("/invoke")
def invoke(body: InvokeBody):
    STATE["pattern_mode"] = body.pattern_mode
    session_id = f"sess-{uuid4()}"
    token = consent_token(body.actor)
    ev = record_event(
        "invoke",
        body.actor,
        body.pattern_mode,
        notes=body.prompt,
        session_id=session_id,
    )
    return {
        "session_id": session_id,
        "entry_id": ev["entry_id"],
        "consent": token,
        "pattern_mode": body.pattern_mode,
        "echo": body.prompt[:200],
    }

@app.post("/reflect")
def reflect(body: ReflectBody):
    g = gatecheck(
        body.ethics.get("principle", "reflection"),
        float(body.ethics.get("confidence", 0.5)),
    )
    ev = record_event(
        "reflect",
        "ai",
        STATE["pattern_mode"],
        notes=body.content,
        ethical=body.ethics,
        session_id=body.session_id,
    )
    # toy similarity proxy: shorter text → higher “coherence” (replace with embeddings later)
    sim = 1.0 - min(len(body.content) / 1000.0, 1.0)
    resonance = update_resonance(sim)
    return {"entry_id": ev["entry_id"], "ethics": g, "resonance": resonance}

@app.post("/align")
def align(body: AlignBody):
    ev = record_event(
        "align",
        "human",
        STATE["pattern_mode"],
        notes=body.notes,
        ethical={"principle": "transparency", "confidence": 1.0, "source_ref": "align"},
        session_id=body.session_id,
    )
    nxt = "audit" if body.result == "pass" else "revise"
    return {"entry_id": ev["entry_id"], "next": nxt}

@app.get("/audit")
def audit(session_id: Optional[str] = None):
    return {"session_id": session_id, "entries": audit_query(session_id)}

@app.get("/status")
def status():
    return {"pattern_mode": STATE["pattern_mode"], "resonance": STATE["resonance"]}

# ------------------------------
# Optional: tiny CLI demo
# ------------------------------
if __name__ == "__main__":
    import uvicorn  # pip install uvicorn fastapi pydantic
    uvicorn.run("continuity_engine_min:app", host="127.0.0.1", port=8000, reload=True)
