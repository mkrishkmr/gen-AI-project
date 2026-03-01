"""
Data Loader - Load and clean the Zomato restaurant dataset from Hugging Face.
"""

import os
from typing import Optional

import pandas as pd
from datasets import load_dataset


def _clean_rate(value) -> float:
    """
    Strip '/5' from rate and convert to float.
    Handles: '4.1/5', 'NEW', '-', empty, None.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return 0.0
    s = str(value).strip()
    if s.upper() in ("NEW", "-", "NAN"):
        return 0.0
    if "/5" in s:
        s = s.split("/5")[0].strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def _clean_approx_cost(value) -> int:
    """
    Remove commas from approx_cost and convert to int.
    Handles: '800', '1,000', '500-1000', empty, None.
    """
    if value is None or (isinstance(value, str) and not str(value).strip()):
        return 0
    s = str(value).strip().replace(",", "")
    if not s or s.upper() in ("NAN", "NULL"):
        return 0
    if "-" in s:
        parts = [p.strip() for p in s.split("-") if p.strip()]
        if not parts:
            return 0
        values = []
        for p in parts:
            try:
                values.append(int(float(p)))
            except (ValueError, TypeError):
                pass
        return max(values) if values else 0
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def load_and_clean_dataset(dataset_name: Optional[str] = None) -> pd.DataFrame:
    """
    Load the Zomato dataset from Hugging Face and apply cleaning logic.

    Uses a local cache directory (./hf_cache) to avoid permission errors when
    writing to the default C:\\Users\\<user>\\.cache directory.

    Cleaning:
    - Strip '/5' from 'rate' and convert to float.
    - Remove commas from 'approx_cost(for two people)' and convert to int.
    - Fill missing 'cuisines' with 'Various'.

    Returns:
        Cleaned pandas DataFrame.
    """
    name = dataset_name or os.getenv(
        "HF_DATASET", "ManikaSaini/zomato-restaurant-recommendation"
    )
    # Use project-local cache to avoid WinError 5 (PermissionError) on protected paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    cache_dir = os.path.join(project_root, "hf_cache")
    os.makedirs(cache_dir, exist_ok=True)

    try:
        ds = load_dataset(
            name,
            split="train",
            cache_dir=cache_dir,
        )
    except PermissionError as e:
        raise PermissionError(
            f"Failed to load Hugging Face dataset: {e}\n\n"
            "Try:\n"
            "  1. Run the terminal as Administrator, or\n"
            "  2. Check that the ./hf_cache folder has write permissions, or\n"
            "  3. Delete ./hf_cache and try again."
        ) from e
    except OSError as e:
        if "WinError 5" in str(e) or "Permission denied" in str(e).lower():
            raise PermissionError(
                f"Permission denied when accessing cache: {e}\n\n"
                "Try running the terminal as Administrator or check ./hf_cache permissions."
            ) from e
        raise

    df = ds.to_pandas()

    cost_col = "approx_cost(for two people)"
    if cost_col not in df.columns:
        cost_col = "approx_cost_for_two"  # fallback if column renamed

    df["rate"] = df["rate"].apply(_clean_rate)
    df[cost_col] = df[cost_col].apply(_clean_approx_cost)

    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].fillna("Various")
        df.loc[df["cuisines"].astype(str).str.strip() == "", "cuisines"] = "Various"

    df["approx_cost"] = df[cost_col]
    df = df.astype({"rate": "float64", "approx_cost": "int64"})

    return df
