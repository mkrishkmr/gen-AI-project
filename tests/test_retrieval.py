"""
Tests for the Retrieval Engine - search and filtering.
"""

import pytest
import pandas as pd

from Phase_2_Search.engine.search import get_candidates


def _mock_dataframe() -> pd.DataFrame:
    """Create a mock dataframe for testing retrieval logic."""
    return pd.DataFrame(
        {
            "name": ["Resto A", "Resto B", "Resto C", "Resto D", "Resto E", "Resto F"],
            "location": ["Koramangala", "Koramangala", "Koramangala", "Indiranagar", "Indiranagar", "Koramangala"],
            "listed_in(city)": ["Bangalore"] * 6,
            "cuisines": [
                "North Indian",
                "North Indian, Chinese",
                "North Indian",
                "South Indian",
                "North Indian",
                "North Indian",
            ],
            "rate": [4.5, 4.2, 4.8, 4.1, 3.9, 4.3],
            "approx_cost": [800, 600, 1200, 500, 400, 900],
            "votes": [100, 50, 200, 80, 30, 150],
        }
    )


class TestGetCandidates:
    """Tests for get_candidates function."""

    def test_returns_top_5_candidates(self):
        df = _mock_dataframe()
        result = get_candidates(
            df,
            location="Koramangala",
            cuisine="North Indian",
            max_budget=1500,
            min_rating=4.0,
            top_k=5,
        )
        assert len(result) <= 5
        assert len(result) >= 1

    def test_filters_by_location_and_cuisine(self):
        df = _mock_dataframe()
        result = get_candidates(
            df,
            location="Koramangala",
            cuisine="North Indian",
            max_budget=1500,
            min_rating=0.0,
            top_k=5,
        )
        assert all(r["location"] == "Koramangala" for _, r in result.iterrows())
        assert all(
            "North Indian" in str(r["cuisines"]) for _, r in result.iterrows()
        )

    def test_filters_by_max_budget(self):
        df = _mock_dataframe()
        result = get_candidates(
            df,
            location="Koramangala",
            cuisine="North Indian",
            max_budget=700,
            min_rating=0.0,
            top_k=5,
        )
        # Accounts for relaxed price search (up to 1.5x budget) when < 3 results
        assert all(r["approx_cost"] <= 700 * 1.5 for _, r in result.iterrows())

    def test_filters_by_min_rating(self):
        df = _mock_dataframe()
        result = get_candidates(
            df,
            location="Koramangala",
            cuisine="North Indian",
            max_budget=1500,
            min_rating=4.3,
            top_k=5,
        )
        assert all(r["rate"] >= 4.3 for _, r in result.iterrows())

    def test_relaxed_search_broadens_when_few_results(self):
        df = _mock_dataframe()
        result = get_candidates(
            df,
            location="Koramangala",
            cuisine="South Indian",
            max_budget=600,
            min_rating=4.0,
            top_k=5,
        )
        assert len(result) <= 5
        assert all(
            "South Indian" in str(r["cuisines"]) for _, r in result.iterrows()
        )

    def test_empty_df_returns_empty(self):
        df = pd.DataFrame()
        result = get_candidates(
            df,
            location="Koramangala",
            cuisine="North Indian",
            max_budget=1000,
            min_rating=4.0,
        )
        assert len(result) == 0
