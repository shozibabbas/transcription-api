# 🚀 Transcription API - START HERE

Welcome! This is a production-grade audio transcription API built with FastAPI.

## ⚡ Quick Start (5 minutes)

### 1️⃣ Activate Virtual Environment
```bash
cd /Users/shozibsayyed/Projects/volgatest
source venv/bin/activate
```

### 2️⃣ Start the Server
```bash
python main.py
```

You'll see: `Uvicorn running on http://0.0.0.0:8000`

### 3️⃣ Try the API

**Browser:** Open http://localhost:8000/docs
- Click endpoints
- Click "Try it out"
- Upload an audio file
- See results!

**Or command line:**
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -F "file=@scene_001.wav"
```

## 📚 Documentation Map

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [README.md](README.md) | Complete API documentation |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Architecture & deployment |
| [VERIFICATION.md](VERIFICATION.md) | Test results & verification |

## 🧪 Running Tests

```bash
# All tests
pytest

# Verbose with output
pytest -v

# With coverage
pytest --cov=app

# Just the real audio test
pytest tests/test_api.py::TestRealAudio -v
```

✅ **Result**: 23 tests passing, 2 integration tests (skipped)

## 🎯 What This API Does

Converts audio files to text with exact timing for each phrase.

**Supported formats:** WAV, MP3, FLAC, OGG, WebM, MP4, M4A

**Example response:**
```json
{
  "transcript": "In a quiet corridor of a Sydney hospital...",
  "segments": [
    {"start": 0.0, "end": 3.42, "text": "In a quiet corridor"},
    {"start": 3.42, "end": 6.81, "text": "of a Sydney hospital"}
  ]
}
```

## 📋 API Endpoints

| Method | Endpoint | What it does |
|--------|----------|------------|
| GET | `/api/health` | Check if server is running |
| POST | `/api/transcribe` | Convert audio file to text |
| POST | `/api/upload` | Upload and validate audio file |

## ⚙️ Configuration

All settings in `.env.example` file:

```bash
MODEL_SIZE=base         # tiny, base, small, medium, large
DEVICE=cpu              # cpu or cuda (GPU)
COMPUTE_TYPE=int8       # int8, float16, float32
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
```

## 🗂️ Project Structure

```
app/                 # Main application
├── config.py       # Settings
├── schemas.py      # Data models
├── api/routes.py   # Endpoints
└── services/       # Business logic
    ├── whisper_service.py   # Transcription
    └── file_service.py      # File handling

tests/              # Test suite (23 tests)
├── test_api.py
└── test_services.py

main.py             # Start the server
requirements.txt    # Python packages
.env.example        # Configuration template
README.md           # Full documentation
```

## 🔧 Common Tasks

### Change Model Size
```bash
MODEL_SIZE=small python main.py
```

### Use GPU Instead of CPU
```bash
DEVICE=cuda COMPUTE_TYPE=float16 python main.py
```

### Check Health
```bash
curl http://localhost:8000/api/health
```

### See API Documentation
```
http://localhost:8000/docs
```

## 🚨 Troubleshooting

**"Model not found"** → First run takes 1-2 minutes to download

**"Out of memory"** → Use smaller model: `MODEL_SIZE=tiny`

**"GPU not detected"** → Use CPU: `DEVICE=cpu`

**Tests failing** → Run: `pytest -v` to see details

## 📦 What's Installed

All dependencies in `requirements.txt`:
- **FastAPI** - Web framework
- **Uvicorn** - Server
- **Faster-Whisper** - Transcription model
- **Pydantic** - Data validation
- **Pytest** - Testing

Run `pip install -r requirements.txt` to reinstall if needed.

## ✨ Key Features

- ✅ Convert audio to text with timestamps
- ✅ Support 7 audio formats
- ✅ Async for fast, concurrent requests
- ✅ Full error handling and validation
- ✅ Interactive API documentation
- ✅ Production-ready code
- ✅ 23 automated tests
- ✅ Configurable via environment
- ✅ GPU acceleration support
- ✅ CORS enabled for frontends

## 🚀 Production Deployment

For production use:

```bash
# Multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With GPU
DEVICE=cuda COMPUTE_TYPE=float16 \
  uvicorn main:app --workers 4

# With logging
LOG_LEVEL=WARNING uvicorn main:app --workers 4
```

## 📞 Next Steps

1. ✅ Run the server: `python main.py`
2. ✅ Visit: http://localhost:8000/docs
3. ✅ Upload an audio file
4. ✅ See the transcript!

For detailed docs, read [README.md](README.md)

---

**Status**: ✅ Production Ready | **Tests**: 23 passing | **Docs**: Complete
