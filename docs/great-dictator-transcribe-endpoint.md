# Add /api/transcribe endpoint to great-dictator

## Goal

Add a stateless transcription endpoint that accepts audio and returns text. This allows other services (e.g., wake-word detection in Much) to share the Faster-Whisper instance running on polwarth.

## Endpoint specification

```
POST /api/transcribe
Content-Type: audio/wav
Body: raw audio bytes (WAV format, 16kHz mono preferred)

Response: 
{
  "text": "transcribed text here",
  "language": "en",
  "duration": 3.2
}

Errors:
- 400: Invalid audio format
- 503: Transcription service unavailable
```

## Implementation steps

### 1. Add a threading lock for concurrent access

Faster-Whisper should not process multiple transcriptions simultaneously on the same model instance. Add a lock to serialise requests.

```python
import threading

# At module level or in app state
transcribe_lock = threading.Lock()
```

### 2. Create the endpoint

```python
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import io
import time

router = APIRouter()

@router.post("/api/transcribe")
async def transcribe_audio(request: Request):
    """
    Stateless transcription endpoint.
    Accepts WAV audio, returns transcribed text.
    """
    content_type = request.headers.get("content-type", "")
    if "audio/wav" not in content_type and "audio/wave" not in content_type:
        raise HTTPException(400, "Content-Type must be audio/wav")
    
    audio_bytes = await request.body()
    if len(audio_bytes) < 44:  # WAV header minimum
        raise HTTPException(400, "Audio too short or invalid")
    
    start = time.time()
    
    with transcribe_lock:
        # Use existing Faster-Whisper model instance
        segments, info = model.transcribe(
            io.BytesIO(audio_bytes),
            language="en",  # or None for auto-detect
            vad_filter=True
        )
        text = " ".join(segment.text for segment in segments).strip()
    
    return JSONResponse({
        "text": text,
        "language": info.language,
        "duration": round(time.time() - start, 2)
    })
```

### 3. Register the router

In your main FastAPI app setup, include the new router.

### 4. Access control decision

Options:
- **No auth**: Internal network only, don't expose via Cloudflare tunnel
- **Cloudflare Access**: Same as existing app, but the endpoint is available to authenticated users
- **API key**: Simple shared secret in header for service-to-service calls

Recommendation: No auth for now, rely on network isolation. The endpoint is stateless and low-risk.

### 5. Test

```bash
# From trend or another machine on the network
curl -X POST http://polwarth:8000/api/transcribe \
  -H "Content-Type: audio/wav" \
  --data-binary @test.wav
```

## Notes

- The lock means requests queue up - acceptable for low concurrency
- Consider adding a timeout if queue gets too deep
- WAV at 16kHz mono is optimal; Faster-Whisper handles resampling but it adds overhead
- The existing model instance is reused - no additional GPU memory needed
