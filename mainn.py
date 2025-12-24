from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="LinkedIn Auto Connect Pro",
    version="2.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/", response_class=JSONResponse)
def root():
    return {
        "status": "ok",
        "service": "LinkedIn Auto Connect Pro",
        "version": "2.0.0"
    }

@app.get("/client", response_class=HTMLResponse)
def serve_client():
    file_path = os.path.join(BASE_DIR, "client.html")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="client.html not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health():
    return {"status": "running"}
