"""
Atlas Protocol — Enterprise Single-File Demo
===========================================

Two-lane reasoning system:
- ATLAS Lane: expert curation, weighted scoring, recommendations
- COPILOT Lane: execution planning, comparisons, checklists
With SignalCraft ethical overlay + continuity memory

FastAPI endpoint for Teams / Copilot tool calling.

Install:
  pip install fastapi uvicorn

Run:
  uvicorn atlas_protocol_enterprise:app --reload --port 8000
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import json
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# =========================================================
# MODES
# =========================================================

class Mode(str, Enum):
    LIGHT = "light"
    DUAL_LANE = "dual_lane"
    DEEP_DIVE = "deep_dive"


# =========================================================
# CORE MODELS
# =========================================================

@dataclass(frozen=True)
class Citation:
    source_name: str
    url: Optional[str] = None
    note: Optional[str] = None


@dataclass
class EvidenceItem:
    claim: str
    citations: List[Citation] = field(default_factory=list)
    time_sensitive: bool = True


@dataclass
class RiskItem:
    risk: str
    mitigation: str
    severity: int = 3


@dataclass
class ChecklistItem:
    step: str
    why: Optional[str] = None


@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float
    min_score: int = 1
    max_score: int = 10


@dataclass
class Option:
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    scores: Dict[str, Tuple[float, str]] = field(default_factory=dict)


@dataclass
class TravelRequest:
    topic: str
    travelers: str = "unspecified"
    dates: Optional[str] = None
    budget: Optional[str] = None
    departure_airport: Optional[str] = None
    destination: Optional[str] = None
    priorities: Dict[str, float] = field(default_factory=dict)
    mode: Mode = Mode.DUAL_LANE
    minimal_citations: bool = True


@dataclass
class AtlasPreferences:
    vibe: Optional[str] = None
    noise_sensitivity: Optional[str] = None
    dining_priority: Optional[str] = None
    budget_tier: Optional[str] = None
    favorite_brands: List[str] = field(default_factory=list)
    avoid_brands: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class DecisionLogEntry:
    timestamp_utc: str
    request_topic: str
    recommendation: str
    rationale: str
    weights: Dict[str, float]


@dataclass
class ScoredOption:
    option: Option
    weighted_total: float
    breakdown: List[Tuple[str, float, float, str]]


@dataclass
class AtlasLaneReport:
    summary_bullets: List[str]
    weighted_table: List[Dict[str, Any]]
    top_pick: str
    top_pick_rationale: str
    alternates: List[str]
    pacing_notes: List[str]


@dataclass
class CopilotLaneReport:
    snapshot: Dict[str, str]
    evidence: List[EvidenceItem]
    comparison_scorecard: List[Dict[str, Any]]
    checklist: List[ChecklistItem]
    risks: List[RiskItem]


@dataclass
class EthicalAssessment:
    pluralism_notes: List[str] = field(default_factory=list)
    harm_minimization_notes: List[str] = field(default_factory=list)
    transparency_notes: List[str] = field(default_factory=list)
    autonomy_notes: List[str] = field(default_factory=list)
    hard_blocks: List[str] = field(default_factory=list)


@dataclass
class DualLaneReport:
    request: TravelRequest
    preferences_used: AtlasPreferences
    criteria: List[Criterion]
    scored: List[ScoredOption]
    assumptions: Dict[str, str]
    ethical: EthicalAssessment
    atlas: Optional[AtlasLaneReport] = None
    copilot: Optional[CopilotLaneReport] = None


# =========================================================
# MEMORY (CONTINUITY)
# =========================================================

class JsonMemoryStore:
    def __init__(self, path: str = "atlas_memory.json"):
        self.path = path

    def _read(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"preferences": asdict(AtlasPreferences()), "decisions": []}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_preferences(self) -> AtlasPreferences:
        return AtlasPreferences(**self._read().get("preferences", {}))

    def append_decision(self, entry: DecisionLogEntry):
        data = self._read()
        data["decisions"].append(asdict(entry))
        self._write(data)


# =========================================================
# ETHICAL OVERLAY (SIGNALCRAFT)
# =========================================================

class SignalCraftOverlay:
    def assess(
        self,
        request: TravelRequest,
        options: List[Option],
        assumptions: Dict[str, str],
        evidence: List[EvidenceItem],
    ) -> EthicalAssessment:
        a = EthicalAssessment()

        if len(options) >= 2:
            a.pluralism_notes.append("Multiple options preserved to honor user choice.")
        else:
            a.pluralism_notes.append("Single option only; recommend alternates.")

        if request.budget is None:
            a.harm_minimization_notes.append("Budget unspecified; avoid financial over-commitment.")

        if assumptions:
            a.transparency_notes.append("Assumptions explicitly stated.")
        else:
            a.transparency_notes.append("No assumptions provided; add for audit clarity.")

        a.autonomy_notes.append("Alternates presented using non-coercive language.")

        return a


# =========================================================
# SCORING ENGINE
# =========================================================

def normalize_weights(criteria: List[Criterion]) -> List[Criterion]:
    total = sum(c.weight for c in criteria)
    return [Criterion(c.name, (c.weight / total) * 100) for c in criteria]


class WeightedScorer:
    def score(self, criteria: List[Criterion], options: List[Option]) -> List[ScoredOption]:
        criteria = normalize_weights(criteria)
        scored: List[ScoredOption] = []

        for opt in options:
            total = 0.0
            breakdown = []
            for c in criteria:
                s, note = opt.scores.get(c.name, (5.0, "Defaulted"))
                s = max(c.min_score, min(c.max_score, float(s)))
                total += (c.weight / 100) * s
                breakdown.append((c.name, c.weight, s, note))
            scored.append(ScoredOption(opt, total, breakdown))

        scored.sort(key=lambda x: x.weighted_total, reverse=True)
        return scored


# =========================================================
# EVIDENCE PROVIDER (PLUGIN INTERFACE)
# =========================================================

class EvidenceProvider(ABC):
    @abstractmethod
    def get_evidence(self, request: TravelRequest, options: List[Option]) -> List[EvidenceItem]:
        pass

    @abstractmethod
    def enrich_options(self, request: TravelRequest, options: List[Option]) -> List[Option]:
        pass

    def assumptions(self) -> Dict[str, str]:
        return {}


class StaticEvidenceProvider(EvidenceProvider):
    def get_evidence(self, request, options):
        return [
            EvidenceItem(
                claim="Resort schedules, renovations, and airline baggage rules can change; verify before booking.",
                citations=[Citation("Supplier portal / airline policy")],
            )
        ]

    def enrich_options(self, request, options):
        for o in options:
            o.metadata.setdefault("Total Estimated Cost", "TBD")
            o.metadata.setdefault("Cancellation Terms", "Verify supplier policy")
        return options

    def assumptions(self):
        return {"Evidence": "Static demo provider (not live)"}


# =========================================================
# ATLAS ENGINE
# =========================================================

DEFAULT_CRITERIA = [
    Criterion("Vibe Fit", 20),
    Criterion("Amenities", 15),
    Criterion("Nightlife", 15),
    Criterion("Beach / Location", 15),
    Criterion("Dining / Bar", 10),
    Criterion("Room Quality", 10),
    Criterion("Price / Value", 10),
    Criterion("Safety / Reviews", 5),
]


class AtlasEngine:
    def __init__(self):
        self.memory = JsonMemoryStore()
        self.scorer = WeightedScorer()
        self.overlay = SignalCraftOverlay()

    def run(
        self,
        request: TravelRequest,
        options: List[Option],
        assumptions: Dict[str, str],
        evidence: List[EvidenceItem],
        snapshot: Dict[str, str],
    ) -> DualLaneReport:
        prefs = self.memory.load_preferences()

        criteria = (
            normalize_weights([Criterion(k, v) for k, v in request.priorities.items()])
            if request.priorities else normalize_weights(DEFAULT_CRITERIA)
        )

        scored = self.scorer.score(criteria, options)
        ethical = self.overlay.assess(request, options, assumptions, evidence)

        atlas = self._atlas_lane(request, scored, criteria)
        copilot = self._copilot_lane(request, options, evidence, snapshot)

        self.memory.append_decision(
            DecisionLogEntry(
                datetime.now(timezone.utc).isoformat(),
                request.topic,
                scored[0].option.name if scored else "N/A",
                "Top weighted score",
                {c.name: c.weight for c in criteria},
            )
        )

        return DualLaneReport(
            request, prefs, criteria, scored, assumptions, ethical, atlas, copilot
        )

    def _atlas_lane(self, request, scored, criteria):
        if not scored:
            return None

        top = scored[0]
        drivers = ", ".join(f"{c.name} ({c.weight:.0f}%)" for c in criteria[:2])

        table = []
        for c in criteria:
            row = {"Criterion": c.name, "Weight (%)": c.weight}
            for s in scored[:3]:
                row[s.option.name] = s.option.scores.get(c.name, (5, ""))[0]
            table.append(row)

        return AtlasLaneReport(
            summary_bullets=[
                f"Best fit: {top.option.name} ({top.weighted_total:.2f}/10)",
                f"Primary drivers: {drivers}",
            ],
            weighted_table=table,
            top_pick=top.option.name,
            top_pick_rationale="Aligned with highest-weighted criteria.",
            alternates=[s.option.name for s in scored[1:3]],
            pacing_notes=["Hold availability early; verify promos before ticketing."],
        )

    def _copilot_lane(self, request, options, evidence, snapshot):
        return CopilotLaneReport(
            snapshot=snapshot,
            evidence=evidence,
            comparison_scorecard=[
                {"Factor": "Total Estimated Cost", **{o.name: o.metadata.get("Total Estimated Cost") for o in options}}
            ],
            checklist=[
                ChecklistItem("Validate dates and budget"),
                ChecklistItem("Confirm room category"),
                ChecklistItem("Check insurance"),
            ],
            risks=[RiskItem("Noise", "Request quiet room")],
        )


# =========================================================
# RENDERER
# =========================================================

def render_dual_lane(report: DualLaneReport) -> str:
    lines = [
        "# Atlas Overlay Protocol Report",
        f"- Topic: {report.request.topic}",
        "",
        "## Ethics",
    ]

    for n in report.ethical.pluralism_notes:
        lines.append(f"- {n}")

    lines.append("\n## [ATLAS LANE]")
    for b in report.atlas.summary_bullets:
        lines.append(f"- {b}")

    lines.append("\n## [COPILOT LANE]")
    for k, v in report.copilot.snapshot.items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines)


# =========================================================
# FASTAPI ADAPTER (TEAMS / COPILOT)
# =========================================================

app = FastAPI(title="Atlas Protocol Enterprise Demo", version="1.0")

class OptionIn(BaseModel):
    name: str
    metadata: Dict[str, Any] = {}
    scores: Dict[str, List[Any]] = {}


class AtlasRunRequest(BaseModel):
    request: Dict[str, Any]
    options: List[OptionIn]
    snapshot: Optional[Dict[str, str]] = None


class AtlasRunResponse(BaseModel):
    markdown: str
    report: Dict[str, Any]


@app.post("/atlas/run", response_model=AtlasRunResponse)
def run_atlas(payload: AtlasRunRequest):
    try:
        req_dict = payload.request
        req_dict["mode"] = Mode(req_dict.get("mode", "dual_lane"))
        request = TravelRequest(**req_dict)

        options = []
        for o in payload.options:
            scores = {k: (v[0], v[1]) for k, v in o.scores.items()}
            options.append(Option(o.name, o.metadata, scores))

        provider = StaticEvidenceProvider()
        options = provider.enrich_options(request, options)
        evidence = provider.get_evidence(request, options)

        assumptions = provider.assumptions()

        engine = AtlasEngine()
        report = engine.run(
            request,
            options,
            assumptions,
            evidence,
            payload.snapshot or {},
        )

        return AtlasRunResponse(
            markdown=render_dual_lane(report),
            report=asdict(report),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



pip install fastapi uvicorn
uvicorn atlas_protocol_enterprise:app --reload --port 8000

http://localhost:8000/atlas/run
