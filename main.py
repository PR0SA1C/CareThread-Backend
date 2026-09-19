from fastapi import FastAPI
from routers.auth_router import router as auth_router
from routers.clinical_router import router as clinical_router
from routers.patient_router import router as patient_router

app = FastAPI(
    title="CareThread ABDM Backend", 
    version="1.2.0",
    description="Added patient demographics, radiology document fetch, vitals, and fixed RBAC strictness."
)

app.include_router(auth_router)
app.include_router(clinical_router)
app.include_router(patient_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CareThread Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
