"""
Mock wardrobe using typed subclasses — demonstrates polymorphism (LO2).
Each item is the most specific type: Top, Bottom, Outerwear, or Shoes.
"""
from __future__ import annotations

from .items import Bottom, Outerwear, Shoes, Top

MOCK_WARDROBE = [
    # ---- Tops ----
    Top(id="t1", color="white", warmth_rating=1,
        style_tag=["minimal", "classic"],
        occasion_suitability=["work", "date", "casual", "formal"],
        notes="crisp white cotton t-shirt, versatile base layer"),
    Top(id="t2", color="black", warmth_rating=2,
        style_tag=["minimal", "streetwear"],
        occasion_suitability=["casual", "date", "gym"],
        notes="black long-sleeve fitted tee"),
    Top(id="t3", color="beige", warmth_rating=2,
        style_tag=["earth tones", "minimal"],
        occasion_suitability=["work", "date", "casual"],
        notes="oversized beige linen button-up"),
    Top(id="t4", color="navy", warmth_rating=3,
        style_tag=["classic", "preppy", "formal"],
        occasion_suitability=["work", "formal", "casual"],
        notes="navy merino wool sweater"),
    Top(id="t5", color="grey", warmth_rating=4,
        style_tag=["athleisure"],
        occasion_suitability=["gym", "casual"],
        notes="grey heavyweight hoodie"),

    # ---- Bottoms ----
    Bottom(id="b1", color="black", warmth_rating=3,
           style_tag=["minimal", "classic", "leg lengthening"],
           occasion_suitability=["work", "date", "formal", "casual"],
           notes="high-rise black tailored trousers"),
    Bottom(id="b2", color="blue", warmth_rating=3,
           style_tag=["casual", "classic"],
           occasion_suitability=["casual", "date"],
           notes="dark indigo slim jeans"),
    Bottom(id="b3", color="beige", warmth_rating=2,
           style_tag=["earth tones", "minimal"],
           occasion_suitability=["work", "casual", "date"],
           notes="beige cotton chinos"),
    Bottom(id="b4", color="black", warmth_rating=2,
           style_tag=["athleisure"],
           occasion_suitability=["gym", "casual"],
           notes="black performance joggers"),
    Bottom(id="b5", color="grey", warmth_rating=4,
           style_tag=["classic"],
           occasion_suitability=["work", "formal"],
           notes="charcoal wool flannel trousers"),

    # ---- Outerwear ----
    Outerwear(id="o1", color="black", warmth_rating=4,
              style_tag=["streetwear", "minimal"],
              occasion_suitability=["casual", "date"],
              notes="black bomber jacket"),
    Outerwear(id="o2", color="beige", warmth_rating=4,
              style_tag=["classic", "earth tones"],
              occasion_suitability=["work", "date", "formal", "casual"],
              notes="beige trench coat, rain-resistant"),
    Outerwear(id="o3", color="navy", warmth_rating=5,
              style_tag=["classic", "formal"],
              occasion_suitability=["work", "formal", "date"],
              notes="navy heavyweight wool overcoat"),

    # ---- Shoes ----
    Shoes(id="s1", color="white", warmth_rating=2,
          style_tag=["minimal", "streetwear"],
          occasion_suitability=["casual", "date", "work"],
          notes="clean white leather sneakers"),
    Shoes(id="s2", color="black", warmth_rating=3,
          style_tag=["classic", "formal"],
          occasion_suitability=["work", "formal", "date"],
          notes="black leather derby shoes"),
    Shoes(id="s3", color="black", warmth_rating=2,
          style_tag=["athleisure"],
          occasion_suitability=["gym", "casual"],
          notes="black running trainers"),
    Shoes(id="s4", color="brown", warmth_rating=4,
          style_tag=["earth tones", "classic"],
          occasion_suitability=["work", "casual", "date"],
          notes="brown suede chelsea boots, rain-friendly"),
]