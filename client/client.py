import asyncio
import sys
import time
import socket

HOST = '64.188.68.161'
PORT = 65432

async def receive_messages(reader):
    """Асинхронный поток для приёма сообщений от сервера."""
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print("\nСервер отключился.")
                break
            
            message = data.decode('utf-8', errors='replace')
            sys.stdout.write(f"\r{message}\n>> ")
            sys.stdout.flush()

    except asyncio.exceptions.IncompleteReadError:
        pass
    except Exception as e:
        print(f"\nПроизошла ошибка при получении сообщения: {e}")

async def send_messages(writer):
    """Асинхронный поток для отправки сообщений на сервер."""
    try:
        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            
            if user_input.lower().strip() == 'exit':
                print("Отключение от чата.")
                writer.close()
                await writer.wait_closed()
                break
            
            writer.write(user_input.encode('utf-8'))
            await writer.drain()
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

async def run_client():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print("Подключен к чату. Начните общение.")
        print("Чтобы выйти, введите 'exit'.")
        sys.stdout.write("")
        sys.stdout.flush()

        # Запускаем два асинхронных потока одновременно
        receive_task = asyncio.create_task(receive_messages(reader))
        send_task = asyncio.create_task(send_messages(writer))
        
        await asyncio.gather(receive_task, send_task)

    except ConnectionRefusedError:
        print("Ошибка: Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
    except Exception as e:
        print(f"Произошла критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(run_client())