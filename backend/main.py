from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import settings
from runway_client import RunwayClient

# Create FastAPI app
app = FastAPI(
    title="Sports Editor API",
    description="AI-powered video animation using Runway Act Two",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(settings.JOBS_DIRECTORY, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="uploads")
app.mount("/jobs", StaticFiles(directory=settings.JOBS_DIRECTORY), name="jobs")

# Add a simple endpoint to serve videos with CORS headers for external access
@app.get("/serve/{filename}")
async def serve_video(filename: str):
    from fastapi.responses import FileResponse
    file_path = Path(settings.UPLOAD_DIRECTORY) / filename
    if file_path.exists():
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*",
            }
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Initialize Runway client
runway_client = RunwayClient()

@app.get("/")
async def root():
    return {"message": "Sports Editor API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/validate-videos")
async def validate_videos(
    character_file: UploadFile = File(...),
    reference_file: UploadFile = File(...)
):
    """Quick validation to help users understand video requirements"""
    
    # Basic file validation
    issues = []
    
    # Check character file
    if not character_file.content_type or not character_file.content_type.startswith('video/'):
        issues.append("Character file must be a video")
    elif character_file.size and character_file.size > settings.MAX_FILE_SIZE:
        issues.append("Character file too large")
    
    # Check reference file  
    if not reference_file.content_type or not reference_file.content_type.startswith('video/'):
        issues.append("Reference file must be a video")
    elif reference_file.size and reference_file.size > settings.MAX_FILE_SIZE:
        issues.append("Reference file too large")
    
    if issues:
        return {"valid": False, "issues": issues}
    
    # Return guidance for Act Two requirements
    return {
        "valid": True,
        "guidance": {
            "requirements": [
                "Both videos must show clear, visible faces",
                "Front-facing faces work best",
                "Good lighting is essential", 
                "Avoid motion blur or fast movements",
                "Close-up or medium shots are preferred",
                "Videos should be at least 1-2 seconds long"
            ],
            "tips": [
                "Test with simple talking head videos first",
                "Ensure faces are the main subject",
                "Avoid profile shots or partially obscured faces"
            ]
        }
    }

@app.post("/api/upload")
async def upload_video(
    character_file: UploadFile = File(...),
    reference_file: UploadFile = File(...)
):
    # Validate character file
    if not character_file.content_type or not character_file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Character file must be a video")
    
    if character_file.size and character_file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Character file too large")
    
    # Validate reference file
    if not reference_file.content_type or not reference_file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Reference file must be a video")
    
    if reference_file.size and reference_file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Reference file too large")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save character file
    char_extension = Path(character_file.filename).suffix
    character_filename = f"{job_id}_character{char_extension}"
    character_path = Path(settings.UPLOAD_DIRECTORY) / character_filename
    
    with open(character_path, "wb") as buffer:
        content = await character_file.read()
        buffer.write(content)
    
    # Save reference file
    ref_extension = Path(reference_file.filename).suffix
    reference_filename = f"{job_id}_reference{ref_extension}"
    reference_path = Path(settings.UPLOAD_DIRECTORY) / reference_filename
    
    with open(reference_path, "wb") as buffer:
        content = await reference_file.read()
        buffer.write(content)
    
    # Create job record
    job_data = {
        "id": job_id,
        "status": "processing",
        "character_file": character_filename,
        "reference_file": reference_filename,
        "output_file": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # Save job data
    job_file = Path(settings.JOBS_DIRECTORY) / f"{job_id}.json"
    with open(job_file, "w") as f:
        json.dump(job_data, f)
    
    # Start processing in background
    asyncio.create_task(process_video(job_id, str(character_path), str(reference_path)))
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job_file = Path(settings.JOBS_DIRECTORY) / f"{job_id}.json"
    
    if not job_file.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    with open(job_file, "r") as f:
        job_data = json.load(f)
    
    return job_data

async def process_video(job_id: str, character_path: str, reference_path: str):
    """Process video with Runway Act Two API"""
    job_file = Path(settings.JOBS_DIRECTORY) / f"{job_id}.json"
    
    try:
        # Load job data
        with open(job_file, "r") as f:
            job_data = json.load(f)
        
        # Call Runway API
        result = await runway_client.process_video(character_path, reference_path)
        
        if result["success"]:
            # Save output file
            output_filename = f"{job_id}_output.mp4"
            output_path = Path(settings.JOBS_DIRECTORY) / output_filename
            
            # Download result from Runway
            await runway_client.download_video(result["video_url"], str(output_path))
            
            # Update job status
            job_data.update({
                "status": "completed",
                "output_file": output_filename,
                "completed_at": datetime.now().isoformat()
            })
        else:
            job_data.update({
                "status": "failed",
                "error": result["error"],
                "completed_at": datetime.now().isoformat()
            })
    
    except Exception as e:
        job_data.update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
    
    # Save updated job data
    with open(job_file, "w") as f:
        json.dump(job_data, f)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 