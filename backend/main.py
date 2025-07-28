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

# Initialize Runway client
runway_client = RunwayClient()

@app.get("/")
async def root():
    return {"message": "Sports Editor API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/upload")
async def upload_video(
    file: UploadFile = File(...),
    prompt: str = Form(...)
):
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_extension = Path(file.filename).suffix
    input_filename = f"{job_id}_input{file_extension}"
    input_path = Path(settings.UPLOAD_DIRECTORY) / input_filename
    
    with open(input_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create job record
    job_data = {
        "id": job_id,
        "status": "processing",
        "prompt": prompt,
        "input_file": input_filename,
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
    asyncio.create_task(process_video(job_id, str(input_path), prompt))
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    job_file = Path(settings.JOBS_DIRECTORY) / f"{job_id}.json"
    
    if not job_file.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    with open(job_file, "r") as f:
        job_data = json.load(f)
    
    return job_data

async def process_video(job_id: str, input_path: str, prompt: str):
    """Process video with Runway Act Two API"""
    job_file = Path(settings.JOBS_DIRECTORY) / f"{job_id}.json"
    
    try:
        # Load job data
        with open(job_file, "r") as f:
            job_data = json.load(f)
        
        # Call Runway API
        result = await runway_client.process_video(input_path, prompt)
        
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