from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from enum import Enum as PyEnum

class SeverityEnum(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class StatusEnum(str, PyEnum):
    new = "new"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

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
    severity: SeverityEnum = SeverityEnum.low
    assigned_to: Optional[UUID]= None 

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[SeverityEnum] = SeverityEnum.low 
    status: Optional[StatusEnum]  = None
    assigned_to: Optional[UUID] = None

class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    severity: str
    status: str
    assigned_to: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str