from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from app.database import get_db
from fastapi.responses import Response
from app.models.lecture import Session, Fragment
from sqlalchemy.orm import Session as DBSession
from app.config import settings
from app.services.gigachat import send_photo, compile_fragments
import uuid
from datetime import datetime
import httpx

router = APIRouter(prefix="/lectures", tags=["lectures"])

def get_user_id(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен не передан")

    try:
        response = httpx.get(
            f"{settings.AUTH_SERVICE_URL}/auth/validate",
            headers={"Authorization": authorization},
            timeout = 5
        )
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=403, detail="Auth сервис не доступен")
    
    if not data.get("valid"):
        raise HTTPException(status_code=403, detail="Токен недействителен")

    return data["user_id"]
    


@router.post("/session")
def create_session(
    subject: str,
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
    ):
    user_id = get_user_id(authorization)

    session = Session(
        user_id=uuid.UUID(user_id),
        subject = subject
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": str(session.id),
        "subject": session.subject,
        "created_at": session.created_at
    }

@router.post("/session/{session_id}/data")
def load_photo(
    session_id: str,
    comment: str,
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
):
    user_id = get_user_id(authorization)
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != user_id:
        raise HTTPException(status_code=403, detail="You are not owner of this session")
    
    image_bytes = file.file.read()
    if len(image_bytes) > 15* 1024**2:
        raise HTTPException(status_code=400, detail="Image size must be less than 15MB")

    try:
        md_text, gigachat_image_id = send_photo(image_bytes, file.filename or "image.jpg", comment)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send photo to Gigachat")

    last_fragment = db.query(Fragment).filter_by(session_id = session_id).order_by(Fragment.index.desc()).first()
    index = (last_fragment.index + 1) if last_fragment else 1

    fragment = Fragment(
        session_id = uuid.UUID(session_id),
        index = index,
        markdown_text = md_text,
        gigachat_file_id = gigachat_image_id,
    )

    db.add(fragment)

    db.commit()

    return {
        "fragment_index": index, 
        "md_text": md_text
    }

@router.post("/session/{session_id}/compile")
def compile(
    session_id: str,
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
):
    
    user_id = get_user_id(authorization)
    
    session = db.query(Session).filter_by(id=session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != user_id:
        raise HTTPException(status_code=403, detail="You are not owner of this session")
    
    fragments = db.query(Fragment).filter_by(session_id=session_id).order_by(Fragment.index).all()

    if not fragments:
        raise HTTPException(status_code=404, detail="No fragments found")
    md_content = compile_fragments([frag.markdown_text for frag in fragments], session.subject)

    session.md_content = md_content

    session.compiled_at = datetime.now() 

    db.query(Fragment).filter_by(session_id=session_id).delete()
    db.commit()

    return Response(content=md_content, media_type="text/markdown", headers={'Content-Disposition': f'attachment; filename="{session.subject}-{session.compiled_at}lecture.md"'} )
    

@router.get("/lectures")
def get_lectures(
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
):
    user_id = get_user_id(authorization)
    sessions = db.query(Session).filter_by(user_id=uuid.UUID(user_id)).order_by(Session.created_at.desc()).all()

    return [
        {
            "session_id": str(s.id),
            "subject": s.subject,
            "created_at": s.created_at,
            "compiled_at": s.compiled_at,
            "is_compiled": s.compiled_at is not None,
        }
        for s in sessions
    ]



@router.get("/session/{session_id}")
def get_session(
    session_id: str,
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
):
    user_id = get_user_id(authorization)

    session = db.query(Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != user_id:
        raise HTTPException(status_code=403, detail="You are not owner of this session")

    return {
        "session_id": str(session.id),
        "subject": session.subject,
        "created_at": session.created_at,
        "compiled_at": session.compiled_at,
        "is_compiled": session.compiled_at is not None,
        'md_content': session.md_content 
    }
    
    

@router.delete("/session/{session_id}")
def delete_session(
    session_id: str,
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
):
    user_id = get_user_id(authorization)

    session = db.query(Session).filter_by(id = session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != user_id:
        raise HTTPException(status_code=403, detail="You are not owner of this session")
    
    db.query(Fragment).filter_by(session_id=session_id).delete()

    db.delete(session)
    db.commit()


    

