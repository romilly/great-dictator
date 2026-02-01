# Installing great-dictator on Jetson Xavier

Guide for running great-dictator with faster-whisper on NVIDIA Jetson Xavier (16GB).

## Prerequisites

- Jetson Xavier with JetPack installed
- Python 3.8 (comes with JetPack)

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/romilly/great-dictator.git
cd great-dictator
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 3. Install Rust (required for building CTranslate2 on ARM64)

CTranslate2 (used by faster-whisper) doesn't have pre-built ARM64 wheels, so it must be compiled from source. This requires Rust.

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### 4. Install maturin (Rust/Python build tool)

```bash
pip install maturin
```

### 5. Install the application

```bash
pip install .
```

This will compile CTranslate2 from source (takes a while on ARM64).

### 6. Run the server

```bash
./scripts/dev-server.sh
```

The server will:
- Bind to `0.0.0.0:8765` (accessible from other machines)
- Load the Whisper large-v3 model with CUDA GPU acceleration
- Warm up the model before accepting requests

## Configuration

### Model Cache Location

The large-v3 model is ~3GB. By default, Hugging Face downloads models to `~/.cache/huggingface/`. If your root filesystem is small (common on Jetson with NVMe boot + HDD storage), set `HF_HOME` to redirect downloads:

```bash
# Add to ~/.bashrc
export HF_HOME=/path/to/large/drive/.cache/huggingface
```

Then `source ~/.bashrc` before running the server.

### Whisper Model

The Whisper model is configured in `src/great_dictator/app.py`:

```python
transcriber = WhisperTranscriber(
    model_size="large-v3",
    device="cuda",
    compute_type="float16"
)
```

## Notes

- First startup downloads the large-v3 model (~3GB)
- Model loading can take several minutes on Jetson
- 16GB RAM is sufficient for large-v3 with float16
