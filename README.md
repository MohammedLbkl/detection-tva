# Document Transcription

A local OCR application that scans a document image and extracts the text automatically. Built with YOLO for document segmentation and Tesseract for text recognition, wrapped in a simple Gradio interface.

---

## What it does

1. You upload an image of a document (PNG, JPG…)
2. The app detects and segments each line of text
3. OCR reads each segment
4. You get the full transcription in the interface and as a downloadable `.txt` file

---

## Project structure

```
project/
├── src/
│   ├── segmentation/
│   │   └── document_segmenter.py
│   ├── ocr/
│   │   └── ocr_reader.py
├── app.py
├── requirements.txt
├── run.command      ← Mac launcher
└── run.bat          ← Windows launcher
```

---

## Installation & usage

### Mac

> Requirements: none — everything is installed automatically.

1. Clone or download this repository
2. Open a terminal in the project folder and run once:
```bash
chmod +x "run.command"
```
3. Double-click `run.command`
4. The app opens in your browser at `http://localhost:7860`

The first launch installs Homebrew, Python, Tesseract and all dependencies automatically. The following launches are instant.

---

### Windows

> Requirements: Python and Tesseract must be installed manually.

**Step 1 — Install Python**

Download and install Python from [python.org](https://www.python.org/downloads/).
During installation, make sure to check **"Add Python to PATH"**.

**Step 2 — Install Tesseract**

Download and install Tesseract from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki).
During installation, make sure to check **"Add to PATH"**.

**Step 3 — Launch the app**

Double-click `run.bat`.
The first launch installs all Python dependencies automatically.
The app opens in your browser at `http://localhost:7860`.

---

## Dependencies

| Package | Role |
|---|---|
| `gradio` | Web interface |
| `pillow` | Image handling |
| `pytesseract` | OCR (Tesseract wrapper) |
| `opencv-python` | Image processing |
| `huggingface-hub` | Model download |
| `ultralytics` | YOLO segmentation |

Install manually with:
```bash
pip install -r requirements.txt
```

---

## License

This project is open source and free to use.