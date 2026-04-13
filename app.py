import gradio as gr
import os
import threading
import time

from src.ocr_processor import run_ocr

PORT = int(os.getenv("PORT", 8080))


def run_ocr_with_progress(file_path, dir_files, progress=gr.Progress()):
    if not file_path and not dir_files:
        raise gr.Error("Veuillez charger une image/PDF ou un dossier.")

    yield gr.update(value="Chargement..."), gr.update(value=None), gr.update(value=None), gr.update(value=None)

    result = [None]
    finished = threading.Event()

    def ocr_thread():
        result[0] = run_ocr(file_path=file_path, dir_files=dir_files)
        finished.set()

    thread = threading.Thread(target=ocr_thread)
    thread.start()

    total_seconds = 400
    elapsed = 0


    while not finished.is_set():
        percent = min(elapsed / total_seconds, 0.95)
        progress(percent, desc=f"OCR en cours... {int(percent*100)}%")


        time.sleep(1)
        elapsed += 1

    thread.join()

    md_content, img_path, zip_path, csv_path = result[0]
    yield md_content, img_path, zip_path, csv_path

# CSS
css = """
.gradio-container {
    min-height: 600px;
}
#col-result {
    min-height: 500px;
}
/* La classe pour le scroll du Markdown */
.scroll-markdown {
    max-height: 800px;   /* Hauteur maximum avant l'apparition du scroll */
    overflow-y: auto;    /* Active la barre de défilement à droite */
    padding: 15px;
    border: 1px solid var(--border-color-primary);
    border-radius: 10px;
    background-color: var(--background-fill-secondary);
}
"""

with gr.Blocks(title="OCR Database App") as demo:
    gr.Markdown("# Extracteur de Documents & Archivage")

    with gr.Row():
        with gr.Column():
            image_input = gr.File(
                label="Image ou PDF à analyser",
                file_types=[".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"],
                type="filepath",
            )
            dir_input = gr.File(
                label="Ou dossier à analyser",
                file_count="directory",
                type="filepath",
            )
            run_btn = gr.Button("Lancer l'OCR", variant="primary")


        with gr.Column(elem_id="col-result"):
            with gr.Tabs():
                with gr.TabItem("Résultat Texte"):
                    with gr.Column(elem_classes="scroll-markdown"):
                        markdown_out = gr.Markdown(min_height=700)

                with gr.TabItem("Image Analysée"):
                    image_out = gr.Image(label= "Zones détectées")

                with gr.TabItem("Archive ZIP"):
                    zip_file_out = gr.File(
                        label="Archive ZIP (Markdown + TXT)",
                        interactive=False,
                    )

                with gr.TabItem("Fichier CSV"):
                    csv_file_out = gr.File(
                        label="Fichier CSV récapitulatif",
                        interactive=False,
                    )

    run_btn.click(
        fn=run_ocr_with_progress,
        inputs=[image_input, dir_input],
        outputs=[markdown_out, image_out, zip_file_out, csv_file_out]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        css=css,
    )
