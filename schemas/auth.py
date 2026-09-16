from pydantic import BaseModel
from typing import Optional

# -----------------
# Login Requests
# -----------------
class PatientLogin(BaseModel):
    abha_id: str
    password: Optional[str] = None # Used for mock/local login currently
    otp: Optional[str] = None      # Will be used for ABDM integration later

class OrgLogin(BaseModel):
    abdm_hpr_id: str  # Healthcare Professional Registry ID or Employee ID
    password: str
    facility_id: str

# -----------------
# Token Responses
# -----------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -----------------
# JWT Payload Context
# -----------------
class UserContext(BaseModel):
    user_id: str
    user_type: str  # 'PATIENT' or 'ORG_STAFF'
    department: Optional[str] = None  # e.g., 'RECEPTION', 'DOCTOR', 'ER', 'RADIOLOGY'
    facility_id: Optional[str] = None 
