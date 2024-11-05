import cv2
import numpy as np
import time
from ultralytics import YOLO
import os

# Mô hình yolov10 phát hiện lửa
model = YOLO(f"{os.getcwd()}/fire.pt")

# Đọc và hiển thị hình ảnh từ webcam
def stream_video():
    # Mở luồng webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không thể mở webcam")
        return

    while True:
        ret, img = cap.read()
        if not ret:
            print("Không nhận được khung hình từ webcam")
            break

        # Phát hiện lửa
        results = model(img, conf=0.8)
        
        # Vẽ khung bao quanh và nhãn
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy.tolist()[0]
                c = box.cls
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                label = model.names[int(c)]
                
                # Vẽ khung và nhãn
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    img,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2,
                )

        # Hiển thị khung hình từ webcam
        cv2.imshow("Webcam Stream", img)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Giải phóng và đóng cửa sổ hiển thị
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_video()
