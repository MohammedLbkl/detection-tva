#!/bin/bash
set -e

# Detect GPU and CUDA version
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi | grep -oP 'CUDA Version: \K[0-9]+\.[0-9]+')
    CUDA_MAJOR=$(echo "$CUDA_VERSION" | cut -d. -f1)
    CUDA_MINOR=$(echo "$CUDA_VERSION" | cut -d. -f2)

    echo "GPU détecté, CUDA $CUDA_VERSION"

    if [ "$CUDA_MAJOR" -ge 13 ]; then
        CUDA_TAG="cu130"
    elif [ "$CUDA_MAJOR" -eq 12 ] && [ "$CUDA_MINOR" -ge 9 ]; then
        CUDA_TAG="cu129"
    elif [ "$CUDA_MAJOR" -eq 12 ] && [ "$CUDA_MINOR" -ge 6 ]; then
        CUDA_TAG="cu126"
    elif [ "$CUDA_MAJOR" -eq 11 ] && [ "$CUDA_MINOR" -ge 8 ]; then
        CUDA_TAG="cu118"
    else
        echo "CUDA $CUDA_VERSION non supporté par PaddlePaddle, installation CPU..."
        uv pip install paddlepaddle==3.3.1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
        uv pip install -r requirements.txt
        exit 0
    fi

    echo "Installation de paddlepaddle-gpu avec $CUDA_TAG..."
    uv pip install paddlepaddle-gpu==3.3.1 -i "https://www.paddlepaddle.org.cn/packages/stable/${CUDA_TAG}/"
else
    echo "Pas de GPU détecté, installation de paddlepaddle (CPU)..."
    uv pip install paddlepaddle==3.3.1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
fi

# Install remaining dependencies
uv pip install -r requirements.txt
