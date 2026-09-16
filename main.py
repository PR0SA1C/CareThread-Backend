from fastapi import FastAPI

app = FastAPI(title="CareThread ABDM Backend", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the CareThread Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
