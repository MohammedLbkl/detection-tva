import os
import glob
import shutil
import csv
import zipfile
from datetime import datetime

from src.pipeline import get_pipeline
from src.text_utils import html_to_text
from src.file_utils import filter_supported_files


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
            return "Aucun fichier compatible trouvé dans le dossier.", None, None, None
    elif file_path:
        files_to_process = [file_path]
    else:
        return "Aucun fichier à traiter.", None, None, None

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
        return "Aucun texte détecté.", None, None, None

    combined_md = "\n\n---\n\n".join(all_md)

    # Générer le fichier CSV récapitulatif
    csv_path = os.path.join(base_path, "resultats_ocr.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["Nom du fichier", "Extension", "Taille (Ko)", "Date de modification", "Nb pages/images", "Contenu texte"])
        for idx, fp in enumerate(files_to_process):
            filename = os.path.basename(fp)
            name, ext = os.path.splitext(filename)
            size_ko = round(os.path.getsize(fp) / 1024, 2)
            mod_time = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M:%S")
            # Lire le contenu txt correspondant
            txt_path = os.path.join(base_path, f"file_{idx}", f"{name}.txt")
            txt_content = ""
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as f:
                    txt_content = f.read()
            nb_pages = len(glob.glob(os.path.join(base_path, f"file_{idx}", "*.png"))) or 1
            writer.writerow([filename, ext, size_ko, mod_time, nb_pages, txt_content])

    # Archive zip des fichiers md et txt
    zip_path = os.path.join(base_path, "resultats_ocr.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in md_file_paths:
            if path and os.path.exists(path):
                zf.write(path, arcname=os.path.join("markdown", os.path.basename(path)))
        for path in txt_file_paths:
            if path and os.path.exists(path):
                zf.write(path, arcname=os.path.join("txt", os.path.basename(path)))

    return combined_md, first_img_path, zip_path, csv_path
