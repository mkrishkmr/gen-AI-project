"""
Tests for the LLM Service - Groq client and JSON parsing logic.
"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.llm.groq_client import (
    _build_candidate_text,
    _parse_json_response,
    format_recommendation,
)


class TestParseJsonResponse:
    """Test JSON parsing logic."""

    def test_parses_plain_json(self):
        data = {"recommendations": [{"name": "Test", "why_it_fits": "Great"}]}
        result = _parse_json_response(json.dumps(data))
        assert result == data

    def test_strips_markdown_code_fences(self):
        data = {"recommendations": [{"name": "Test"}]}
        wrapped = "```json\n" + json.dumps(data) + "\n```"
        result = _parse_json_response(wrapped)
        assert result == data

    def test_strips_code_block_without_lang(self):
        data = {"recommendations": []}
        wrapped = "```\n" + json.dumps(data) + "\n```"
        result = _parse_json_response(wrapped)
        assert result == data

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("not valid json")


class TestBuildCandidateText:
    """Test candidate text building."""

    def test_builds_compact_text(self):
        df = pd.DataFrame(
            {
                "name": ["Resto A"],
                "location": ["Koramangala"],
                "listed_in(city)": ["Bangalore"],
                "cuisines": ["North Indian"],
                "rate": [4.5],
                "approx_cost": [800],
                "dish_liked": ["Biryani"],
                "rest_type": ["Casual Dining"],
            }
        )
        text = _build_candidate_text(df)
        assert "Resto A" in text
        assert "Koramangala" in text
        assert "North Indian" in text
        assert "4.5" in text
        assert "800" in text


class TestFormatRecommendationWithMock:
    """Test format_recommendation with mocked Groq API."""

    @patch("src.llm.groq_client.Groq")
    def test_returns_parsed_json_from_mock_response(self, mock_groq_class):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "recommendations": [
                                {
                                    "name": "Resto A",
                                    "why_it_fits": "Great for North Indian.",
                                    "suggested_dishes": ["Biryani", "Butter Chicken"],
                                    "vibe": "Cozy and family-friendly",
                                }
                            ]
                        }
                    )
                )
            )
        ]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        df = pd.DataFrame(
            {
                "name": ["Resto A"],
                "location": ["Koramangala"],
                "listed_in(city)": ["Bangalore"],
                "cuisines": ["North Indian"],
                "rate": [4.5],
                "approx_cost": [800],
            }
        )
        user_input = {
            "location": "Koramangala",
            "cuisine": "North Indian",
            "max_budget": 1000,
            "min_rating": 4.0,
        }

        with patch.dict("os.environ", {"GROQ_API_KEY": "test_key"}):
            result = format_recommendation(user_input, df, api_key="test_key")

        assert "recommendations" in result
        assert len(result["recommendations"]) == 1
        rec = result["recommendations"][0]
        assert rec["name"] == "Resto A"
        assert rec["why_it_fits"] == "Great for North Indian."
        assert rec["suggested_dishes"] == ["Biryani", "Butter Chicken"]
        assert rec["vibe"] == "Cozy and family-friendly"

    @patch("src.llm.groq_client.Groq")
    def test_passes_candidates_to_prompt(self, mock_groq_class):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps({"recommendations": []})
                )
            )
        ]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        df = pd.DataFrame(
            {
                "name": ["Resto X"],
                "location": ["Indiranagar"],
                "listed_in(city)": ["Bangalore"],
                "cuisines": ["Chinese"],
                "rate": [4.2],
                "approx_cost": [600],
            }
        )
        user_input = {
            "location": "Indiranagar",
            "cuisine": "Chinese",
            "max_budget": 800,
            "min_rating": 4.0,
        }

        with patch.dict("os.environ", {"GROQ_API_KEY": "test_key"}):
            format_recommendation(user_input, df, api_key="test_key")

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        user_msg = next(m for m in messages if m["role"] == "user")
        assert "Resto X" in user_msg["content"]
        assert "Indiranagar" in user_msg["content"]
        assert "Chinese" in user_msg["content"]
        assert call_args.kwargs["response_format"] == {"type": "json_object"}

    def test_raises_without_api_key(self):
        df = pd.DataFrame({"name": ["A"], "location": [""], "cuisines": [""], "rate": [4.0], "approx_cost": [500]})
        user_input = {"location": "", "cuisine": "", "max_budget": 1000, "min_rating": 4.0}
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GROQ_API_KEY"):
                format_recommendation(user_input, df)
