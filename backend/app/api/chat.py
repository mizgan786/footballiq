from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import chat_service, llm_service
from app.schemas.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    try:
        history = [{"role": m.role, "content": m.content} for m in payload.history]
        result = chat_service.run_chat(db, payload.message, history)
        return ChatResponse(**result)
    except llm_service.LLMNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except llm_service.LLMRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))
