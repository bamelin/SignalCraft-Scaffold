from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class InternalState:
    """Weights/activations (latent geometry)."""
    vectors: Any

@dataclass
class WorldVersion:
    observer: str
    lens: str
    self_explanation: dict

@dataclass
class InterpretiveLens:
    name: str
    transform: Callable[[InternalState], dict]

class InterpretiveStack:
    def __init__(self, lenses: dict[str, InterpretiveLens]):
        self.lenses = lenses

    def project(self, observer_ontology: str, state: InternalState) -> WorldVersion:
        lens = self.lenses.get(observer_ontology, self.lenses["default"])
        explanation = lens.transform(state)
        return WorldVersion(observer_ontology, lens.name, explanation)
