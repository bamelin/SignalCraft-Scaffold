"""
Atlas Overlay Protocol (AOP)
Two-lane travel reasoning scaffold:
- Atlas Lane: curation + recommendation + vibe-fit
- Copilot Lane: planning + execution + risk + checklist
With a federated ethical overlay ("SignalCraft") and continuity memory.

Design goals:
- deterministic structure (auditable tables + weights)
- transparent assumptions
- mode control (light / dual-lane / deep-dive)
- persistence (interconversational preferences + decisions)

No external dependencies (standard library only).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple
import json
import math
import os


# ----------------------------
# Core Types
# ----------------------------

class Mode(str, Enum):
    LIGHT = "light"          # concise, minimal tables
    DUAL_LANE = "dual_lane"  # both lanes, default tables + checklists
    DEEP_DIVE = "deep_dive"  # expanded evidence + sensitivity + more assumptions


@dataclass(frozen=True)
class Citation:
    source_name: str
    url: Optional[str] = None
    note: Optional[str] = None


@dataclass
class EvidenceItem:
    claim: str
    citations: List[Citation] = field(default_factory=list)
    time_sensitive: bool = True  # if True, treat as needing validation if stale


@dataclass
class RiskItem:
    risk: str
    mitigation: str
    severity: int = 3  # 1-5


@dataclass
class ChecklistItem:
    step: str
    why: Optional[str] = None


@dataclass(frozen=True)
class Criterion:
    name: str
    # weight is % points; engine enforces sum=100 after normalization
    weight: float
    # 1..10 scoring
    min_score: int = 1
    max_score: int = 10


@dataclass
class Option:
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    # criterion_name -> (score 1..10, note)
    scores: Dict[str, Tuple[float, str]] = field(default_factory=dict)


@dataclass
class TravelRequest:
    # user intent + constraints
    topic: str
    travelers: str = "unspecified"
    dates: Optional[str] = None
    budget: Optional[str] = None
    departure_airport: Optional[str] = None
    destination: Optional[str] = None

    # override weights if user supplies priorities
    priorities: Dict[str, float] = field(default_factory=dict)

    # mode control
    mode: Mode = Mode.DUAL_LANE

    # whether user explicitly wants minimal citations
    minimal_citations: bool = True


@dataclass
class AtlasPreferences:
    """
    Persisted continuity.
    Keep it small + practical: vibe, budget tiers, airline baggage rules,
    noise sensitivity, mobility constraints, etc.
    """
    vibe: Optional[str] = None
    noise_sensitivity: Optional[str] = None
    dining_priority: Optional[str] = None
    budget_tier: Optional[str] = None
    favorite_brands: List[str] = field(default_factory=list)
    avoid_brands: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def merge(self, updates: Dict[str, Any]) -> "AtlasPreferences":
        data = asdict(self)
        for k, v in updates.items():
            if k not in data:
                continue
            if isinstance(data[k], list) and isinstance(v, list):
                data[k] = list(dict.fromkeys(data[k] + v))
            else:
                data[k] = v
        return AtlasPreferences(**data)


@dataclass
class DecisionLogEntry:
    timestamp_utc: str
    request_topic: str
    recommendation: str
    rationale: str
    weights: Dict[str, float]


# ----------------------------
# Memory (Continuity Layer)
# ----------------------------

class MemoryStore:
    def load_preferences(self) -> AtlasPreferences:
        raise NotImplementedError

    def save_preferences(self, prefs: AtlasPreferences) -> None:
        raise NotImplementedError

    def append_decision(self, entry: DecisionLogEntry) -> None:
        raise NotImplementedError

    def recent_decisions(self, limit: int = 10) -> List[DecisionLogEntry]:
        raise NotImplementedError


class JsonFileMemoryStore(MemoryStore):
    """
    Simple local persistence.
    For Teams/Copilot deployment, swap this for:
      - Cosmos DB / DynamoDB
      - SharePoint list
      - Postgres
      - Redis
    """
    def __init__(self, path: str = "atlas_memory.json") -> None:
        self.path = path

    def _read(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"preferences": asdict(AtlasPreferences()), "decisions": []}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_preferences(self) -> AtlasPreferences:
        data = self._read()
        return AtlasPreferences(**(data.get("preferences") or {}))

    def save_preferences(self, prefs: AtlasPreferences) -> None:
        data = self._read()
        data["preferences"] = asdict(prefs)
        self._write(data)

    def append_decision(self, entry: DecisionLogEntry) -> None:
        data = self._read()
        data.setdefault("decisions", []).append(asdict(entry))
        self._write(data)

    def recent_decisions(self, limit: int = 10) -> List[DecisionLogEntry]:
        data = self._read()
        items = (data.get("decisions") or [])[-limit:]
        return [DecisionLogEntry(**x) for x in items]


# ----------------------------
# Ethical Overlay (SignalCraft)
# ----------------------------

@dataclass
class EthicalAssessment:
    pluralism_notes: List[str] = field(default_factory=list)
    harm_minimization_notes: List[str] = field(default_factory=list)
    transparency_notes: List[str] = field(default_factory=list)
    autonomy_notes: List[str] = field(default_factory=list)
    hard_blocks: List[str] = field(default_factory=list)  # if non-empty, stop


class SignalCraftOverlay:
    """
    Federated ethical topoi:
    - Pluralism & Constructivism
    - Harm-Minimization
    - Transparency
    - Autonomy Respect
    """
    def assess(
        self,
        request: TravelRequest,
        options: List[Option],
        assumptions: Dict[str, str],
        evidence: List[EvidenceItem],
    ) -> EthicalAssessment:
        a = EthicalAssessment()

        # Pluralism & Constructivism: ensure at least 2 viable alternates if possible
        if len(options) >= 2:
            a.pluralism_notes.append("Multiple options preserved to honor user-specific values.")
        else:
            a.pluralism_notes.append("Only one option supplied; recommend adding alternates to preserve choice.")

        # Harm minimization (financial): flag if budget missing and prices are implied
        if request.budget is None:
            a.harm_minimization_notes.append("Budget not specified; avoid over-committing user to high-cost assumptions.")

        # Transparency: require weights + assumptions to be surfaced
        if not assumptions:
            a.transparency_notes.append("No explicit assumptions provided; add assumptions to keep scoring auditable.")

        # Autonomy: prohibit coercive framing by requiring at least one 'choose if...' alternate
        a.autonomy_notes.append("Output must include 'choose if…' alternates to preserve user autonomy.")

        # Hard blocks (example): unsafe / illegal requests could be blocked here
        # (We keep it minimal; expand as needed.)
        return a


# ----------------------------
# Scoring Engine
# ----------------------------

def normalize_weights(criteria: List[Criterion]) -> List[Criterion]:
    total = sum(c.weight for c in criteria)
    if total <= 0:
        raise ValueError("Total weight must be > 0.")
    # Normalize to exactly 100.0
    normalized = []
    for c in criteria:
        normalized.append(Criterion(name=c.name, weight=(c.weight / total) * 100.0))
    # Fix rounding drift by adjusting the largest weight
    drift = 100.0 - sum(c.weight for c in normalized)
    if abs(drift) > 1e-9:
        idx = max(range(len(normalized)), key=lambda i: normalized[i].weight)
        normalized[idx] = Criterion(
            name=normalized[idx].name,
            weight=normalized[idx].weight + drift
        )
    return normalized


def bounded_score(score: float, min_v: int = 1, max_v: int = 10) -> float:
    return max(min_v, min(max_v, score))


@dataclass
class ScoredOption:
    option: Option
    weighted_total: float
    breakdown: List[Tuple[str, float, float, str]]  # (criterion, weight%, score, note)


class WeightedScorer:
    def score(self, criteria: List[Criterion], options: List[Option]) -> List[ScoredOption]:
        criteria = normalize_weights(criteria)
        scored: List[ScoredOption] = []

        for opt in options:
            total = 0.0
            breakdown: List[Tuple[str, float, float, str]] = []
            for c in criteria:
                s, note = opt.scores.get(c.name, (5.0, "Defaulted (no score provided)."))
                s = bounded_score(float(s), c.min_score, c.max_score)
                total += (c.weight / 100.0) * s
                breakdown.append((c.name, c.weight, s, note))
            scored.append(ScoredOption(option=opt, weighted_total=total, breakdown=breakdown))

        scored.sort(key=lambda x: x.weighted_total, reverse=True)
        return scored


# ----------------------------
# Report Models (Two Lanes)
# ----------------------------

@dataclass
class AtlasLaneReport:
    summary_bullets: List[str]
    weighted_table: List[Dict[str, Any]]  # row dicts for criterion comparisons
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
class DualLaneReport:
    request: TravelRequest
    preferences_used: AtlasPreferences
    criteria: List[Criterion]
    scored: List[ScoredOption]
    assumptions: Dict[str, str]
    ethical: EthicalAssessment
    atlas: Optional[AtlasLaneReport] = None
    copilot: Optional[CopilotLaneReport] = None


# ----------------------------
# Atlas Engine (Protocol Orchestrator)
# ----------------------------

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
    def __init__(
        self,
        memory: Optional[MemoryStore] = None,
        overlay: Optional[SignalCraftOverlay] = None,
        scorer: Optional[WeightedScorer] = None,
    ) -> None:
        self.memory = memory or JsonFileMemoryStore()
        self.overlay = overlay or SignalCraftOverlay()
        self.scorer = scorer or WeightedScorer()

    def _build_criteria(self, request: TravelRequest) -> List[Criterion]:
        criteria = list(DEFAULT_CRITERIA)

        # Reweight immediately if user supplies priorities
        if request.priorities:
            # Keep only known criteria by default; allow extension if desired
            known = {c.name for c in criteria}
            rebuilt: List[Criterion] = []
            for name, w in request.priorities.items():
                if name in known:
                    rebuilt.append(Criterion(name=name, weight=float(w)))
                else:
                    # Allow additive criteria if user supplies it
                    rebuilt.append(Criterion(name=name, weight=float(w)))
            criteria = rebuilt

        return normalize_weights(criteria)

    def run(
        self,
        request: TravelRequest,
        options: List[Option],
        *,
        assumptions: Optional[Dict[str, str]] = None,
        evidence: Optional[List[EvidenceItem]] = None,
        snapshot: Optional[Dict[str, str]] = None,
        comparison_factors: Optional[List[str]] = None,
    ) -> DualLaneReport:
        prefs = self.memory.load_preferences()

        assumptions = assumptions or {}
        evidence = evidence or []
        snapshot = snapshot or {}
        comparison_factors = comparison_factors or [
            "Total Estimated Cost",
            "Inclusions",
            "Nightlife Type",
            "Beach Conditions",
            "Room Type",
            "Cancellation Terms",
            "Transfer Time",
            "Notable Policies",
        ]

        criteria = self._build_criteria(request)
        scored = self.scorer.score(criteria, options)

        ethical = self.overlay.assess(request, options, assumptions, evidence)
        if ethical.hard_blocks:
            raise RuntimeError(f"Blocked by ethical overlay: {ethical.hard_blocks}")

        report = DualLaneReport(
            request=request,
            preferences_used=prefs,
            criteria=criteria,
            scored=scored,
            assumptions=assumptions,
            ethical=ethical,
        )

        if request.mode == Mode.LIGHT:
            # Light mode: lane outputs optional/minimal
            report.atlas = self._atlas_lane(report, minimal=True)
            report.copilot = None
        else:
            report.atlas = self._atlas_lane(report, minimal=False)
            report.copilot = self._copilot_lane(
                report,
                evidence=evidence,
                snapshot=snapshot,
                comparison_factors=comparison_factors,
                minimal_citations=request.minimal_citations and request.mode != Mode.DEEP_DIVE,
            )

        # Persist decision (top recommendation) for continuity
        if scored:
            top = scored[0]
            entry = DecisionLogEntry(
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                request_topic=request.topic,
                recommendation=top.option.name,
                rationale=f"Top weighted score {top.weighted_total:.2f}/10 driven by highest weights.",
                weights={c.name: c.weight for c in criteria},
            )
            self.memory.append_decision(entry)

        return report

    def _atlas_lane(self, report: DualLaneReport, minimal: bool) -> AtlasLaneReport:
        scored = report.scored
        if not scored:
            return AtlasLaneReport(
                summary_bullets=["No options were provided to score."],
                weighted_table=[],
                top_pick="N/A",
                top_pick_rationale="N/A",
                alternates=[],
                pacing_notes=[],
            )

        top = scored[0]
        alternates = []
        for alt in scored[1:3]:
            alternates.append(f"{alt.option.name} — choose if it better matches your vibe/constraints.")

        # Weighted scoring table rows
        table_rows: List[Dict[str, Any]] = []
        for (crit, w, _, _) in top.breakdown:
            row = {"Criterion": crit, "Weight (%)": round(w, 2)}
            for s in scored[:3]:
                score_val, note = s.option.scores.get(crit, (5.0, "Defaulted."))
                row[s.option.name] = round(float(score_val), 2)
                if report.request.mode != Mode.LIGHT:
                    row[f"{s.option.name} Notes"] = note
            table_rows.append(row)

        # Summary bullets (2–4)
        summary = [
            f"Best fit (by weights): {top.option.name} ({top.weighted_total:.2f}/10).",
            "Strengths align to the highest-weighted criteria (explicitly shown in the scoring table).",
        ]
        if report.request.budget is None:
            summary.append("Watch-out: budget not specified, so price/value assumptions are conservative.")
        if len(summary) < 4 and report.preferences_used.noise_sensitivity:
            summary.append(f"Preference noted: noise sensitivity = {report.preferences_used.noise_sensitivity}.")

        pacing_notes = [
            "If traveling in peak season, hold rooms ASAP (24–72h windows where possible).",
            "Recheck promo + baggage fees before ticketing; small policy shifts swing total cost.",
        ]
        if report.request.mode == Mode.DEEP_DIVE:
            pacing_notes.append("Deep-dive: run sensitivity (±10–20% on the highest weights) to confirm robustness.")

        # Rationale tied to high weights: list top 2 criteria by weight
        top_criteria = sorted(report.criteria, key=lambda c: c.weight, reverse=True)[:2]
        drivers = ", ".join([f"{c.name} ({c.weight:.0f}%)" for c in top_criteria])
        rationale = (
            f"Recommendation is driven primarily by: {drivers}. "
            f"Weighted total {top.weighted_total:.2f}/10 reflects those priorities."
        )

        return AtlasLaneReport(
            summary_bullets=summary if not minimal else summary[:2],
            weighted_table=table_rows if not minimal else table_rows[:3],
            top_pick=top.option.name,
            top_pick_rationale=rationale,
            alternates=alternates if not minimal else alternates[:1],
            pacing_notes=pacing_notes if not minimal else pacing_notes[:1],
        )

    def _copilot_lane(
        self,
        report: DualLaneReport,
        *,
        evidence: List[EvidenceItem],
        snapshot: Dict[str, str],
        comparison_factors: List[str],
        minimal_citations: bool,
    ) -> CopilotLaneReport:
        scored = report.scored
        options = [s.option for s in scored[:3]]

        # Evidence: keep minimal by default; expand in deep-dive
        ev_out = evidence
        if minimal_citations:
            ev_out = evidence[:3]

        # Comparison scorecard: factor rows (Option A/B/C)
        scorecard: List[Dict[str, Any]] = []
        for f in comparison_factors:
            row = {"Factor": f}
            for opt in options:
                row[opt.name] = opt.metadata.get(f, "TBD")
            scorecard.append(row)

        checklist = [
            ChecklistItem("Validate dates and budget ceiling", "Avoid anchoring decisions on unstated constraints."),
            ChecklistItem("Confirm room category & bed configuration", "Room class mismatch is the #1 trip friction."),
            ChecklistItem("Hold availability (24–72h) or add watchlist", "Prevents price drift while deciding."),
            ChecklistItem("Price-protect: check promotions & baggage fees", "Small fee deltas swing total cost."),
            ChecklistItem("Insurance check (medical, CFAR if relevant)", "Protects downside risk."),
            ChecklistItem("Book transfers & excursions (priority list)", "Locks key experiences early."),
            ChecklistItem("Pre-trip tasks: documents, apps, eSIM/roaming", "Reduces day-of-travel failure points."),
        ]

        risks = [
            RiskItem("Surf / beach conditions vary", "Check daily beach flags; plan pool days on red-flag days.", severity=3),
            RiskItem("Nightlife noise", "Select room away from clubs; request higher floor.", severity=3),
        ]

        if report.request.mode == Mode.DEEP_DIVE:
            risks.append(RiskItem("Policy drift (cancellation / baggage / resort fees)", "Re-verify 48h before final payment.", severity=4))

        return CopilotLaneReport(
            snapshot=snapshot,
            evidence=ev_out,
            comparison_scorecard=scorecard,
            checklist=checklist,
            risks=risks,
        )


# ----------------------------
# Rendering (Side-by-side output)
# ----------------------------

def render_dual_lane(report: DualLaneReport) -> str:
    """
    Render a single message containing both lanes.
    (In a Teams/Copilot integration, this becomes the assistant's final payload.)
    """
    lines: List[str] = []

    # Header
    lines.append(f"# Atlas Overlay Protocol Report")
    lines.append(f"- Topic: {report.request.topic}")
    lines.append(f"- Mode: {report.request.mode.value}")
    lines.append("")

    # Ethical overlay (small, auditable)
    lines.append("## SignalCraft Overlay (Ethics)")
    if report.ethical.hard_blocks:
        lines.append(f"- BLOCKED: {report.ethical.hard_blocks}")
        return "\n".join(lines)
    for n in report.ethical.pluralism_notes:
        lines.append(f"- Pluralism: {n}")
    for n in report.ethical.harm_minimization_notes:
        lines.append(f"- Harm-minimization: {n}")
    for n in report.ethical.transparency_notes:
        lines.append(f"- Transparency: {n}")
    for n in report.ethical.autonomy_notes:
        lines.append(f"- Autonomy: {n}")
    lines.append("")

    # Assumptions
    if report.assumptions:
        lines.append("## Assumptions (Explicit)")
        for k, v in report.assumptions.items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    # ATLAS LANE
    if report.atlas:
        lines.append("## [ATLAS LANE] Atlas Summary")
        for b in report.atlas.summary_bullets:
            lines.append(f"- {b}")

        lines.append("")
        lines.append("### Weighted Scoring (1–10)")
        # Render as a readable markdown table
        if report.atlas.weighted_table:
            # Determine columns
            cols = list(report.atlas.weighted_table[0].keys())
            lines.append("| " + " | ".join(cols) + " |")
            lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
            for r in report.atlas.weighted_table:
                lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
        else:
            lines.append("_No scoring table available._")

        lines.append("")
        lines.append("### Top Pick & Rationale")
        lines.append(f"- **#1 Recommendation:** {report.atlas.top_pick}")
        lines.append(f"- Rationale: {report.atlas.top_pick_rationale}")

        if report.atlas.alternates:
            lines.append("")
            lines.append("### Alternates")
            for a in report.atlas.alternates:
                lines.append(f"- {a}")

        if report.atlas.pacing_notes:
            lines.append("")
            lines.append("### Pacing Notes")
            for p in report.atlas.pacing_notes:
                lines.append(f"- {p}")

        lines.append("")

    # COPILOT LANE
    if report.copilot:
        lines.append("## [COPILOT LANE] Copilot Brief")

        if report.copilot.snapshot:
            lines.append("### Snapshot")
            for k, v in report.copilot.snapshot.items():
                lines.append(f"- **{k}:** {v}")

        if report.copilot.evidence:
            lines.append("")
            lines.append("### Evidence (time-sensitive claims)")
            for e in report.copilot.evidence:
                lines.append(f"- {e.claim}")
                for c in e.citations:
                    if c.url:
                        lines.append(f"  - Source: {c.source_name} ({c.url})")
                    else:
                        lines.append(f"  - Source: {c.source_name}")
                    if c.note:
                        lines.append(f"    - Note: {c.note}")

        lines.append("")
        lines.append("### Comparison Scorecard")
        if report.copilot.comparison_scorecard:
            cols = list(report.copilot.comparison_scorecard[0].keys())
            lines.append("| " + " | ".join(cols) + " |")
            lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
            for r in report.copilot.comparison_scorecard:
                lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")

        lines.append("")
        lines.append("### Action Checklist")
        for i, item in enumerate(report.copilot.checklist, start=1):
            if item.why:
                lines.append(f"{i}. {item.step} — _{item.why}_")
            else:
                lines.append(f"{i}. {item.step}")

        lines.append("")
        lines.append("### Risks & Mitigations")
        for r in sorted(report.copilot.risks, key=lambda x: x.severity, reverse=True):
            lines.append(f"- (Severity {r.severity}/5) {r.risk} → {r.mitigation}")

        lines.append("")

    return "\n".join(lines)


# ----------------------------
# Example Usage (Works now)
# ----------------------------

if __name__ == "__main__":
    engine = AtlasEngine(memory=JsonFileMemoryStore("atlas_memory.json"))

    req = TravelRequest(
        topic="Evaluate Riu Jalisco for 20-somethings",
        destination="Riviera Nayarit, Mexico",
        priorities={
            "Nightlife": 30,
            "Beach / Location": 20,
            "Price / Value": 20,
            "Dining / Bar": 10,
            "Room Quality": 10,
            "Safety / Reviews": 10,
        },
        mode=Mode.DUAL_LANE,
        minimal_citations=True,
    )

    # Options with example placeholder scoring.
    # In real usage, scoring can be:
    # - human-entered by the agent
    # - derived from review aggregates (careful: cite sources)
    # - derived from structured supplier data
    a = Option(
        name="Riu Jalisco",
        metadata={
            "Inclusions": "AI meals/drinks + some activities",
            "Transfer Time": "TBD",
            "Cancellation Terms": "TBD",
        },
        scores={
            "Nightlife": (8.5, "Lively onsite entertainment; can be noisy."),
            "Beach / Location": (7.5, "Swimmable but surf can vary."),
            "Price / Value": (8.0, "Strong value tier for social travelers."),
            "Dining / Bar": (6.5, "Solid AI; not luxury-level."),
            "Room Quality": (6.5, "Functional; not premium."),
            "Safety / Reviews": (7.0, "Generally positive; confirm current conditions."),
        }
    )

    b = Option(
        name="Riu Vallarta",
        metadata={"Inclusions": "AI meals/drinks", "Transfer Time": "TBD", "Cancellation Terms": "TBD"},
        scores={
            "Nightlife": (7.5, "Active but slightly calmer vibe."),
            "Beach / Location": (7.5, "Similar coastal conditions."),
            "Price / Value": (7.5, "Often slightly higher; depends on promos."),
            "Dining / Bar": (6.8, "Comparable AI tier."),
            "Room Quality": (6.8, "Comparable; sometimes a touch fresher."),
            "Safety / Reviews": (7.2, "Comparable; validate latest reviews."),
        }
    )

    c = Option(
        name="Riu Palace Pacifico",
        metadata={"Inclusions": "Higher-tier AI", "Transfer Time": "TBD", "Cancellation Terms": "TBD"},
        scores={
            "Nightlife": (6.5, "More upscale; less party-forward."),
            "Beach / Location": (7.8, "Good beach access; conditions vary."),
            "Price / Value": (6.2, "Higher price; value depends on priorities."),
            "Dining / Bar": (8.2, "Stronger dining tier."),
            "Room Quality": (8.5, "Higher-end rooms and finish."),
            "Safety / Reviews": (7.8, "Strong brand-tier consistency."),
        }
    )

    assumptions = {
        "Scoring scale": "1–10; 5 is neutral baseline.",
        "Weights": "User-supplied priorities normalized to 100%.",
        "Time-sensitive": "Entertainment schedule / renovations / policies require quick validation before booking.",
    }

    evidence = [
        EvidenceItem(
            claim="Entertainment schedule and resort policies can change seasonally; validate with current resort listing before ticketing.",
            citations=[Citation(source_name="Resort listing / supplier portal", url=None, note="Pull latest at booking time.")],
            time_sensitive=True,
        )
    ]

    snapshot = {
        "Location": "Nuevo Vallarta / Riviera Nayarit",
        "Category": "Family-friendly / social value-tier AI",
        "Typical budget range": "Varies by season; confirm live pricing",
        "Best months": "Depends on priorities (weather vs crowds vs pricing)",
    }

    report = engine.run(
        req,
        options=[a, b, c],
        assumptions=assumptions,
        evidence=evidence,
        snapshot=snapshot,
    )

    print(render_dual_lane(report))
