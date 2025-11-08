from pathlib import Path
import json

import sys
import os
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)
    
from src.segmentation.document_segmenter import DocumentSegmenter
from src.ocr.ocr_reader import OCRReader


def pipeline(img_path) :

    segmenter = DocumentSegmenter(model_index=0)
    
    boxes = segmenter.detect_sentence(img_path)
    segmenter.crop_segments(img_path, boxes)
    
    ocr = OCRReader(folder_path="src/test/tmp")
    texte_final = ocr.read_images()
    
    with open("src/test/results.txt", "w", encoding="utf-8") as f:
        f.write(texte_final)


    result = {
        "image_path": img_path,
        "transcription": texte_final
    }


    with open("src/test/results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
        
    sys.stdout = open("src/test/results.txt", "w")
    
    print(texte_final)
    
    sys.stdout.close()
    
    
if __name__ == "__main__":
    
    # Cleanup leftover recording chunks from previous runs
    folder_tmp = Path("src/test/tmp")
    for f in folder_tmp.glob("*.png"):
        f.unlink()

    IMAGE_PATH = "src/test/images/doc1.png"
    pipeline(IMAGE_PATH)

