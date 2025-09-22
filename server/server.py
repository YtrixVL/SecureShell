import socket
import threading
import datetime

# Хост и порт для сервера
HOST = '64.188.68.161'
PORT = 65432
connections = []
lock = threading.Lock()

def handle_client(conn, addr):
    print(f"Подключен новый клиент: {addr}")
    with lock:
        connections.append(conn)

    try:
        while True:
            # Получаем данные от клиента
            data = conn.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Формируем сообщение для вывода и пересылки
            formatted_message = f"[{timestamp}] {addr[0]}:{addr[1]}: {message}"
            print(formatted_message)
            
            # Пересылаем сообщение всем, кроме отправителя
            with lock:
                for client_conn in connections:
                    if client_conn != conn:
                        try:
                            client_conn.sendall(formatted_message.encode('utf-8'))
                        except (ConnectionResetError, BrokenPipeError):
                            continue
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        with lock:
            connections.remove(conn)
            print(f"Клиент {addr} отключился.")
        conn.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Сервер чата запущен на {HOST}:{PORT}")
        print("Ожидаем подключения клиентов...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    run_server()