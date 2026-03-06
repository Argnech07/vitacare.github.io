# Importar todos los modelos para que SQLAlchemy pueda resolver las relaciones
# El orden importa: primero los modelos base, luego los que tienen relaciones

from app.models.admin import Admin
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.vitals import Vitals
from app.models.patient_medical_history import PatientMedicalHistory
from app.models.visit import Visit
from app.models.study_order import StudyOrder
from app.models.study_item import StudyItem
from app.models.cie10 import CIE10Diagnosis
from app.models.visit_diagnosis import VisitDiagnosis
from app.models.prescription import Prescription
from app.models.prescribed_item import PrescribedItem
from app.models.medication import Medication
from app.models.appoinments import Appointment
from app.models.patient_incapacity import PatientIncapacity
from app.models.app_setting import AppSetting
#from app.models.attention import Attention
