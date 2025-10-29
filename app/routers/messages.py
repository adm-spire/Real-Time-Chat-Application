from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Message, Chat, User
from Schemas import MessageCreate, MessageResponse

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageResponse)
def send_message(message_data: MessageCreate, db: Session = Depends(get_db)):
    """
    Send a new message in a chat.
    """
    chat = db.query(Chat).filter(Chat.id == message_data.chat_id).first()
    sender = db.query(User).filter(User.id == message_data.sender_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    if sender not in chat.participants:
        raise HTTPException(status_code=403, detail="Sender not in chat")

    message = Message(
        chat_id=message_data.chat_id,
        sender_id=message_data.sender_id,
        content=message_data.content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/chat/{chat_id}", response_model=List[MessageResponse])
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    """
    Get all messages in a chat.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat.messages
