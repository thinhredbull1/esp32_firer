from flask import Flask, render_template, Response, request,jsonify
import cv2
import numpy as np
import time
from ultralytics import YOLO
import os
import logging
logging.getLogger('ultralytics').setLevel(logging.ERROR)
video_path = '/home/thinh/Downloads/input.mp4'
app = Flask(__name__)
model = YOLO("../yolov10-firedetection/fire.pt")
speed_linear=0
speed_angular=0
# Khởi động camera
camera = cv2.VideoCapture(0)  # 0 là camera mặc định, có thể thay đổi nếu bạn có nhiều camera
# camera = cv2.VideoCapture(video_path)
fire_detected=False
def generate_frames():
    global fire_detected
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
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/control2', methods=['POST'])
def control2():
    # global speed_linear
    """Nhận lệnh điều khiển từ các nút"""
    # speed_linear=10
    direction = request.json.get('direction')
    print(f"Received command: {direction}")
    return "Command received", 200
@app.route('/speed_status', methods=['GET'])
def speed_status():
    global speed_linear
    global speed_angular
    return jsonify({'speed_linear': speed_linear, 'speed_angular': speed_angular})
@app.route('/control', methods=['POST'])
def control():
    direction = request.json.get('direction')
    # print(f"Received command: {direction}")
    speed=direction.split("k")
    speed_left=int(float(speed[0])*100)
    speed_right=int(float(speed[1])*100)
    speed_left=max(min(speed_left,200),-200)
    speed_right=max(min(speed_right,200),-200)

    cmd_send=f"{speed_left}k{speed_right}"
    print(f"left:{speed_left}  right:{speed_right}")

    return "Command received", 200


@app.route('/fire_status', methods=['GET'])
def fire_status():
    global fire_detected
    if(fire_detected):
        cmd="1p"
    return jsonify({'fire_detected': fire_detected})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
