"""
Search Service - Filter and rank restaurant candidates with relaxed search fallback.
"""

import math
from typing import Union

import pandas as pd


def _normalize(s: Union[str, float, None]) -> str:
    """Normalize string for comparison (lowercase, strip)."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return str(s).strip().lower()


def _matches_cuisine(row_cuisines: str, target_cuisine: str) -> bool:
    """Check if target cuisine is in restaurant's cuisines (case-insensitive)."""
    if not target_cuisine:
        return True
    cuisines = _normalize(row_cuisines).split(",")
    target = _normalize(target_cuisine)
    return any(target in c.strip() for c in cuisines if c.strip())


def _matches_location(
    row_loc: str, row_city: str, target: str, exact_loc: bool
) -> bool:
    """
    Check if target matches location or city.
    exact_loc=True: match location (area). exact_loc=False: match city.
    """
    if not target:
        return True
    t = _normalize(target)
    loc_n = _normalize(row_loc)
    city_n = _normalize(row_city)
    if exact_loc:
        return t == loc_n or t in loc_n or loc_n in t
    return t == city_n or t in city_n or city_n in t


def get_candidates(
    df: pd.DataFrame,
    location: str,
    cuisine: str,
    max_budget: int,
    min_rating: float,
    top_k: int = 5,
) -> pd.DataFrame:
    """
    Filter restaurants by location, cuisine, budget, and rating.
    Implements relaxed search: if < 3 results, broaden to entire city or similar price points.

    Args:
        df: Cleaned dataframe with columns: location, listed_in(city), cuisines,
            approx_cost (or approx_cost(for two people)), rate, votes (optional).
        location: Target location (area) or city.
        cuisine: Target cuisine type.
        max_budget: Maximum cost for two people.
        min_rating: Minimum rating (0-5).
        top_k: Number of candidates to return.

    Returns:
        Top `top_k` rows, sorted by relevance (rating * log(1 + votes)).
    """
    if df.empty:
        return df.head(0)

    cost_col = (
        "approx_cost"
        if "approx_cost" in df.columns
        else "approx_cost(for two people)"
    )
    city_col = (
        "listed_in(city)"
        if "listed_in(city)" in df.columns
        else "listed_in_city"
    )
    if city_col not in df.columns:
        df = df.copy()
        df[city_col] = ""

    def _apply_filters(
        data: pd.DataFrame,
        loc_target: str,
        use_exact_location: bool,
        budget: int,
    ) -> pd.DataFrame:
        mask = pd.Series(True, index=data.index)
        if cuisine:
            mask &= data["cuisines"].apply(
                lambda x: _matches_cuisine(str(x), cuisine)
            )
        mask &= data[cost_col] <= budget
        mask &= data["rate"] >= min_rating
        if loc_target:
            mask &= data.apply(
                lambda r: _matches_location(
                    r["location"], r[city_col], loc_target, use_exact_location
                ),
                axis=1,
            )
        return data[mask].copy()

    loc_norm = _normalize(location)

    candidates = _apply_filters(df, loc_norm, use_exact_location=True, budget=max_budget)

    if len(candidates) < 3:
        relaxed_city = _apply_filters(
            df, loc_norm, use_exact_location=False, budget=max_budget
        )
        relaxed_price = _apply_filters(
            df, loc_norm, use_exact_location=True, budget=int(max_budget * 1.5)
        )
        candidates = (
            pd.concat([relaxed_city, relaxed_price])
            .drop_duplicates()
            .reset_index(drop=True)
        )

    if candidates.empty:
        return candidates.head(0)

    if "votes" in candidates.columns:
        candidates = candidates.copy()
        candidates["_score"] = candidates["rate"] * (
            1 + candidates["votes"].fillna(0).apply(math.log1p)
        )
        candidates = candidates.sort_values(
            "_score", ascending=False
        ).drop(columns=["_score"], errors="ignore")
    else:
        candidates = candidates.sort_values("rate", ascending=False)

    return candidates.head(top_k)
