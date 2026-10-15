import json
import os
from fastapi import APIRouter

from app.services import ml_service
from app.schemas.schemas import ModelMetricsOut

router = APIRouter(prefix="/api/model", tags=["model"])

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models")


@router.get("/metrics", response_model=ModelMetricsOut)
def metrics():
    with open(os.path.join(MODELS_DIR, "validation_results.json")) as f:
        validation = json.load(f)
    with open(os.path.join(MODELS_DIR, "test_results.json")) as f:
        test = json.load(f)
    return ModelMetricsOut(model_name=ml_service.MODEL_NAME, validation=validation, test=test)
