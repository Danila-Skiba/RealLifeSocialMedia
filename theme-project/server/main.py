from fastapi import FastAPI, Request,WebSocket
import htpy as ht
from .websocket_service import connection

app = FastAPI()

@app.get("/")
async def root(request: Request):
    accept_header = request.headers.get("Accept")

    if  'text/html' in accept_header:
        html  = ht.html[
            ht.body[ht.h1["Социальная сеть"]]
        ],
        return ht.render_node(html)

    else:
        return {'Error: Accept: text/html not found in headers'}

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await connection(websocket)


    