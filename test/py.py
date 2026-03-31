from paddleocr import PaddleOCRVL
import glob

pipeline = PaddleOCRVL(pipeline_version="v1.5")
output = pipeline.predict("test/doc1.png")
for res in output:
    res.print()
    res.save_to_json(save_path="output")
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


