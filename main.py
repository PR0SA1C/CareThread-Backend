from fastapi import FastAPI
from routers.auth_router import router as auth_router
from routers.clinical_router import router as clinical_router

app = FastAPI(
    title="CareThread ABDM Backend", 
    version="1.1.0",
    description="Added clinical data retrieval with strict RBAC tiering."
)

app.include_router(auth_router)
app.include_router(clinical_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CareThread Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
