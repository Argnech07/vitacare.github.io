from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.prescribed_item import PrescribedItem
from app.models.prescription import Prescription
from app.schemas.prescribed_item import PrescribedItemCreate, PrescribedItemUpdate


def create_prescribed_item(db: Session, data: PrescribedItemCreate, clear_existing: bool = False) -> PrescribedItem:
    """
    Crea un prescribed_item.
    Si clear_existing es True, elimina TODOS los items existentes de la prescripción primero.
    Por defecto, si hay más de 5 items existentes (duplicados masivos), los elimina.
    Esto permite crear hasta 5 items normalmente, pero detecta y limpia duplicados masivos.
    """
    # Verificar cuántos items existen
    existing_items = db.query(PrescribedItem).filter(
        PrescribedItem.prescription_id == data.prescription_id
    ).all()
    
    # Si se solicita limpiar explícitamente, o si hay más de 5 items (duplicados masivos),
    # eliminar todos los items existentes primero
    if clear_existing or len(existing_items) > 5:
        for item in existing_items:
            db.delete(item)
        db.flush()
    
    # Crear el nuevo item
    obj = PrescribedItem(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_prescribed_item(db: Session, item_id: int) -> Optional[PrescribedItem]:
    return db.query(PrescribedItem).filter(PrescribedItem.id == item_id).first()


def list_prescribed_items(
    db: Session,
    prescription_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[PrescribedItem]:
    query = db.query(PrescribedItem)

    if prescription_id is not None:
        query = query.filter(PrescribedItem.prescription_id == prescription_id)

    if patient_id is not None:
        query = (
            query.join(Prescription, PrescribedItem.prescription_id == Prescription.id)
            .filter(Prescription.patient_id == patient_id)
        )

    return query.offset(skip).limit(limit).all()


def update_prescribed_item(
    db: Session,
    item_id: int,
    data: PrescribedItemUpdate,
) -> Optional[PrescribedItem]:
    obj = get_prescribed_item(db, item_id)
    if not obj:
        return None
    upd = data.model_dump(exclude_unset=True)
    for k, v in upd.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_prescribed_item(db: Session, item_id: int) -> bool:
    obj = get_prescribed_item(db, item_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def replace_prescribed_items(
    db: Session,
    prescription_id: int,
    items: List[PrescribedItemCreate],
) -> List[PrescribedItem]:
    """
    Reemplaza todos los prescribed_items de una prescripción.
    Primero elimina todos los existentes (dejando la prescripción en blanco),
    luego inserta los nuevos items.
    """
    try:
        # Paso 1: Obtener y eliminar TODOS los items existentes de esta prescripción
        existing_items = db.query(PrescribedItem).filter(
            PrescribedItem.prescription_id == prescription_id
        ).all()
        
        # Eliminar cada item uno por uno
        for item in existing_items:
            db.delete(item)
        
        # Hacer flush antes del commit para asegurar que las eliminaciones se procesen
        db.flush()
        # Hacer commit de la eliminación para asegurar que quede en blanco
        db.commit()
        
        # Paso 2: Crear los nuevos items (si se proporcionaron)
        new_items = []
        if items and len(items) > 0:
            for item_data in items:
                # Asegurar que el prescription_id sea el correcto
                item_dict = item_data.model_dump()
                item_dict['prescription_id'] = prescription_id
                obj = PrescribedItem(**item_dict)
                db.add(obj)
                new_items.append(obj)
            
            # Hacer flush antes del commit
            db.flush()
            # Hacer commit de la creación de los nuevos items
            db.commit()
            
            # Refrescar los objetos para obtener los IDs generados
            for item in new_items:
                db.refresh(item)
        
        return new_items
    except Exception as e:
        # Si hay algún error, hacer rollback
        db.rollback()
        raise
