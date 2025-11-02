"""
Ce script utilise un modèle YOLOv8 pour la détection en temps réel.
La capture d'images est déclenchée manuellement avec la touche 'c'.
Chaque frame affichée à l'écran (avec les détections) est également
sauvegardée dans le dossier 'tmp'.

Fonctionnement :
    1. Le script affiche le flux de la webcam en continu.
    2. Chaque image annotée est sauvegardée dans le dossier /tmp.
    3. Appuyez sur la touche 'c' pour lancer la capture d'une séquence de 20 frames.
    4. La frame la moins floue de la séquence est sélectionnée et sauvegardée.
    5. Appuyez sur la touche 'q' pour quitter.
"""
import os
import time
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np

# --- Assurez-vous que ces fichiers existent ---
from save_image import save_masked_image
from blurry import less_blurred





# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR_TMP = os.path.join(BASE_DIR, "tmp")

# Créer le répertoire de sauvegarde s'il n'existe pas
os.makedirs(SAVE_DIR_TMP, exist_ok=True)


folder_tmp = Path("src/detection/tmp")
# Cleanup leftover recording chunks from previous runs
for f in folder_tmp.glob("*.jpg"):
    try:
        f.unlink()
    except Exception as e:
        print(f"Could not remove {f}: {e}")
        
        
# Modèle YOLOv8
MODEL_PATH = os.path.join(BASE_DIR, "models/Yolo-seg.pt")
model = YOLO(MODEL_PATH)

# Liste pour stocker les frames capturées
video_frames = []
captured_results = []

# États du programme
capturing = False
capture_countdown = 20 # Nombre de frames à capturer

# Initialisation de la webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la webcam.")
    exit()

# --- Boucle principale ---
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur: Impossible de recevoir la frame.")
            break

        # Inférence YOLO sur la frame actuelle
        results = model.predict(source=frame, conf=0.8, verbose=False)
        annotated_frame = results[0].plot() # `plot()` dessine les détections

        if capturing:
            if capture_countdown > 0:
                video_frames.append(frame)
                captured_results.append(results[0])
                text = f"Capture en cours... {capture_countdown}"
                cv2.putText(annotated_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                capture_countdown -= 1
            else:
                print("Capture terminée. Sélection de la meilleure image...")
                best_index = less_blurred(captured_results) 
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                save_masked_image(captured_results[best_index], SAVE_DIR_TMP, stamp)
                print(f"Image la plus nette (index {best_index}) sauvegardée.")
                
                video_frames = []
                captured_results = []
                capturing = False
        else:
            cv2.putText(annotated_frame, "Appuyez sur 'c' pour capturer ou 'q' pour quitter", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Afficher le flux vidéo annoté
        cv2.imshow('YOLOv8 Detection', annotated_frame)

        # Gestion des touches
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and not capturing:
            print("Début de la capture !")
            capturing = True
            capture_countdown = 20

        elif key == ord('q'):
            print("Arrêt demandé par l'utilisateur.")
            break

except Exception as e:
    print(f"Une erreur est survenue: {e}")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Fin.")