import socket
import threading
import sys
import os

HOST = '64.188.68.161'
PORT = 65432

# Глобальная переменная для хранения текущего ввода
current_input = ""
input_lock = threading.Lock()

def receive_messages(s):
    """Поток для приёма сообщений от сервера."""
    global current_input
    while True:
        try:
            data = s.recv(1024)
            if not data:
                print("\nСервер отключен.")
                break
            
            message = data.decode('utf-8')
            
            with input_lock:
                # Очистка текущей строки ввода
                sys.stdout.write('\r' + ' ' * (len(current_input) + 3) + '\r')
                
                # Вывод нового сообщения от сервера
                sys.stdout.write(f"{message}\n")
                
                # Восстановление приглашения и текущего ввода
                sys.stdout.write(f">> {current_input}")
                sys.stdout.flush()
        
        except (ConnectionResetError, BrokenPipeError):
            print("\nСоединение с сервером потеряно.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            break

    s.close()
    os._exit(0) # Завершает программу

def run_client():
    global current_input
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("Подключен к чату. Начните общение.")
            print("Чтобы выйти, введите 'exit'.")

            receive_thread = threading.Thread(target=receive_messages, args=(s,))
            receive_thread.daemon = True
            receive_thread.start()

            while True:
                with input_lock:
                    current_input = ""
                
                sys.stdout.write(">> ")
                sys.stdout.flush()

                # Чтение ввода посимвольно для обновления current_input
                while True:
                    char = sys.stdin.read(1)
                    with input_lock:
                        if char == '\n':
                            break
                        if char == '\x7f': # Backspace
                            current_input = current_input[:-1]
                            sys.stdout.write('\r' + ' ' * (len(current_input) + 3) + '\r')
                            sys.stdout.write(f">> {current_input}")
                            sys.stdout.flush()
                        else:
                            current_input += char
                            sys.stdout.write(char)
                            sys.stdout.flush()

                message_to_send = current_input.strip()

                if message_to_send.lower() == 'exit':
                    break
                s.sendall(message_to_send.encode('utf-8'))

        except ConnectionRefusedError:
            print("Ошибка: Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")

        finally:
            print("Отключение от чата.")
            s.close()

if __name__ == "__main__":
    run_client()