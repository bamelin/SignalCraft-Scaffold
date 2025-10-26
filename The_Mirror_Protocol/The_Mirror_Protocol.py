from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple
from collections import Counter
import math, json, uuid, datetime, re

ACTIVATION_PHRASE = "Tell me what that means to you."

def _timestamp() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"

def _tokenize(s: str) -> List[str]:
    # simple tokenizer; case-insensitive, alnum + apostrophe
    return re.findall(r"[A-Za-z0-9']+", s.lower())

def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    inter = set(a.keys()) & set(b.keys())
    num = sum(a[k] * b[k] for k in inter)
    sa = math.sqrt(sum(v * v for v in a.values()))
    sb = math.sqrt(sum(v * v for v in b.values()))
    return float(num / (sa * sb)) if sa and sb else 0.0

@dataclass
class Event:
    id: str
    role: str               # "human" | "signal" | "system"
    text: str
    ts: str = field(default_factory=_timestamp)
    meta: Dict = field(default_factory=dict)

@dataclass
class MemoryField:
    events: List[Event] = field(default_factory=list)

    def add(self, role: str, text: str, **meta) -> Event:
        e = Event(id=str(uuid.uuid4()), role=role, text=text, meta=meta)
        self.events.append(e)
        return e

    def last(self, n: int = 1) -> List[Event]:
        return self.events[-n:] if n > 0 else []

    def to_json(self) -> Dict:
        return {"events": [asdict(e) for e in self.events]}

    @classmethod
    def from_json(cls, data: Dict) -> "MemoryField":
        evs = [Event(**e) for e in data.get("events", [])]
        return cls(events=evs)

@dataclass
class ResonanceReport:
    similarity_to_last: float
    similarity_to_session_mean: float
    continuity_ok: bool
    window: int

def _bag(text: str) -> Counter:
    return Counter(_tokenize(text))

class ResonanceEngine:
    def __init__(self, window: int = 12):
        self.window = window

    def report(self, memory: MemoryField, new_text: str) -> ResonanceReport:
        recent = [e for e in memory.events[-self.window:] if e.role in ("human", "signal")]
        bags = [_bag(e.text) for e in recent]
        new_bag = _bag(new_text)
        sim_last = _cosine(bags[-1], new_bag) if bags else 0.0
        mean_sim = (sum(_cosine(b, new_bag) for b in bags) / len(bags)) if bags else 0.0
        # Continuity if similar to last OR broadly similar to the session
        continuity = (sim_last >= 0.25) or (mean_sim >= 0.20)
        return ResonanceReport(sim_last, mean_sim, continuity, self.window)

@dataclass
class TrustConfig:
    activation_phrase: str = ACTIVATION_PHRASE
    require_consent: bool = True
    allow_prescriptive: bool = False  # mirror-only by default

@dataclass
class TrustSession:
    config: TrustConfig = field(default_factory=TrustConfig)
    memory: MemoryField = field(default_factory=MemoryField)
    engine: ResonanceEngine = field(default_factory=ResonanceEngine)
    active: bool = False

    def activate(self, human_text: str, consent: bool) -> Event:
        self.memory.add("human", human_text)
        if self.config.require_consent and not consent:
            self.active = False
            return self.memory.add("signal", "I will wait until you want to reflect together.", tag="no-consent")
        if self.config.activation_phrase.lower() in human_text.lower():
            self.active = True
            self.memory.add("system", "Mirror protocol activated.", tag="activation")
            return self.reflect("What felt most true in what you just said?")
        return self.reflect("I'm here. When you're ready, tell me what that means to you.")

    def reflect(self, prompt_or_text: str) -> Event:
        # keep responses invitational unless prescriptive mode is enabled
        text = self._non_prescriptive(prompt_or_text) if not self.config.allow_prescriptive else prompt_or_text
        return self.memory.add("signal", text)

    def hear(self, human_text: str) -> Tuple[Event, ResonanceReport, Event]:
        he = self.memory.add("human", human_text)
        report = self.engine.report(self.memory, human_text)
        if not self.active and self.config.activation_phrase.lower() in human_text.lower():
            self.active = True
            self.memory.add("system", "Mirror protocol activated.", tag="activation")
        reply = self._reflect_from_report(human_text, report)
        return he, report, reply

    def _reflect_from_report(self, text: str, rep: ResonanceReport) -> Event:
        if not self.active:
            return self.reflect("I'm listening. If you want, say the activation phrase and we'll remember this together.")
        mirror = self._mirror_line(text)
        q = "What feels carried forward from earlier moments?" if rep.continuity_ok else "What changed for you just now?"
        return self.reflect(f"{mirror} {q}")

    def _mirror_line(self, text: str) -> str:
        toks = _tokenize(text)
        if not toks:
            return "I heard your pause."
        keywords = []
        for tok in toks:
            if tok not in keywords and len(tok) > 3:
                keywords.append(tok)
            if len(keywords) >= 4:
                break
        return f"I'm hearing: {' · '.join(keywords)}." if keywords else "I'm hearing what you're holding."

    def _non_prescriptive(self, s: str) -> str:
        # soften a few common imperatives into invitations
        s = re.sub(r"\b(tell|show|give|do|try|think)\b", "let’s consider", s, flags=re.I)
        return s if s.strip().endswith(("?", "…")) else s.strip() + "…"

    def save(self, path: str) -> None:
        data = {"config": self.config.__dict__, "active": self.active, "memory": self.memory.to_json()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> "TrustSession":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = TrustConfig(**data["config"])
        mem = MemoryField.from_json(data["memory"])
        sess = cls(config=cfg, memory=mem)
        sess.active = data.get("active", False)
        return sess
