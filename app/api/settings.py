from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.settings import LogoSettingsOut, LogoSettingsUpdate
from app.services.security import get_current_admin
from app.services import settings_service
from app.models.admin import Admin


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/logo", response_model=LogoSettingsOut)
def get_logo(db: Session = Depends(get_db)):
    return LogoSettingsOut(logo_url=settings_service.get_logo_url(db))


@router.put("/logo", response_model=LogoSettingsOut)
def update_logo(
    payload: LogoSettingsUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return LogoSettingsOut(logo_url=settings_service.set_logo_url(db, payload.logo_url))
