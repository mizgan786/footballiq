import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.database.db import Base, engine
from app.api import players, predict, compare, analytics, model, chat, clubs

# app.services.ml_service loads the trained model at import time (module-level
# joblib.load), so importing it here - once - is what satisfies "load the model
# once at startup, never per-request".
from app.services import ml_service  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # no-op if seed.py already ran
    print(f"FootballIQ API starting up. Model loaded: {ml_service.MODEL_NAME}")
    yield


app = FastAPI(
    title="FootballIQ API",
    description="ML-powered football player market-value prediction and analytics.",
    version="0.1.0",
    lifespan=lifespan,
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(clubs.router)
app.include_router(predict.router)
app.include_router(compare.router)
app.include_router(analytics.router)
app.include_router(model.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"service": "FootballIQ API", "status": "ok", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
