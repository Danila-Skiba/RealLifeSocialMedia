from fastapi import FastAPI
from app.routers import lecture

app = FastAPI(
    title='Lecturer service',
    description='Сервис конспектирования'
)

app.include_router(lecture.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "lecture-service"}

