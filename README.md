# OCR Document Extractor

A document OCR tool powered by PaddleOCR. Upload an image and get the extracted text as Markdown, along with a visual showing detected zones.

## Requirements
- Python 3.10
- PaddlePaddle 3.3.0 (CPU)
- PaddleOCR with doc-parser
- Gradio

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web app
```bash
python app.py
```
Opens a Gradio interface at `http://localhost:8080`.

### CLI
```bash
python run.py -i path/to/file_or_folder -o Results -v v1.5
```

## Docker
```bash
docker build -t ocr-app .
docker run -p 8080:8080 ocr-app
```