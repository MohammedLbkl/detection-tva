import os

SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf")


def filter_supported_files(paths):
    files = []
    for p in paths or []:
        if p and os.path.isfile(p) and p.lower().endswith(SUPPORTED_EXTS):
            files.append(p)
    return sorted(files, key=lambda p: os.path.basename(p))
