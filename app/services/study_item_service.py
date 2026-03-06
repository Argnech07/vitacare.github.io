from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.study_item import StudyItem
from app.schemas.study_item import StudyItemCreate, StudyItemUpdate
from fastapi import HTTPException, status  
from app.models.study_item import StudyItem
from app.models.study_order import StudyOrder 
from app.models.doctor import Doctor          

def create_study_item(db: Session, data: StudyItemCreate) -> StudyItem:
    # Obtener la orden de estudio para acceder al doctor_id
    study_order = db.query(StudyOrder).filter(StudyOrder.id == data.study_order_id).first()
    if not study_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de estudio no encontrada"
        )
    
    # Obtener el doctor desde la orden
    doctor = db.query(Doctor).filter(Doctor.id == study_order.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor no encontrado en la orden de estudio"
        )
    
    # Crear el objeto con el nombre del doctor
    item_data = data.model_dump()
    
    # Si no se proporcionó assigned_doctor, calcularlo desde la orden
    if not item_data.get("assigned_doctor"):
        # Construir el nombre completo del doctor con prefijo "Dr."
        doctor_parts = []
        if doctor.first_name:
            doctor_parts.append(doctor.first_name)
        if doctor.middle_name:
            doctor_parts.append(doctor.middle_name)
        if doctor.last_name:
            doctor_parts.append(doctor.last_name)
        doctor_name = " ".join(doctor_parts) if doctor_parts else ""
        doctor_full_name = f"Dr. {doctor_name}" if doctor_name else "Dr."
        item_data["assigned_doctor"] = doctor_full_name
    
    obj = StudyItem(**item_data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_study_item(db: Session, item_id: int) -> Optional[StudyItem]:
    """Obtiene un study_item, manejando el caso donde assigned_doctor no existe"""
    from sqlalchemy import text
    try:
        # Intentar con el modelo normal primero
        return db.query(StudyItem).filter(StudyItem.id == item_id).first()
    except Exception:
        # Si falla (probablemente por columna faltante), usar SQL crudo
        db.rollback()
        items_query = text("""
            SELECT id, study_order_id, study_type, name, reason, 
                   document_date, status, url
            FROM study_items 
            WHERE id = :item_id
        """)
        result = db.execute(items_query, {"item_id": item_id}).fetchone()
        
        if not result:
            return None
        
        # Crear un objeto StudyItem con los datos obtenidos
        # Usar un valor por defecto para assigned_doctor
        item_dict = {
            "id": result.id,
            "study_order_id": result.study_order_id,
            "study_type": result.study_type,
            "name": result.name,
            "reason": result.reason,
            "document_date": result.document_date,
            "status": result.status or "pending",
            "url": result.url,
            "assigned_doctor": "Falta Definir"
        }
        # Crear un objeto StudyItem manualmente
        obj = StudyItem(**item_dict)
        # Asignar el ID directamente ya que es una primary key
        obj.id = result.id
        return obj

def list_study_items(db: Session, study_order_id: int = None, skip=0, limit=50) -> List[StudyItem]:
    query = db.query(StudyItem)
    if study_order_id is not None:
        query = query.filter(StudyItem.study_order_id == study_order_id)
    return query.offset(skip).limit(limit).all()

def list_items_by_order(db: Session, study_order_id: int) -> list[StudyItem]:
    return db.query(StudyItem).filter(StudyItem.study_order_id == study_order_id).all()

def update_study_item(
    db: Session,
    item_id: int,
    data: StudyItemUpdate,
) -> Optional[StudyItem]:
    """Actualiza un study_item, manejando el caso donde assigned_doctor no existe"""
    from sqlalchemy import text
    
    # Verificar que el item existe primero
    check_query = text("SELECT id FROM study_items WHERE id = :item_id")
    result = db.execute(check_query, {"item_id": item_id}).fetchone()
    if not result:
        return None
    
    upd = data.model_dump(exclude_unset=True)
    
    if not upd:
        return get_study_item(db, item_id)  # No hay nada que actualizar
    
    # Usar SQL crudo directamente para mayor confiabilidad
    # Construir la query de actualización dinámicamente
    set_clauses = []
    params = {"item_id": item_id}
    
    # Mapeo de nombres de campos Python a nombres de columnas SQL
    field_to_column = {
        'study_order_id': 'study_order_id',
        'study_type': 'study_type',
        'name': 'name',
        'reason': 'reason',
        'document_date': 'document_date',
        'status': 'status',
        'url': 'url',
        'assigned_doctor': 'assigned_doctor'  # Intentar incluir, pero puede fallar
    }
    
    for k, v in upd.items():
        if k in field_to_column:
            column_name = field_to_column[k]
            set_clauses.append(f"{column_name} = :{k}")
            params[k] = v
    
    if not set_clauses:
        return get_study_item(db, item_id)  # No hay nada que actualizar
    
    # Intentar actualización con assigned_doctor primero
    try:
        update_query = text(f"""
            UPDATE study_items 
            SET {', '.join(set_clauses)}
            WHERE id = :item_id
        """)
        db.execute(update_query, params)
        db.commit()
    except Exception:
        # Si falla, probablemente assigned_doctor no existe, intentar sin ella
        db.rollback()
        set_clauses = [clause for clause in set_clauses if 'assigned_doctor' not in clause]
        params.pop('assigned_doctor', None)
        
        if set_clauses:
            update_query = text(f"""
                UPDATE study_items 
                SET {', '.join(set_clauses)}
                WHERE id = :item_id
            """)
            db.execute(update_query, params)
            db.commit()
    
    # Obtener el objeto actualizado
    return get_study_item(db, item_id)
