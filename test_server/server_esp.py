from flask import Flask, render_template, Response, request,jsonify
import cv2
import numpy as np
import time
from ultralytics import YOLO
import os
import logging
import base64
from flask_socketio import SocketIO, emit
from threading import Thread
logging.getLogger('ultralytics').setLevel(logging.ERROR)
video_path = '/home/thinh/Downloads/input.mp4'
app = Flask(__name__)
model = YOLO("/home/thinh/project_test/esp32_cam_fire/yolov10-firedetection/fire.pt")
# Khởi động camera


fire_detected=False
def generate_frames():
    global fire_detected
    # global camera
    camera = cv2.VideoCapture(0)  # 0 là camera mặc định, có thể thay đổi nếu bạn có nhiều camera
# camera = cv2.VideoCapture(video_path)
    if not camera.isOpened():
        print("Error: Camera not found!")
    else:
        print("Camera opened successfully.")
        camera.release()
    while True:
        # Đọc frame từ camera
        success, img = camera.read()
        if not success:
            print("NOT camera")
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
                    # print(label)
                    if label == 'Fire':
                        fire_detected = True
                        # print("firer")
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
    global fire_detected
    direction = request.json.get('direction', 'Unknown')
    if direction=='stop':
        fire_detected=True
    else:
        fire_detected=False
    print(f"Received command: {direction}")
    return "Command received", 200
@app.route('/fire_status', methods=['GET'])
def fire_status():
    """Gửi trạng thái phát hiện lửa"""
    # print(fire_detected)
    return jsonify({'fire_detected': fire_detected})
socketio = SocketIO(app, cors_allowed_origins="*",threaded=True)  # Bật CORS toàn cầu
@socketio.on('connect')
def handle_connect():
    print("User connected!")
    emit('event', {'message': 'Connected !!!!'})


@socketio.on('status')
def handle_status(data):
    print(f"Status received from client: {data}")
@socketio.on('image_frame')
def handle_image_frame(data):
    print(f"Status received from client: {data}")
    image_data = data.get('image_frame')
    if image_data:
        image_bytes = base64.b64decode(image_data)
        # print("Image successfully saved as 'received_image.jpg'")
        print(f"Received base64 image data: {image_bytes}")
    else:
        print("No image data found")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000,debug=True)


