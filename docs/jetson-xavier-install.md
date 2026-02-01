# Installing great-dictator on Jetson Xavier

Guide for running great-dictator with faster-whisper and GPU acceleration on NVIDIA Jetson Xavier (16GB).

## Prerequisites

- Jetson Xavier with JetPack 4.x or 5.x installed
- Python 3.9 (Python 3.8 has compatibility issues with tokenizers)
- CUDA and cuDNN (included with JetPack)

### Install Python 3.9 if needed

```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev
```

## Installation Steps

### 1. Set up Hugging Face cache location (if root filesystem is small)

The large-v3 model is ~3GB. If your root filesystem is small (common on Jetson with NVMe boot + HDD storage), redirect the cache:

```bash
echo 'export HF_HOME=/path/to/large/drive/.cache/huggingface' >> ~/.bashrc
source ~/.bashrc
```

### 2. Clone the repository

```bash
cd /path/to/large/drive/git
git clone https://github.com/romilly/great-dictator.git
cd great-dictator
```

### 3. Create virtual environment with Python 3.9

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 4. Install Rust (required for building dependencies)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### 5. Install build dependencies

```bash
pip install maturin pybind11 wheel
```

### 6. Build CTranslate2 with CUDA support

The pip version of CTranslate2 doesn't include CUDA support for ARM64. You must build from source using v3.24.0 (newer versions have bfloat16 issues on Xavier's compute capability 7.2).

```bash
cd ..
git clone --recursive https://github.com/OpenNMT/CTranslate2.git
cd CTranslate2
git checkout v3.24.0
git submodule update --init --recursive
```

Build the C++ library:

```bash
cmake . -DWITH_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=72 -DWITH_CUDNN=ON -DWITH_MKL=OFF -DOPENMP_RUNTIME=COMP
make -j2
sudo make install
sudo ldconfig
```

Build and install the Python bindings:

```bash
cd python
pip install . --no-build-isolation
cd ../..
```

### 7. Install the application

```bash
cd great-dictator
pip install .
```

This will download the large-v3 Whisper model (~3GB) on first run.

### 8. Run the server

```bash
./scripts/dev-server.sh
```

The server will:
- Bind to `0.0.0.0:8765` (accessible from other machines)
- Load the Whisper large-v3 model with CUDA GPU acceleration
- Warm up the model before accepting requests

## Accessing from another machine

The browser requires a secure context for microphone access. Use SSH port forwarding:

```bash
ssh -L 8765:localhost:8765 user@<xavier-ip>
```

Then access `http://localhost:8765` in your browser.

## Configuration

### Whisper Model

The Whisper model is configured in `src/great_dictator/app.py`:

```python
transcriber = WhisperTranscriber(
    model_size="large-v3",
    device="cuda",
    compute_type="float16"
)
```

## Troubleshooting

### "This CTranslate2 package was not compiled with CUDA support"

The pip package got reinstalled over your CUDA build. Reinstall the local build:

```bash
pip uninstall ctranslate2
cd /path/to/CTranslate2/python
pip install . --no-build-isolation --no-deps
```

### bfloat16 compilation errors

Use CTranslate2 v3.24.0 - newer versions try to compile bfloat16 ops which aren't supported on Xavier (compute capability 7.2).

### Python.h not found

Install Python dev headers:

```bash
sudo apt install python3.9-dev
```

### Model loading is slow

First load downloads the model and takes several minutes. Subsequent loads are faster but still take time to load ~3GB into GPU memory.

## Notes

- CTranslate2 must be v3.24.0 for Xavier compatibility
- Python must be 3.9+ (tokenizers library requires it)
- Build with `-j2` to avoid memory issues during compilation
- 16GB RAM is sufficient for large-v3 with float16
