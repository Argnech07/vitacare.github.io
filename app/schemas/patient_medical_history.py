# app/schemas/patient_medical_history.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FamilyHistory(BaseModel):
    diabetes: Optional[bool] = None
    breast_cancer: Optional[bool] = None
    other_cancers: Optional[bool] = None
    hypertension: Optional[bool] = None
    tuberculosis: Optional[bool] = None
    cardiopathies: Optional[bool] = None
    renal_disease: Optional[bool] = None
    allergies: Optional[bool] = None
    allergies_text: Optional[str] = None
    osteoporosis: Optional[bool] = None
    bleeding_disorders: Optional[bool] = None
    smoking: Optional[bool] = None
    addictions: Optional[bool] = None
    other: Optional[str] = None


class PersonalHabits(BaseModel):
    tobacco: Optional[bool] = None
    smoking_start_age: Optional[int] = None
    cigarettes_per_day: Optional[int] = None
    alcohol: Optional[bool] = None
    drugs: Optional[bool] = None

    allergies_text: Optional[str] = None

    previous_hospitalizations: Optional[str] = None
    chronic_diseases: Optional[str] = None
    surgeries: Optional[str] = None
    fractures: Optional[str] = None
    transfusions: Optional[str] = None


class PatientMedicalHistoryBase(BaseModel):
    family_history: Optional[FamilyHistory] = None
    personal_habits: Optional[PersonalHabits] = None


class PatientMedicalHistoryCreate(PatientMedicalHistoryBase):
    pass  # porque created_at/updated_at los maneja la DB


class PatientMedicalHistoryUpdate(PatientMedicalHistoryBase):
    pass  # partial update; usamos exclude_unset en el servicio


class PatientMedicalHistoryOut(PatientMedicalHistoryBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
