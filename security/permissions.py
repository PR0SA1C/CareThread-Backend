# security/permissions.py

# This is a dynamic access map. 
# In the future, if you add a new database collection or department, 
# you just add a new 'resource_group' here. No deep code changes required!

RESOURCE_PERMISSIONS = {
    # -----------------
    # Administrative Data
    # -----------------
    "read_admin_basic": ["ORG_RECEPTION", "ORG_BILLING", "ORG_DOCTOR", "ORG_ER"],
    "read_insurance": ["ORG_BILLING", "ORG_RECEPTION"],

    # -----------------
    # Clinical Data
    # -----------------
    # Needs standard active consent
    "read_clinical_standard": ["ORG_DOCTOR", "ORG_PHARMACY", "ORG_NURSE"],
    
    # Needs specific department routing
    "read_pathology": ["ORG_PATHOLOGY", "ORG_DOCTOR"],
    "read_radiology": ["ORG_RADIOLOGY", "ORG_DOCTOR"],
    
    # -----------------
    # Highly Restricted Data
    # -----------------
    "read_clinical_restricted": ["ORG_PSYCHIATRIST"],
    
    # -----------------
    # Emergency Overrides
    # -----------------
    # Break-glass access (Audited)
    "read_emergency_critical": ["ORG_ER", "ORG_DOCTOR"]
}

def get_allowed_departments(resource_group: str) -> list[str]:
    """Returns the list of departments allowed to access a specific resource group."""
    return RESOURCE_PERMISSIONS.get(resource_group, [])
