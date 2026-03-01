<div align="center">

# 🍽️ AI Restaurant Recommendations

**Hyper-personalized restaurant discovery, powered by Groq LLaMA 3.3 and the Zomato dataset.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?logo=groq&logoColor=white)](https://console.groq.com/)
[![Hugging Face](https://img.shields.io/badge/Dataset-Hugging_Face-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 🚀 What is this?

**AI Restaurant Recommendations** is a full-stack GenAI application that combines **semantic search** with **LLM-powered reasoning** to help users find the perfect restaurant — not just by keyword, but by *why it fits you*.

Simply tell the app your preferred cuisine, location, and budget. The system:
1. Filters 50,000+ Zomato restaurants in milliseconds
2. Sends the top candidates to **Groq's LLaMA 3.3 70B** model
3. Returns AI-generated cards explaining *why each restaurant suits you*, with dish suggestions and vibe descriptions

> Built with a Zomato-inspired UI — red accents, clean cards, instant search.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Smart Filtering** | Filters by cuisine, location, budget, and rating. Auto-relaxes search if results are sparse |
| 🤖 **AI Insights** | LLaMA 3.3 70B generates personalized "why it fits you" explanations per restaurant |
| 🎨 **Zomato-style UI** | Clean Streamlit interface with `#E23744` brand color, card layout, and dish tags |
| 🌐 **REST API** | FastAPI backend (`/recommend`) for headless or programmatic access |
| 🧪 **Test Suite** | pytest coverage for data cleaning, search engine, and LLM logic |

---

## 🏗️ Project Structure

```
ai-restaurant-recommender/
│
├── Phase_1_Data/                 # Phase 1: Data Preparation
│   └── data/
│       └── loader.py             # Hugging Face dataset loader & cleaner
├── Phase_2_Search/               # Phase 2: Core Search Engine
│   └── engine/
│       └── search.py             # Restaurant filtering & ranking logic
├── Phase_3_LLM/                  # Phase 3: AI Insights Generation
│   └── llm/
│       └── groq_client.py        # Groq API client (LLaMA 3.3 70B)
├── Phase_4_App/                  # Phase 4: Full App API & UI
│   ├── api/
│   │   └── main.py               # FastAPI REST endpoint
│   └── ui/
│       └── app.py                # Streamlit web interface
│
├── tests/                        # pytest test suite
│   ├── test_data.py              # Data loader & cleaning tests
│   ├── test_retrieval.py         # Search engine tests
│   ├── test_llm_logic.py         # LLM client logic tests
│   └── e2e_test.py               # End-to-end integration tests
│
├── docs/
│   └── ARCHITECTURE.md           # System architecture diagrams
│
├── .streamlit/
│   └── config.toml               # Streamlit theme config
│
├── validate_components.py        # Component health-check script
├── start.py                      # Dev launcher (auto port-finding)
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
└── ARCHITECTURE.md               # Architecture overview (root)
```

---

## ⚡ Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/mkrishkmr/ai-restaurant-recommender.git
cd ai-restaurant-recommender
```

### 2. Set up environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API keys
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_DATASET=ManikaSaini/zomato-restaurant-recommendation
```
> Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run the app
```bash
python -m streamlit run Phase_4_App/ui/app.py
```
The app will be available at **http://localhost:8501**

---

## 🔌 REST API

To run the FastAPI backend independently:
```bash
uvicorn src.api.main:app --reload
```

**Endpoint:** `POST /recommend`
```json
{
  "location": "Indiranagar",
  "cuisine": "North Indian",
  "max_budget": 800,
  "min_rating": 4.0
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "name": "Punjabi Tadka",
      "why_it_fits": "Highly rated North Indian spot in Indiranagar within your budget...",
      "suggested_dishes": ["Dal Makhani", "Butter Naan"],
      "vibe": "Casual, family-friendly"
    }
  ]
}
```

---

## 🧪 Running Tests

```bash
# Run all unit tests (fast, no API calls)
pytest tests/test_data.py tests/test_retrieval.py tests/test_llm_logic.py -v

# Run component health check
python validate_components.py

# Run full suite including integration
pytest -v
```

---

## 🧠 How It Works

```
User Input (Cuisine + Location + Budget)
         │
         ▼
  [src/engine/search.py]          ← Filters 51,717 restaurants
         │                           Relaxed fallback if <3 results
         ▼
  [src/llm/groq_client.py]        ← LLaMA 3.3 70B via Groq API
         │                           Structured JSON output
         ▼
  [src/ui/app.py]                 ← Zomato-style card rendering
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed data flow diagrams.

---

## 🛠️ Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **UI** | Streamlit | Web interface with Zomato-style CSS |
| **LLM** | Groq + LLaMA 3.3 70B | AI-powered recommendation reasoning |
| **Data** | Hugging Face Datasets + pandas | Dataset loading and cleaning |
| **API** | FastAPI + Uvicorn | Backend REST endpoint |
| **Tests** | pytest | Automated test coverage |

---

## 🗺️ Roadmap

- [ ] Semantic search with vector embeddings (FAISS/ChromaDB)
- [ ] Multi-city support beyond Bangalore
- [ ] User preference memory across sessions
- [ ] Restaurant photo thumbnails via Google Places API
- [ ] Mobile-responsive PWA wrapper

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to get started.

---

## 📄 License

MIT © 2025 [mkrishkmr](https://github.com/mkrishkmr)
