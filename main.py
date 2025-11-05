import os
from typing import List
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


@app.post("/api/upload")
async def upload_video(
    video: UploadFile = File(...),
    caption: str = Form("") ,
    platforms: str = Form("[]"),
):
    """
    Accept a single video file and metadata, then simulate publishing to multiple platforms.
    In a production build this would:
      - Use OAuth tokens per platform
      - Upload to each platform's API with platform-specific parameters
      - Track job status in the database
    Here we validate the payload and return a mocked success response so the UI can function.
    """
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Please upload a valid video file")

    # Basic size guard (if available)
    size = video.size if hasattr(video, "size") else None

    # Parse platforms array if sent as JSON-encoded string
    try:
        import json
        platform_list: List[str] = json.loads(platforms) if isinstance(platforms, str) else platforms
        if not isinstance(platform_list, list):
            platform_list = []
    except Exception:
        platform_list = []

    if not platform_list:
        platform_list = ["youtube", "tiktok", "instagram"]

    # Read a tiny chunk to ensure stream is accessible
    await video.read(1024)

    mock_ids = {p: f"job_{p}_12345" for p in platform_list}

    return JSONResponse(
        {
            "message": "Video queued for publishing to selected platforms.",
            "filename": video.filename,
            "size": size,
            "caption": caption,
            "platforms": platform_list,
            "jobs": mock_ids,
            "note": "This is a demo endpoint. Replace with real platform integrations."
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
