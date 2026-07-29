"""
StylingAgent — orchestrates the full recommendation pipeline.

Design:
  - StylingAgent uses COMPOSITION (has-a wardrobe, has-a scorer) — LO4
  - Conforms to the Recommender Protocol — LO5, DIP (SOLID)
  - LoggableMixin adds reusable logging — Mixin, SRP (SOLID)
  - _assemble() uses polymorphic occasion_fit() — LO2
"""
from __future__ import annotations

from typing import List, Optional

from .base import LoggableMixin, Recommender
from .schema import WardrobeItem, Outfit, StylingRequest, WeatherData
from .wardrobe import MOCK_WARDROBE
from .weather import get_weather
from .rules import RulesEngine
from .gemini import write_rationale, evaluate_color_harmony
from .exceptions import StylingError

SLOTS = ["top", "bottom", "shoes"]


class StylingAgent(LoggableMixin):
    """
    High-level recommender. Conforms to Recommender Protocol.

    Composition:
      - HAS-A wardrobe (list of WardrobeItem)
      - HAS-A RulesEngine (scoring + constraint logic)

    SOLID:
      - SRP: only orchestrates; scoring lives in RulesEngine
      - OCP: swap wardrobe or rules engine without touching this class
      - DIP: depends on abstractions (Recommender, RulesEngine), not concretions
    """

    def __init__(
        self,
        wardrobe: Optional[List[WardrobeItem]] = None,
        extra_wardrobe: Optional[List[WardrobeItem]] = None,
        rules: Optional["RulesEngine"] = None,
    ) -> None:
        base = wardrobe or MOCK_WARDROBE
        self._wardrobe: List[WardrobeItem] = base + (extra_wardrobe or [])
        self._rules: RulesEngine = rules or RulesEngine()   # DIP injection

    # ---- Public interface ---------------------------------------------------

    def recommend(self, request: StylingRequest) -> Outfit:
        """
        Main entry point.
        Conforms to Recommender Protocol — structural subtyping (LO5).
        """
        try:
            weather = get_weather(request.region)
        except Exception as exc:
            self.log(f"Weather fetch failed: {exc} — using mock")
            from .weather import _mock_weather
            weather = _mock_weather(request.region)

        # Walk constraint relaxation ladder (defined in RulesEngine)
        for kept, relaxed in self._rules.relaxation_ladder(request.constraints):
            outfit_items = self._assemble(request, weather, kept)
            if outfit_items and self._rules.satisfies_constraints(outfit_items, kept):
                return self._build_outfit(outfit_items, request, weather, kept, relaxed)

        # Last resort — no constraints
        items = self._assemble(request, weather, []) or []
        if not items:
            raise StylingError("Could not assemble any outfit from the wardrobe.")
        return self._build_outfit(items, request, weather, [], request.constraints)

    # ---- Private helpers (abstraction — LO2) --------------------------------

    def _build_outfit(
        self,
        items: List[WardrobeItem],
        request: StylingRequest,
        weather: WeatherData,
        kept: List[str],
        relaxed: List[str],
    ) -> Outfit:
        rationale = write_rationale(
            items, weather=weather, event_type=request.event_type,
            constraints=kept, preferences=request.preferences,
            relaxed=relaxed, style_profile=request.style_profile,
        )
        harmony = evaluate_color_harmony(items, style_profile=request.style_profile)
        return Outfit(
            items=items, rationale=rationale, relaxed_constraints=relaxed,
            weather=weather,
            color_harmony_score=harmony["harmony_score"],
            color_rationale=harmony["color_rationale"],
        )

    def _candidates(self, slot: str, event_type: str) -> List[WardrobeItem]:
        """Filter wardrobe by slot, preferring occasion matches."""
        slot_matches = [it for it in self._wardrobe if it.item_type == slot]
        occasion_matches = [
            it for it in slot_matches if event_type in it.occasion_suitability
        ]
        return occasion_matches or slot_matches

    def _assemble(
        self,
        request: StylingRequest,
        weather: WeatherData,
        constraints: List[str],
    ) -> List[WardrobeItem]:
        """
        Greedy slot fill using POLYMORPHIC occasion_fit() per item type.
        Each WardrobeItem subclass (Top, Bottom, Shoes...) scores differently — LO2.
        """
        slots = list(SLOTS)
        if self._rules.needs_outerwear(weather):
            slots.append("outerwear")

        chosen: List[WardrobeItem] = []
        for slot in slots:
            candidates = self._candidates(slot, request.event_type)
            if not candidates:
                continue
            best = max(
                candidates,
                key=lambda it: (
                    self._rules.score(it, weather=weather,
                                      event_type=request.event_type,
                                      preferences=request.preferences)
                    + self._cohesion_bonus(it, chosen, constraints)
                ),
            )
            chosen.append(best)
        return chosen

    @staticmethod
    def _cohesion_bonus(
        item: WardrobeItem,
        chosen: List[WardrobeItem],
        constraints: List[str],
    ) -> float:
        """Bonus score for constraint-aware cohesion between chosen items."""
        bonus = 0.0
        cs = {c.lower() for c in constraints}
        if "monochromatic" in cs and chosen:
            if item.color in {c.color for c in chosen}:
                bonus += 2.0
        if "leg lengthening" in cs and item.item_type == "bottom":
            if "leg lengthening" in item.style_tag:
                bonus += 3.0
        return bonus

    # ---- Dunder (LO6) -------------------------------------------------------

    def __repr__(self) -> str:
        return f"StylingAgent(wardrobe_size={len(self._wardrobe)})"

    def __len__(self) -> int:
        return len(self._wardrobe)