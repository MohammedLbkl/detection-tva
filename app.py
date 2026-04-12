import gradio as gr
import os
import re
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

def detect_device():
    try:
        if paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0:
            print(f"GPU détecté : {paddle.device.cuda.device_count()} device(s) CUDA disponible(s).")
            return "gpu"
    except Exception as e:
        print(f"Erreur lors de la détection du GPU : {e}")
    print("Aucun GPU détecté, utilisation du CPU.")
    return "cpu"

def get_pipeline():
    global pipeline
    if pipeline is None:
        from paddleocr import PaddleOCRVL
        device = detect_device()
        pipeline = PaddleOCRVL(pipeline_version="v1.5", device=device)
    return pipeline

SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf")


def html_to_text(content):
    text = content
    # Retours à la ligne pour les balises block
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</td>', '\t', text, flags=re.IGNORECASE)
    text = re.sub(r'</th>', '\t', text, flags=re.IGNORECASE)
    # Supprimer toutes les balises HTML restantes
    text = re.sub(r'<[^>]+>', '', text)
    # Décoder les entités HTML courantes
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    # Lignes vides multiples
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Espaces en fin de ligne
    text = re.sub(r'[ \t]+\n', '\n', text)
    return text.strip()


def filter_supported_files(paths):
    files = []
    for p in paths or []:
        if p and os.path.isfile(p) and p.lower().endswith(SUPPORTED_EXTS):
            files.append(p)
    return sorted(files, key=lambda p: os.path.basename(p))


def process_single_file(file_path, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    pipeline = get_pipeline()
    output = pipeline.predict(file_path)

    for res in output:
        res.save_to_markdown(save_path=save_dir)
        res.save_to_img(save_path=save_dir)

    md_files = glob.glob(f"{save_dir}/*.md")
    if not md_files:
        return None, None, None, None

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

    # Renommer le fichier md selon le fichier source
    src_name = os.path.splitext(os.path.basename(file_path))[0]
    named_md = os.path.join(save_dir, f"{src_name}.md")
    if md_files[0] != named_md:
        shutil.move(md_files[0], named_md)

    # Générer le fichier txt (markdown converti en texte brut)
    named_txt = os.path.join(save_dir, f"{src_name}.txt")
    with open(named_txt, "w", encoding="utf-8") as f:
        f.write(html_to_text(md_content))

    img_files = glob.glob(f"{save_dir}/*.png") + glob.glob(f"{save_dir}/*.jpg") + glob.glob(f"{save_dir}/*.pdf")
    img_path = img_files[0] if img_files else None

    return md_content, img_path, named_md, named_txt


def run_ocr(file_path=None, dir_files=None):
    base_path = "tmp/"

    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path, exist_ok=True)

    files_to_process = []
    if dir_files:
        files_to_process = filter_supported_files(dir_files)
        if not files_to_process:
            return "Aucun fichier compatible trouvé dans le dossier.", None, [], []
    elif file_path:
        files_to_process = [file_path]
    else:
        return "Aucun fichier à traiter.", None, [], []

    print(f"OCR traitement en cours sur {len(files_to_process)} fichier(s)...")

    all_md = []
    md_file_paths = []
    txt_file_paths = []
    first_img_path = None

    for idx, fp in enumerate(files_to_process):
        save_dir = os.path.join(base_path, f"file_{idx}")
        md_content, img_path, md_path, txt_path = process_single_file(fp, save_dir)

        if md_content is None:
            continue

        filename = os.path.basename(fp)
        #save_to_db(filename, md_content)

        if len(files_to_process) > 1:
            all_md.append(f"## {filename}\n\n{md_content}")
        else:
            all_md.append(md_content)

        md_file_paths.append(md_path)
        txt_file_paths.append(txt_path)

        if first_img_path is None and img_path is not None:
            first_img_path = img_path

    print("OCR terminé, traitement des résultats...")

    if not all_md:
        return "Aucun texte détecté.", None, [], []

    combined_md = "\n\n---\n\n".join(all_md)
    return combined_md, first_img_path, md_file_paths, txt_file_paths

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

    md_content, img_path, md_file_paths, txt_file_paths = result[0]
    yield md_content, img_path, md_file_paths, txt_file_paths

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

                with gr.TabItem("Fichiers Markdown"):
                    md_files_out = gr.File(
                        label="Fichiers Markdown générés",
                        file_count="multiple",
                        interactive=False,
                    )

                with gr.TabItem("Fichiers Texte"):
                    txt_files_out = gr.File(
                        label="Fichiers TXT générés",
                        file_count="multiple",
                        interactive=False,
                    )

    run_btn.click(
        fn=run_ocr_with_progress,
        inputs=[image_input, dir_input],
        outputs=[markdown_out, image_out, md_files_out, txt_files_out]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        css=css,
    )


