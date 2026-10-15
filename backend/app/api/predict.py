import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.orm import Prediction
from app.services import player_service, ml_service
from app.services.defaults import default_height
from app.schemas.schemas import PredictRequest, PredictResponse

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db)):
    if payload.club_id is not None:
        prestige = player_service.latest_club_prestige(db, payload.club_id)
        if prestige is None:
            prestige = player_service.league_average_prestige(db, payload.league)
    else:
        prestige = player_service.league_average_prestige(db, payload.league)

    height = payload.height_in_cm or default_height(payload.sub_position)

    predicted_value = ml_service.predict_market_value(payload.model_dump(), prestige, height)

    record = Prediction(
        player_id=None,
        predicted_value_eur=predicted_value,
        model_version=ml_service.MODEL_NAME,
        input_payload=json.dumps(payload.model_dump()),
    )
    db.add(record)
    db.commit()

    return PredictResponse(
        predicted_value_eur=predicted_value,
        model_used=ml_service.MODEL_NAME,
        important_factors=ml_service.top_feature_names(5),
    )
