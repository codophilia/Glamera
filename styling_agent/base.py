"""Abstract base classes, mixins, and protocols — LO2, LO4, LO5, LO8."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, runtime_checkable, Protocol


# ---- Mixin ------------------------------------------------------------------

class LoggableMixin:
    """
    Mixin that adds a lightweight log() helper.
    Single-purpose, reusable — follows SRP and ISP (SOLID).
    """
    def log(self, msg: str) -> None:
        print(f"[{self.__class__.__name__}] {msg}")


# ---- Abstract Base Class ----------------------------------------------------

class ClothingItem(ABC):
    """
    Abstract base for every garment type.
    Defines the contract all items must honour — LO5.
    Subclasses MUST implement occasion_fit() and warmth_description().
    """

    def __init__(
        self,
        id: str,
        color: str,
        style_tag: List[str],
        occasion_suitability: List[str],
        notes: str = "",
        image_url: str = "",
    ) -> None:
        # Protected attributes — subclasses may read, outside code uses @property
        self._id = id
        self._color = color.lower().strip()
        self._style_tag = list(style_tag)
        self._occasion_suitability = list(occasion_suitability)
        self._notes = notes
        self._image_url = image_url

    # ---- Properties (encapsulation — LO3) -----------------------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def color(self) -> str:
        return self._color

    @property
    def style_tag(self) -> List[str]:
        return list(self._style_tag)       # defensive copy

    @property
    def occasion_suitability(self) -> List[str]:
        return list(self._occasion_suitability)

    @property
    def notes(self) -> str:
        return self._notes

    @property
    def image_url(self) -> str:
        return self._image_url

    # ---- Abstract methods (contract — LO5) ----------------------------------

    @abstractmethod
    def occasion_fit(self, event_type: str) -> float:
        """Return a 0–1 score for how well this item suits the event."""

    @abstractmethod
    def warmth_description(self) -> str:
        """Return a human-readable warmth label."""

    @property
    @abstractmethod
    def item_type(self) -> str:
        """The slot this item fills: top | bottom | outerwear | shoes | accessory."""

    @property
    @abstractmethod
    def warmth_rating(self) -> int:
        """Warmth on a 1–5 scale."""

    # ---- Dunder methods (LO6) -----------------------------------------------

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, color={self._color!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClothingItem):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)


# ---- Protocol (structural subtyping — LO5) ----------------------------------

@runtime_checkable
class Recommender(Protocol):
    """
    Structural contract for any outfit recommender.
    Lets us swap StylingAgent for another implementation without
    changing the Streamlit UI — Dependency Inversion (SOLID).
    """
    def recommend(self, request: object) -> object:
        ...