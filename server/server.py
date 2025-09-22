import socket
import threading
import uuid
import time

SERVER_HOST = '64.188.68.161'
SERVER_PORT = 65432

# Словарь для хранения сокетов клиентов по их секретному ключу
# {secret: socket}
client_sockets = {}
socket_lock = threading.Lock()

# Очередь для сообщений, которые нужно отправить клиентам
# {secret: [message1, message2, ...]}
message_queues = {}
queue_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"Сервер: Новый клиент подключился с адреса {addr}")
    secret = None
    try:
        # Первым делом клиент отправляет свой секрет
        secret = conn.recv(32).decode('utf-8')
        if not secret:
            return

        print(f"Сервер: Получен секрет от {addr}: {secret}")
        
        # Сохраняем сокет клиента для последующей отправки
        with socket_lock:
            client_sockets[secret] = conn

        while True:
            # Получаем сообщение от клиента
            data = conn.recv(1024)
            if not data:
                break
            
            encrypted_message = data
            print(f"Сервер: Получено зашифрованное сообщение от {addr}")
            
            # Помещаем сообщение в очередь для всех клиентов с этим секретом
            with queue_lock:
                if secret not in message_queues:
                    message_queues[secret] = []
                message_queues[secret].append(encrypted_message)

    except Exception as e:
        print(f"Сервер: Соединение с {addr} разорвано. Ошибка: {e}")
    finally:
        if secret in client_sockets:
            with socket_lock:
                del client_sockets[secret]
        conn.close()

def send_queued_messages():
    """Отдельный поток для отправки сообщений из очередей."""
    while True:
        with queue_lock:
            for secret, messages in message_queues.items():
                while messages:
                    message = messages.pop(0)
                    with socket_lock:
                        if secret in client_sockets:
                            try:
                                client_sockets[secret].sendall(message)
                            except Exception as e:
                                print(f"Сервер: Ошибка отправки сообщения клиенту с секретом {secret}: {e}")
        time.sleep(0.5)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen()
        print(f"Сервер слушает на {SERVER_HOST}:{SERVER_PORT}")
        
        # Запускаем поток для отправки сообщений из очередей
        sender_thread = threading.Thread(target=send_queued_messages)
        sender_thread.daemon = True
        sender_thread.start()

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    start_server()