"""
FastAPI Backend - Recommendation API endpoint.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import from src modules (run with PYTHONPATH=.)
from Phase_1_Data.data.loader import load_and_clean_dataset
from Phase_2_Search.engine.search import get_candidates
from Phase_3_LLM.llm.groq_client import format_recommendation

app = FastAPI(title="AI Restaurant Recommendation API")

# CORS for Streamlit/frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cached dataframe (loaded once)
_df = None


def get_df():
    """Lazy-load and cache the dataset."""
    global _df
    if _df is None:
        _df = load_and_clean_dataset()
    return _df


class RecommendRequest(BaseModel):
    """Request schema for /recommend."""
    location: str
    cuisine: str
    max_budget: int
    min_rating: float = 0.0
    notes: Optional[str] = None


@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Get AI-powered restaurant recommendations.
    """
    df = get_df()
    candidates = get_candidates(
        df,
        location=req.location,
        cuisine=req.cuisine,
        max_budget=req.max_budget,
        min_rating=req.min_rating,
        top_k=5,
    )
    if candidates.empty:
        raise HTTPException(status_code=404, detail="No restaurants found for your criteria.")
    user_input = {
        "location": req.location,
        "cuisine": req.cuisine,
        "max_budget": req.max_budget,
        "min_rating": req.min_rating,
        "notes": req.notes or "",
    }
    try:
        result = format_recommendation(user_input, candidates)
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
