from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class VitalsBase(BaseModel):
    # Campos sin límites para permitir guardar cualquier dato o null
    systolic: Optional[int] = Field(None, description="Presión sistólica (mmHg)")
    diastolic: Optional[int] = Field(None, description="Presión diastólica (mmHg)")
    heart_rate: Optional[int] = Field(None, description="Frecuencia cardíaca (bpm)")
    respiratory_rate: Optional[int] = Field(None, description="Frecuencia respiratoria (rpm)")
    temperature: Optional[float] = Field(None, description="Temperatura (°C)")
    glucose: Optional[float] = Field(None, description="Glucosa (mg/dL)")
    weight: Optional[float] = Field(None, description="Peso (kg)")
    height: Optional[float] = Field(None, description="Estatura (cm)")
    bmi: Optional[float] = Field(None, description="Índice de masa corporal")

    waist_cm: Optional[float] = Field(None, description="Circunferencia de cintura (cm)")
    abdomen_cm: Optional[float] = Field(None, description="Circunferencia abdominal (cm)")
    hip_cm: Optional[float] = Field(None, description="Circunferencia de cadera (cm)")
    head_circumference_cm: Optional[float] = Field(None, description="Circunferencia cefálica (cm)")


class VitalsCreate(VitalsBase):
    taken_at: datetime = Field(..., description="Fecha y hora de la toma")


class VitalsUpdate(VitalsBase):
    taken_at: Optional[datetime] = None


class VitalsOut(VitalsBase):
    id: int
    patient_id: int
    taken_at: datetime

    class Config:
        from_attributes = True  # si usas Pydantic v2
        # orm_mode = True  # usa esto en lugar de from_attributes si estás en Pydantic v1
