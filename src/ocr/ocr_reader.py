import pytesseract
from PIL import Image
from pathlib import Path
import re
import os

class OCRReader:
    def __init__(self, folder_path="src/tmp"):
        """
        Initialise le lecteur OCR.
        folder_path : dossier contenant les images à lire.
        """
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists():
            raise FileNotFoundError(f"Le dossier {self.folder_path} n'existe pas.")

    def _get_sorted_images(self):
        """Récupère et trie les fichiers .png du dossier."""
        files = list(self.folder_path.glob("*.png"))
        files_sorted = sorted(
            files,
            key=lambda x: int(re.search(r'table_crop_(\d+)', x.name).group(1))
            if re.search(r'table_crop_(\d+)', x.name) else 0
        )
        return files_sorted

    def read_images(self, delete_after=True):
        """
        Lit le texte de toutes les images du dossier.
        delete_after : supprime les images après lecture (True par défaut)
        """
        files_sorted = self._get_sorted_images()
        all_texts = []

        for img_path in files_sorted:
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img)
            all_texts.append(text)

            if delete_after:
                os.remove(img_path)

        # Combine tous les textes avec une séparation claire
        final_text = "\n------------------------------------------------------------------\n\n".join(all_texts)
        return final_text


if __name__ == "__main__":
    ocr = OCRReader(folder_path="src/tmp")
    texte_final = ocr.read_images()
    
    import sys
    sys.stdout = open("src/ocr/results.txt", "w")
    
    print(texte_final)
    
    sys.stdout.close()
