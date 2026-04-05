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
python run.py -i <input> -o <output> -v <version>
```

| Argument | Short | Required | Default | Description |
|---|---|---|---|---|
| `--input` | `-i` | ✅ | — | Path to a single image file or a directory of images |
| `--output` | `-o` | ❌ | `Results` | Destination directory where results will be saved |
| `--version` | `-v` | ❌ | `v1.5` | OCR pipeline version (`v1.5` or `v1.0`) |

**Process a single file:**
```bash
python run.py -i document.png
```

**Process a full directory:**
```bash
python run.py -i ./images -o ./output
```

**Use a specific pipeline version:**
```bash
python run.py -i ./images -o ./output -v v1.0
```

## Docker
```bash
docker build -t ocr-app .
docker run -p 8080:8080 ocr-app
```