from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import player_service
from app.schemas.schemas import ClubOut

router = APIRouter(prefix="/api/clubs", tags=["clubs"])


@router.get("", response_model=list[ClubOut])
def list_clubs(db: Session = Depends(get_db)):
    return player_service.list_clubs(db)
