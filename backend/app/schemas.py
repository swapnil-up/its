from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserReponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: str
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
    id: str
    title: str
    description: str
    severity: str
    status: str
    assigned_to: str
    created_by: str
    created_at: datetime