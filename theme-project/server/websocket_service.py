from fastapi import WebSocket, WebSocketDisconnect
import asyncio, random


async def connection(websocket: WebSocket):
    await websocket.accept()

    send_task = asyncio.create_task(message(websocket))
    try:
        messages = []
        while True:
            data = await websocket.receive_text()

            if data not in messages:
                messages.append(data)
                await websocket.send_text('Да? Хорошо. Спасибо за поддержку!')
    except WebSocketDisconnect:
        send_task.cancel()


async def message(websocket: WebSocket):
    try:
        while True:
            await asyncio.sleep(random.uniform(2,5))
            
            if random.random() < 0.65:
                message = "Это лучшая тема, что есть. Хотя..."
            else:
                message = "Надо менять тему..."
            await websocket.send_text(message)
    except Exception as e:
        print(f"Ошибка {e}")
