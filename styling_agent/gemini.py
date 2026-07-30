"""Gemini wrapper + prompt logic.

Single place to swap LLM providers. Exposes:
  - get_model(): returns an object with `.invoke(prompt) -> str`
  - write_rationale(...): builds the stylist-explanation prompt and calls
    the model, falling back to a deterministic template when no API key
    is configured (so the demo runs fully offline).

Reads GEMINI_API_KEY (preferred) or GOOGLE_API_KEY from the environment.
Model name can be overridden with GEMINI_MODEL (default: gemini-2.5-flash).
"""
from __future__ import annotations

import os
from typing import Optional

from .schema import WardrobeItem, WeatherData

# ---------------------------------------------------------------------------
# Model factory
# ---------------------------------------------------------------------------

class _NullModel:
    """No-op model used when no API key is set. Keeps the demo runnable."""

    def invoke(self, prompt: str) -> str:  # noqa: ARG002
        return ""


def get_model() -> object:
    """Return a Gemini-backed wrapper, or a null stub when no key is set."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return _NullModel()

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)

        class _GeminiWrapper:
            def invoke(self, prompt: str) -> str:
                try:
                    resp = model.generate_content(prompt)
                    return (getattr(resp, "text", "") or "").strip()
                except Exception:
                    return ""

        return _GeminiWrapper()
    except Exception:
        # Library missing or import failed — degrade gracefully.
        return _NullModel()


# ---------------------------------------------------------------------------
# Prompting
# ---------------------------------------------------------------------------

_SYSTEM = (
    "You are a concise personal stylist. Explain why the chosen outfit works "
    "given the weather, event, and the user's preferences. 2-3 short sentences. "
    "Reference specific items (e.g. 'the navy oxford'). Avoid filler."
)


def _format_items(items: list[WardrobeItem]) -> str:
    return "\n".join(
        f"- {it.item_type}: {it.color} ({', '.join(it.style_tag)})"
        for it in items
    )


def _template_fallback(
    items: list[WardrobeItem],
    weather: WeatherData | None,
    event_type: str,
) -> str:
    """Deterministic rationale used when the LLM is unavailable."""
    parts = [f"For a {event_type} setting"]
    if weather:
        parts.append(
            f"in {weather.region} ({round(weather.temperature_c)}°C, {weather.condition})"
        )
    parts.append(
        "this combination balances comfort and style: "
        + ", ".join(f"{it.color} {it.item_type}" for it in items) + "."
    )
    return " ".join(parts)


def write_rationale(
    items: list[WardrobeItem],
    *,
    weather: Optional[WeatherData],
    event_type: str,
    constraints: list[str],
    preferences: list[str],
    relaxed: list[str],
    style_profile: str = "",
) -> str:
    """Build the prompt, call Gemini, fall back to template on empty response."""
    model = get_model()

    weather_str = (
        f"{weather.region}, {round(weather.temperature_c)}°C, {weather.condition}"
        if weather else "unknown"
    )
    profile_line = (
        f"User style profile (personalize to this): {style_profile.strip()}"
        if style_profile.strip() else "User style profile: (none provided)"
    )
    prompt = (
        f"{_SYSTEM}\n\n"
        f"Weather: {weather_str}\n"
        f"Event: {event_type}\n"
        f"User preferences: {', '.join(preferences) or 'none'}\n"
        f"Style constraints kept: {', '.join(constraints) or 'none'}\n"
        f"Constraints relaxed (mention briefly if any): {', '.join(relaxed) or 'none'}\n"
        f"{profile_line}\n"
        f"Outfit:\n{_format_items(items)}\n\n"
        "Write the rationale now."
    )

    text = model.invoke(prompt)
    return text or _template_fallback(items, weather, event_type)


# ---------------------------------------------------------------------------
# Color harmony evaluation (pure LLM reasoning — no hardcoded color rules)
# ---------------------------------------------------------------------------

_COLOR_SYSTEM = (
    "You are a stylist grounded in color theory (complementary, analogous, "
    "triadic, neutrals, warm/cool balance, contrast, monochrome). Evaluate an "
    "outfit's color harmony. Return STRICT JSON only with keys: "
    '{"harmony_score": integer 1-10, "color_rationale": "1-2 sentences using '
    'color-theory language explaining why the palette works or does not"}.'
)


def evaluate_color_harmony(
    items: list[WardrobeItem],
    *,
    style_profile: str = "",
) -> dict:
    """Ask Gemini to score color compatibility and explain it. No fallback rules."""
    import json

    model = get_model()
    palette = ", ".join(f"{it.item_type}:{it.color}" for it in items) or "none"
    profile_line = (
        f"User style profile: {style_profile.strip()}"
        if style_profile.strip() else "User style profile: (none)"
    )
    prompt = (
        f"{_COLOR_SYSTEM}\n\n"
        f"Outfit palette: {palette}\n"
        f"{profile_line}\n\n"
        "Return the JSON now."
    )

    raw = model.invoke(prompt) or ""
    try:
        start, end = raw.find("{"), raw.rfind("}")
        data = json.loads(raw[start : end + 1]) if start >= 0 else {}
    except Exception:
        data = {}

    score = int(data.get("harmony_score") or 5)
    score = max(1, min(10, score))
    rationale = str(data.get("color_rationale") or "").strip()
    if not rationale:
        rationale = f"Palette ({palette}) evaluated with default score — Gemini unavailable."
    return {"harmony_score": score, "color_rationale": rationale}