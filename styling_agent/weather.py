"""Weather tool exposed for LLM function-calling.

Real call goes to OpenWeatherMap when OPENWEATHER_API_KEY is set. Otherwise
returns a deterministic mock so the demo runs offline.
"""
from __future__ import annotations

import os

import requests

from .schema import WeatherData

WEATHER_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city or region.",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "City or region name"},
            },
            "required": ["region"],
        },
    },
}


def _mock_weather(region: str) -> WeatherData:
    """Stable mock: hash the region into a plausible temperature/condition."""
    seed = sum(ord(c) for c in region.lower()) if region else 0
    temp = -5 + (seed % 35)                # -5..29 C
    conditions = ["clear", "clouds", "rain", "wind", "snow"]
    cond = conditions[seed % len(conditions)]
    return WeatherData(region=region, temperature_c=float(temp),
                       condition=cond, is_mock=True)


def get_weather(region: str) -> WeatherData:
    """Function-calling tool. Returns WeatherData for the given region."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return _mock_weather(region)

    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": region, "appid": api_key, "units": "metric"},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        return WeatherData(
            region=region,
            temperature_c=float(data["main"]["temp"]),
            condition=str(data["weather"][0]["main"]).lower(),
            is_mock=False,
        )
    except Exception:
        # Network or API failure -> degrade gracefully.
        return _mock_weather(region)
