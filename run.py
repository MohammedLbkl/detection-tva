import argparse
import os
from pathlib import Path

import tqdm

from src.pipeline import get_pipeline
from src.ocr_processor import process_single_file
from src.file_utils import SUPPORTED_EXTS


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

    # Initialise le pipeline avec la version demandée
    get_pipeline(version=args.version)

    if os.path.isfile(args.input):
        files = [args.input]
    elif os.path.isdir(args.input):
        files = [
            os.path.join(args.input, name)
            for name in sorted(os.listdir(args.input))
            if name.lower().endswith(SUPPORTED_EXTS)
            and os.path.isfile(os.path.join(args.input, name))
        ]
    else:
        print(f"Chemin invalide : {args.input}")
        return

    for fp in tqdm.tqdm(files):
        save_dir = os.path.join(args.output, Path(fp).stem)
        try:
            process_single_file(fp, save_dir)
        except Exception as e:
            print(f"Erreur sur {fp} : {e}. Passage au suivant.")


if __name__ == "__main__":
    run_cli()
