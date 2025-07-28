# 🚀 How to Start Sports Editor

## Method 1: Two Terminal Windows (Recommended)

### Terminal 1 - Backend:
```bash
cd backend
python main.py
```
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm start
```
You should see:
```
webpack compiled successfully!
Local:            http://localhost:3000
```

## Method 2: Background Processes

### Start Backend in Background:
```bash
cd backend
python main.py &
```

### Start Frontend in Background:
```bash
cd frontend
npm start &
```

## ✅ Verify Everything is Running

### Test Backend:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Test Frontend:
Open your browser to: **http://localhost:3000**

## 🛑 How to Stop

### Stop Background Processes:
```bash
# Kill all node processes (frontend)
pkill -f "react-scripts"

# Kill python processes (backend)  
pkill -f "python main.py"
```

### Or use Ctrl+C in each terminal window

## 🔧 Don't Forget!

Add your Runway API key to `backend/.env`:
```
RUNWAY_API_KEY=your_actual_runway_api_key_here
``` 