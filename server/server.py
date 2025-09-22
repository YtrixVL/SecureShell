import socket
import threading
import uuid

# --- Серверная сторона ---
# Роль сервера — принимать сообщения и ретранслировать их клиентам с тем же секретом.

SERVER_HOST = '64.188.68.161'
SERVER_PORT = 65432

# Временное хранилище для сообщений.
# В реальном приложении это будет система очередей, например, RabbitMQ.
message_queues = {}
queue_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"Сервер: Новый клиент подключился с адреса {addr}")
    try:
        # Первым делом клиент отправляет свой уникальный секрет (адрес доставки)
        secret = conn.recv(32).decode('utf-8')
        if not secret:
            return

        print(f"Сервер: Получен секрет от {addr}: {secret}")

        with queue_lock:
            # Создаем очередь для этого секрета, если её ещё нет
            if secret not in message_queues:
                message_queues[secret] = []

        # Теперь работаем с сообщениями от этого клиента
        while True:
            data = conn.recv(1024)
            if not data:
                break

            # Сервер получает зашифрованное сообщение (на самом деле просто байты)
            encrypted_message = data
            print(f"Сервер: Получено зашифрованное сообщение от {addr}")

            # Сервер добавляет сообщение в очередь для этого секрета
            with queue_lock:
                message_queues[secret].append(encrypted_message)

    except Exception as e:
        print(f"Сервер: Соединение с {addr} разорвано. Ошибка: {e}")
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen()
        print(f"Сервер слушает на {SERVER_HOST}:{SERVER_PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    start_server()