import cv2
from pathlib import Path
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

import os, sys
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)
    
class DocumentSegmenter:
    def __init__(self, model_index=0):
        """
        Initialise la classe avec le modèle YOLO choisi.
        model_index : 0 = nano, 1 = small, 2 = medium
        """
        self.model_files = [
            "yolo11n_doc_layout.pt",
            "yolo11s_doc_layout.pt",
            "yolo11m_doc_layout.pt",
        ]
        self.model_path = self._download_model(model_index)
        self.model = YOLO(self.model_path)

    def _download_model(self, model_index):
        """Télécharge le modèle depuis Hugging Face si nécessaire."""
        selected_model = self.model_files[model_index]
        download_path = Path("src/segmentation/models")
        download_path.mkdir(exist_ok=True)

        model_path = hf_hub_download(
            repo_id="Armaggheddon/yolo11-document-layout",
            filename=selected_model,
            repo_type="model",
            local_dir=download_path,
        )
        return model_path

    def detect_sentence(self, image_path):
        """Fait la segmentation de l’image et retourne les boîtes filtrées."""
        img = cv2.imread(image_path)
        results = self.model.predict(img)

        boxes = results[0].boxes
        all_boxes = [box.xyxy[0].tolist() for box in boxes]
        all_classes = [int(box.cls) for box in boxes]
        all_conf = [float(box.conf.item()) for box in boxes]

        filtered_boxes = []

        # Filtrage des boîtes imbriquées
        for i, b1 in enumerate(all_boxes):
            x1_1, y1_1, x2_1, y2_1 = b1
            is_inside = False

            for j, b2 in enumerate(all_boxes):
                if i == j:
                    continue
                x1_2, y1_2, x2_2, y2_2 = b2

                if (x1_1 >= x1_2 and y1_1 >= y1_2 and 
                    x2_1 <= x2_2 and y2_1 <= y2_2):
                    is_inside = True
                    break

            if not is_inside:
                filtered_boxes.append((b1, all_classes[i], all_conf[i]))

        filtered_boxes.sort(key=lambda b: b[0][1])  # tri du haut vers le bas
        return filtered_boxes

    def crop_segments(self, image_path, filtered_boxes, zoom_factor=2):
        """Découpe et sauvegarde les zones détectées."""
        img = cv2.imread(image_path)
        print(img.shape)
        crop_count = 0

        for b, c, conf in filtered_boxes:
            x1, y1, x2, y2 = map(int, b)
            crop = img[y1:y2, x1:x2]

            crop_zoom = cv2.resize(
                crop,
                (crop.shape[1] * zoom_factor, crop.shape[0] * zoom_factor),
                interpolation=cv2.INTER_LINEAR
            )

            crop_path = f"src/test/tmp/table_crop_{crop_count}.png"
            cv2.imwrite(crop_path, crop_zoom)
            crop_count += 1





