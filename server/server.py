import asyncio
import datetime
import logging
import re
import socket

# Настройка логирования
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '64.188.68.161'  # Используем localhost для асинхронного сервера
PORT = 65432
connections = {}  # Словарь для хранения подключенных клиентов по их адресам
lock = asyncio.Lock()

def is_safe_message(message):
    unsafe_patterns = re.compile(r'[\x00-\x1F;&|`$(){}<>\\]')
    return not unsafe_patterns.search(message)

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f"Подключен новый клиент: {addr}")
    
    with await lock:
        connections[addr] = writer

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            
            if not is_safe_message(message):
                logging.warning(f"Попытка инъекции команды от {addr}: {message}")
                writer.write("Ваше сообщение содержит запрещенные символы.".encode('utf-8'))
                await writer.drain()
                continue
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {addr[0]}:{addr[1]}: {message}"
            
            print(formatted_message)
            logging.info(formatted_message)
            
            # Пересылаем сообщение всем, кроме отправителя
            with await lock:
                for client_addr, client_writer in connections.items():
                    if client_addr != addr:
                        try:
                            client_writer.write(formatted_message.encode('utf-8'))
                            await client_writer.drain()
                        except (ConnectionResetError, BrokenPipeError):
                            logging.error(f"Ошибка при отправке сообщения клиенту {client_addr}")

    except (ConnectionResetError, asyncio.exceptions.IncompleteReadError):
        pass
    finally:
        with await lock:
            if addr in connections:
                del connections[addr]
            logging.info(f"Клиент {addr} отключился.")
        writer.close()
        await writer.wait_closed()

async def run_server():
    server = await asyncio.start_server(handle_client, HOST, PORT, family=socket.AF_INET)
    
    addr = server.sockets[0].getsockname()
    print(f"Сервер чата запущен на {addr}")
    logging.info("Сервер чата запущен.")
    print("Ожидаем подключения клиентов...")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(run_server())