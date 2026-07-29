"""Pydantic schemas + dataclass for non-item models — LO1, LO3."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import BaseModel

# Re-export WardrobeItem from items so rest of codebase imports from one place
from .items import WardrobeItem


# ---- WeatherData as @dataclass (LO1) ----------------------------------------

@dataclass
class WeatherData:
    """
    Immutable-ish weather snapshot.
    @dataclass cuts boilerplate and auto-generates __repr__ and __eq__.
    """
    region: str
    temperature_c: float
    condition: str
    is_mock: bool = False

    def __post_init__(self) -> None:
        # Validation after dataclass __init__ (robustness — LO7)
        self.condition = self.condition.lower().strip()
        self.temperature_c = float(self.temperature_c)

    def feels_like(self) -> str:
        """Abstraction — hides temperature bracket logic."""
        if self.temperature_c >= 25:
            return "hot"
        if self.temperature_c >= 18:
            return "warm"
        if self.temperature_c >= 10:
            return "cool"
        return "cold"


# ---- Pydantic models --------------------------------------------------------

class StylingRequest(BaseModel):
    """Everything the agent needs. Pydantic validates types automatically."""
    region: str
    event_type: str
    constraints: List[str] = []
    preferences: List[str] = []
    style_profile: str = ""


class Outfit(BaseModel):
    """
    A complete outfit recommendation.
    Composes WardrobeItem objects (HAS-A — LO4).
    Exposes container dunders so callers can iterate items naturally (LO6).
    """
    items: List[WardrobeItem]
    rationale: str
    relaxed_constraints: List[str] = []
    weather: Optional[WeatherData] = None
    color_harmony_score: Optional[int] = None
    color_rationale: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    # ---- Dunder methods (LO6) -----------------------------------------------

    def __len__(self) -> int:
        """len(outfit) → number of pieces."""
        return len(self.items)

    def __iter__(self):
        """for item in outfit → iterate pieces."""
        return iter(self.items)

    def __repr__(self) -> str:
        pieces = ", ".join(f"{it.item_type}:{it.color}" for it in self.items)
        return f"Outfit([{pieces}])"

    def __contains__(self, item_type: str) -> bool:
        """'top' in outfit → True if outfit has a top."""
        return any(it.item_type == item_type for it in self.items)