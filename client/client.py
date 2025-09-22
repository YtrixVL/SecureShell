import socket
import threading
import uuid
import sys
import time

SERVER_HOST = '64.188.68.161'
SERVER_PORT = 65432

def listen_for_messages(s):
    """Отдельный поток для прослушивания сообщений, отправленных сервером."""
    try:
        while True:
            data = s.recv(1024)
            if not data:
                break
            # В реальном приложении вы бы расшифровали сообщение здесь
            print(f"Получено сообщение: {data.decode('utf-8')}")
    except Exception as e:
        print(f"Соединение с сервером потеряно. Ошибка: {e}")
    finally:
        s.close()
        print("Соединение закрыто.")
        sys.exit()

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

            # Запускаем поток для прослушивания сообщений
            listen_thread = threading.Thread(target=listen_for_messages, args=(s,))
            listen_thread.daemon = True
            listen_thread.start()

            while True:
                user_input = input("")
                if user_input.lower() == 'exit':
                    break

                # Шифруем сообщение (здесь это просто кодировка)
                encrypted_message = user_input.encode('utf-8')
                s.sendall(encrypted_message)

        except ConnectionRefusedError:
            print("Клиент: Ошибка! Не удалось подключиться к серверу.")
        except Exception as e:
            print(f"Клиент: Произошла ошибка: {e}")

if __name__ == "__main__":
    start_client()