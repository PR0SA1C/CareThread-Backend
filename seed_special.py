import os
import uuid
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url and url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

engine = create_engine(url)

with engine.begin() as conn:
    patients = conn.execute(text("SELECT id FROM patients LIMIT 3")).fetchall()
    
    for p in patients:
        pid = p[0]
        enc = conn.execute(text("SELECT id FROM encounters WHERE patient_id = :pid LIMIT 1"), {"pid": pid}).first()
        eid = enc[0] if enc else None

        # 1. Insert Radiology & Pathology Documents
        conn.execute(text("""
            INSERT INTO documents (id, patient_id, encounter_id, title, file_type, storage_key, uploaded_at)
            VALUES 
            (:id1, :pid, :eid, 'Chest X-Ray AP View', 'application/dicom', 's3://carethread-bucket/scans/chest_xray_2026.dcm', CURRENT_TIMESTAMP),
            (:id2, :pid, :eid, 'Complete Blood Count (CBC)', 'application/pdf', 's3://carethread-bucket/reports/cbc_blood_report.pdf', CURRENT_TIMESTAMP)
        """), {"id1": str(uuid.uuid4()), "id2": str(uuid.uuid4()), "pid": pid, "eid": eid})
        
        # 2. Insert Psychiatry Condition (Restricted Subclass)
        conn.execute(text("""
            INSERT INTO conditions (id, patient_id, encounter_id, icd10_code, description, status, onset_date, recorded_at, sensitivity_subclass, locked)
            VALUES 
            (:id, :pid, :eid, 'F32.9', 'Major Depressive Disorder, Single Episode', 'active', '2025-01-01', CURRENT_TIMESTAMP, 'mental_health', false)
        """), {"id": str(uuid.uuid4()), "pid": pid, "eid": eid})
        
print("Successfully injected mock Medical Documents (DICOM/PDF) and Psychiatric Conditions!")
