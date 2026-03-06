from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate, PrescriptionOut
from app.services import prescription_service
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import qrcode
import datetime
import os

# Directorio para almacenar PDFs de recetas
PDF_STORAGE_DIR = os.path.join(os.getcwd(), "uploads", "prescriptions")
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

# Debug: Log the current working directory and storage path
import logging
logger = logging.getLogger(__name__)
logger.info(f"[PDF] Current working directory: {os.getcwd()}")
logger.info(f"[PDF] PDF_STORAGE_DIR: {PDF_STORAGE_DIR}")
logger.info(f"[PDF] Directory exists after makedirs: {os.path.exists(PDF_STORAGE_DIR)}")

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.post("/", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
def create(payload: PrescriptionCreate, db: Session = Depends(get_db)):
    # Crear la prescripción
    prescription = prescription_service.create_prescription(db, payload)
    
    # Generar y guardar el PDF (después de que se agreguen los medicamentos)
    # Esto se hará en un endpoint separado o cuando se consulte el PDF por primera vez
    
    return prescription

@router.get("/", response_model=List[PrescriptionOut])
def all(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return prescription_service.list_prescriptions(db, patient_id=patient_id, doctor_id=doctor_id, skip=skip, limit=limit)

@router.get("/{prescription_id}", response_model=PrescriptionOut)
def get_one(prescription_id: int, db: Session = Depends(get_db)):
    obj = prescription_service.get_prescription(db, prescription_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return obj

@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update(prescription_id: int, payload: PrescriptionUpdate, db: Session = Depends(get_db)):
    obj = prescription_service.update_prescription(db, prescription_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return obj

@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(prescription_id: int, db: Session = Depends(get_db)):
    deleted = prescription_service.delete_prescription(db, prescription_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prescription not found")


def generate_prescription_pdf(data: dict) -> io.BytesIO:
    """Genera un PDF de receta médica con los datos proporcionados"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Estilo personalizado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#111827'),
        alignment=1,  # Centrado
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        alignment=1,
        spaceAfter=6
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#111827'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )
    
    # Título
    story.append(Paragraph("RECETA MÉDICA", title_style))
    story.append(Spacer(1, 12))
    
    # Folio y Fecha
    folio = data.get('folio', '---')
    date_str = data.get('date', datetime.date.today().isoformat())
    story.append(Paragraph(f"<b>Folio:</b> {folio} &nbsp;&nbsp;&nbsp; <b>Fecha:</b> {date_str}", subtitle_style))
    story.append(Spacer(1, 12))
    
    # Paciente
    patient = data.get('patient', {})
    if patient:
        story.append(Paragraph("DATOS DEL PACIENTE", section_style))
        patient_name = patient.get('full_name', '---')
        patient_bd = patient.get('birth_date', '---')
        patient_gender = patient.get('gender', '---')
        story.append(Paragraph(f"<b>Nombre:</b> {patient_name}", normal_style))
        story.append(Paragraph(f"<b>F. Nacimiento:</b> {patient_bd} &nbsp;&nbsp;&nbsp; <b>Sexo:</b> {patient_gender}", normal_style))
        story.append(Spacer(1, 12))
    
    # Diagnóstico
    diagnosis = data.get('diagnosis', {})
    primary = diagnosis.get('primary', '') if diagnosis else ''
    secondary = diagnosis.get('secondary', []) if diagnosis else []
    if primary or secondary:
        story.append(Paragraph("DIAGNÓSTICO", section_style))
        if primary:
            story.append(Paragraph(f"<b>Principal:</b> {primary}", normal_style))
        if secondary:
            story.append(Paragraph(f"<b>Secundarios:</b> {', '.join(secondary)}", normal_style))
        story.append(Spacer(1, 12))
    
    # Medicamentos
    medications = data.get('medications', [])
    if medications:
        story.append(Paragraph("TRATAMIENTO", section_style))
        for i, med in enumerate(medications, 1):
            med_name = med.get('name', '---')
            presentation = med.get('presentation', '')
            dosage = med.get('dosage', '')
            freq = med.get('frequency_hours', '')
            duration = med.get('duration_days', '')
            route = med.get('route', '')
            notes = med.get('notes', '')
            
            med_text = f"<b>{i}. {med_name}</b>"
            if presentation:
                med_text += f" - {presentation}"
            story.append(Paragraph(med_text, normal_style))
            
            details = []
            if dosage:
                details.append(f"Dosis: {dosage}")
            if freq:
                details.append(f"cada {freq} horas")
            if duration:
                details.append(f"por {duration} días")
            if route:
                details.append(f"Vía: {route.upper()}")
            if details:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{', '.join(details)}", normal_style))
            if notes:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;<i>Notas: {notes}</i>", normal_style))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))
    
    # Notas generales
    notes = data.get('notes', '')
    if notes:
        story.append(Paragraph("INSTRUCCIONES ADICIONALES", section_style))
        story.append(Paragraph(notes, normal_style))
        story.append(Spacer(1, 12))
    
    # Médico
    doctor = data.get('doctor', {})
    if doctor:
        story.append(Paragraph("MÉDICO TRATANTE", section_style))
        doctor_name = doctor.get('full_name', '---')
        specialty = data.get('specialty', '---')
        license = data.get('license_number', '---')
        story.append(Paragraph(f"<b>Dr. {doctor_name}</b>", normal_style))
        story.append(Paragraph(f"<b>Especialidad:</b> {specialty}", normal_style))
        story.append(Paragraph(f"<b>Céd. Profesional:</b> {license}", normal_style))
        story.append(Spacer(1, 24))
    
    # Firma
    story.append(Spacer(1, 36))
    story.append(Table([['', '______________________________']], colWidths=[200, 200]))
    story.append(Paragraph("Firma del Médico", ParagraphStyle('Signature', parent=styles['Normal'], fontSize=9, alignment=1)))
    story.append(Spacer(1, 12))
    
    # Footer
    story.append(Spacer(1, 24))
    footer_text = f"Receta generada el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} hrs - Expira a los 3 días hábiles"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)))
    
    # Generar QR con URL completa del PDF (configurable)
    # Usar variable de entorno VITACARE_SERVER_URL o fallback a localhost
    SERVER_URL = os.environ.get('VITACARE_SERVER_URL', 'http://localhost:8000')
    qr_url = f"{SERVER_URL}/prescriptions/pdf/{folio}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Agregar QR al final
    story.append(Spacer(1, 12))
    qr_rl_image = RLImage(qr_buffer, width=1.2*inch, height=1.2*inch)
    qr_table = Table([[qr_rl_image]], colWidths=[100])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(qr_table)
    story.append(Paragraph(f"Código de verificación: {folio}", ParagraphStyle('QRLabel', parent=styles['Normal'], fontSize=8, alignment=1)))
    story.append(Paragraph(f"<i>Escanea para ver el PDF</i>", ParagraphStyle('QRHint', parent=styles['Normal'], fontSize=7, alignment=1, textColor=colors.gray)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def save_prescription_pdf_to_file(pdf_buffer: io.BytesIO, folio: str) -> str:
    """Guarda el PDF de la receta en el servidor y retorna la ruta del archivo"""
    import logging
    logger = logging.getLogger(__name__)
    
    filename = f"receta-{folio}.pdf"
    filepath = os.path.join(PDF_STORAGE_DIR, filename)
    
    logger.info(f"[PDF] Intentando guardar en: {filepath}")
    logger.info(f"[PDF] Directorio de almacenamiento: {PDF_STORAGE_DIR}")
    logger.info(f"[PDF] Directorio existe: {os.path.exists(PDF_STORAGE_DIR)}")
    logger.info(f"[PDF] Directorio es escribible: {os.access(PDF_STORAGE_DIR, os.W_OK)}")
    
    try:
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        logger.info(f"[PDF] Archivo guardado exitosamente: {filepath}")
    except Exception as e:
        logger.error(f"[PDF] Error al escribir archivo: {str(e)}")
        raise
    
    return filepath


@router.get("/pdf/{folio}")
def get_pdf_by_folio(folio: str, db: Session = Depends(get_db)):
    """Obtener el PDF de una receta por su folio - genera, guarda y sirve el archivo"""
    import logging
    logger = logging.getLogger(__name__)
    
    # El folio tiene formato RC-YYYY-XXX, extraer el ID
    try:
        parts = folio.split("-")
        if len(parts) >= 3:
            prescription_id = int(parts[-1])
        else:
            raise HTTPException(status_code=400, detail="Formato de folio inválido")
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Formato de folio inválido")
    
    # Verificar si existe un PDF guardado en la base de datos
    prescription = prescription_service.get_prescription(db, prescription_id)
    # NOTA: Siempre regenerar el PDF para asegurar que el QR tenga la URL correcta
    # El PDF se sirve desde memoria, no desde archivo guardado
    if False and prescription and prescription.pdf_path and os.path.exists(prescription.pdf_path):
        # Servir el PDF guardado - DESHABILITADO para forzar regeneración
        logger.info(f"[PDF] Sirviendo PDF guardado: {prescription.pdf_path}")
        return FileResponse(
            prescription.pdf_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=receta-{folio}.pdf",
            }
        )
    
    # Si no existe PDF guardado, generar uno nuevo y guardarlo
    logger.info(f"[PDF] Generando nuevo PDF para receta {prescription_id}")
    result = prescription_service.verify_prescription_by_id(db, prescription_id)
    if not result:
        raise HTTPException(status_code=404, detail="Receta no encontrada o inválida")
    
    # Generar PDF
    try:
        pdf_buffer = generate_prescription_pdf(result)
        logger.info(f"[PDF] PDF generado, tamaño: {len(pdf_buffer.getvalue())} bytes")
    except Exception as e:
        logger.error(f"[PDF] Error generando PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
    
    # Guardar PDF en disco
    try:
        pdf_path = save_prescription_pdf_to_file(pdf_buffer, folio)
        logger.info(f"[PDF] PDF guardado en: {pdf_path}")
    except Exception as e:
        logger.error(f"[PDF] Error guardando PDF en disco: {str(e)}")
        # Continuar sin guardar - servir el PDF desde memoria
        pdf_path = None
    
    # Actualizar la BD con la ruta del PDF (si se guardó exitosamente)
    if pdf_path and prescription:
        try:
            prescription_service.update_prescription_pdf_path(db, prescription_id, pdf_path)
            logger.info(f"[PDF] Ruta actualizada en BD: {pdf_path}")
        except Exception as e:
            logger.error(f"[PDF] Error actualizando BD: {str(e)}")
    
    # Servir el PDF (desde archivo si se guardó, o desde memoria)
    if pdf_path and os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=receta-{folio}.pdf",
            }
        )
    else:
        # Fallback: servir desde memoria
        pdf_buffer.seek(0)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=receta-{folio}.pdf",
                "Content-Type": "application/pdf"
            }
        )


@router.post("/generate-pdf/{prescription_id}")
def generate_and_save_pdf(prescription_id: int, db: Session = Depends(get_db)):
    """Genera y guarda el PDF de una receta en el servidor"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[PDF] Iniciando generación PDF para prescription_id: {prescription_id}")
    
    # Verificar que la receta existe
    prescription = prescription_service.get_prescription(db, prescription_id)
    if not prescription:
        logger.error(f"[PDF] Receta no encontrada: {prescription_id}")
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    logger.info(f"[PDF] Receta encontrada: {prescription.id}")
    
    # Obtener los datos completos de la receta
    result = prescription_service.verify_prescription_by_id(db, prescription_id)
    if not result:
        logger.error(f"[PDF] No se pudieron obtener datos de receta: {prescription_id}")
        raise HTTPException(status_code=404, detail="No se pudieron obtener los datos de la receta")
    
    logger.info(f"[PDF] Datos de receta obtenidos: {result.get('folio')}")
    
    # Generar el folio
    folio = result.get('folio', f"RC-{prescription.date.year}-{str(prescription.id).zfill(3)}")
    logger.info(f"[PDF] Folio generado: {folio}")
    
    # Generar el PDF
    try:
        pdf_buffer = generate_prescription_pdf(result)
        logger.info(f"[PDF] PDF generado en buffer, tamaño: {len(pdf_buffer.getvalue())} bytes")
    except Exception as e:
        logger.error(f"[PDF] Error generando PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
    
    # Guardar el PDF en el servidor
    try:
        pdf_path = save_prescription_pdf_to_file(pdf_buffer, folio)
        logger.info(f"[PDF] PDF guardado en: {pdf_path}")
    except Exception as e:
        logger.error(f"[PDF] Error guardando PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error guardando PDF: {str(e)}")
    
    # Actualizar la receta con la ruta del PDF
    try:
        prescription_service.update_prescription_pdf_path(db, prescription_id, pdf_path)
        logger.info(f"[PDF] Ruta de PDF actualizada en BD para prescription_id: {prescription_id}")
    except Exception as e:
        logger.error(f"[PDF] Error actualizando BD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error actualizando BD: {str(e)}")
    
    return {
        "success": True,
        "message": "PDF generado y guardado correctamente",
        "folio": folio,
        "pdf_path": pdf_path,
        "pdf_url": f"/prescriptions/pdf/{folio}"
    }


@router.get("/verify/{folio}")
def verify_by_folio(folio: str, db: Session = Depends(get_db)):
    """Verificar una receta por su folio - ahora redirige al PDF"""
    # El folio tiene formato RC-YYYY-XXX, extraer el ID
    try:
        parts = folio.split("-")
        if len(parts) >= 3:
            prescription_id = int(parts[-1])
        else:
            raise HTTPException(status_code=400, detail="Formato de folio inválido")
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Formato de folio inválido")
    
    result = prescription_service.verify_prescription_by_id(db, prescription_id)
    if not result:
        raise HTTPException(status_code=404, detail="Receta no encontrada o inválida")
    
    # Retornar la información básica y la URL del PDF
    return {
        "valid": True,
        "folio": folio,
        "pdf_url": f"/prescriptions/pdf/{folio}",
        "prescription": result
    }
