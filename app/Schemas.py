from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional


# ---------------------------
# User Schemas
# ---------------------------

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str  # plain password input when creating user


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_online: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_online: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---------------------------
# Chat Schemas
# ---------------------------

class ChatBase(BaseModel):
    is_group: bool = False


class ChatCreate(ChatBase):
    participant_ids: List[int]  # IDs of users to add in chat


class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    participants: List[UserResponse] = []

    class Config:
        orm_mode = True


# ---------------------------
# Chat Participant Schemas
# ---------------------------

class ChatParticipantBase(BaseModel):
    chat_id: int
    user_id: int


class ChatParticipantResponse(ChatParticipantBase):
    id: int

    class Config:
        orm_mode = True


# ---------------------------
# Message Schemas
# ---------------------------

class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int


class MessageResponse(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    timestamp: datetime
    is_read: bool
    sender: Optional[UserResponse] = None

    class Config:
        orm_mode = True
