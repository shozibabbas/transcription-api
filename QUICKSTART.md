# Quick Start Guide

Get the Transcription API running in 5 minutes.

## 1. Activate Virtual Environment

```bash
cd /Users/shozibsayyed/Projects/volgatest
source venv/bin/activate
```

## 2. Start the API Server

```bash
python main.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 3. Test the API

### Option A: Interactive API Docs (Recommended)

Open your browser to: **http://localhost:8000/docs**

- Click "Try it out" on any endpoint
- Upload an audio file to `/api/transcribe`
- View response

### Option B: Command Line with curl

**Health check:**
```bash
curl -X GET http://localhost:8000/api/health
```

**Transcribe audio:**
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -F "file=@scene_001.wav"
```

**Upload only (no transcription):**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@scene_001.wav"
```

### Option C: Python

```python
import requests

# Transcribe
with open("scene_001.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/transcribe",
        files={"file": f}
    )
    result = response.json()
    print(f"Transcript: {result['transcript']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Segments: {len(result['segments'])} segments")
```

## 4. Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_api.py

# With real audio (if available)
pytest tests/test_api.py::TestRealAudio -v

# With coverage
pytest --cov=app
```

## 5. Configuration

Copy and modify environment:

```bash
cp .env.example .env
nano .env
```

Restart the server to apply changes:

```bash
# Stop current server (Ctrl+C)
# Then restart
python main.py
```

## Supported Audio Formats

- WAV (`.wav`)
- MP3 (`.mp3`)
- FLAC (`.flac`)
- OGG (`.ogg`)
- WebM (`.webm`)
- MP4 (`.mp4`)
- M4A (`.m4a`)

## Common Issues

**"Model not found"** - First run downloads model (1-2 minutes)

**"GPU not detected"** - Set `DEVICE=cpu` in `.env`

**"Out of memory"** - Use smaller model: `MODEL_SIZE=tiny` or `base`

See full [README.md](README.md) for detailed documentation.
