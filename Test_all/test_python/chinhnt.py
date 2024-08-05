import socket

def start_client(host, port):
    # Tạo socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f'Đã kết nối tới server {host}:{port}')
    
    try:
        while True:
            message = input('Nhập tin nhắn: ')
            client_socket.send(message.encode('utf-8'))
            if message.lower() == 'exit':
                break
    finally:
        client_socket.close()

start_client('192.168.31.6', 12345)