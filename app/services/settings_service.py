from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting


def get_setting(db: Session, key: str) -> AppSetting | None:
    return db.query(AppSetting).filter(AppSetting.key == key).first()


def upsert_setting(db: Session, key: str, value: str | None) -> AppSetting:
    existing = get_setting(db, key)
    if existing:
        existing.value = value
        db.commit()
        db.refresh(existing)
        return existing

    obj = AppSetting(key=key, value=value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_logo_url(db: Session) -> str | None:
    s = get_setting(db, "logo_url")
    return s.value if s else None


def set_logo_url(db: Session, logo_url: str | None) -> str | None:
    s = upsert_setting(db, "logo_url", logo_url)
    return s.value
