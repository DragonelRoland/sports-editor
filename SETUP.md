# 🚀 Sports Editor - Quick Setup

## ✅ Current Status
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ All dependencies installed

## 🔧 Next Steps

### 1. Add Your Runway API Key
```bash
cd backend
nano .env  # or open in your preferred editor
```

Add your Runway API key:
```
RUNWAY_API_KEY=your_actual_runway_api_key_here
```

### 2. Test the Application
1. Open http://localhost:3000 in your browser
2. You should see the Sports Editor interface with:
   - Beautiful gradient background
   - Video upload area
   - Prompt input field
   - "Transform Video" button

### 3. How to Use
1. **Upload a video** (MP4, WebM, MOV - max 16MB)
2. **Enter a prompt** like:
   - "change colors to neon, add sparkle effects"
   - "make it look like a cartoon"
   - "add lightning effects"
3. **Click "Transform Video"**
4. **Wait for processing** (may take 2-5 minutes)
5. **Download your transformed video**

## 🔍 Troubleshooting

### Backend Issues
```bash
cd backend
python main.py
# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

### Frontend Issues
```bash
cd frontend
npm start
# Should show: "webpack compiled successfully"
```

### Test API Connection
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## 🎬 Ready to Transform Videos!

Your Sports Editor is now ready. Just add your Runway API key and start creating amazing AI-powered video animations! 