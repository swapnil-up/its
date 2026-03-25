from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID
from enum import Enum as PyEnum
from typing import Generic, TypeVar

T = TypeVar("T")


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
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)

class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str


class IssueCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: str
    severity: SeverityEnum = SeverityEnum.low
    assigned_to: Optional[UUID]= None 

class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    status: Optional[StatusEnum]  = None
    assigned_to: Optional[UUID] = None

class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    severity: str
    status: str
    assignee: Optional[UserResponse] = None
    creator: UserResponse
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class IssueStats(BaseModel):
    total: int
    by_status: dict[str, int]
    by_severity: dict[str, int]

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
    stats: IssueStats