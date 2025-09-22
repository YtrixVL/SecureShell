import socket
import threading
import sys
import os
import time

HOST = '64.188.68.161'
PORT = 65432

print_lock = threading.Lock()
is_connected = False

def receive_messages(s):
    """Поток для приёма сообщений от сервера."""
    global is_connected
    while is_connected:
        try:
            data = s.recv(1024)
            if not data:
                with print_lock:
                    print("\nСервер отключился. Попытка переподключения...")
                is_connected = False
                break
            
            message = data.decode('utf-8')
            
            with print_lock:
                sys.stdout.write(f"\r{message}\n>> ")
                sys.stdout.flush()

        except (ConnectionResetError, BrokenPipeError):
            with print_lock:
                print("\nСоединение с сервером потеряно. Попытка переподключения...")
            is_connected = False
            break
        except Exception as e:
            with print_lock:
                print(f"\nПроизошла ошибка: {e}. Попытка переподключения...")
            is_connected = False
            break

def run_client():
    global is_connected
    
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with print_lock:
                print("Попытка подключения к серверу...")
            s.connect((HOST, PORT))
            is_connected = True
            with print_lock:
                print("Подключен к чату. Начните общение.")
                print("Чтобы выйти, введите 'exit'.")

            receive_thread = threading.Thread(target=receive_messages, args=(s,))
            receive_thread.daemon = True
            receive_thread.start()

            while is_connected:
                with print_lock:
                    user_input = input(">> ")
                
                if user_input.lower() == 'exit':
                    is_connected = False
                    break
                
                s.sendall(user_input.encode('utf-8'))

        except ConnectionRefusedError:
            with print_lock:
                print("Ошибка: Не удалось подключиться к серверу. Повторная попытка через 5 секунд...")
            time.sleep(5)
            continue
        except Exception as e:
            with print_lock:
                print(f"Критическая ошибка: {e}. Попытка переподключения...")
            is_connected = False
            s.close()
            time.sleep(5)
            continue

        finally:
            s.close()
        
        # Если is_connected стал False, выходим из внутреннего while и пытаемся переподключиться
        if not is_connected:
            with print_lock:
                print("Отключение от чата.")
            time.sleep(5) # Ждём перед попыткой переподключения
            continue
        
        break # Выход из внешнего цикла при вводе 'exit'

if __name__ == "__main__":
    run_client()