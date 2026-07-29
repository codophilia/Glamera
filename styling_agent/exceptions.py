"""Custom exception hierarchy for Glamera — LO7."""
from __future__ import annotations


class GlameraError(Exception):
    """Base exception for all Glamera domain errors."""


class WardrobeError(GlameraError):
    """Raised when wardrobe data is invalid or incomplete."""


class StylingError(GlameraError):
    """Raised when the agent cannot assemble a valid outfit."""


class WeatherError(GlameraError):
    """Raised when weather data cannot be fetched or parsed."""


class InvalidWarmthRating(WardrobeError):
    """Raised when warmth_rating is outside 1–5."""
    def __init__(self, value: int) -> None:
        super().__init__(f"warmth_rating must be 1–5, got {value}")


class InvalidItemType(WardrobeError):
    """Raised when an unrecognised item_type is supplied."""
    def __init__(self, value: str) -> None:
        super().__init__(
            f"'{value}' is not a valid item type. "
            "Expected: top, bottom, outerwear, shoes, dress, accessory."
        )