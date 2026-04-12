# OCR Document Extractor

A document OCR tool powered by PaddleOCR. Upload an image and get the extracted text as Markdown, along with a visual showing detected zones.

## Requirements
- Python 3.10
- PaddlePaddle 3.3.1 (CPU or GPU)
- PaddleOCR with doc-parser
- Gradio

## Installation

```bash
./install.sh
```

The script automatically detects GPU availability and CUDA version to install the appropriate PaddlePaddle package:

| Environment | Installed package |
|---|---|
| No GPU | `paddlepaddle` (CPU) |
| CUDA >= 13.0 | `paddlepaddle-gpu` (cu130) |
| CUDA 12.9 | `paddlepaddle-gpu` (cu129) |
| CUDA 12.6 - 12.8 | `paddlepaddle-gpu` (cu126) |
| CUDA 11.8 - 12.5 | `paddlepaddle-gpu` (cu118) |

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