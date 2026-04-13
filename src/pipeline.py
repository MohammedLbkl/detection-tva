import paddle

paddle.disable_static()

_pipeline = None


def detect_device():
    try:
        if paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0:
            print(f"GPU détecté : {paddle.device.cuda.device_count()} device(s) CUDA disponible(s).")
            return "gpu"
    except Exception as e:
        print(f"Erreur lors de la détection du GPU : {e}")
    print("Aucun GPU détecté, utilisation du CPU.")
    return "cpu"


def get_pipeline(version="v1.5"):
    global _pipeline
    if _pipeline is None:
        from paddleocr import PaddleOCRVL
        device = detect_device()
        _pipeline = PaddleOCRVL(pipeline_version=version, device=device)
    return _pipeline
