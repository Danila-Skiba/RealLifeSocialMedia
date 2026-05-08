from fastapi import FastAPI
from app.routers import schedule


app = FastAPI(
    title='Schedule Service',
    description='Сервис Расписания',
)

app.include_router(schedule.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "schedule-service"}

