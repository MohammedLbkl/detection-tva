from transformers import AutoModel, AutoProcessor
from chandra.model.hf import generate_hf
from chandra.model.schema import BatchInputItem
from chandra.output import parse_markdown
from PIL import Image

model = AutoModel.from_pretrained("datalab-to/chandra").cuda()
model.processor = AutoProcessor.from_pretrained("datalab-to/chandra")

PIL_IMAGE = Image.open("../images/doc1.png")

batch = [
    BatchInputItem(
        image=PIL_IMAGE,
        prompt_type="ocr_layout"
    )
]

import sys
sys.stdout = open("resultats.txt", "w")

result = generate_hf(batch, model)[0]
markdown = parse_markdown(result.raw)

print(markdown)
sys.stdout.close()