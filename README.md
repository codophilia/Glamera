# Glamera 👗
### *Snap · Sync · Glam*

> **Glamera** is an AI-powered personal fashion stylist web application that suggests outfit combinations from your wardrobe based on weather conditions, occasion, color theory, and your personal style profile.

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- A Google Gemini API key
- Optional: OpenWeatherMap API key

### Setup

```bash
# 1. Clone or download the project folder
cd "Sem 2 Glamera"

# 2. Create and activate virtual environment
python -m venv glamera
glamera\Scripts\activate        # Windows
source glamera/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file in the project root
# Add the following lines:
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_key_here   # optional

# 5. Run the app
streamlit run webapp.py
```

The app opens automatically at `http://localhost:8501`.

---

## 📁 Project Structure

```
Sem 2 Glamera/
├── webapp.py                  # Streamlit UI — main entry point
├── requirements.txt           # Python dependencies
├── .env                       # API keys (never commit this)
├── assets/
│   └── glamera_g.png          # Custom G logo
├── gallery/                   # Auto-created on first upload
│   ├── tops/
│   ├── bottoms/
│   ├── outerwear/
│   ├── shoes/
│   └── accessories/
└── styling_agent/
    ├── __init__.py            # Package exports
    ├── base.py                # Abstract Base Class, Mixin, Protocol
    ├── exceptions.py          # Custom exception hierarchy
    ├── items.py               # WardrobeItem + typed subclasses
    ├── schema.py              # Pydantic models + Outfit dataclass
    ├── agent.py               # StylingAgent — orchestration logic
    ├── rules.py               # RulesEngine — scoring & constraints
    ├── wardrobe.py            # Mock wardrobe seed data
    ├── weather.py             # OpenWeatherMap integration
    └── gemini.py              # Gemini AI calls — rationale & color
```

---

## ✨ Features

### 🤖 AI-Powered Features
| Feature | Description |
|---|---|
| **Outfit Suggestion Engine** | Gemini 2.5 Flash analyses your wardrobe, weather, occasion, and preferences to suggest a complete outfit |
| **Image Metadata Extraction** | Upload a photo of any clothing item — Gemini automatically identifies item type, color, style tags, warmth rating, and occasion suitability |
| **Color Theory Analysis** | Gemini evaluates the color harmony of the suggested outfit (score out of 10) and explains the palette using fashion color theory |
| **Stylist Rationale** | Natural language explanation of why the suggested outfit works, written by Gemini in a warm stylist voice |
| **"Why This Outfit?" Deep Dive** | On-demand Gemini analysis covering color theory, body type considerations, current trend context, and styling tips |
| **AI Stylist Chat** | Multi-turn conversational interface — chat with Glamera about style, ask for tweaks, or describe your mood and get personalized advice |
| **Feedback Loop** | 👍 Love it / 👎 Try again buttons — "Try again" sends the outfit back to Gemini for a specific improvement suggestion |
| **Style Profile Personalization** | Users describe their style once; the profile is passed to Gemini on every request to personalize all suggestions |
| **Weather-Aware Suggestions** | Live weather data from OpenWeatherMap (with offline mock fallback) feeds into AI outfit scoring |
| **RAG-Style Retrieval** | Wardrobe items are filtered and scored by relevance before being passed to Gemini — mirrors RAG architecture |

### 🛠️ Other Features
- Tag-based style constraints and preferences input (press Enter to add)
- Wardrobe gallery with folder organisation by clothing type
- Constraint relaxation — if no outfit satisfies all constraints, Glamera relaxes them gracefully and tells you
- UI: Streamlit, mobile-first
- Session state persistence within a session

---

## 🧰 Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **Streamlit** | Web application framework |
| **Google Gemini 2.5 Flash** | AI model for outfit generation, image analysis, chat, and rationale |
| **google-generativeai** | Gemini Python SDK |
| **Pydantic v2** | Data validation and schema modelling |
| **Pillow (PIL)** | Image processing for clothing photo uploads |
| **Requests** | HTTP calls to OpenWeatherMap API |
| **python-dotenv** | Environment variable management |
| **OpenWeatherMap API** | Live weather data (optional) |

---

## 🏗️ Object-Oriented Design

Glamera is built with a full OOP architecture to satisfy the Object-Oriented Programming course requirements.

### Class Hierarchy

```
ClothingItem (Abstract Base Class)
    └── WardrobeItem
            ├── Top
            ├── Bottom
            ├── Outerwear
            └── Shoes
```

### OOP Concepts Applied

| Concept | Where Used |
|---|---|
| **Abstraction** | `ClothingItem` ABC hides internal logic behind a clean interface |
| **Encapsulation** | Private `_attributes` with `@property` getters and validation in `WardrobeItem` |
| **Inheritance** | `Top`, `Bottom`, `Outerwear`, `Shoes` all inherit from `WardrobeItem` |
| **Polymorphism** | Each subclass overrides `occasion_fit()` and `warmth_description()` differently |
| **Composition** | `Outfit` HAS-A list of `WardrobeItem`; `StylingAgent` HAS-A `RulesEngine` |
| **Abstract Base Class** | `ClothingItem` uses `abc.ABC` and `@abstractmethod` |
| **Protocol** | `Recommender` Protocol defines structural contract for the agent |
| **Mixin** | `LoggableMixin` adds reusable logging to `StylingAgent` |
| **Custom Exceptions** | `GlameraError`, `WardrobeError`, `StylingError`, `WeatherError`, `InvalidWarmthRating`, `InvalidItemType` |
| **Dunder Methods** | `__repr__`, `__eq__`, `__hash__`, `__lt__`, `__len__`, `__iter__`, `__contains__` |
| **@dataclass** | `WeatherData` uses `@dataclass` with `__post_init__` validation |
| **@classmethod** | `WardrobeItem.from_dict()` and `WardrobeItem.from_upload()` alternative constructors |
| **@staticmethod** | `RulesEngine.required_warmth()`, `RulesEngine.needs_outerwear()`, `WardrobeItem.valid_types()` |
| **SOLID — SRP** | Each file/class has one clear responsibility |
| **SOLID — OCP** | `RulesEngine` can be subclassed without modifying `StylingAgent` |
| **SOLID — DIP** | `StylingAgent` depends on the `Recommender` Protocol, not a concrete class |

---

## 👥 Team Members

| Name | Role |
|---------|----------------|
| Shehzadi Urooj (BSASI-II) | Team captain |
| Maryam Muazzam (BSCS-II) | Developer | Team Member |
| Nabia Sajid (BSAI-II) | Team Memeber |
| Noor Khan (BSSE-II) | Team Memmber |

---

## 📦 Dependencies

```
streamlit>=1.36
google-generativeai>=0.7
requests>=2.31
pydantic>=2.7
python-dotenv>=1.0
pillow>=10.0
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 📝 License

© 2026 Glamera. All Rights Reserved.

This project was created for academic purposes. No part of this codebase may be copied, modified, distributed, or used commercially without explicit written permission from the authors.

---

> Built as a final capstone project for the AI and Object-Oriented Programming courses.
> *Glamera — because your wardrobe deserves a stylist.*
