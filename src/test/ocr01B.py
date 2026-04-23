from openocr import OpenOCR

# Initialize OpenDoc
doc_parser = OpenOCR(
    task='doc',
    use_layout_detection=True,
)

# Parse document
result = doc_parser(image_path='data/doc1.png')

# Save results
doc_parser.save_to_markdown(result, './output')
doc_parser.save_visualization(result, './output')