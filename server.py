# multithread_server.py (Dùng cho Chat/Broadcast)
import socket
import threading
import datetime
import sys # Để thoát Server an toàn

HOST = '127.0.0.1'
PORT = 65432

# Danh sách toàn cục để lưu trữ các socket client đang hoạt động
connected_clients = []
file_lock = threading.Lock()
client_list_lock = threading.Lock() # Lock mới để bảo vệ danh sách client

def broadcast(message, sender_conn):
    """Gửi tin nhắn đến TẤT CẢ client ngoại trừ client gửi (sender_conn)."""
    with client_list_lock:
        for client_socket in connected_clients:
            try:
                client_socket.send(message.encode('utf-8'))
            except:
                # Nếu gửi không thành công (client đã ngắt kết nối), xóa client đó
                client_socket.close()
                if client_socket in connected_clients:
                    connected_clients.remove(client_socket)

def handle_client(conn, addr):
    """Hàm xử lý kết nối, nhận tin nhắn và gọi hàm broadcast."""
    print(f"[ACTIVE] Đã kết nối bởi client từ: {addr}")

    # 1. Thêm client mới vào danh sách
    with client_list_lock:
        connected_clients.append(conn)
    
    # Thông báo cho tất cả mọi người có client mới tham gia
    join_msg = f"[INFO] Client {addr} đã tham gia chat room!\n"
    print(join_msg.strip())
    broadcast(join_msg, conn)

    try:
        # Gửi thông báo chào mừng ban đầu
        initial_message = "Chào mừng bạn. Hãy gõ tin nhắn (hoặc 'quit' để thoát):"
        conn.sendall(initial_message.encode('utf-8'))

        while True:
            data = conn.recv(1024)
            
            if not data:
                break # Client ngắt kết nối

            client_message = data.decode('utf-8')
            
            # 2. Phát lại tin nhắn đến các client khác
            full_message = f"{client_message}"
            broadcast(full_message + '\n')
            
            print(f"[RECV] {full_message}")

            # 3. Ghi dữ liệu vào file
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {full_message}\n"
            
            with file_lock:
                with open("data.txt", 'a', encoding='utf-8') as f:
                    f.write(log_entry)

    except Exception as e:
        print(f"Lỗi khi xử lý client {addr}: {e}")

    finally:
        # 4. Xóa client khỏi danh sách và đóng kết nối
        with client_list_lock:
            if conn in connected_clients:
                connected_clients.remove(conn)
        conn.close()
        
        # Thông báo cho mọi người biết client đã rời đi
        leave_msg = f"[INFO] Client {addr} đã rời chat room."
        print(leave_msg)
        broadcast(leave_msg + '\n', None) # Gửi broadcast thông báo rời đi (sender=None)
        
        print(f"[INFO] Luồng xử lý {addr} đã kết thúc.")
        print(f"[INFO] Số lượng luồng đang hoạt động: {threading.active_count() - 1}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server CHAT đang lắng nghe tại {HOST}:{PORT}")
        print("[INFO] Đang chờ client kết nối...")

        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer đang tắt...")
        # Đóng tất cả kết nối client trước khi thoát
        with client_list_lock:
            for client in connected_clients:
                client.close()
    except Exception as e:
        print(f"Lỗi Server: {e}")
    finally:
        server.close()
        sys.exit()

if __name__ == "__main__":
    start_server()
