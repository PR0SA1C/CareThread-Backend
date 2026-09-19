from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from security.dependencies import get_current_user
from schemas.auth import UserContext

router = APIRouter(prefix="/api/v1/clinical", tags=["Clinical Data"])

@router.get("/patients/{abha_id}/timeline")
def get_patient_timeline(
    abha_id: str, 
    db: Session = Depends(get_db), 
    current_user: UserContext = Depends(get_current_user)
):
    """
    Fetches the clinical timeline for a patient.
    Dynamically filters the output based on the user's Tier (Department) and Sensitivity.
    """
    
    # 1. Resolve ABHA ID to internal Patient UUID
    patient_row = db.execute(
        text("SELECT id FROM patients WHERE abha_id = :abha"), 
        {"abha": abha_id}
    ).first()
    
    if not patient_row:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    patient_uuid = patient_row[0]
    dept = current_user.department
    
    # 2. Tier 1: Administrative (Blocked from clinical)
    if dept in ["ORG_RECEPTION", "ORG_BILLING"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tier 1 Administrative roles cannot view clinical timelines."
        )
        
    # [Future Feature: Check active consent in the 'consents' table here]

    timeline = {}
    
    # Tier 2 (Pathology / Radiology): Fetch Documents (Scans / Reports)
    if dept in ["ORG_PATHOLOGY", "ORG_RADIOLOGY", "ORG_DOCTOR", "ORG_NURSE", "ORG_ER", "ORG_PSYCHIATRIST"] or current_user.user_type == "PATIENT":
        # We can add an extra filter here based on file_type if we want to get extremely strict
        # (e.g., Radiology sees DICOM scans and PDF reports, Pathology sees PDF blood reports)
        doc_filter = ""
        if dept == "ORG_RADIOLOGY": doc_filter = "AND file_type IN ('application/dicom', 'application/pdf')"
        elif dept == "ORG_PATHOLOGY": doc_filter = "AND file_type = 'application/pdf'"
        
        docs = db.execute(
            text(f"SELECT id, title, file_type, storage_key, uploaded_at FROM documents WHERE patient_id = :pid {doc_filter}"), 
            {"pid": patient_uuid}
        ).fetchall()
        
        timeline['documents'] = [
            {"id": str(r[0]), "title": r[1], "file_type": r[2], "url": r[3], "uploaded_at": r[4]} 
            for r in docs
        ]

    # 3. Tier 2 (Pharmacist), Tier 3 (Doctor/Nurse/ER), Tier 4 (Psychiatrist), & Patient
    if dept in ["ORG_PHARMACIST", "ORG_DOCTOR", "ORG_NURSE", "ORG_ER", "ORG_PSYCHIATRIST"] or current_user.user_type == "PATIENT":
        # Fetch Medications
        meds = db.execute(
            text("SELECT id, name, dosage, frequency, status, start_date FROM medications WHERE patient_id = :pid"), 
            {"pid": patient_uuid}
        ).fetchall()
        timeline['medications'] = [
            {"id": str(r[0]), "name": r[1], "dosage": r[2], "frequency": r[3], "status": r[4], "start_date": r[5]} 
            for r in meds
        ]
        
    # 4. Tier 3 (Doctor/Nurse/ER), Tier 4 (Psychiatrist), & Patient
    if dept in ["ORG_DOCTOR", "ORG_NURSE", "ORG_ER", "ORG_PSYCHIATRIST"] or current_user.user_type == "PATIENT":
        
        # Enforce Sensitivity Subclass Filter
        # Only Psychiatrists or the Patient themselves can see restricted subclasses (Mental Health)
        sens_filter = "" 
        if dept != "ORG_PSYCHIATRIST" and current_user.user_type != "PATIENT":
            sens_filter = "AND sensitivity_subclass = 'standard'"
            
        # Fetch Conditions (Diagnoses)
        conds = db.execute(
            text(f"SELECT id, description, status, onset_date, sensitivity_subclass FROM conditions WHERE patient_id = :pid {sens_filter}"), 
            {"pid": patient_uuid}
        ).fetchall()
        timeline['conditions'] = [
            {"id": str(r[0]), "description": r[1], "status": r[2], "onset_date": r[3], "sensitivity": r[4]} 
            for r in conds
        ]
        
        # Fetch Encounters (Visits)
        encs = db.execute(
            text("SELECT id, encounter_type, reason, started_at FROM encounters WHERE patient_id = :pid"), 
            {"pid": patient_uuid}
        ).fetchall()
        timeline['encounters'] = [
            {"id": str(r[0]), "type": r[1], "reason": r[2], "date": r[3]} 
            for r in encs
        ]
        
        # Fetch Vitals
        vts = db.execute(
            text("""
                SELECT id, body_temperature_celsius, blood_pressure_systolic, 
                       blood_pressure_diastolic, heart_rate_bpm, respiratory_rate_bpm, spo2_percent, recorded_at 
                FROM vitals WHERE patient_id = :pid
                ORDER BY recorded_at DESC
            """), 
            {"pid": patient_uuid}
        ).fetchall()
        timeline['vitals'] = [
            {
                "id": str(r[0]), 
                "temperature": r[1], 
                "bp_systolic": r[2], 
                "bp_diastolic": r[3],
                "heart_rate": r[4],
                "resp_rate": r[5],
                "spo2": r[6],
                "recorded_at": r[7]
            } 
            for r in vts
        ]

    # Return the aggregated, filtered data
    return {
        "abha_id": abha_id,
        "accessed_by_role": dept or "PATIENT",
        "data": timeline
    }
