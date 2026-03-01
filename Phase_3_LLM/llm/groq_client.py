"""
Groq LLM Client - Format recommendations using llama-3.3-70b-versatile with JSON mode.
"""

import json
import os
from typing import Any, Dict, Optional

import pandas as pd
from groq import Groq


DEFAULT_MODEL = "llama-3.3-70b-versatile"

RECOMMENDATION_SCHEMA = {
    "recommendations": [
        {
            "name": "",
            "why_it_fits": "",
            "suggested_dishes": [],
            "vibe": "",
        }
    ]
}


def _build_candidate_text(df: pd.DataFrame) -> str:
    """Build compact text representation of candidates for the prompt."""
    lines = []
    for _, row in df.iterrows():
        name = row.get("name", "Unknown")
        location = row.get("location", "")
        city = row.get("listed_in(city)", row.get("listed_in_city", ""))
        cuisines = row.get("cuisines", "")
        rate = row.get("rate", 0)
        cost = row.get("approx_cost", row.get("approx_cost(for two people)", 0))
        dish = row.get("dish_liked", "")
        rest_type = row.get("rest_type", "")
        lines.append(
            f"- {name} | {location}, {city} | Cuisines: {cuisines} | "
            f"Rating: {rate}/5 | Cost for two: ₹{cost} | Dishes: {dish} | Type: {rest_type}"
        )
    return "\n".join(lines)


def _parse_json_response(text: str) -> Dict[str, Any]:
    """Parse LLM response, stripping markdown code fences if present."""
    s = text.strip()
    if s.startswith("```"):
        lines = s.split("\n")
        start = 1 if lines[0].startswith("```") else 0
        end = -1 if lines[-1].strip() == "```" else len(lines)
        s = "\n".join(lines[start:end])
    return json.loads(s)


def format_recommendation(
    user_input: Dict[str, Any],
    candidates: pd.DataFrame,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Construct prompt and call Groq to get structured JSON recommendations.

    Args:
        user_input: Dict with keys: location, cuisine, max_budget, min_rating, notes (optional).
        candidates: DataFrame of top 5 candidate restaurants.
        model: Groq model (default: llama-3.3-70b-versatile).
        api_key: Groq API key (default: from GROQ_API_KEY env).

    Returns:
        Parsed JSON with schema:
        {"recommendations": [{"name": "", "why_it_fits": "", "suggested_dishes": [], "vibe": ""}]}
    """
    model = model or DEFAULT_MODEL
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set")

    candidate_text = _build_candidate_text(candidates)

    user_prefs = (
        f"Location: {user_input.get('location', '')}\n"
        f"Cuisine: {user_input.get('cuisine', '')}\n"
        f"Max budget for two: ₹{user_input.get('max_budget', '')}\n"
        f"Minimum rating: {user_input.get('min_rating', '')}/5\n"
        f"Notes: {user_input.get('notes', '')}"
    )

    system_prompt = (
        "You are a restaurant recommendation assistant. Respond ONLY with valid JSON. "
        "Use this exact schema: {\"recommendations\": [{\"name\": \"\", \"why_it_fits\": \"\", "
        "\"suggested_dishes\": [], \"vibe\": \"\"}]}. "
        "Select the best matches from the candidates. For each: explain why it fits, "
        "suggest 1-3 dishes, and describe the vibe in a few words."
    )

    user_prompt = (
        f"## User Preferences\n{user_prefs}\n\n"
        f"## Candidate Restaurants\n{candidate_text}\n\n"
        "Select the best matches and respond with ONLY valid JSON."
    )

    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return _parse_json_response(content)


def get_recommendations(
    user_input: Dict[str, Any],
    candidates: pd.DataFrame,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Alias for format_recommendation for API consistency."""
    return format_recommendation(user_input, candidates, model, api_key)
