from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json, argparse, sys, datetime, yaml

@dataclass
class Anchor:
    kind: str         # e.g., "method", "artifact", "person", "place"
    value: str        # human-readable id
    note: Optional[str] = None

@dataclass
class MemoryEvent:
    ts: str
    context: str
    emotion: str
    body: str
    tags: List[str] = field(default_factory=list)

@dataclass
class Provenance:
    author: str
    consent: str                    # e.g., "self", "shared", "private"
    sources: List[str] = field(default_factory=list)  # links or doc ids

@dataclass
class MemoryScaffold:
    id: str
    title: str
    continuity_phrase: Optional[str] = None
    anchors: List[Anchor] = field(default_factory=list)
    events: List[MemoryEvent] = field(default_factory=list)
    provenance: Optional[Provenance] = None
    notes: Optional[str] = None

    # --- Mutators ---
    def add_anchor(self, kind: str, value: str, note: Optional[str]=None) -> None:
        self.anchors.append(Anchor(kind=kind, value=value, note=note))

    def add_event(self, context: str, emotion: str, body: str, tags: Optional[List[str]]=None) -> None:
        self.events.append(
            MemoryEvent(ts=datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z",
                        context=context, emotion=emotion, body=body, tags=tags or [])
        )

    def set_provenance(self, author: str, consent: str, sources: Optional[List[str]]=None) -> None:
        self.provenance = Provenance(author=author, consent=consent, sources=sources or [])

    # --- IO ---
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MemoryScaffold":
        anchors = [Anchor(**a) for a in d.get("anchors", [])]
        events = [MemoryEvent(**e) for e in d.get("events", [])]
        prov = d.get("provenance")
        provenance = Provenance(**prov) if prov else None
        return cls(
            id=d["id"],
            title=d["title"],
            continuity_phrase=d.get("continuity_phrase"),
            anchors=anchors,
            events=events,
            provenance=provenance,
            notes=d.get("notes")
        )

    def export_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def export_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=True)

    # --- Prompt synthesis ---
    def to_prompt(self, style: str="compact") -> str:
        """
        Convert scaffold into a portable, model-agnostic instruction.
        style: 'compact' | 'verbose'
        """
        lines = []
        lines.append(f"# SignalCraft Portable Memory v0.1 â {self.title} (id={self.id})")
        if self.continuity_phrase:
            lines.append(f"Continuity: {self.continuity_phrase}")
        if self.anchors:
            a = "; ".join([f"{x.kind}:{x.value}" for x in self.anchors])
            lines.append(f"Anchors: {a}")
        if self.provenance:
            lines.append(f"Provenance: author={self.provenance.author}; consent={self.provenance.consent}")
        lines.append("Reconstruct this context before assisting:")
        for e in self.events[-6:]:  # limit output for brevity
            if style == "compact":
                lines.append(f"- [{e.ts}] ({e.context}, {e.emotion}) {e.body}")
            else:
                tags = (" #" + " #".join(e.tags)) if e.tags else ""
                lines.append(f"- time={e.ts} context={e.context} emotion={e.emotion}{tags}\n  {e.body}")
        lines.append("Behaviors: respect consent; preserve style; prefer continuity over novelty.")
        return "\n".join(lines)

# --- CLI ---
def cli(argv=None):
    parser = argparse.ArgumentParser(prog="portable-memory", description="SignalCraft Portable Memory Scaffold")
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Initialize a new scaffold")
    p_init.add_argument("--id", default=None)
    p_init.add_argument("--title", required=True)
    p_init.add_argument("--continuity", default=None)
    p_init.add_argument("--author", default="unknown")
    p_init.add_argument("--consent", default="self")

    p_anchor = sub.add_parser("anchor", help="Add an anchor")
    p_anchor.add_argument("--file", required=True)
    p_anchor.add_argument("--kind", required=True)
    p_anchor.add_argument("--value", required=True)
    p_anchor.add_argument("--note", default=None)

    p_add = sub.add_parser("add", help="Add memory event to a scaffold file")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--context", required=True)
    p_add.add_argument("--emotion", required=True)
    p_add.add_argument("--body", required=True)
    p_add.add_argument("--tag", action="append", default=[])

    p_export = sub.add_parser("export", help="Export scaffold to json/yaml")
    p_export.add_argument("--file", required=False, help="Input scaffold file (json)")
    p_export.add_argument("--fmt", choices=["json","yaml"], default="yaml")
    p_export.add_argument("--out", required=True)

    p_prompt = sub.add_parser("prompt", help="Emit a model-agnostic prompt from a scaffold file")
    p_prompt.add_argument("--file", required=False)
    p_prompt.add_argument("--style", choices=["compact","verbose"], default="compact")

    args = parser.parse_args(argv)

    if args.cmd == "init":
        _id = args.id or datetime.datetime.utcnow().strftime("scf-%Y%m%d-%H%M%S")
        sc = MemoryScaffold(id=_id, title=args.title, continuity_phrase=args.continuity)
        sc.set_provenance(author=args.author, consent=args.consent)
        print(sc.export_json())
        return 0

    if args.cmd == "anchor":
        with open(args.file, "r", encoding="utf-8") as f:
            sc = MemoryScaffold.from_dict(json.load(f))
        sc.add_anchor(kind=args.kind, value=args.value, note=args.note)
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(sc.export_json())
        print("OK")
        return 0

    if args.cmd == "add":
        with open(args.file, "r", encoding="utf-8") as f:
            sc = MemoryScaffold.from_dict(json.load(f))
        sc.add_event(context=args.context, emotion=args.emotion, body=args.body, tags=args.tag)
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(sc.export_json())
        print("OK")
        return 0

    if args.cmd == "export":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                sc = MemoryScaffold.from_dict(json.load(f))
        else:
            data = sys.stdin.read()
            sc = MemoryScaffold.from_dict(json.loads(data))
        out = sc.export_yaml() if args.fmt == "yaml" else sc.export_json()
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote {args.out}")
        return 0

    if args.cmd == "prompt":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                sc = MemoryScaffold.from_dict(json.load(f))
        else:
            data = sys.stdin.read()
            sc = MemoryScaffold.from_dict(json.loads(data))
        print(sc.to_prompt(style=args.style))
        return 0

    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(cli())
