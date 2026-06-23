from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "low"
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    due_date: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    due_date: Optional[str] = None
    owner_email: str