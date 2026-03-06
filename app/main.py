import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse
from pathlib import Path
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.db import Base, engine, SessionLocal
# Import all models to register metadata before create_all
import app.models
import app.models.appoinments
from app.api.doctor import router as doctors_router
from app.api.patient import router as patients_router
from app.api.visit import router as visits_router
from app.api.studies import router as studies_router
from app.api.study_items import router as study_items_route
from app.api.cie10 import router as cie10_router
from app.api.visit_diagnoses import router as visit_diag_router
from app.api.medications import router as medications_router
from app.api.prescriptions import router as prescriptions_router
from app.api.prescribed_items import router as prescribed_items_router
from app.api.attentions import router as attentions_router
from app.api.auth import router as auth_router
from app.api.admin import router as admins_router
from app.api.vitals import router as vitals_router
from app.api.patient_medical_history import router as medic_history
from app.api.patient_incapacities import router as patient_incapacities_router
from app.api.appoinments import router as appointments_router
from app.api.settings import router as settings_router
from app.services.file_storage import get_file_path, file_exists
from app.models.admin import Admin
from app.models.cie10 import CIE10Diagnosis
from app.services.passwords import get_password_hash

logger = logging.getLogger(__name__)

app = FastAPI(title="VitaCare API")

# CORS - Configuración permisiva para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Global exception handler para capturar todos los errores 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()},
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Routers
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(visits_router)
app.include_router(studies_router)
app.include_router(study_items_route)
app.include_router(cie10_router)
app.include_router(visit_diag_router)
app.include_router(medications_router)
app.include_router(prescriptions_router)
app.include_router(prescribed_items_router)
app.include_router(attentions_router)
app.include_router(auth_router)
app.include_router(admins_router)
app.include_router(vitals_router)
app.include_router(medic_history)
app.include_router(patient_incapacities_router)
app.include_router(appointments_router)
app.include_router(settings_router)


def _ensure_patients_columns() -> None:
    """Asegura compatibilidad de esquema para instalaciones existentes.

    Si la tabla patients existe pero no tiene columnas nuevas (occupation/origin/worker_type),
    las agrega para evitar errores 500 al consultar.
    """
    try:
        insp = inspect(engine)
        if "patients" not in insp.get_table_names():
            return

        cols = {c["name"] for c in insp.get_columns("patients")}
        missing = [c for c in ("occupation", "origin", "worker_type") if c not in cols]
        if not missing:
            return

        # Solo aplicar ALTER en MySQL/MariaDB (en otros motores, se deja manual)
        if engine.dialect.name != "mysql":
            logger.warning(
                "Tabla patients sin columnas %s, pero el motor no es mysql (%s).",
                ",".join(missing),
                engine.dialect.name,
            )
            return

        alter_parts = []
        if "occupation" in missing:
            alter_parts.append("ADD COLUMN occupation VARCHAR(255) NULL")
        if "origin" in missing:
            alter_parts.append("ADD COLUMN origin VARCHAR(255) NULL")
        if "worker_type" in missing:
            alter_parts.append("ADD COLUMN worker_type VARCHAR(20) NULL")

        if alter_parts:
            stmt = "ALTER TABLE patients " + ", ".join(alter_parts)
            with engine.begin() as conn:
                conn.execute(text(stmt))
            logger.info("Migración aplicada: %s", stmt)
    except Exception as e:
        logger.exception("No se pudo verificar/aplicar migración de patients: %s", e)


def _ensure_patient_incapacities_columns() -> None:
    """Asegura compatibilidad de esquema para patient_incapacities.

    Si la tabla patient_incapacities existe pero no tiene columnas nuevas (incapacity_for),
    las agrega para evitar errores 500 al consultar.
    """
    try:
        insp = inspect(engine)
        if "patient_incapacities" not in insp.get_table_names():
            return

        cols = {c["name"] for c in insp.get_columns("patient_incapacities")}
        if "incapacity_for" in cols:
            return

        # Solo aplicar ALTER en MySQL/MariaDB (en otros motores, se deja manual)
        if engine.dialect.name != "mysql":
            logger.warning(
                "Tabla patient_incapacities sin columna incapacity_for, pero el motor no es mysql (%s).",
                engine.dialect.name,
            )
            return

        stmt = "ALTER TABLE patient_incapacities ADD COLUMN incapacity_for VARCHAR(50) NULL"
        with engine.begin() as conn:
            conn.execute(text(stmt))
        logger.info("Migración aplicada: %s", stmt)
    except Exception as e:
        logger.exception(
            "No se pudo verificar/aplicar migración de patient_incapacities: %s", e
        )


def _ensure_prescriptions_pdf_path_column() -> None:
    """Asegura que la tabla prescriptions tenga la columna pdf_path.

    Si la tabla prescriptions existe pero no tiene la columna pdf_path,
    la agrega para almacenar la ruta del PDF generado.
    """
    try:
        insp = inspect(engine)
        if "prescriptions" not in insp.get_table_names():
            return

        cols = {c["name"] for c in insp.get_columns("prescriptions")}
        if "pdf_path" in cols:
            return

        # Solo aplicar ALTER en MySQL/MariaDB
        if engine.dialect.name != "mysql":
            logger.warning(
                "Tabla prescriptions sin columna pdf_path, pero el motor no es mysql (%s).",
                engine.dialect.name,
            )
            return

        stmt = "ALTER TABLE prescriptions ADD COLUMN pdf_path VARCHAR(255) NULL"
        with engine.begin() as conn:
            conn.execute(text(stmt))
        logger.info("Migración aplicada: %s", stmt)
    except Exception as e:
        logger.exception(
            "No se pudo verificar/aplicar migración de prescriptions pdf_path: %s", e
        )


