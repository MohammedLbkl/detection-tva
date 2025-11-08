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
    
    sys.stdout = open("src/test/results.txt", "w")
    
    print(texte_final)
    
    sys.stdout.close()
    
    
if __name__ == "__main__":
    IMAGE_PATH = "src/test/images/doc1.png"
    pipeline(IMAGE_PATH)

