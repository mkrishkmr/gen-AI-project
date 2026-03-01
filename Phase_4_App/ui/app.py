"""
Zomato-style Restaurant Recommendation UI.
Design: Primary #E23744, Background #FFFFFF. Hero search + restaurant cards.
"""

import os
import sys

# Ensure project root is on path and load .env
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _root)
os.chdir(_root)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st

# Load data and logic directly (no API required for standalone mode)
from Phase_1_Data.data.loader import load_and_clean_dataset
from Phase_2_Search.engine.search import get_candidates
from Phase_3_LLM.llm.groq_client import format_recommendation

# Zomato brand colors
PRIMARY = "#E23744"
BACKGROUND = "#FFFFFF"
CARD_BORDER = "#E5E7EB"
TEXT_MUTED = "#6B7280"
RATING_GREEN = "#22c55e"

# Custom CSS for Zomato-style look (primary #E23744, clean sans-serif, card styling)
st.set_page_config(
    page_title="AI Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
    /* Global: Zomato Red #E23744, clean sans-serif */
    * {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    .stApp {{ background-color: {BACKGROUND}; }}
    
    /* Hero: Zomato Red gradient */
    .hero {{
        background: linear-gradient(135deg, {PRIMARY} 0%, #c42f3a 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(226, 55, 68, 0.3);
    }}
    .hero h1 {{
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }}
    .hero p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1rem;
    }}
    
    /* Restaurant card: white container, light grey border, subtle shadow */
    .restaurant-card {{
        background: {BACKGROUND};
        border: 1px solid {CARD_BORDER};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s;
    }}
    .restaurant-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }}
    
    .card-title {{
        font-size: 1.35rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }}
    
    /* Rating badge: green (Zomato-style) */
    .rating-badge {{
        display: inline-block;
        background: {RATING_GREEN};
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }}
    
    .ai-insight {{
        background: #FEF2F2;
        border-left: 4px solid {PRIMARY};
        padding: 0.75rem 1rem;
        margin: 0.75rem 0;
        font-style: italic;
        color: #4B5563;
        border-radius: 0 8px 8px 0;
    }}
    
    .dish-tag {{
        display: inline-block;
        background: #FEE2E2;
        color: {PRIMARY};
        padding: 0.25rem 0.6rem;
        margin: 0.2rem 0.2rem 0 0;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
    }}
    .dish-tag:hover {{
        background: #FECACA;
    }}
    
    .vibe-text {{
        color: {TEXT_MUTED};
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """Load and cache the dataset (runs once)."""
    return load_and_clean_dataset()


def _get_unique_locations(df) -> list:
    """Extract unique location values, sorted."""
    if "location" not in df.columns:
        return []
    locs = df["location"].dropna().astype(str).str.strip()
    locs = locs[locs != ""].unique().tolist()
    return sorted([str(x) for x in locs])


def _get_unique_cuisines(df) -> list:
    """Extract unique cuisine types from comma-separated 'cuisines' column."""
    if "cuisines" not in df.columns:
        return []
    cuisines = set()
    for val in df["cuisines"].dropna().astype(str):
        for c in val.split(","):
            c = c.strip()
            if c and c.lower() != "various":
                cuisines.add(c)
    return sorted(cuisines)


def main():
    # Hero search section
    st.markdown(
        """
        <div class="hero">
            <h1>🍽️ AI Restaurant Recommendations</h1>
            <p>Tell us what you crave. We'll find the perfect spot.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load data for dropdown options and search
    try:
        df = load_data()
    except PermissionError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    # Use df['location'].unique() for locations (sorted)
    locations = sorted(df["location"].dropna().astype(str).str.strip().unique().tolist())
    locations = [x for x in locations if x and x.lower() != "nan"]
    if not locations:
        locations = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]

    cuisines_list = _get_unique_cuisines(df)
    if not cuisines_list:
        cuisines_list = ["North Indian", "Chinese", "South Indian", "Italian", "Bakery"]

    # Filter inputs: dropdowns and slider
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        cuisines_selected = st.multiselect(
            "Cuisine",
            options=cuisines_list,
            default=[cuisines_list[0]] if cuisines_list else [],
            help="Select one or more cuisines.",
        )
        cuisine = cuisines_selected[0] if cuisines_selected else (cuisines_list[0] if cuisines_list else "")
    with col2:
        location = st.selectbox(
            "Location / City",
            options=locations,
            index=0 if locations else 0,
            help="Where do you want to eat?",
        )
    with col3:
        price_options = {
            "Budget (<300)": 300,
            "Mid-range (300-700)": 700,
            "Premium (700-1500)": 1500,
            "Fine Dining (1500+)": 99999,
        }
        price_label = st.selectbox(
            "Price Range",
            options=list(price_options.keys()),
            index=1,
            help="Budget for two people.",
        )
        max_budget = price_options[price_label]
    with col4:
        min_rating = st.select_slider(
            "Min Rating",
            options=[2.0, 3.0, 4.0, 4.5],
            value=4.0,
            format_func=lambda x: f"{x}⭐",
            help="Minimum restaurant rating.",
        )

    search_clicked = st.button("🔍 Find Restaurants", type="primary", use_container_width=False)

    if search_clicked:
        if not cuisines_selected:
            st.warning("Please select at least one cuisine.")
            st.stop()
        with st.spinner("Finding restaurants..."):
            candidates = get_candidates(
                df,
                location=location,
                cuisine=cuisine,
                max_budget=max_budget,
                min_rating=min_rating,
                top_k=5,
            )

        if candidates.empty:
            st.error(f"No restaurants found for **{cuisine}** in **{location}** under ₹{max_budget}. Try broadening your search.")
        else:
            with st.spinner("Getting AI insights from Groq..."):
                try:
                    user_input = {
                        "location": location,
                        "cuisine": cuisine,
                        "max_budget": max_budget,
                        "min_rating": min_rating,
                    }
                    result = format_recommendation(user_input, candidates)

                    # Build name->row lookup for rating/address
                    name_to_row = {}
                    for _, row in candidates.iterrows():
                        name_to_row[str(row.get("name", "")).strip()] = row

                    st.markdown("---")
                    st.subheader("Your Recommendations")

                    for rec in result.get("recommendations", []):
                        name = rec.get("name", "Unknown")
                        why = rec.get("why_it_fits", "")
                        dishes = rec.get("suggested_dishes", [])
                        vibe = rec.get("vibe", "")

                        row = name_to_row.get(name)
                        rating = float(row["rate"]) if row is not None and "rate" in row else 0
                        address = ""
                        if row is not None:
                            address = str(row.get("address", "") or row.get("location", ""))

                        dish_tags = "".join(f'<span class="dish-tag">{d}</span>' for d in dishes)
                        card_html = (
                            f'<div class="restaurant-card">'
                            f'<div class="card-title">{name}</div>'
                            f'<span class="rating-badge">{rating:.1f} ⭐</span>'
                            f'<div class="ai-insight">{why}</div>'
                            f'<div><strong>Top dishes:</strong> {dish_tags}</div>'
                        )
                        if vibe:
                            card_html += f'<div class="vibe-text">Vibe: {vibe}</div>'
                        if address:
                            card_html += f'<div class="vibe-text" style="margin-top:0.5rem">📍 {address}</div>'
                        card_html += "</div>"

                        st.markdown(card_html, unsafe_allow_html=True)

                except ValueError as e:
                    if "GROQ_API_KEY" in str(e):
                        st.error("Please set GROQ_API_KEY in your .env file to use AI recommendations.")
                    else:
                        st.error(str(e))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")


if __name__ == "__main__":
    main()
