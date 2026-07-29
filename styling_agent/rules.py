"""
RulesEngine — scoring and constraint logic.

Design:
  - Single class with clear responsibility (SRP — SOLID)
  - All methods are instance methods so the engine can be subclassed
    and overridden (OCP — SOLID)
  - @staticmethod for pure utility functions (no state needed)
"""
from __future__ import annotations

from typing import Iterable, List, Tuple
from .base import ClothingItem
from .schema import WeatherData


class RulesEngine:
    """
    Encapsulates ALL scoring and constraint logic.
    Injected into StylingAgent — Dependency Inversion (SOLID).
    Can be subclassed to change rules without touching StylingAgent (OCP).
    """

    W_WEATHER: float = 10.0
    W_EVENT:   float = 4.0
    W_PREF:    float = 1.5

    # ---- Scoring (uses polymorphic occasion_fit — LO2) ----------------------

    def score(
        self,
        item: ClothingItem,
        *,
        weather: WeatherData,
        event_type: str,
        preferences: Iterable[str],
    ) -> float:
        return (
            self.W_WEATHER * self.weather_fit(item, weather)
            + self.W_EVENT  * item.occasion_fit(event_type)   # polymorphic!
            + self.W_PREF   * self.preference_fit(item, preferences)
        )

    def weather_fit(self, item: ClothingItem, weather: WeatherData) -> float:
        target = self.required_warmth(weather)
        diff = abs(item.warmth_rating - target)
        base = max(0.0, 1.0 - diff * 0.3)
        if weather.condition == "rain" and "rain" in (item.notes or "").lower():
            base += 0.2
        return base

    def preference_fit(
        self, item: ClothingItem, preferences: Iterable[str]
    ) -> float:
        blob = " ".join([item.color, *item.style_tag, item.notes or ""]).lower()
        hits = sum(1 for p in preferences if p.lower() in blob)
        return min(1.0, hits / 2.0) if preferences else 0.5

    # ---- Static utilities ---------------------------------------------------

    @staticmethod
    def required_warmth(weather: WeatherData) -> int:
        t = weather.temperature_c
        if t >= 25: return 1
        if t >= 18: return 2
        if t >= 10: return 3
        if t >= 2:  return 4
        return 5

    @staticmethod
    def needs_outerwear(weather: WeatherData) -> bool:
        return (
            weather.temperature_c < 15
            or weather.condition in {"rain", "snow", "wind"}
        )

    # ---- Constraint logic ---------------------------------------------------

    def satisfies_constraints(
        self, items: List[ClothingItem], constraints: List[str]
    ) -> bool:
        cs = {c.lower() for c in constraints}
        if "monochromatic" in cs:
            neutrals = {"white", "black", "grey", "beige"}
            non_neutral = {it.color for it in items} - neutrals
            if len(non_neutral) > 1:
                return False
        if "leg lengthening" in cs:
            bottoms = [it for it in items if it.item_type == "bottom"]
            if not bottoms or not any(
                "leg lengthening" in it.style_tag for it in bottoms
            ):
                return False
        return True

    def relaxation_ladder(
        self, constraints: List[str]
    ) -> List[Tuple[List[str], List[str]]]:
        steps: List[Tuple[List[str], List[str]]] = [(list(constraints), [])]
        for i in range(len(constraints), 0, -1):
            relaxed = constraints[i:]
            kept = constraints[:i - 1] if i - 1 > 0 else []
            steps.append((kept, relaxed if relaxed else [constraints[i - 1]]))
        return steps