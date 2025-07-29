# SportsVoice AI - Sports Interview Generator

A full-stack application that transforms athletes into professional sports interviewers using Runway's Act Two API. Upload your favorite athlete video and a professional interview reference, and create custom sports content with AI-powered performance transfer.

## Workflow

1. **Upload Athlete**: User uploads video of their favorite sports player
2. **Upload Interview Style**: User uploads professional interview/presenter reference
3. **AI Processing**: Backend calls Runway Act Two API to transfer interview style to athlete
4. **Monitor**: Real-time status updates via polling
5. **Download**: User receives custom sports interview content

## Video Requirements & Limitations

### ✅ **What Works Best**
- **Resolution**: 720p (1280x720) or higher recommended
- **Duration**: 2-10 seconds optimal
- **Face Requirements**: 
  - Clear, front-facing faces
  - Good lighting (not dark or shadowy)
  - Faces should fill a significant portion of the frame
  - Minimal motion blur
- **Format**: MP4 with H.264 codec
- **Content**: Talking head videos, interviews, press conferences, award ceremonies

### ❌ **Common Issues**
- **Low Resolution**: Videos below 720p often fail face detection
- **Poor Lighting**: Dark or poorly lit faces won't be detected
- **Fast Motion**: Sports action shots with motion blur
- **Wide Shots**: Faces too small in the frame
- **Profile Views**: Side-angle faces (need front-facing)
- **Obstructed Faces**: Masks, sunglasses, or partial coverage

### 🎯 **Best Practices**
- **Test with phone recordings**: Modern phone cameras work great
- **Use interview/press conference footage**: These typically have ideal face positioning
- **Avoid sports action clips**: Use post-game interviews instead
- **Debug tip**: Upload the same video for both character and reference to test if it has a detectable face

### 🔧 **Troubleshooting**
If you get "No face found" errors:
1. Check video resolution (should be 720p+)
2. Ensure faces are clearly visible and well-lit
3. Try the same video for both inputs to isolate which video is problematic
4. Record a simple selfie video as a test case

## Runway API Integration

Using Runway's Act Two model for character performance transfer:
- Model: `act_two` via `character_performance` endpoint
- Transfers facial expressions and movements between videos
- Input formats: MP4, WebM, MOV (max 16MB)
- Output ratio: 1280:720 (HD sports broadcast format)
- Face detection required in both character and reference videos

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