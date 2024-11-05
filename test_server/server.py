from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)

# Khởi động camera
camera = cv2.VideoCapture(0)  # 0 là camera mặc định, có thể thay đổi nếu bạn có nhiều camera

def generate_frames():
    while True:
        # Đọc frame từ camera
        success, frame = camera.read()
        if not success:
            break
        else:
            # Mã hóa frame thành JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Trả frame theo định dạng multipart để stream video
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
