import argparse
import os
from src.model import OCRProcessor

def run_cli():
    parser = argparse.ArgumentParser(
        description="Traitement OCR"
    )

    parser.add_argument("-i", "--input", required=True, 
                        help="Path to the input file or directory")
    parser.add_argument("-o", "--output", default="Results", 
                        help="Destination directory for the results")
    parser.add_argument("-v", "--version", default="v1.5", 
                        help="OCR pipeline version (v1.5 or v1.0)")

    args = parser.parse_args()

    manager = OCRProcessor(pipeline_version=args.version)

    if os.path.isfile(args.input):
        manager.process_item(args.input, args.output)
    elif os.path.isdir(args.input):
        manager.process_batch(args.input, args.output)
    else:
        print(f"Path False : {args.input}")

if __name__ == "__main__":
    run_cli()