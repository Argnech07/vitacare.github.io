from pydantic import BaseModel


class LogoSettingsOut(BaseModel):
    logo_url: str | None = None


class LogoSettingsUpdate(BaseModel):
    logo_url: str | None = None
