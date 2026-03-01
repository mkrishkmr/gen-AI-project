"""
End-to-End Test: Full cycle from dataset load to recommendation object.
1. Load Hugging Face dataset
2. Filter for 'Italian' in 'Bangalore' under 1000 INR
3. Pass mock list to Groq logic
4. Assert final recommendation object has correct keys
"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from Phase_1_Data.data.loader import load_and_clean_dataset
from Phase_2_Search.engine.search import get_candidates
from Phase_3_LLM.llm.groq_client import format_recommendation, _parse_json_response

# Expected keys in each recommendation
REQUIRED_KEYS = ["name", "why_it_fits", "suggested_dishes", "vibe"]


class TestE2E:
    """End-to-end integration tests."""

    def test_load_dataset_filters_italian_bangalore_under_1000(self):
        """Step 1 & 2: Load dataset and filter for Italian in Bangalore under 1000 INR."""
        df = load_and_clean_dataset()
        assert not df.empty
        assert "cuisines" in df.columns
        assert "location" in df.columns
        assert "approx_cost" in df.columns

        candidates = get_candidates(
            df,
            location="Bangalore",
            cuisine="Italian",
            max_budget=1000,
            min_rating=0.0,
            top_k=5,
        )
        # May be empty if no Italian in Bangalore under 1000 - that's ok
        assert isinstance(candidates, pd.DataFrame)
        if not candidates.empty:
            assert all("Italian" in str(c) for c in candidates["cuisines"])
            assert all(c <= 1000 for c in candidates["approx_cost"])

    @patch("Phase_3_LLM.llm.groq_client.Groq")
    def test_mock_groq_returns_valid_recommendation_structure(self, mock_groq_class):
        """Step 3 & 4: Mock Groq, verify recommendation object has correct keys."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "recommendations": [
                                {
                                    "name": "Tuscany Garden",
                                    "why_it_fits": "Perfect for Italian in Bangalore.",
                                    "suggested_dishes": ["Pasta", "Pizza"],
                                    "vibe": "Cozy",
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

        mock_candidates = pd.DataFrame(
            {
                "name": ["Tuscany Garden"],
                "location": ["Indiranagar"],
                "listed_in(city)": ["Bangalore"],
                "cuisines": ["Italian"],
                "rate": [4.2],
                "approx_cost": [800],
            }
        )
        user_input = {
            "location": "Bangalore",
            "cuisine": "Italian",
            "max_budget": 1000,
            "min_rating": 0.0,
        }

        result = format_recommendation(user_input, mock_candidates, api_key="test_key")

        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) >= 1

        for rec in result["recommendations"]:
            for key in REQUIRED_KEYS:
                assert key in rec, f"Missing key: {key}"
            assert isinstance(rec["suggested_dishes"], list)
