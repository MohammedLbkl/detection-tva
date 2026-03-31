import gradio as gr
import os
import glob
from paddleocr import PaddleOCRVL
import threading
import time
import shutil
import psycopg2

pipeline = PaddleOCRVL(pipeline_version="v1.5")

DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 8080))

def save_to_db(filename, transcription):
    """Sauvegarde en base de données : Crée ou met à jour la transcription"""
    if not DATABASE_URL:
        print("DATABASE_URL non configurée.")
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 1. Création de la table avec created_at uniquement
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id SERIAL PRIMARY KEY,
                filename TEXT UNIQUE,
                transcription TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Logique Anti-doublon (Upsert)
        # On insère le nouveau scan. Si le nom de fichier existe déjà, 
        # on met seulement à jour la transcription.
        query = """
            INSERT INTO scans (filename, transcription) 
            VALUES (%s, %s)
            ON CONFLICT (filename) 
            DO UPDATE SET transcription = EXCLUDED.transcription;
        """
        cur.execute(query, (filename, transcription))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"Base de données : '{filename}' enregistré avec succès.")
    except Exception as e:
        print(f"Erreur Base de données : {e}")


def run_ocr(image_path):

    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output", exist_ok=True)
    
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

    filename = os.path.basename(image_path)
    save_to_db(filename, md_content)

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
    # Configuration pour le déploiement Railway
    demo.launch(
        server_name="0.0.0.0", 
        server_port=PORT,
        show_api=False
    )


