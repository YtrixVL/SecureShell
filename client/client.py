import socket
import threading
import time
import uuid

# --- Клиентская сторона ---
# Роль клиента — отправлять и получать сообщения, используя общий секрет.

SERVER_HOST = '64.188.68.161'
SERVER_PORT = 65432

def listen_for_messages(secret):
    # Клиент постоянно проверяет "очереди" на сервере
    # (в этом примере мы используем in-memory словарь)
    while True:
        # Эту часть кода нужно было бы написать на сервере в реальном приложении.
        # Здесь она находится для демонстрации механики.
        global message_queues, queue_lock
        with queue_lock:
            if secret in message_queues and message_queues[secret]:
                encrypted_message = message_queues[secret].pop(0)
                # В реальном приложении вы бы расшифровали сообщение здесь
                print(f"Клиент: Получено сообщение для секрета {secret}: {encrypted_message.decode('utf-8')}")

        time.sleep(1) # Проверяем наличие сообщений каждую секунду

def start_client():
    my_secret = input("Введите ваш секретный ключ (или нажмите Enter, чтобы сгенерировать новый): ")
    if not my_secret:
        my_secret = str(uuid.uuid4())[:8]
        print(f"Сгенерирован новый секрет: {my_secret}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(my_secret.encode('utf-8'))
            print(f"Клиент: Подключён к серверу с секретом: {my_secret}")

            # Запускаем поток для прослушивания входящих сообщений
            listen_thread = threading.Thread(target=listen_for_messages, args=(my_secret,))
            listen_thread.daemon = True
            listen_thread.start()

            while True:
                user_input = input("")
                if user_input.lower() == 'exit':
                    break

                # Шифруем сообщение перед отправкой (здесь это простая кодировка)
                encrypted_message = user_input.encode('utf-8')
                s.sendall(encrypted_message)

        except ConnectionRefusedError:
            print("Клиент: Ошибка! Не удалось подключиться к серверу.")
        except Exception as e:
            print(f"Клиент: Произошла ошибка: {e}")

if __name__ == "__main__":
    start_client()