from fastapi import APIRouter, Depends, HTTPException, Header


from app.database import get_db
from app.models.lecture import Session, Fragment


router = APIRouter(prefix="/lectures", tags=["lectures"])

@router.post("/session")
def create_session():
    pass

@router.post("/session/{id}/data")
def load_photo():
    pass

@router.post("/session/{id}/compile")
def compile():
    pass

@router.get("/lectures")
def get_lectures():
    pass

@router.get("/session/{id}")
def get_session():
    pass

@router.get("/session/{id}")
def delete_session():
    pass

