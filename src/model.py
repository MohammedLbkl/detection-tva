import os
import glob
import shutil
import tqdm
from pathlib import Path
from paddleocr import PaddleOCRVL

class OCRProcessor:
    def __init__(self, pipeline_version="v1.5"):

        self.pipeline = PaddleOCRVL(pipeline_version=pipeline_version)

        self.exts = ["jpg", "png", "jpeg", "bmp", "pdf"]

    def process_item(self, input_path, output_dir):

        file_path = Path(input_path)
        
        if os.path.exists("tmp/"):
            shutil.rmtree("tmp/")
        os.makedirs("tmp/", exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        results = self.pipeline.predict(str(file_path))
        
        for res in results:
            res.save_to_markdown(save_path="tmp/")
            res.save_to_img(save_path=output_dir)

        md_files = glob.glob("tmp/*.md")

        lines = []

        if not os.path.exists(md_files[0]):
            raise ValueError("Aucun fichier .md généré")

        with open(md_files[0], "r",encoding="utf-8") as f:
            for line in f:
                firt_word = line.split()[0] if line.split() else ""
                if firt_word != "<div":
                    lines.append(line)

        basename = Path(input_path).stem

        with open(f"{output_dir}/{basename}.md", "w",encoding="utf-8") as f:
            for line in lines:
                f.write(line)


    def process_batch(self, input_dir, output_dir):

        files = []
        
        for ext in self.exts:
            pattern = os.path.join(input_dir, f"*.{ext}")
            files.extend(glob.glob(pattern))

        for file in tqdm.tqdm(files):
            try:
                self.process_item(file, output_dir)
            except Exception as e:
                print(f"Erreur sur {file} : {e}. Passage au suivant.")
                continue