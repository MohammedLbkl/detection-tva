from ultralytics import YOLO
import cv2
import os
from datetime import datetime

# Charger le modèle
MODEL_PATH = "src/detection/models/Yolo-seg.pt"
model = YOLO(MODEL_PATH)

# Source de la caméra
SOURCE = 0
tmp_dir = "tmp"
os.makedirs(tmp_dir, exist_ok=True)

print("Votre iPhone 14 Pro Max 512GO est activé")

try:
    # Boucle de détection en temps réel
    for result in model.predict(source=SOURCE, show=True, stream=True, conf=0.7, verbose=False):
        # Récupération de l'image actuelle
        frame = result.orig_img  # Image originale du flux

        # Affichage de la frame (optionnel si show=True déjà utilisé)
        # cv2.imshow("YOLO", frame)

        # Vérifier si l'utilisateur appuie sur 'm' pour prendre une photo
        key = cv2.waitKey(1) & 0xFF
        if key == ord('m'):
            # Générer un nom de fichier unique basé sur la date et l'heure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(tmp_dir, f"capture_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Photo enregistrée dans {filename}")

except KeyboardInterrupt:
    print("Ctrl+C est pressé.")

finally:
    print("Fin.")
    cv2.destroyAllWindows()
