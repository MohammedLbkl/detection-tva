import cv2

print("Recherche des caméras disponibles...")

nb_index = 3

for i in range(nb_index):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"Caméra détectée à l'index {i}")
            cv2.imshow(f"Camera {i}", frame)
            cv2.waitKey(1000)  # affiche 1 seconde
            cv2.destroyAllWindows()
        cap.release()
    else:
        print(f"Pas de caméra à l'index {i}")

print("Test terminé.")
