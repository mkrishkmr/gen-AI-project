
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from Phase_1_Data.data.loader import load_and_clean_dataset
from Phase_2_Search.engine.search import get_candidates

def test_loader():
    print("Testing DataLoader...")
    try:
        df = load_and_clean_dataset()
        print(f"[SUCCESS] Dataset loaded successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[FAIL] DataLoader failed: {e}")
        return None

def test_search(df):
    if df is None:
        print("[SKIP] Skipping Search test due to DataLoader failure.")
        return

    print("Testing Search engine...")
    locations = ['Indiranagar', 'BTM', 'Koramangala']
    for loc in locations:
        candidates = get_candidates(
            df,
            location=loc,
            cuisine='North Indian',
            max_budget=1000,
            min_rating=3.0,
            top_k=5
        )
        if len(candidates) >= 3:
            print(f"[SUCCESS] Search for '{loc}' returned {len(candidates)} candidates.")
        else:
            print(f"[WARNING] Search for '{loc}' returned only {len(candidates)} candidates.")

if __name__ == "__main__":
    df = test_loader()
    test_search(df)
