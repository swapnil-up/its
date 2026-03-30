from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
import uuid

from ..database import get_db
from ..models import Issue
from ..schemas import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    PaginatedResponse,
    SeverityEnum,
    StatusEnum,
)
from ..core.dependencies import get_current_user
from ..models import User
import math

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("/", response_model=IssueResponse, status_code=201)
def create_issue(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = Issue(**payload.model_dump(), created_by=current_user.id)
    db.add(issue)
    db.commit()
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.creator), joinedload(Issue.assignee))
        .filter(Issue.id == issue.id)
        .first()
    )
    return issue


@router.get("/", response_model=PaginatedResponse[IssueResponse])
def list_issues(
    status: Optional[StatusEnum] = Query(None),
    severity: Optional[SeverityEnum] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).options(
        joinedload(Issue.creator), joinedload(Issue.assignee)
    )
    if status:
        issue = issue.filter(Issue.status == status)
    if severity:
        issue = issue.filter(Issue.severity == severity)
    if search:
        issue = issue.filter(Issue.title.ilike(f"%{search}%"))
    total = issue.count()
    status_counts = (
        db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
    )
    severity_counts = (
        db.query(Issue.severity, func.count(Issue.id)).group_by(Issue.severity).all()
    )
    stats_data = {
        "total": total,
        "by_status": {s.value: count for s, count in status_counts},
        "by_severity": {sev.value: count for sev, count in severity_counts},
    }
    items = (
        issue.order_by(Issue.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    pages = math.ceil(total / size) if total > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "stats": stats_data,
    }


@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found."
        )
    return issue


@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: uuid.UUID,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found."
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)
    db.commit()
    return (
        db.query(Issue)
        .options(joinedload(Issue.creator), joinedload(Issue.assignee))
        .filter(Issue.id == issue_id)
        .first()
    )


@router.delete("/{issue_id}", status_code=204)
def delete_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found."
        )
    if current_user.id != issue.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You aren't allowed to delete if you didn't create",
        )
    db.delete(issue)
    db.commit()
    return None
