import websockets, asyncio, random


messages = ['Классная тема!', 'Интересная тема!','Ты генийЙ!']

async def main():
    uri = "ws://127.0.0.1:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print('Подключён к Websocket сервису')

            get_messages = asyncio.create_task(recieve_message(websocket))

            await asyncio.sleep(7)
            for _ in range(5):
                mess = random.choice(messages)
                await websocket.send(mess)
                print(f'''Отправлено: {mess}''')
                await asyncio.sleep(10)

            get_messages.cancel()

    except Exception as e:
        print('Ошибка ', e)

async def recieve_message(websocket):
    while True:
        message = await websocket.recv()
        print("Получено: ", message)

if __name__ == "__main__":
    asyncio.run(main())



