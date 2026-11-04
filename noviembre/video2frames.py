import cv2
import os

# Ruta del archivo de vídeo
video_path = "video.mp4"
# Carpeta donde se guardarán los fotogramas
output_folder = "frames_output"

# Crear la carpeta si no existe
if not os.path.exists(output_folder):
  os.makedirs(output_folder)

# Abrir el vídeo
cap = cv2.VideoCapture(video_path)
count = 0
success = True

while success:
  # Leer el siguiente fotograma
  success, frame = cap.read()

  if success:
    # Guardar el fotograma como imagen JPG
    image_name = os.path.join(output_folder, f"frame_{count:04d}.jpg")
    cv2.imwrite(image_name, frame)
    count += 1

cap.release()
print(f"¡Proceso terminado! Se extrajeron {count} fotogramas.")
