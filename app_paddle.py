import gradio as gr
import os
import glob
from paddleocr import PaddleOCRVL
import threading
import time
import shutil

def run_ocr(image_path):

    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output", exist_ok=True)
    
    pipeline = PaddleOCRVL(pipeline_version="v1.5")
    output = pipeline.predict(image_path)
    
    for res in output:
        res.save_to_markdown(save_path="output")
        res.save_to_img(save_path="output")

    md_files = glob.glob("output/*.md")

    lines = []
    with open(md_files[0], "r",encoding="utf-8") as f:
        for line in f:
            firt_word = line.split()[0] if line.split() else ""
            if firt_word != "<div":
                lines.append(line)

    with open(md_files[0], "w",encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            
    md_content = open(md_files[0], encoding="utf-8").read() if md_files else "Aucun markdown généré."
    
    img_files = glob.glob("output/*.png") + glob.glob("output/*.jpg")
    img_path = img_files[0] if img_files else None

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

with gr.Blocks(css=css) as demo:
    gr.Markdown("## PaddleOCR VL")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="filepath", label="Image à analyser")
            run_btn = gr.Button("Lancer l'OCR", variant="primary")


        with gr.Column(elem_id="col-result"): 
            with gr.Tabs():
                with gr.TabItem("Résultat Markdown"):
                    with gr.Column(elem_classes="scroll-markdown"):
                        markdown_out = gr.Markdown(min_height=700)
                
                with gr.TabItem("Image annotée"):
                    image_out = gr.Image()

    run_btn.click(
        fn=run_ocr_with_progress, 
        inputs=image_input, 
        outputs=[markdown_out, image_out]
    )

demo.launch()


