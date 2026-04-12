from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
import htpy as ht
from websocket_service import connection

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    accept_header = request.headers.get("Accept", "")
    
    if 'text/html' in accept_header:
        link = ht.a(href="http://127.0.0.1:8001")["Перейти к клиентскому серверу"]
        html = ht.html[
            ht.body[
                ht.h1["Социальная сеть"],
                ht.p[link]
            ]
        ]
        return ht.render_node(html)
    else:
        return {'error': 'Accept: text/html not found in headers'}

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await connection(websocket)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)