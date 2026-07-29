"""
Concrete ClothingItem subclasses — LO2, LO4.

Each subclass:
  - inherits from ClothingItem (is-a relationship)
  - overrides occasion_fit() and warmth_description() (polymorphism — LO2)
  - calls super().__init__() (LO4)
  - uses @classmethod from_dict() as an alternative constructor
  - uses @staticmethod for small utilities
"""
from __future__ import annotations

from typing import List, Optional
from .base import ClothingItem
from .exceptions import InvalidWarmthRating, InvalidItemType


VALID_TYPES = {"top", "bottom", "outerwear", "shoes", "dress", "accessory"}


class WardrobeItem(ClothingItem):
    """
    General-purpose clothing item.
    Composition root: the Outfit class HAS-A list of WardrobeItems (LO4).

    Also acts as a factory via from_dict() and from_upload() class methods.
    """

    def __init__(
        self,
        id: str,
        item_type: str,
        color: str,
        warmth_rating: int,
        style_tag: List[str],
        occasion_suitability: List[str],
        notes: str = "",
        image_url: Optional[str] = None,
    ) -> None:
        # Validate before storing — encapsulation & robustness (LO3, LO7)
        if not 1 <= warmth_rating <= 5:
            raise InvalidWarmthRating(warmth_rating)
        if item_type not in VALID_TYPES:
            raise InvalidItemType(item_type)

        super().__init__(
            id=id,
            color=color,
            style_tag=style_tag,
            occasion_suitability=occasion_suitability,
            notes=notes,
            image_url=image_url or "",
        )
        self._item_type = item_type
        self._warmth_rating = warmth_rating

    # ---- Abstract property implementations ----------------------------------

    @property
    def item_type(self) -> str:
        return self._item_type

    @property
    def warmth_rating(self) -> int:
        return self._warmth_rating

    # ---- Polymorphic methods (LO2) ------------------------------------------

    def occasion_fit(self, event_type: str) -> float:
        """1.0 if the event matches, else 0.0 — overridden by subclasses."""
        return 1.0 if event_type in self._occasion_suitability else 0.0

    def warmth_description(self) -> str:
        labels = {1: "very light", 2: "light", 3: "medium", 4: "warm", 5: "very warm"}
        return labels.get(self._warmth_rating, "unknown")

    # ---- Alternative constructors (@classmethod — LO1) ----------------------

    @classmethod
    def from_dict(cls, data: dict) -> "WardrobeItem":
        """
        Alternative constructor from a plain dict (e.g. Gemini JSON output).
        @classmethod so it can be called without an instance.
        """
        return cls(
            id=str(data.get("id", f"item_{id(data)}")),
            item_type=str(data.get("item_type", "top")),
            color=str(data.get("color", "unknown")),
            warmth_rating=max(1, min(5, int(data.get("warmth_rating", 3)))),
            style_tag=list(data.get("style_tag", ["casual"])),
            occasion_suitability=list(data.get("occasion_suitability", ["casual"])),
            notes=str(data.get("notes", "")),
            image_url=data.get("image_url"),
        )

    @classmethod
    def from_upload(cls, filename: str, meta: dict) -> "WardrobeItem":
        """Alternative constructor for gallery-uploaded items."""
        meta["id"] = f"u_{filename}"
        meta["image_url"] = f"gallery/{meta.get('item_type', 'other')}s/{filename}"
        return cls.from_dict(meta)

    # ---- Static utility (@staticmethod) -------------------------------------

    @staticmethod
    def valid_types() -> List[str]:
        """Return all accepted item_type values."""
        return sorted(VALID_TYPES)

    # ---- Dunder (LO6) -------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"WardrobeItem(id={self._id!r}, type={self._item_type!r}, "
            f"color={self._color!r}, warmth={self._warmth_rating})"
        )

    def __lt__(self, other: "WardrobeItem") -> bool:
        """Sort by warmth_rating — enables sorted(wardrobe)."""
        if not isinstance(other, WardrobeItem):
            return NotImplemented
        return self._warmth_rating < other._warmth_rating


# ---- Specialised subclasses (polymorphism — LO2, LO4) ----------------------

class Top(WardrobeItem):
    """A top garment. Overrides occasion_fit to boost formal events."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("item_type", "top")
        super().__init__(**kwargs)

    def occasion_fit(self, event_type: str) -> float:
        base = super().occasion_fit(event_type)
        # Tops with 'formal' tag get a bonus for work/formal events
        if event_type in {"work", "formal"} and "formal" in self._style_tag:
            return min(1.0, base + 0.3)
        return base

    def warmth_description(self) -> str:
        return f"top — {super().warmth_description()}"


class Bottom(WardrobeItem):
    """A bottom garment. Boosts leg-lengthening items for date events."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("item_type", "bottom")
        super().__init__(**kwargs)

    def occasion_fit(self, event_type: str) -> float:
        base = super().occasion_fit(event_type)
        if event_type == "date" and "leg lengthening" in self._style_tag:
            return min(1.0, base + 0.2)
        return base

    def warmth_description(self) -> str:
        return f"bottom — {super().warmth_description()}"


class Outerwear(WardrobeItem):
    """Outer layer. Always scores high occasion_fit — needed in cold weather."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("item_type", "outerwear")
        super().__init__(**kwargs)

    def occasion_fit(self, event_type: str) -> float:
        # Outerwear is always contextually appropriate
        return max(0.5, super().occasion_fit(event_type))

    def warmth_description(self) -> str:
        return f"outerwear — {super().warmth_description()}"


class Shoes(WardrobeItem):
    """Footwear. Gym shoes score poorly for formal events."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("item_type", "shoes")
        super().__init__(**kwargs)

    def occasion_fit(self, event_type: str) -> float:
        base = super().occasion_fit(event_type)
        if event_type == "formal" and "athleisure" in self._style_tag:
            return max(0.0, base - 0.5)
        return base

    def warmth_description(self) -> str:
        return f"shoes — {super().warmth_description()}"