import gradio as gr
from pathlib import Path
import json
import os
import tempfile
from PIL import Image

from src.segmentation.document_segmenter import DocumentSegmenter
from src.ocr.ocr_reader import OCRReader

TMP_FOLDER = Path("src/test/tmp")
RESULTS_TXT = Path("src/test/results.txt")
RESULTS_JSON = Path("src/test/results.json")


def pipeline(image_path: str) -> tuple[str, str]:
    """
    Reçoit le chemin d'une image, lance la segmentation + OCR,
    retourne (texte_transcrit, chemin_du_fichier_txt_à_télécharger).
    """
    # Nettoyage du dossier temporaire
    TMP_FOLDER.mkdir(parents=True, exist_ok=True)
    for f in TMP_FOLDER.glob("*.png"):
        f.unlink()

    # Segmentation
    segmenter = DocumentSegmenter(model_index=0)
    boxes = segmenter.detect_sentence(image_path)
    segmenter.crop_segments(image_path, boxes)

    # OCR
    ocr = OCRReader(folder_path=str(TMP_FOLDER))
    texte_final = ocr.read_images()

    # Sauvegarde résultats
    RESULTS_TXT.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_TXT.write_text(texte_final, encoding="utf-8")

    result = {
        "image_path": image_path,
        "transcription": texte_final,
    }
    RESULTS_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=4), encoding="utf-8"
    )

    # Fichier temporaire téléchargeable
    tmp_out = tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", mode="w", encoding="utf-8"
    )
    tmp_out.write(texte_final)
    tmp_out.close()

    return texte_final, tmp_out.name


def traiter(image):
    """
    Callback Gradio : reçoit un tableau numpy (image uploadée),
    le sauvegarde temporairement, puis lance le pipeline.
    """
    if image is None:
        return "Aucune image fournie.", None

    tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    Image.fromarray(image.astype("uint8")).save(tmp_img.name)
    tmp_img.close()

    try:
        texte, fichier_txt = pipeline(tmp_img.name)
    except Exception as e:
        return f"Erreur : {e}", None
    finally:
        os.unlink(tmp_img.name)

    return texte, fichier_txt


with gr.Blocks(title="Transcription de document") as demo:

    gr.Markdown("## Transcription de document")
    gr.Markdown(
        "Dépose une image de document (PNG, JPG…). "
        "Le pipeline segmente et transcrit le texte automatiquement."
    )

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(
                label="Image du document",
                type="numpy",
            )
            btn = gr.Button("Transcrire", variant="primary")

        with gr.Column():
            texte_output = gr.Textbox(
                label="Texte transcrit",
                lines=20,
            )
            fichier_output = gr.File(
                label="Télécharger le fichier .txt",
            )

    btn.click(
        fn=traiter,
        inputs=[image_input],
        outputs=[texte_output, fichier_output],
    )

if __name__ == "__main__":
    demo.launch()