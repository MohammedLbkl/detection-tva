from ultralytics import YOLO


MODEL_PATH = "src/detection/model/Yolo-seg.pt"
model = YOLO(MODEL_PATH)


SOURCE = 0

try:
    print("Your Iphone14 pro max 512GO is activate")
    for result in model.predict(
        source=SOURCE,
        show=True,        # Affiche la vidéo avec les bounding boxes
        stream=True,      
        conf=0.7,         
        verbose=False
    ):
        pass 

except KeyboardInterrupt:
    print("Ctrl+C is press.")
finally:
    print("End.")
