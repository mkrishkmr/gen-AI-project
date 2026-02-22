"""
Tests for the Data Layer - data loading and cleaning.
"""

import pytest
import pandas as pd

from src.data.loader import load_and_clean_dataset, _clean_rate, _clean_approx_cost


class TestCleanHelpers:
    """Unit tests for cleaning helper functions."""

    def test_clean_rate_strips_slash5(self):
        assert _clean_rate("4.1/5") == 4.1
        assert _clean_rate("3.8/5") == 3.8

    def test_clean_rate_handles_new_and_dash(self):
        assert _clean_rate("NEW") == 0.0
        assert _clean_rate("-") == 0.0

    def test_clean_rate_handles_empty(self):
        assert _clean_rate("") == 0.0
        assert _clean_rate(None) == 0.0

    def test_clean_approx_cost_removes_commas(self):
        assert _clean_approx_cost("1,000") == 1000
        assert _clean_approx_cost("800") == 800

    def test_clean_approx_cost_handles_range(self):
        assert _clean_approx_cost("500-1000") == 1000

    def test_clean_approx_cost_handles_empty(self):
        assert _clean_approx_cost("") == 0
        assert _clean_approx_cost(None) == 0


class TestLoadAndCleanDataset:
    """Integration tests for load_and_clean_dataset."""

    def test_cleaned_dataframe_has_correct_dtypes(self):
        df = load_and_clean_dataset()
        assert df["rate"].dtype == "float64"
        assert df["approx_cost"].dtype == "int64"

    def test_cleaned_dataframe_has_no_nulls_in_rate_or_approx_cost(self):
        df = load_and_clean_dataset()
        assert df["rate"].isna().sum() == 0
        assert df["approx_cost"].isna().sum() == 0

    def test_cleaned_dataframe_has_cuisines_filled(self):
        df = load_and_clean_dataset()
        assert df["cuisines"].isna().sum() == 0
