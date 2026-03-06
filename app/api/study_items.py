from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db import get_db
from app.schemas.study_item import StudyItemCreate, StudyItemUpdate, StudyItemOut
from app.services import study_item_service
from app.services.file_storage import save_pdf_file

router = APIRouter(prefix="/study-items", tags=["study-items"])


class FileUploadResponse(BaseModel):
    """Respuesta del endpoint de subida de archivo"""
    url: str
    filename: str


@router.post("/", response_model=StudyItemOut, status_code=status.HTTP_201_CREATED)
def create(payload: StudyItemCreate, db: Session = Depends(get_db)):
    return study_item_service.create_study_item(db, payload)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    item_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo PDF para un study item.
    
    - Acepta archivos PDF en formato multipart/form-data
    - Valida que el archivo es un PDF (máximo 10 MB)
    - Guarda el archivo en el servidor
    - Si se proporciona item_id, actualiza el study_item con la URL automáticamente
    - Retorna la URL donde se puede acceder al archivo y el nombre del archivo
    
    Body (multipart/form-data):
        file: Archivo PDF a subir
        item_id (opcional): ID del study_item a actualizar con la URL
    
    Returns:
        {
            "url": "string",      # URL donde se puede acceder al archivo
            "filename": "string"  # Nombre del archivo guardado
        }
    """
    try:
        url, filename = await save_pdf_file(file)
        
        # Si se proporciona item_id, actualizar el study_item con la URL ANTES de retornar
        if item_id is not None:
            try:
                update_data = StudyItemUpdate(url=url)
                updated_item = study_item_service.update_study_item(db, item_id, update_data)
                if not updated_item:
                    # Si no se encontró el item, lanzar error
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Study item con id {item_id} no encontrado"
                    )
                # Verificar que la URL se guardó correctamente
                print(f"✓ URL actualizada para study_item {item_id}: {url}")
            except HTTPException:
                raise
            except Exception as update_error:
                # Si falla la actualización, lanzar error
                print(f"✗ Error al actualizar study_item {item_id}: {str(update_error)}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al actualizar study_item: {str(update_error)}"
                )
        
        return FileUploadResponse(url=url, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el archivo: {str(e)}"
        )

@router.post("/{item_id}/upload", response_model=StudyItemOut)
async def upload_file_and_update(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo PDF y actualiza el study_item con la URL del archivo.
    
    - Acepta archivos PDF en formato multipart/form-data
    - Valida que el archivo es un PDF (máximo 10 MB)
    - Guarda el archivo en el servidor
    - Actualiza el study_item con la URL del archivo
    
    Args:
        item_id: ID del study_item a actualizar
        file: Archivo PDF a subir
    
    Returns:
        StudyItemOut: El study_item actualizado con la URL del archivo
    """
    try:
        # Subir el archivo
        url, filename = await save_pdf_file(file)
        
        # Actualizar el study_item con la URL
        update_data = StudyItemUpdate(url=url)
        obj = study_item_service.update_study_item(db, item_id, update_data)
        
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study item not found"
            )
        
        return obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el archivo y actualizar el study item: {str(e)}"
        )

@router.get("/", response_model=List[StudyItemOut])
def all(study_order_id: int = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return study_item_service.list_study_items(db, study_order_id=study_order_id, skip=skip, limit=limit)

@router.get("/by-order/{study_order_id}", response_model=List[StudyItemOut])
def get_items_by_order(study_order_id: int, db: Session = Depends(get_db)):
    items = study_item_service.list_items_by_order(db, study_order_id)
    return items

@router.put("/{item_id}", response_model=StudyItemOut)
def update(item_id: int, payload: StudyItemUpdate, db: Session = Depends(get_db)):
    obj = study_item_service.update_study_item(db, item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Study item not found")
    return obj
