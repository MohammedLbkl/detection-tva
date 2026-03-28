#!/bin/bash
cd "$(dirname "$0")"

echo "========================================"
echo "  Transcription de document - Lancement"
echo "========================================"
echo ""

if ! command -v brew &>/dev/null; then
    echo "Installation de Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

if ! command -v python3 &>/dev/null; then
    echo "Installation de Python..."
    brew install python
fi

if ! command -v tesseract &>/dev/null; then
    echo "Installation de Tesseract..."
    brew install tesseract
fi

if [ ! -d ".venv" ]; then
    echo "Creation de l'environnement virtuel..."
    python3 -m venv .venv
fi

source .venv/bin/activate

if ! python3 -c "import gradio" &>/dev/null; then
    echo "Installation des dependances (quelques minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo ""
echo "Lancement de l'application..."
echo "Ouvre ton navigateur sur : http://localhost:7860"
echo ""

python3 app.py
