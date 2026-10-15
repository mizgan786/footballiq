"""
conftest.py

Tests shouldn't depend on a developer having manually run `python -m
app.database.seed` beforehand. This fixture makes sure the DB is created
and seeded exactly once per test session, regardless of run order.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.database.db import Base, engine
from app.models.orm import Player
from app.database.db import SessionLocal
from app.database import seed as seed_module


@pytest.fixture(scope="session", autouse=True)
def ensure_seeded_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    has_data = db.query(Player).first() is not None
    db.close()
    if not has_data:
        seed_module.main()
    yield
