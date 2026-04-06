import gradio as gr
import os
import glob
import threading
import time
import shutil
import psycopg2
import io
import tempfile
from google.cloud import storage
import paddle
paddle.disable_static()



PORT = int(os.getenv("PORT", 8080))
pipeline = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        from paddleocr import PaddleOCRVL
        pipeline = PaddleOCRVL(pipeline_version="v1.5")
    return pipeline

def run_ocr(image_path):
    base_path = "tmp/" 

    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path, exist_ok=True)

    pipeline = get_pipeline()
    
    print("OCR traitement en cours...")

    output = pipeline.predict(image_path)
    
    for res in output:
        res.save_to_markdown(save_path=base_path)
        res.save_to_img(save_path=base_path)

    print("OCR terminé, traitement des résultats...")

    md_files = glob.glob(f"{base_path}/*.md")

    if not md_files:
        return "Aucun texte détecté.", None

    lines = []
    with open(md_files[0], "r", encoding="utf-8") as f:
        for line in f:
            first_word = line.split()[0] if line.split() else ""
            if first_word != "<div":
                lines.append(line)

    with open(md_files[0], "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            
    md_content = open(md_files[0], encoding="utf-8").read()
    
    img_files = glob.glob(f"{base_path}/*.png") + glob.glob(f"{base_path}/*.jpg") + glob.glob(f"{base_path}/*.pdf")
    img_path = img_files[0] if img_files else None

    filename = os.path.basename(image_path)
    #save_to_db(filename, md_content)

    return md_content, img_path

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

    total_seconds = 400
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

with gr.Blocks(title="OCR Database App") as demo:
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
        css=css,
    )


