from fastapi import FastAPI
from routers.auth_router import router as auth_router

app = FastAPI(title="CareThread ABDM Backend", version="1.0.0")

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the CareThread Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
