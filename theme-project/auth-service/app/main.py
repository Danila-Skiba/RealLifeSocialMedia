from fastapi import FastAPI
from app.routers import auth


app = FastAPI(
    title='Auth Service',
    description='Сервис Авторизации',
)

app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

