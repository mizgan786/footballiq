# FootballIQ

**Football player market-value prediction with an AI assistant.**
A full-stack project that predicts a player's market value from performance and context, explains the prediction, and lets you ask questions about the data in plain English.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![XGBoost](https://img.shields.io/badge/XGBoost-model-EB5B27)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)

<!-- Add screenshots here once you have them, e.g.:
![Dashboard](docs/screenshots/dashboard.png)
-->

## Features

- **Dashboard** with headline numbers and the most valuable players in the dataset.
- **Player search and profile** with season-by-season stats and a predicted vs. actual value history.
- **Value predictor** where you enter a player's profile and stats and get an estimate.
- **Player comparison** with a side-by-side radar chart and stat table.
- **Analytics** page with model performance, feature importance, and league-level breakdowns.
- **AI assistant** (floating chat widget plus a full page) that answers football questions from a small knowledge base (RAG) and looks up live player data and predictions through tool calls. Each reply comes with suggested follow-up questions.

## How it works

```
Browser (React) --> FastAPI --> Database (PostgreSQL or SQLite)
                       |
                       +--> XGBoost model
                       |
                       +--> Chat service --> RAG index (TF-IDF)
                                         --> Tools --> Database / Model
                                         --> OpenAI API
```

1. **Data**: Transfermarkt exports for the top-5 European leagues, 2012 to 2025, are cleaned and turned into a player-season panel. Each row is one player in one season, joined to the market valuation closest to the end of that season (30 June, within about 6 months).
2. **Model**: an XGBoost regressor trained on the log of market value, using 26 features (age, height, position, preferred foot, league, appearances, goals, assists, minutes, cards, and a club-prestige feature based on the club's average value in the previous season).
3. **API**: FastAPI serves players, predictions, comparisons, analytics, and chat. The model is loaded once when the app starts.
4. **Assistant**: a tool-calling loop over OpenAI. For football-concept questions it retrieves relevant chunks from a small document set; for data questions it calls tools that query the database and run the model.

## Model results

The split is **time-aware**, so the model never sees the future during training.

| Split | Seasons |
|-------|---------|
| Train | 2012 to 2020 |
| Validation | 2021 to 2022 |
| Test | 2023 to 2025 |

On the held-out test seasons, the selected XGBoost model reaches:

| Metric | Value |
|--------|-------|
| R² | about 0.73 |
| MAE | about €4.7M |
| MAPE | about 65% |

Dataset: 35,858 cleaned player-seasons. Plots are in [`reports/`](reports/).

## Tech stack

| Layer | Tools |
|-------|-------|
| ML | pandas, NumPy, scikit-learn, XGBoost, joblib |
| Backend | FastAPI, SQLAlchemy, Pydantic v2, SQLite (default) or PostgreSQL |
| Assistant | OpenAI API (tool calling), TF-IDF retrieval over local documents |
| Frontend | React, Vite, Tailwind CSS v4, React Router, Recharts, Axios |
| Tests | pytest, httpx, Vitest, Testing Library |
| DevOps | Docker, Docker Compose, nginx |

## Project structure

```
footballiq/
├── backend/          FastAPI app (api, services, models, schemas, database) and tests
├── frontend/         React app (pages, components, hooks, context, services)
├── scripts/          data collection, cleaning, feature engineering, training, evaluation
├── data/processed/   cleaned panel and model features
├── models/           trained model and evaluation results
├── rag/              knowledge-base documents and the retrieval index
├── reports/          evaluation plots
├── tests/            data pipeline tests
└── docker-compose.yml
```

## Getting started

### Option 1: Docker (simplest)

Requires Docker Desktop.

```bash
git clone https://github.com/mizgan786/footballiq.git
cd footballiq
cp .env.example .env        # then add your OpenAI key (optional, see below)
docker compose up --build
```

- App: http://localhost:5173
- API docs: http://localhost:8000/docs

The AI assistant needs `OPENAI_API_KEY` in `.env`. Everything else works without it.

### Option 2: Run locally

Requires Python 3.12 and Node 20+.

**Backend**

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp ../.env.example .env               # add OPENAI_API_KEY if you want the assistant
python -m app.database.seed
uvicorn app.main:app --reload
```

On macOS, XGBoost needs OpenMP: `brew install libomp`.

**Frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Rebuilding the model and search index

The trained model and retrieval index are included. If you hit a pickle or version warning on your machine, retrain inside your own environment:

```bash
pip install -r scripts/requirements.txt
python scripts/train_model.py
python scripts/evaluate_model.py
python rag/ingest.py
```

### Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | Enables the AI assistant | not set |
| `LLM_PROVIDER` | Chat provider | `openai` |
| `OPENAI_MODEL` | Chat model | `gpt-4o-mini` |
| `CORS_ORIGINS` | Allowed browser origins | local dev origins |
| `DATABASE_URL` | Database connection | SQLite file |

For PostgreSQL, use the driver in the URL, for example `postgresql+psycopg2://user:pass@host:5432/db`.

Never commit a real `.env` file.

## API overview

Interactive docs are served at `/docs`. Main groups:

| Area | Purpose |
|------|---------|
| `/api/players` | Search, filter, and fetch player profiles with season history |
| `/api/predict` | Predict market value for a player profile |
| `/api/compare` | Compare players side by side |
| `/api/analytics` | Aggregated stats for
