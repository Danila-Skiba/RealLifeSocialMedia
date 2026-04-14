from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import htpy as ht
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="client/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    accept_header = request.headers.get("Accept", "")
    if 'text/html' in accept_header:
        html = ht.html[
            ht.body[
                ht.h1["Была выбрана тема Социальная сеть"], 
                ht.h2(id="connection-status"),
                ht.p(id="send-message"),
                ht.p(id="message-area"),
                ht.button(
                    id="send-btn", 
                    disabled=True
                )["Отправить сообщение"],
                ht.script(src="/static/client.js")
            ],
        ]
        return ht.render_node(html)
    else:
        return {'Error: Accept: text/html not found in headers'}
    
# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8001)