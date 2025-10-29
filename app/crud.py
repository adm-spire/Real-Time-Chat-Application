from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import models, Schemas


# ---------------------------
# USER CRUD
# ---------------------------

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: Schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: Schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


# ---------------------------
# CHAT CRUD
# ---------------------------

def create_chat(db: Session, chat: Schemas.ChatCreate) -> models.Chat:
    new_chat = models.Chat(is_group=chat.is_group)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    # Add participants
    for user_id in chat.participant_ids:
        participant = models.ChatParticipant(chat_id=new_chat.id, user_id=user_id)
        db.add(participant)
    db.commit()

    db.refresh(new_chat)
    return new_chat


def get_chat_by_id(db: Session, chat_id: int) -> Optional[models.Chat]:
    return db.query(models.Chat).filter(models.Chat.id == chat_id).first()


def get_user_chats(db: Session, user_id: int) -> List[models.Chat]:
    return (
        db.query(models.Chat)
        .join(models.ChatParticipant)
        .filter(models.ChatParticipant.user_id == user_id)
        .all()
    )


def delete_chat(db: Session, chat_id: int) -> bool:
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        return False
    db.delete(chat)
    db.commit()
    return True


# ---------------------------
# MESSAGE CRUD
# ---------------------------

def create_message(db: Session, message: Schemas.MessageCreate) -> models.Message:
    new_message = models.Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content,
        timestamp=datetime.utcnow(),
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def get_messages_by_chat(db: Session, chat_id: int) -> List[models.Message]:
    return (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat_id)
        .order_by(models.Message.timestamp)
        .all()
    )


def mark_message_as_read(db: Session, message_id: int) -> Optional[models.Message]:
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if msg:
        msg.is_read = True
        db.commit()
        db.refresh(msg)
    return msg


def delete_message(db: Session, message_id: int) -> bool:
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        return False
    db.delete(msg)
    db.commit()
    return True


# ---------------------------
# CHAT PARTICIPANTS
# ---------------------------

def add_participant_to_chat(db: Session, chat_id: int, user_id: int) -> models.ChatParticipant:
    participant = models.ChatParticipant(chat_id=chat_id, user_id=user_id)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def remove_participant_from_chat(db: Session, chat_id: int, user_id: int) -> bool:
    participant = (
        db.query(models.ChatParticipant)
        .filter(
            models.ChatParticipant.chat_id == chat_id,
            models.ChatParticipant.user_id == user_id,
        )
        .first()
    )
    if not participant:
        return False
    db.delete(participant)
    db.commit()
    return True
