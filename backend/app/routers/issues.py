import math
import traceback
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..core.dependencies import get_current_user
from ..database import get_db
from ..models import Attachment, Issue, User
from ..schemas import (
    IssueCreate,
    IssueResponse,
    IssueUpdate,
    PaginatedResponse,
    SeverityEnum,
    StatusEnum,
)
from ..storage import get_presigned_url
from ..websocket_manager import manager

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("/", response_model=IssueResponse, status_code=201)
async def create_issue(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = Issue(**payload.model_dump(), created_by=current_user.id)
    db.add(issue)
    db.commit()
    await manager.broadcast("dashboard", {"type": "issue_created", "issue_id": str(issue.id)})
    issue = (
        db.query(Issue)
        .options(joinedload(Issue.creator), joinedload(Issue.assignee))
        .filter(Issue.id == issue.id)
        .first()
    )
    return issue


@router.get("/", response_model=PaginatedResponse[IssueResponse])
def list_issues(
    status: StatusEnum | None = Query(None),
    severity: SeverityEnum | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).options(
        joinedload(Issue.creator),
        joinedload(Issue.assignee),
        joinedload(Issue.attachments).joinedload(Attachment.uploader),
    )
    if status:
        issue = issue.filter(Issue.status == status)
    if severity:
        issue = issue.filter(Issue.severity == severity)
    if search:
        issue = issue.filter(Issue.title.ilike(f"%{search}%"))
    total = issue.count()
    status_counts = db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
    severity_counts = db.query(Issue.severity, func.count(Issue.id)).group_by(Issue.severity).all()
    stats_data = {
        "total": total,
        "by_status": {s.value: count for s, count in status_counts},
        "by_severity": {sev.value: count for sev, count in severity_counts},
    }
    items = issue.order_by(Issue.created_at.desc()).offset((page - 1) * size).limit(size).all()
    try:
        attached_items = []
        for issue in items:
            issue_pydantic = IssueResponse.model_validate(issue)
            for attachment in issue_pydantic.attachments:
                attachment.url = get_presigned_url(attachment.object_key)
            attached_items.append(issue_pydantic)

    except Exception as e:
        print("--- DEBUG ERROR ---")
        print(traceback.format_exc())  # This will show exactly which field failed
        raise HTTPException(status_code=500, detail=str(e))

    pages = math.ceil(total / size) if total > 0 else 0
    return {
        "items": attached_items,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")

    response_data = IssueResponse.model_validate(issue)
    for attachment in response_data.attachments:
        attachment.url = get_presigned_url(attachment.object_key)

    return response_data


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: uuid.UUID,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)
    db.commit()
    await manager.broadcast("dashboard", {"type": "issue_created", "issue_id": str(issue_id)})
    return (
        db.query(Issue)
        .options(joinedload(Issue.creator), joinedload(Issue.assignee))
        .filter(Issue.id == issue_id)
        .first()
    )


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")
    if current_user.id != issue.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You aren't allowed to delete if you didn't create",
        )
    db.delete(issue)
    db.commit()
    await manager.broadcast("dashboard", {"type": "issue_created", "issue_id": str(issue_id)})
    return None
