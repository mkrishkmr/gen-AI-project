# Contributing to AI Restaurant Recommendations

Thank you for your interest in contributing! This guide will get you set up quickly.

---

## Getting Started

### 1. Fork and clone
```bash
git clone https://github.com/<your-username>/ai-restaurant-recommender.git
cd ai-restaurant-recommender
```

### 2. Set up environment
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. Configure `.env`
```env
GROQ_API_KEY=your_key_here
HF_DATASET=ManikaSaini/zomato-restaurant-recommendation
```

### 4. Verify your setup
```bash
python validate_components.py
```
All checks should pass before making changes.

---

## Development Workflow

```
feature branch → local tests → PR to main
```

- Create a branch: `git checkout -b feat/short-description`
- Keep commits atomic and descriptive
- Run tests before pushing: `pytest tests/test_data.py tests/test_retrieval.py -v`
- Open a PR with a clear description of what and why

---

## Code Style

| Rule | Convention |
|---|---|
| Formatting | PEP 8; 4-space indent |
| Docstrings | Google-style (`Args:`, `Returns:`, `Raises:`) |
| Type hints | Required on all public functions |
| Max line length | 100 characters |

---

## Project Structure (Quick Ref)

| Folder | Add code here when... |
|---|---|
| `Phase_1_Data/` | Changing how the dataset is loaded or cleaned |
| `Phase_2_Search/` | Modifying search/filter/ranking logic |
| `Phase_3_LLM/` | Changing prompt design or LLM provider |
| `Phase_4_App/api/` | Adding or modifying REST endpoints |
| `Phase_4_App/ui/` | Changing the Streamlit UI |
| `tests/` | Adding test coverage for any of the above |

---

## Tests

```bash
# Unit tests only (fast, no network)
pytest tests/test_data.py tests/test_retrieval.py tests/test_llm_logic.py -v

# Full suite
pytest -v
```

New features must include corresponding test coverage.

---

## Reporting Issues

Please open a GitHub Issue with:
- A clear title
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

---

## Questions?

Open a [GitHub Discussion](https://github.com/mkrishkmr/ai-restaurant-recommender/discussions) for questions, ideas, or feature requests.
