import gradio as gr
import os
import glob
import threading
import time
import shutil
import psycopg2
import os
import io
import glob
import shutil
import tempfile
from google.cloud import storage
from paddleocr import PaddleOCRVL
pipeline = PaddleOCRVL(pipeline_version="v1.5")


PORT = int(os.getenv("PORT", 8080))


def run_ocr(image_path):
    client = storage.Client(project='project-3b645245-14b9-4448-94f')

    bucket_name = 'bucket_detection-tva'
    bucket = client.bucket(bucket_name)

 
    # Il crée un dossier caché et le SUPPRIME automatiquement à la fin du 'with'
    with tempfile.TemporaryDirectory() as temp_dir:
        

        output = pipeline.predict(image_path)
        
        for res in output:
            res.save_to_markdown(save_path=temp_dir)
            res.save_to_img(save_path=temp_dir)


        md_files = glob.glob(os.path.join(temp_dir, "*.md"))
        if not md_files:
            return "Aucun texte détecté.", None

        local_md_path = md_files[0]
        lines = []
        with open(local_md_path, "r", encoding="utf-8") as f:
            lines = [line for line in f if not line.strip().startswith("<div")]

        with open(local_md_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        md_content = open(local_md_path, encoding="utf-8").read()
        
        # 3. Upload vers GCS
        filename_base = os.path.basename(image_path).split('.')[0]
        
        # Upload Markdown
        bucket.blob(f"{filename_base}.md").upload_from_filename(local_md_path)

        # Upload Image
        img_files = glob.glob(os.path.join(temp_dir, "*.png")) + glob.glob(os.path.join(temp_dir, "*.jpg"))
        gcs_img_url = None
        
        if img_files:
            remote_img_path = f"{os.path.basename(img_files[0])}"
            bucket.blob(remote_img_path).upload_from_filename(img_files[0])
            gcs_img_url = f"gs://{bucket_name}/{remote_img_path}"

    return md_content, gcs_img_url

def run_ocr_with_progress(image_path, progress=gr.Progress()):
    if not image_path:
        raise gr.Error("Veuillez charger une image.")

    yield gr.update(value="Chargement..."), gr.update(value=None)

    result = [None]
    finished = threading.Event()

    def ocr_thread():
        result[0] = run_ocr(image_path)
        finished.set()

    thread = threading.Thread(target=ocr_thread)
    thread.start()

    total_seconds = 170 
    elapsed = 0


    while not finished.is_set():
        percent = min(elapsed / total_seconds, 0.95)
        progress(percent, desc=f"OCR en cours... {int(percent*100)}%")
        
        
        time.sleep(1)
        elapsed += 1

    thread.join()
    
    md_content, img_path = result[0]
    yield md_content, img_path

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

with gr.Blocks(css=css, title="OCR Database App") as demo:
    gr.Markdown("# Extracteur de Documents & Archivage")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="filepath", label="Image à analyser")
            run_btn = gr.Button("Lancer l'OCR", variant="primary")


        with gr.Column(elem_id="col-result"): 
            with gr.Tabs():
                with gr.TabItem("Résultat Texte"):
                    with gr.Column(elem_classes="scroll-markdown"):
                        markdown_out = gr.Markdown(min_height=700)
                
                with gr.TabItem("Image Analysée"):
                    image_out = gr.Image(label= "Zones détectées")

    run_btn.click(
        fn=run_ocr_with_progress, 
        inputs=image_input, 
        outputs=[markdown_out, image_out]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
    )


