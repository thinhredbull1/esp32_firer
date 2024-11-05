from flask import Flask, render_template, Response, request
import cv2
import numpy as np
import time
from ultralytics import YOLO
import os
video_path = '/home/thinh/Downloads/input.mp4'
app = Flask(__name__)
model = YOLO("/home/thinh/project_test/esp32_cam_fire/yolov10-firedetection/fire.pt")
# Khởi động camera
# camera = cv2.VideoCapture(0)  # 0 là camera mặc định, có thể thay đổi nếu bạn có nhiều camera
camera = cv2.VideoCapture(video_path)
def generate_frames():
    while True:
        # Đọc frame từ camera
        success, img = camera.read()
        if not success:
            break
        else:
            # Mã hóa frame thành JPEG
            results = model(img, conf=0.6)  # Assuming `model` is your detection model with a confidence threshold of 0.8
            fire_detected = False
            # print("fire")
        # Draw bounding boxes and labels
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

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            # ret, buffer = cv2.imencode('.jpg', frame)
            # frame = buffer.tobytes()
            
            # # Trả frame theo định dạng multipart để stream video
            # yield (b'--frame\r\n'
            #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Trang chủ hiển thị video và nút điều khiển"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream video đến trang web"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    """Nhận lệnh điều khiển từ các nút"""
    direction = request.json.get('direction')
    print(f"Received command: {direction}")
    # Thực hiện hành động cho lệnh nhận được ở đây
    return "Command received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
