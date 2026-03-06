from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.study_item import StudyItem
from app.models.study_order import StudyOrder
from app.models.patient import Patient
from app.models.doctor import Doctor

from app.schemas.study_order import (
    StudyOrderCreate,
    StudyOrderFull,
    PatientInfo,
    DoctorInfo,
)
from app.schemas.study_item import StudyItemOut


def create_study_order(db: Session, data: StudyOrderCreate) -> StudyOrder:
    obj = StudyOrder(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_study_orders(db: Session, skip: int = 0, limit: int = 50) -> List[StudyOrder]:
    return db.query(StudyOrder).offset(skip).limit(limit).all()


def get_study_order(db: Session, order_id: int) -> Optional[StudyOrder]:
    return db.query(StudyOrder).filter(StudyOrder.id == order_id).first()


def get_study_order_full(db: Session, order_id: int) -> Optional[StudyOrderFull]:
    """
    Obtiene una orden de estudio completa con todos sus items,
    información del paciente y médico para mostrar en la card.
    """
    result = (
        db.query(StudyOrder, Patient, Doctor)
        .join(Patient, StudyOrder.patient_id == Patient.id)
        .join(Doctor, StudyOrder.doctor_id == Doctor.id)
        .filter(StudyOrder.id == order_id)
        .first()
    )

    if not result:
        return None

    study_order, patient, doctor = result

    # Items
    try:
        items = (
            db.query(StudyItem)
            .filter(StudyItem.study_order_id == order_id)
            .all()
        )
        items_out = [StudyItemOut.model_validate(item) for item in items]
    except Exception:
        db.rollback()
        items_query = text("""
            SELECT id, study_order_id, study_type, name, reason,
                   document_date, status, url
            FROM study_items
            WHERE study_order_id = :order_id
        """)
        items_result = db.execute(items_query, {"order_id": order_id}).fetchall()

        items_out = []
        for row in items_result:
            item_dict = {
                "id": row.id,
                "study_order_id": row.study_order_id,
                "study_type": row.study_type,
                "name": row.name,
                "reason": row.reason,
                "document_date": row.document_date,
                "status": row.status or "pending",
                "url": row.url,
                "assigned_doctor": "Falta Definir",
            }
            items_out.append(StudyItemOut.model_validate(item_dict))

    # Nombre completo paciente
    patient_parts: list[str] = []
    if patient.first_name:
        patient_parts.append(patient.first_name)
    if patient.middle_name:
        patient_parts.append(patient.middle_name)
    if patient.last_name:
        patient_parts.append(patient.last_name)
    patient_full_name = " ".join(patient_parts)

    # Nombre completo doctor
    doctor_parts: list[str] = []
    if doctor.first_name:
        doctor_parts.append(doctor.first_name)
    if doctor.middle_name:
        doctor_parts.append(doctor.middle_name)
    if doctor.last_name:
        doctor_parts.append(doctor.last_name)
    doctor_name = " ".join(doctor_parts) if doctor_parts else ""
    doctor_full_name = f"Dr. {doctor_name}" if doctor_name else ""

    # Motivo desde el primer item
    reason = items_out[0].reason if items_out and items_out[0].reason else None

    return StudyOrderFull(
        id=study_order.id,
        patient_id=study_order.patient_id,
        doctor_id=study_order.doctor_id,
        order_date=study_order.order_date,
        patient=PatientInfo(
            id=patient.id,
            full_name=patient_full_name,
        ),
        doctor=DoctorInfo(
            id=doctor.id,
            full_name=doctor_full_name,
        ),
        reason=reason,
        items=items_out,
    )


def list_study_orders_by_patient(
    db: Session, patient_id: int, skip: int = 0, limit: int = 50
) -> List[StudyOrder]:
    """
    Lista órdenes de estudio por paciente.
    """
    return (
        db.query(StudyOrder)
        .filter(StudyOrder.patient_id == patient_id)
        .order_by(StudyOrder.order_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def approve_study_order(db: Session, order_id: int) -> Optional[StudyOrder]:
    """
    Aprueba una orden de estudio cambiando el estado de todos sus items a 'approved'.
    """
    order = db.query(StudyOrder).filter(StudyOrder.id == order_id).first()
    if not order:
        return None

    items = db.query(StudyItem).filter(StudyItem.study_order_id == order_id).all()
    for item in items:
        item.status = "approved"

    db.commit()
    db.refresh(order)
    return order


def reject_study_order(db: Session, order_id: int) -> Optional[StudyOrder]:
    """
    Rechaza una orden de estudio cambiando el estado de todos sus items a 'cancelled'.
    """
    order = db.query(StudyOrder).filter(StudyOrder.id == order_id).first()
    if not order:
        return None

    items = db.query(StudyItem).filter(StudyItem.study_order_id == order_id).all()
    for item in items:
        item.status = "cancelled"

    db.commit()
    db.refresh(order)
    return order


def get_pending_study_items_by_order(db: Session, order_id: int) -> List[StudyItem]:
    """
    Obtiene todos los items pendientes de una orden de estudio específica.
    """
    return (
        db.query(StudyItem)
        .filter(StudyItem.study_order_id == order_id)
        .filter(StudyItem.status == "pending")
        .all()
    )


def list_pending_study_orders(
    db: Session, skip: int = 0, limit: int = 50
) -> List[StudyOrderFull]:
    """
    Lista todas las órdenes de estudio que tienen al menos un item pendiente.
    Devuelve las órdenes completas con información de paciente y médico.
    """
    orders_with_pending = (
        db.query(StudyItem.study_order_id)
        .filter(StudyItem.status == "pending")
        .distinct()
        .subquery()
    )

    orders_result = (
        db.query(StudyOrder, Patient, Doctor)
        .join(Patient, StudyOrder.patient_id == Patient.id)
        .join(Doctor, StudyOrder.doctor_id == Doctor.id)
        .join(orders_with_pending, StudyOrder.id == orders_with_pending.c.study_order_id)
        .order_by(StudyOrder.order_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result: list[StudyOrderFull] = []
    for study_order, patient, doctor in orders_result:
        items = (
            db.query(StudyItem)
            .filter(StudyItem.study_order_id == study_order.id)
            .all()
        )

        # Nombre completo paciente
        patient_parts: list[str] = []
        if patient.first_name:
            patient_parts.append(patient.first_name)
        if patient.middle_name:
            patient_parts.append(patient.middle_name)
        if patient.last_name:
            patient_parts.append(patient.last_name)
        patient_full_name = " ".join(patient_parts)

        # Nombre completo doctor
        doctor_parts: list[str] = []
        if doctor.first_name:
            doctor_parts.append(doctor.first_name)
        if doctor.middle_name:
            doctor_parts.append(doctor.middle_name)
        if doctor.last_name:
            doctor_parts.append(doctor.last_name)
        doctor_name = " ".join(doctor_parts) if doctor_parts else ""
        doctor_full_name = f"Dr. {doctor_name}" if doctor_name else ""

        reason = items[0].reason if items and items[0].reason else None

        result.append(
            StudyOrderFull(
                id=study_order.id,
                patient_id=study_order.patient_id,
                doctor_id=study_order.doctor_id,
                order_date=study_order.order_date,
                patient=PatientInfo(
                    id=patient.id,
                    full_name=patient_full_name,
                ),
                doctor=DoctorInfo(
                    id=doctor.id,
                    full_name=doctor_full_name,
                ),
                reason=reason,
                items=[StudyItemOut.model_validate(item) for item in items],
            )
        )

    return result
