"""
LinkedIn Auto Connect Pro - FastAPI Backend with CSV Upload + Frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from threading import Thread
import pandas as pd
import secrets
import logging
import linkedin_bot  # Your existing Selenium bot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== DIRECTORIES ====================
BASE_DIR = Path(__file__).parent
PUBLIC_DIR = BASE_DIR / "public"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# ==================== APP INIT ====================
app = FastAPI(
    title="LinkedIn Auto Connect Pro",
    description="Share this link with clients",
    version="2.0.0"
)

# CORS - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENDPOINTS ====================

# 1️⃣ Serve frontend HTML
@app.get("/", response_class=FileResponse)
def serve_frontend():
    """
    Serve client.html frontend
    """
    html_file = PUBLIC_DIR / "client.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(html_file)

# 2️⃣ Health check
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LinkedIn Auto Connect Pro",
        "version": "2.0.0"
    }

# 3️⃣ Process CSV & run LinkedIn bot
@app.post("/api/process-csv")
async def process_csv(
    email: str = Form(...),
    password: str = Form(...),
    daily_limit: int = Form(50),
    file: UploadFile = File(...)
):
    """
    Receive CSV, email, password, daily limit and start LinkedIn bot
    """
    try:
        # Validate inputs
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        if daily_limit < 0 or daily_limit > 150:
            raise HTTPException(status_code=400, detail="Daily limit must be between 0-150")
        if not file or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Valid CSV file required")

        # Save CSV temporarily
        file_path = UPLOADS_DIR / f"{secrets.token_hex(8)}.csv"
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Parse CSV to validate first column has URLs
        try:
            df = pd.read_csv(file_path)
            urls = df.iloc[:, 0].dropna().tolist()
            if len(urls) == 0:
                raise HTTPException(status_code=400, detail="CSV first column has no URLs")
            logger.info(f"CSV loaded: {len(urls)} URLs")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")

        # Configure linkedin_bot
        linkedin_bot.EMAIL = email
        linkedin_bot.PASSWORD = password
        linkedin_bot.DAILY_LIMIT = daily_limit
        linkedin_bot.CSV_FILE = str(file_path)

        # Run bot in background thread
        thread = Thread(target=linkedin_bot.main, daemon=True)
        thread.start()

        logger.info(f"Started LinkedIn bot for {email} with {len(urls)} URLs")

        return JSONResponse({
            "status": "processing",
            "message": f"✅ Processing {len(urls)} LinkedIn profiles",
            "urls_count": len(urls),
            "daily_limit": daily_limit,
            "email": email
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_csv: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# 4️⃣ Serve frontend with token link (optional)
@app.get("/client/{token}")
def client_page(token: str):
    html_file = PUBLIC_DIR / "client.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    logger.info(f"Client page accessed with token: {token}")
    return FileResponse(html_file)

@app.get("/client")
def client_page_default():
    html_file = PUBLIC_DIR / "client.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(html_file)

# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
