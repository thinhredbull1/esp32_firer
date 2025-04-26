from flask import Flask, render_template, Response, request, jsonify
import asyncio
import websockets
import threading
import cv2
from ultralytics import YOLO
import numpy as np
import logging
import struct
logging.getLogger('ultralytics').setLevel(logging.ERROR)
# Flask app initialization
app = Flask(__name__)
model = YOLO("../yolov10-firedetection/fire.pt")
connected_clients = set()
fire_detected = False
get_msg= False
speed_linear=0
speed_angular=0
min_speed=10
camera_byte=b''
fire_sensor=False
def generateSpeed(speed):
    global min_speed
    new_speed=0
    if(speed>20):
        new_speed=max(speed,min_speed)
    elif(speed<-20):
        new_speed=min(speed,-min_speed)
    return new_speed
def generate_frames():
    """Camera frame generator."""
    global camera_byte
    global get_msg
    camera_data=b''
    print_one=False
    counting_noise=0
    # camera = cv2.VideoCapture(0)  # Change to your camera index or path
    # if not camera.isOpened():
    #     print("Error: Camera not found!")
    #     return
    while True:
        # success, img = camera.read()
        # if not success:
        #     print("Camera read failed!")
        #     break
        if get_msg:
            get_msg=False
            
            try:
                camera_data+=camera_byte
            # Process the frame (e.g., fire detection)
                jpghead = camera_data.find(b'\xff\xd8')
                jpgend = camera_data.find(b'\xff\xd9')
                # # print(jpghead)
                # if(not print_one):
                    
                #     print("1")
                   
                    # print_one=True
                if jpghead > -1 and jpgend > -1:
                    # print("get image")
                    jpg = camera_data[jpghead:jpgend + 2]
                    camera_data = camera_data[jpgend + 2:]
                    img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                    # img = cv2.rotate(img, cv2.ROTATE_180)
                    results = model(img, conf=0.75)
                    global fire_detected
                    fire_detected = False
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy.tolist()[0])
                            label = model.names[int(box.cls)]
                            if label == 'Fire':
                                fire_detected = True
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    height, width = img.shape[:2]
                    new_width = int(width * 0.5)
                    new_height = int(height * 0.5)
                    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                    ret, buffer = cv2.imencode('.jpg', img)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print("Error:" + str(e))
                camera_data = b''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/control2', methods=['POST'])
def control2():
    """Nhận lệnh điều khiển từ các nút"""
    direction = request.json.get('direction')
    print(f"Received command: {direction}")
    asyncio.run(broadcast_command(direction))
    return "Command received", 200

@app.route('/control', methods=['POST'])
def control():
    direction = request.json.get('direction')
    # print(f"Received command: {direction}")
    speed=direction.split("k")
    speed_left=int(float(speed[0])*100)
    speed_right=int(float(speed[1])*120)
    speed_left=max(min(speed_left,200),-200)
    speed_right=max(min(speed_right,200),-200)
    speed_left=generateSpeed(speed_left)
    speed_right=generateSpeed(speed_right)
    cmd_send=f"{speed_left}k{speed_right}"
    print(f"left:{speed_left}  right:{speed_right}")
    asyncio.run(broadcast_command(cmd_send))
    return "Command received", 200


@app.route('/fire_status', methods=['GET'])
def fire_status():
    global fire_detected
    global fire_sensor
    if fire_detected:
        cmd = "1p"
        asyncio.run(broadcast_command(cmd))
    return jsonify({'fire_detected': fire_detected, 'fire_sensor': fire_sensor})
@app.route('/speed_status', methods=['GET'])
def speed_status():
    global speed_linear
    global speed_angular
    return jsonify({'speed_linear': speed_linear, 'speed_angular': speed_angular})
async def broadcast_command(command):
    if connected_clients:
        await asyncio.wait([client.send(command) for client in connected_clients])

# WebSocket server for handling binary data
async def websocket_server(websocket):
    print("WebSocket client connected!")
    global connected_clients
    connected_clients.add(websocket)  # Thêm client vào danh sách
    global camera_byte
    global get_msg
    global speed_linear
    global speed_angular
    global fire_sensor  # Biến toàn cục mới để lưu trạng thái cảm biến lửa
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                # print(f"Received binary data of length {len(message)}")
                if len(message) == 5:
                    lin_int, ang_int,fire = struct.unpack('<hh?', message)
                    speed_linear = lin_int / 100.0
                    speed_angular = ang_int / 10.0
                    fire_sensor = bool(fire)  # Lưu trạng thái cảm biến lửa
                    print(f"Speed Linear: {speed_linear}, Speed Angular: {speed_angular}, Fire Sensor: {fire_sensor}")
                else:
                    camera_byte=message
                    get_msg=True
                # print(message)
                # Save binary data to a file
            elif isinstance(message, str):
                print(f"Received text data: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket client disconnected: {e}")

async def websocket_main():
    start_server = websockets.serve(websocket_server, "0.0.0.0", 6789)
    await start_server  
    await asyncio.Future()  

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

def run_websocket():
    asyncio.run(websocket_main())  # Sử dụng asyncio.run()

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    websocket_thread = threading.Thread(target=run_websocket)
    flask_thread.start()
    websocket_thread.start()
    flask_thread.join()
    websocket_thread.join()
