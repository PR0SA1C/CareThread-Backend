from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from schemas.auth import UserContext
from security.jwt_handler import decode_access_token
from security.permissions import get_allowed_departments

# This creates a simple text box in Swagger UI to paste the token
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserContext:
    if token and token.lower().startswith("bearer "):
        token = token[7:]
        
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserContext(**payload)

def require_resource_access(resource_group: str):
    """
    A dependency generator that checks if the current logged-in Organization Staff
    has the correct department role to access the requested resource group.
    Patients can bypass this if they are hitting their own data (handled in the route).
    """
    def access_checker(current_user: UserContext = Depends(get_current_user)):
        # If it's a PATIENT, they handle their own consent. We let them through here, 
        # but the specific route MUST verify they are accessing their OWN abha_id.
        if current_user.user_type == "PATIENT":
            return current_user
            
        allowed_departments = get_allowed_departments(resource_group)
        if current_user.department not in allowed_departments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Department '{current_user.department}' cannot access {resource_group}."
            )
        return current_user
        
    return access_checker
