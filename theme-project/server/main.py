from fastapi import FastAPI, Request
import htpy as ht

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

    