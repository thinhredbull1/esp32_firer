import asyncio
import websockets

# Danh sách các client đã kết nối
connected_clients = set()

async def handle_client(websocket, path):
    # Thêm client vào danh sách kết nối
    connected_clients.add(websocket)
    print("Client connected")

    try:
        # Lắng nghe tin nhắn từ client
        async for message in websocket:
            print(f"Received from client: {message}")
            
            # Phản hồi lại client (echo message)
            await websocket.send(f"Server received: {message}")
    
    except websockets.ConnectionClosed:
        print("Client disconnected")
    
    finally:
        # Loại bỏ client ra khỏi danh sách nếu mất kết nối
        connected_clients.remove(websocket)

# Gửi dữ liệu dạng text đến tất cả các client
async def broadcast(message):
    if connected_clients:  # Kiểm tra có client nào kết nối không
        await asyncio.wait([client.send(message) for client in connected_clients])

async def main():
    server = await websockets.serve(handle_client, "192.168.0.92", 6789)
    print("WebSocket server is running on ws://0.0.0.0:6789")
    
    # Vòng lặp gửi dữ liệu đến client
    while True:
        await asyncio.sleep(5)  # Gửi mỗi 5 giây
        message = "Hello from server!"
        print(f"Broadcasting message: {message}")
        await broadcast(message)

# Chạy WebSocket server
asyncio.run(main())
