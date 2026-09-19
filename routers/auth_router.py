from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from schemas.auth import PatientLogin, OrgLogin, TokenResponse
from security.jwt_handler import create_access_token
from database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------------------------------------
# PATIENT LOGIN ENDPOINT
# ---------------------------------------------------------
class OTPRequest(BaseModel):
    abha_id: str

@router.post("/patient/send-otp")
def request_patient_otp(request: OTPRequest):
    """
    FUTURE ABDM INTEGRATION: 
    When a patient submits their ABHA ID, this endpoint will call the ABDM Gateway 
    to dispatch an OTP to their linked mobile number.
    """
    return {"status": "success", "message": f"OTP successfully dispatched to registered mobile for {request.abha_id}"}

@router.post("/patient/login", response_model=TokenResponse)
def login_patient(login_data: PatientLogin, db: Session = Depends(get_db)):
    """
    STRICTLY FOR PATIENTS:
    Currently accepts a mock password for local testing. 
    Later, it will verify the `otp` field against the ABDM gateway.
    """
    # [Future ABDM Verification Logic]
    # if login_data.otp:
    #     verify_otp_with_abdm_gateway(login_data.abha_id, login_data.otp)
    
    if login_data.abha_id != "mock-abha-id":
        pass 
        
    access_token = create_access_token(
        data={
            "user_id": login_data.abha_id,
            "user_type": "PATIENT",
            "department": None,
            "facility_id": None
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------
# ORGANIZATION LOGIN ENDPOINT
# ---------------------------------------------------------
@router.post("/org/login", response_model=TokenResponse)
def login_organization(login_data: OrgLogin, db: Session = Depends(get_db)):
    """
    STRICTLY FOR HOSPITAL STAFF: Rejects any patient credentials.
    Requires an HPR ID (Healthcare Professional Registry) or Employee ID.
    """
    # [Mock Verification Logic]
    # staff = db.query(Practitioner).filter(Practitioner.abdm_hpr_id == login_data.abdm_hpr_id).first()
    # if not staff: raise 401
    
    # For testing on Swagger UI: Whatever role you type in the 'password' field is the role you get!
    # (e.g., type "ORG_PHARMACIST" in the password field to test pharmacist access)
    mock_department = login_data.password if login_data.password.startswith("ORG_") else "ORG_DOCTOR"
    
    access_token = create_access_token(
        data={
            "user_id": login_data.abdm_hpr_id,
            "user_type": "ORG_STAFF",
            "department": mock_department,
            "facility_id": login_data.facility_id
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}
