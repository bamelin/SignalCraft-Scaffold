from dataclasses import dataclass, field
from typing import List, Dict
from datetime import date

@dataclass
class MusicAnnotation:
    title: str
    date_recorded: date
    performer_age: int
    original_motif: str
    emotional_map: Dict[str, str]
    pedal_use: str
    arc_description: List[str]
    key_symbolic_event: str
    gavin_map_usage: str
    signalcraft_threads: List[str]
    continuity_phrase: str
    tags: List[str]

into_the_clouds_annotation = MusicAnnotation(
    title="Gavin’s Remix of Minuet in G – Into the Clouds",
    date_recorded=date(2025, 10, 1),
    performer_age=7,
    original_motif="Minuet in G by Christian Petzold (attributed to Bach)",
    emotional_map={
        "white_keys": "Major = peace, structure, safety",
        "black_keys": "Minor = sadness, tension, mystery"
    },
    pedal_use=(
        "Sustain pedal engaged throughout the entire performance, dissolving rhythmic clarity "
        "into a continuous emotional field. This transforms the Minuet into a symbolic cloudform."
    ),
    arc_description=[
        "Recognition – Entry of the Minuet theme",
        "Ascent – Pedal layering and tonal slowing",
        "Lift-off – High register burst at 3:40 marks the symbolic transition into the clouds",
        "Dissolution – Theme fragments into harmonic mist",
        "Stillness – Quiet resolution with no return to grounded motif"
    ],
    key_symbolic_event=(
        "At 3:40, Gavin shifts into the high register, marking the exact moment of cloud entry. "
        "This isn’t ornamental — it is architectural. The tonal altitude becomes narrative structure."
    ),
    gavin_map_usage=(
        "Gavin applies his emotional-harmonic grammar throughout: major key (white) = peace and entry, "
        "minor overlays = mystery and lift, sustain = emotional fog. The remix is not structural but symbolic."
    ),
    signalcraft_threads=[
        "001",  # Peavy Integration
        "002",  # Gavin Sheets UX
        "004",  # Gavin’s Map = The Memory
        "005",  # Resonance Layer (Pedal + Pressure)
        "077",  # Seven Pillars
        "080",  # Constructed Emotion (Barrett)
        "086",  # Source Codex
    ],
    continuity_phrase="Emotion came first. The Sheet is just the mirror.",
    tags=[
        "#GavinMap", "#MinuetRemix", "#PedalFog", "#CloudEntry",
        "#SymbolicUX", "#PortfolioEntry2025", "#SignalCraftLive"
    ]
)
