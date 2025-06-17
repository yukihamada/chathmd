#!/bin/bash
set -e

echo "Setting up Text-to-LoRA with jan-mini-14B-qwen3 Q4_K_XS..."

# Check system requirements
if ! command -v git &> /dev/null; then
    echo "Error: git is required but not installed."
    exit 1
fi

if ! command -v cmake &> /dev/null; then
    echo "Error: cmake is required but not installed."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed."
    exit 1
fi

# Clone llama.cpp if not present
if [ ! -d "llama.cpp" ]; then
    echo "Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp
fi

# Build llama.cpp
echo "Building llama.cpp..."
cd llama.cpp

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring with CMake..."
if command -v nvcc &> /dev/null; then
    echo "CUDA detected, building with GPU support..."
    cmake .. -DLLAMA_CUDA=ON
else
    echo "Building CPU version..."
    cmake ..
fi

# Build
echo "Building..."
cmake --build . --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)

cd ../..

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q torch transformers safetensors accelerate sentencepiece

echo "Setup complete!"
echo "Next steps:"
echo "1. Run 'python scripts/download_and_quantize.py' to prepare the model"
echo "2. Use 'python scripts/generate_lora.py' to create task-specific LoRAs"
echo "3. Run inference with 'python scripts/inference.py'"