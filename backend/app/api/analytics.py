import json
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import player_service, analytics_service
from app.schemas.schemas import AnalyticsSummaryOut, PlayerCardOut, AnalyticsChartsOut

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

TEST_RESULTS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "test_results.json")


@router.get("/summary", response_model=AnalyticsSummaryOut)
def summary(db: Session = Depends(get_db)):
    data = player_service.analytics_summary(db)

    with open(TEST_RESULTS_PATH) as f:
        test_results = json.load(f)

    return AnalyticsSummaryOut(
        players_analyzed=data["players_analyzed"],
        seasons_covered=data["seasons_covered"],
        average_market_value_eur=data["average_market_value_eur"],
        highest_valued_player=PlayerCardOut(**data["highest_valued_player"]),
        model_r2=test_results["R2"],
    )


@router.get("/charts", response_model=AnalyticsChartsOut)
def charts(db: Session = Depends(get_db)):
    """Backs every chart on the Analytics page - all computed from the real
    dataset/model, nothing hard-coded (see analytics_service.py)."""
    return AnalyticsChartsOut(
        market_value_distribution=analytics_service.market_value_distribution(db),
        value_by_position=analytics_service.value_by_position(db),
        age_vs_value=analytics_service.age_vs_value(db),
        goals_vs_value=analytics_service.goals_vs_value(db),
        actual_vs_predicted=analytics_service.actual_vs_predicted(),
        feature_importance=analytics_service.feature_importance(),
    )
