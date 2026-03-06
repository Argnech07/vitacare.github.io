import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status

# Directorio base para almacenar archivos
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
STUDY_ITEMS_DIR = os.path.join(UPLOAD_DIR, "study_items")

# Extensiones permitidas para PDFs
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _ensure_directories():
    """Asegura que los directorios de almacenamiento existan"""
    os.makedirs(STUDY_ITEMS_DIR, exist_ok=True)


def _get_file_extension(filename: str) -> str:
    """Obtiene la extensión del archivo"""
    return Path(filename).suffix.lower()


def _is_allowed_file(filename: str) -> bool:
    """Verifica si el archivo tiene una extensión permitida"""
    return _get_file_extension(filename) in ALLOWED_EXTENSIONS


async def save_pdf_file(file: UploadFile) -> Tuple[str, str]:
    """
    Guarda un archivo PDF y retorna la URL y el nombre del archivo.
    
    Args:
        file: Archivo a guardar (UploadFile de FastAPI)
    
    Returns:
        Tuple[str, str]: (url, filename) - URL relativa y nombre del archivo
    
    Raises:
        HTTPException: Si el archivo no es válido
    """
    # Asegurar que los directorios existan
    _ensure_directories()
    
    # Validar que se proporcionó un archivo
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionó un archivo"
        )
    
    # Validar extensión
    if not _is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos PDF (.pdf)"
        )
    
    # Leer el contenido del archivo
    content = await file.read()
    file_size = len(content)
    
    # Validar tamaño del archivo
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo es demasiado grande. Tamaño máximo: {MAX_FILE_SIZE / (1024*1024):.1f} MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío"
        )
    
    # Generar nombre único para el archivo
    file_extension = _get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    
    # Ruta completa del archivo
    file_path = os.path.join(STUDY_ITEMS_DIR, unique_filename)
    
    # Guardar el archivo
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Retornar URL relativa y nombre del archivo
    # La URL será en formato /uploads/study_items/{nombre}
    url = f"/uploads/study_items/{unique_filename}"
    return url, unique_filename


def get_file_path(filename: str) -> Path:
    """
    Obtiene la ruta completa del archivo a partir del nombre del archivo.
    
    Args:
        filename: Nombre del archivo (sin ruta)
    
    Returns:
        Path: Ruta completa del archivo
    """
    return Path(STUDY_ITEMS_DIR) / filename


def file_exists(filename: str) -> bool:
    """Verifica si un archivo existe"""
    file_path = get_file_path(filename)
    return file_path.exists() and file_path.is_file()

