from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Chat, User
from Schemas import ChatCreate, ChatResponse
import crud

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=ChatResponse)
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db)):
    """
    Create a new chat (group or private).
    - Accepts participant_ids (list of user IDs)
    """
    if len(chat_data.participant_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 participants required")

    participants = db.query(User).filter(User.id.in_(chat_data.participant_ids)).all()
    if len(participants) != len(chat_data.participant_ids):
        raise HTTPException(status_code=404, detail="One or more users not found")

    chat = Chat(is_group=chat_data.is_group)
    chat.participants = participants
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.get("/user/{user_id}", response_model=List[ChatResponse])
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch all chats a user is participating in.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.chats


@router.post("/{chat_id}/add_user/{user_id}", response_model=ChatResponse)
def add_user_to_chat(chat_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Add a user to an existing chat.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    user = db.query(User).filter(User.id == user_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user in chat.participants:
        raise HTTPException(status_code=400, detail="User already in chat")

    chat.participants.append(user)
    db.commit()
    db.refresh(chat)
    return chat
