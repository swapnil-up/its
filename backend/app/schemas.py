from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str


class IssueCreate(BaseModel):
    title: str
    description: str
    severity: Optional[str]
    status: Optional[str]
    assigned_to: Optional[str]

class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    severity: str
    status: str
    assigned_to: str
    created_by: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str