# Progress Report: API Transcribe Endpoint

**Date:** 2026-02-01

## Summary

Added a stateless JSON transcription endpoint at `/api/transcribe` for service-to-service calls, with thread safety for concurrent requests.

## Threading Lock for WhisperTranscriber

### Problem
The Whisper model is not thread-safe. Concurrent transcription requests could interfere with each other.

### Solution
- Added `threading.Lock` to `WhisperTranscriber.__init__()`
- Lock wraps `self._model.transcribe()` call to serialize concurrent requests
- Test verifies serialization by timing concurrent calls (2 concurrent calls take ~2x single call time)

## /api/transcribe Endpoint

### What Was Built
- `POST /api/transcribe` - accepts raw WAV bytes, returns JSON `{"text": "..."}`
- Content-Type validation - requires `audio/wav`, returns 400 otherwise
- Error handling - returns 503 if transcriber is closed (server shutting down)

### Design Decisions
- Raw body (not multipart form) for simplicity in service-to-service calls
- Stateless - no session, no htmx, just audio in → text out
- Same transcription service as the browser UI endpoint

### Usage
```bash
curl -X POST http://localhost:8765/api/transcribe \
  -H "Content-Type: audio/wav" \
  --data-binary @audio.wav
```

## Files Modified

- `src/great_dictator/adapters/outbound/whisper_transcriber.py` - added threading lock
- `src/great_dictator/adapters/inbound/fastapi_app.py` - added /api/transcribe endpoint
- `tests/integration/test_whisper_adapter.py` - added concurrency test
- `tests/integration/test_api.py` - added endpoint tests
- `README.md` - documented API endpoint

## Test Results

All tests passing:
- 25 integration tests
- Includes 3 new tests for /api/transcribe endpoint
- Includes 1 new test for threading lock

Type checking: 0 errors (pyright)

## Commits

1. `b39a3ae` - Add threading lock to WhisperTranscriber for concurrent request safety
2. `cc2af5f` - Add /api/transcribe endpoint for JSON transcription
3. `b3f195d` - Add 400 error for invalid content-type on /api/transcribe
4. `a51c229` - Add 503 error when transcriber is closed on /api/transcribe

## Architecture Notes

### Whisper Model Configuration
- Model size: `medium` (upgraded from `base` for better accuracy)
- Device: `cpu`
- Compute type: `int8`

### Concurrency Model
- Requests are serialized at the transcriber level via threading lock
- FastAPI async endpoint calls synchronous transcription (blocks event loop during transcription)
- This matches existing `/transcribe` htmx endpoint behavior

## Jetson Xavier Deployment

### Challenges Overcome

1. **Python 3.8 incompatibility** - tokenizers library requires Python 3.9+
2. **CTranslate2 CUDA support** - no pre-built ARM64 wheels, must compile from source
3. **bfloat16 errors** - Xavier (compute 7.2) doesn't support bfloat16, requires CTranslate2 v3.24.0
4. **Type annotation compatibility** - `from __future__ import annotations` breaks FastAPI/Pydantic runtime evaluation
5. **htmx file upload** - htmx.ajax doesn't handle FormData with files, switched to fetch
6. **Route ordering** - `/documents/list-html` must be defined before `/documents/{document_id}`
7. **Secure context for microphone** - requires SSH port forwarding for remote access

### Build Process

```bash
# CTranslate2 v3.24.0 with CUDA for Xavier
git clone --recursive https://github.com/OpenNMT/CTranslate2.git
cd CTranslate2 && git checkout v3.24.0
cmake . -DWITH_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=72 -DWITH_CUDNN=ON -DWITH_MKL=OFF -DOPENMP_RUNTIME=COMP
make -j2 && sudo make install && sudo ldconfig
cd python && pip install . --no-build-isolation
```

### Configuration for Jetson

- Model: `large-v3` for best accuracy
- Device: `cuda` (uses Jetson's GPU)
- Compute type: `float16`
- Server binds to `0.0.0.0:8765` for remote access

### Documentation

Created comprehensive `docs/jetson-xavier-install.md` with full installation guide and troubleshooting.

## Next Steps

- Consider `asyncio.to_thread()` for non-blocking transcription
- User authentication
- Multiple user support in UI
