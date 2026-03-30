from fastapi import Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class HistoryClassifyRequest(BaseModel):
    predicted_class: str
    confidence: float
    model_used: str

    @classmethod
    def as_form(
        cls,
        predicted_class: str = Form(...),
        confidence: float = Form(...),
        model_used: str = Form(...),
    ) -> "HistoryClassifyRequest":
        return cls(predicted_class=predicted_class, confidence=confidence, model_used=model_used)


class HistoryClassifyResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    image_path: str
    predicted_class: str
    confidence: float
    model_used: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HistoryClassifyListResponse(BaseModel):
    items: List[HistoryClassifyResponse]
    total: int
    page: int
    paginate: int
    total_pages: int

