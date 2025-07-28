# Performance Transfer Studio - AI Character Animation Platform

A full-stack application that transfers performances between characters using Runway's Act Two API. Upload a character video and a reference performance, and watch the character mimic the reference's movements and expressions.

## Architecture

```
Frontend (React + TypeScript)
├── Video Upload Component
├── Prompt Input Interface  
├── Processing Status Display
└── Results Viewer

Backend (FastAPI + Python)
├── File Upload API
├── Runway Act Two Integration
├── Job Queue Management
└── WebSocket Status Updates

Infrastructure
├── PostgreSQL (job tracking)
├── Redis + Celery (async processing)
└── AWS S3 (video storage)
```

## Workflow

1. **Upload Character**: User uploads video of the character to animate
2. **Upload Reference**: User uploads video of the performance to transfer
3. **Process**: Backend calls Runway Act Two API to transfer performance
4. **Monitor**: Real-time status updates via polling
5. **Download**: User receives character performing the reference movements

## Runway API Integration

Using Runway's Act Two model for character performance control:
- Endpoint: `/v1/character_performance`
- Supports: Color changes, object insertion, style transfers
- Input formats: MP4, WebM, MOV (max 16MB)
- Output ratios: 1280:720, 1584:672, 1104:832, 720:1280, 832:1104, 960:960

## Project Structure

```
sports-editor/
├── frontend/          # React TypeScript app
├── backend/           # FastAPI Python server
├── docker-compose.yml # Local development setup
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- Runway API key

### Environment Variables
```bash
# Backend
RUNWAY_API_KEY=your_runway_api_key
DATABASE_URL=postgresql://user:pass@localhost/sportseditor
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your_bucket_name

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Development Setup
```bash
# Start infrastructure
docker-compose up -d postgres redis

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm start
```

## API Endpoints

### Upload Videos
```http
POST /api/upload
Content-Type: multipart/form-data

{
  "character_file": <character_video>,
  "reference_file": <reference_performance>
}
```

### Get Job Status
```http
GET /api/jobs/{job_id}/status
```

### WebSocket Updates
```
ws://localhost:8000/ws/jobs/{job_id}
```

## Next Steps

1. Set up basic project structure
2. Implement video upload interface
3. Build Runway API integration
4. Add async job processing
5. Create real-time status updates 