from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.cie10 import CIE10Create, CIE10Out
from app.services import cie10_service

router = APIRouter(prefix="/cie10-diagnoses", tags=["cie10"])

@router.post("/", response_model=CIE10Out, status_code=status.HTTP_201_CREATED)
def create(payload: CIE10Create, db: Session = Depends(get_db)):
    return cie10_service.create_cie10(db, payload)

@router.get("/", response_model=List[CIE10Out])
def all(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return cie10_service.list_cie10(db, skip=skip, limit=limit)
