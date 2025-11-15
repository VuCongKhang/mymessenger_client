# client.py (Modified for Chat/Broadcast)
import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

# Hàm chạy trong luồng riêng để nhận tin nhắn
def receive_messages(s):
    """Liên tục lắng nghe và in tin nhắn từ Server."""
    while True:
        try:
            data = s.recv(1024)
            if not data:
                print("\n[DISC] Server đã ngắt kết nối.")
                s.close()
                sys.exit()
            print(f"\n{data.decode('utf-8')}", end="") # In ra tin nhắn nhận được
            
        except OSError: # Lỗi socket khi socket bị đóng
            break
        except Exception as e:
            print(f"\nLỗi nhận tin: {e}")
            break

def start_client(client_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((HOST, PORT))
        print(f"{client_name} đã kết nối thành công!")

        # Khởi tạo luồng nhận tin nhắn
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.daemon = True # Cho phép chương trình thoát ngay cả khi luồng này đang chạy
        receive_thread.start()

        # Luồng chính để gửi tin nhắn
        while True:
            message_content = input()
            # Gửi tin nhắn đến Server
            s.sendall((f"{client_name}: {message_content}").encode('utf-8'))

    except ConnectionRefusedError:
        print(f"Lỗi: {client_name} không thể kết nối. Đảm bảo server đang chạy.")
    except EOFError:
        # Xử lý trường hợp người dùng kết thúc input (Ctrl+D/Ctrl+Z)
        pass
    finally:
        print(f"\n[{client_name}] Đóng kết nối.")
        s.close()
        sys.exit()

if __name__ == "__main__":
    name = input("chọn tên: ")
    start_client(name) 
