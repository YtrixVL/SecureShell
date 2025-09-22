import socket
import threading
import sys
import os

HOST = '64.188.68.161'
PORT = 65432

def receive_messages(s):
    """Поток для приёма сообщений от сервера."""
    while True:
        try:
            data = s.recv(1024)
            if not data:
                print("Сервер отключен.")
                break
            
            message = data.decode('utf-8')
            
            # Очистка текущей строки и вывод сообщения
            sys.stdout.write('\r' + ' ' * len(sys.stdout.readline()) + '\r')
            sys.stdout.write(f"\r{message}\n")
            
            # Перерисовка приглашения для ввода
            sys.stdout.write(">> ")
            sys.stdout.flush()
        
        except (ConnectionResetError, BrokenPipeError):
            print("Соединение с сервером потеряно.")
            break
    s.close()

def run_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("Подключен к чату. Начните общение.")
            print("Чтобы выйти, введите 'exit'.")

            receive_thread = threading.Thread(target=receive_messages, args=(s,))
            receive_thread.daemon = True
            receive_thread.start()

            while True:
                message = input(">> ") 
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))

        except ConnectionRefusedError:
            print("Ошибка: Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")

        finally:
            print("Отключение от чата.")
            s.close()

if __name__ == "__main__":
    run_client()