@app.on_event("startup")
def seed_default_admin() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        logger.exception("No se pudo conectar a la base de datos durante startup: %s", e)
        return

    _ensure_patients_columns()
    _ensure_patient_incapacities_columns()
    _ensure_prescriptions_pdf_path_column()

    seed_enabled = os.getenv("SEED_DEFAULT_ADMIN", "true").lower() == "true"
    if not seed_enabled:
        return

    email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@vitacare.com").strip().lower()
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin123*")

    if not email or not password:
        return

    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.email == email).first()

        force_reset = os.getenv("SEED_DEFAULT_ADMIN_FORCE_RESET", "false").lower() == "true"
        if existing:
            if force_reset:
                existing.first_name = os.getenv("DEFAULT_ADMIN_FIRST_NAME", "Admin")
                existing.last_name = os.getenv("DEFAULT_ADMIN_LAST_NAME", "VitaCare")
                existing.middle_name = os.getenv("DEFAULT_ADMIN_MIDDLE_NAME") or None
                existing.hashed_password = get_password_hash(password)
                existing.is_active = True
                db.commit()
        else:
            obj = Admin(
                first_name=os.getenv("DEFAULT_ADMIN_FIRST_NAME", "Admin"),
                last_name=os.getenv("DEFAULT_ADMIN_LAST_NAME", "VitaCare"),
                middle_name=os.getenv("DEFAULT_ADMIN_MIDDLE_NAME") or None,
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True,
            )
            db.add(obj)
            db.commit()

        cie10_seed_enabled = os.getenv("SEED_CIE10", "true").lower() == "true"
        if cie10_seed_enabled:
            cie10_count = db.query(CIE10Diagnosis).count()
            if cie10_count == 0:
                seed_rows = [
                    {"code": "J00", "description": "Rinofaringitis aguda [resfriado común]", "cie_group": "J00", "notes": None},
                    {"code": "J06.9", "description": "Infección aguda de las vías respiratorias superiores, no especificada", "cie_group": "J06", "notes": None},
                    {"code": "J02.9", "description": "Faringitis aguda, no especificada", "cie_group": "J02", "notes": None},
                    {"code": "J03.9", "description": "Amigdalitis aguda, no especificada", "cie_group": "J03", "notes": None},
                    {"code": "J20.9", "description": "Bronquitis aguda, no especificada", "cie_group": "J20", "notes": None},
                    {"code": "J18.9", "description": "Neumonía, organismo no especificado", "cie_group": "J18", "notes": None},
                    {"code": "I10", "description": "Hipertensión esencial (primaria)", "cie_group": "I10", "notes": None},
                    {"code": "E11", "description": "Diabetes mellitus tipo 2", "cie_group": "E11", "notes": None},
                    {"code": "E10", "description": "Diabetes mellitus tipo 1", "cie_group": "E10", "notes": None},
                    {"code": "E78.5", "description": "Hiperlipidemia, no especificada", "cie_group": "E78", "notes": None},
                    {"code": "E66.9", "description": "Obesidad, no especificada", "cie_group": "E66", "notes": None},
                    {"code": "K29.7", "description": "Gastritis, no especificada", "cie_group": "K29", "notes": None},
                    {"code": "K21.9", "description": "Enfermedad por reflujo gastroesofágico sin esofagitis", "cie_group": "K21", "notes": None},
                    {"code": "R10.4", "description": "Otros dolores abdominales y los no especificados", "cie_group": "R10", "notes": None},
                    {"code": "N39.0", "description": "Infección de vías urinarias, sitio no especificado", "cie_group": "N39", "notes": None},
                    {"code": "M54.5", "description": "Lumbalgia", "cie_group": "M54", "notes": None},
                    {"code": "M25.5", "description": "Dolor articular", "cie_group": "M25", "notes": None},
                    {"code": "R51", "description": "Cefalea", "cie_group": "R51", "notes": None},
                    {"code": "F41.9", "description": "Trastorno de ansiedad, no especificado", "cie_group": "F41", "notes": None},
                    {"code": "F32.9", "description": "Episodio depresivo, no especificado", "cie_group": "F32", "notes": None},
                    {"code": "A09", "description": "Diarrea y gastroenteritis de presunto origen infeccioso", "cie_group": "A09", "notes": None},
                    {"code": "B34.9", "description": "Infección viral, no especificada", "cie_group": "B34", "notes": None},
                    {"code": "U07.1", "description": "COVID-19, virus identificado", "cie_group": "U07", "notes": None},
                    {"code": "Z00.0", "description": "Examen médico general", "cie_group": "Z00", "notes": None},
                ]
                db.add_all([CIE10Diagnosis(**r) for r in seed_rows])
                db.commit()
    finally:
        db.close()

# Configurar directorio de uploads para servir archivos estáticos
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Endpoint para servir archivos de study-items desde /uploads/study_items/
@app.get("/uploads/study_items/{filename}")
async def serve_study_item_file(filename: str):
    """
    Sirve archivos PDF de study items con headers correctos para abrir en el navegador.
    
    Args:
        filename: Nombre del archivo a servir
    
    Returns:
        Response: El archivo PDF con Content-Disposition: inline para abrir en el navegador
    """
    if not file_exists(filename):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    file_path = get_file_path(filename)
    
    # Leer el contenido del archivo
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Retornar Response con headers para abrir en el navegador
    return Response(
        content=file_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Content-Type": "application/pdf",
        }
    )

# Endpoint legacy para compatibilidad con /files/study-items/
@app.get("/files/study-items/{filename}")
async def serve_study_item_file_legacy(filename: str):
    """
    Endpoint legacy para compatibilidad. Redirige a /uploads/study_items/
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/uploads/study_items/{filename}")

@app.get("/")
def root():
  return {"message": "VitaCare backend funcionando"}
