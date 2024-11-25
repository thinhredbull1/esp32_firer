import numpy as np
import time
import os
import cv2

# Địa chỉ IP của ESP32-CAM (nếu bạn muốn vẫn giữ URL)
url = "http://172.16.4.131/stream"

def generate_image_from_file(image_path):
    # Đọc hình ảnh từ máy tính
    img = cv2.imread(image_path)
    
    # Kiểm tra xem ảnh có tồn tại không
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    
    # Giảm kích thước ảnh xuống (thay đổi độ phân giải)
    img_resized = cv2.resize(img, (160, 120))  # Kích thước mới

    # Cấu hình chất lượng nén (giảm chất lượng để giảm kích thước byte)
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 3]  # Chất lượng nén thấp (0-100)
    
    # Mã hóa hình ảnh thành JPEG
    _, img_encoded = cv2.imencode('.jpg', img_resized, encode_params)
    
    # Chuyển đổi thành byte
    img_bytes = img_encoded.tobytes()
    
    # Kiểm tra kích thước byte
    print(f"Image size after encoding: {len(img_bytes)} bytes")
    
    return img_bytes

def save_bytes_to_file(bytes_data, filename):
    # Lưu dữ liệu byte vào tệp văn bản
    with open(filename, 'wb') as file:
        file.write(bytes_data)

def stream_video(url):
    bytes_stream = b""
    
    print("START")

    # Thay vì tạo hình ảnh ngẫu nhiên, sử dụng hình ảnh từ máy tính
    image_path = "/home/thinh/Pictures/Untitled.jpeg"  # Thay đường dẫn này với tệp hình ảnh của bạn
    bytes_stream = generate_image_from_file(image_path)
    
    # Lưu byte stream vào tệp
    # save_bytes_to_file(bytes_stream, 'image_bytes.txt')
    print(bytes_stream)
    # Kiểm tra xem dữ liệu có phải là JPEG hợp lệ không
    a = bytes_stream.find(b"\xff\xd8")  # Start of JPEG
    b = bytes_stream.find(b"\xff\xd9")  # End of JPEG
    if a != -1 and b != -1:
        jpg = bytes_stream[a : b + 2]
        bytes_stream = bytes_stream[b + 2 :]

        img_np = np.frombuffer(jpg, dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if img is not None:
            cv2.imshow("ESP32-CAM Stream", img)
        else:
            print("NONE")
    cv2.waitKey()
    
    print("DONE")

if __name__ == "__main__":
    stream_video(url)
