import socket
import threading
import datetime
import logging
import re

# Настройка логирования
logging.basicConfig(filename='server.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Хост и порт для сервера
HOST = '64.188.68.161'
PORT = 65432
connections = []
lock = threading.Lock()

def is_safe_message(message):
    """
    Проверяет сообщение на наличие потенциально опасных символов.
    """
    # Паттерн для поиска опасных символов, используемых в bash-инъекциях
    unsafe_patterns = re.compile(r'[;&|`$(){}<>]')
    if unsafe_patterns.search(message):
        return False
    return True

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
            
            message = data.decode('utf-8').strip()
            
            # Проверка сообщения на безопасность
            if not is_safe_message(message):
                print(f"Попытка инъекции команды от {addr}")
                conn.sendall("Ваше сообщение содержит запрещенные символы.".encode('utf-8'))
                continue
            
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
                            # Логируем ошибки
                            logging.error(f"Ошибка при отправке сообщения клиенту {client_conn.getpeername()}: {formatted_message}")
                            continue
    except (ConnectionResetError, BrokenPipeError) as e:
        # Логируем отключения и другие ошибки
        logging.error(f"Клиент {addr} отключился или произошла ошибка: {e}")
    finally:
        with lock:
            if conn in connections:
                connections.remove(conn)
            print(f"Клиент {addr} отключился.")
        conn.close()

def run_server():
    try:
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
    except Exception as e:
        logging.critical(f"Критическая ошибка сервера: {e}")

if __name__ == "__main__":
    run_server()