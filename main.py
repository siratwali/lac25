"""
LinkedIn Auto Connect Pro - FastAPI Backend with CSV Upload
Your linkedin_bot.py + File Upload Support
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import EmailStr
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import secrets
from threading import Thread
import logging

# Import your backend
import linkedin_bot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# ==================== PATHS ====================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)
CLIENTS_FILE = Path("clients_registry.json")

# ==================== HELPER FUNCTIONS ====================

def load_clients():
    """Load clients from JSON"""
    if CLIENTS_FILE.exists():
        with open(CLIENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_clients(clients):
    """Save clients to JSON"""
    with open(CLIENTS_FILE, 'w') as f:
        json.dump(clients, f, indent=2)

def generate_token():
    """Generate unique client token"""
    return secrets.token_urlsafe(32)

# ==================== API ENDPOINTS ====================

@app.get("/")
def health():
    """Health check"""
    return {
        "status": "ok",
        "service": "LinkedIn Auto Connect Pro",
        "version": "2.0.0"
    }

@app.post("/api/process-csv")
async def process_csv(
    email: str = Form(...),
    password: str = Form(...),
    daily_limit: int = Form(50),
    file: UploadFile = File(...)
):
    """
    Main endpoint: Client uploads CSV + credentials + daily limit
    
    Args:
        email: LinkedIn email
        password: LinkedIn password
        daily_limit: Daily connection limit (0-150)
        file: CSV file with LinkedIn URLs in first column
    
    Returns:
        Success message with processing status
    """
    try:
        # Validate inputs
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        if daily_limit < 0 or daily_limit > 150:
            raise HTTPException(status_code=400, detail="Daily limit must be between 0 and 150")
        
        if not file:
            raise HTTPException(status_code=400, detail="CSV file required")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be CSV format")
        
        # Read uploaded CSV
        contents = await file.read()
        csv_path = UPLOADS_DIR / f"{secrets.token_hex(8)}.csv"
        
        with open(csv_path, 'wb') as f:
            f.write(contents)
        
        # Parse CSV to validate it has LinkedIn URLs
        try:
            df = pd.read_csv(csv_path)
            urls = df.iloc[:, 0].dropna().tolist()  # First column
            
            if len(urls) == 0:
                raise HTTPException(status_code=400, detail="CSV has no URLs in first column")
            
            logger.info(f"CSV loaded with {len(urls)} URLs")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
        
        # Update linkedin_bot configuration
        linkedin_bot.EMAIL = email
        linkedin_bot.PASSWORD = password
        linkedin_bot.DAILY_LIMIT = daily_limit
        linkedin_bot.CSV_FILE = str(csv_path)
        
        # Run in background thread (non-blocking)
        thread = Thread(target=linkedin_bot.main, daemon=True)
        thread.start()
        
        logger.info(f"Started processing {len(urls)} URLs for {email}")
        
        return {
            "status": "processing",
            "message": f"✅ Processing {len(urls)} LinkedIn profiles",
            "urls_count": len(urls),
            "daily_limit": daily_limit,
            "email": email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_csv: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/client/link")
def create_client_link(company_name: str = "Client"):
    """
    Create a shareable client link (for admin)
    Optional: if you want to track clients
    """
    token = generate_token()
    clients = load_clients()
    
    clients[token] = {
        "company": company_name,
        "created": datetime.now().isoformat(),
        "status": "active"
    }
    save_clients(clients)
    
    return {
        "token": token,
        "company": company_name,
        "link": f"http://localhost:8000/client/{token}",
        "message": f"Share this link: http://localhost:8000/client/{token}"
    }

@app.get("/client/{token}")
def client_page(token: str):
    """
    Serve client form (HTML page)
    Token can be used for tracking if needed
    """
    clients = load_clients()
    if token not in clients and token != "default":
        # Allow access anyway, but log it
        logger.warning(f"Unknown token: {token}")
    
    return FileResponse("public/client.html")

@app.get("/client")
def client_page_default():
    """Default client page (no token required)"""
    return FileResponse("public/client.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)