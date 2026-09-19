from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from security.dependencies import get_current_user
from schemas.auth import UserContext

router = APIRouter(prefix="/api/v1/patients", tags=["Patient Demographics"])

@router.get("/{abha_id}/profile")
def get_patient_profile(
    abha_id: str, 
    db: Session = Depends(get_db), 
    current_user: UserContext = Depends(get_current_user)
):
    """
    Fetches basic demographic and administrative data for a patient.
    Accessible by ALL Organization Staff (including Reception & Billing).
    Strictly NO clinical data is returned here.
    """
    
    # Anyone logged in can view basic demographics (Tier 1 to Tier 4)
    # The database query explicitly only selects non-sensitive columns
    patient_row = db.execute(
        text("""
            SELECT full_name, gender, date_of_birth, phone, address, blood_group
            FROM patients 
            WHERE abha_id = :abha
        """), 
        {"abha": abha_id}
    ).first()
    
    if not patient_row:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    return {
        "abha_id": abha_id,
        "accessed_by_role": current_user.department or "PATIENT",
        "demographics": {
            "full_name": patient_row[0],
            "gender": patient_row[1],
            "date_of_birth": patient_row[2],
            "phone": patient_row[3],
            "address": patient_row[4],
            "blood_group": patient_row[5]
        }
    }
