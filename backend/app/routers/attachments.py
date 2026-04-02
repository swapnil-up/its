from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session, joinedload
import uuid

from ..database import get_db
from ..models import Attachment, Issue, User
from ..schemas import AttachmentResponse
from ..core.dependencies import get_current_user
from ..storage import upload_file, delete_file, get_presigned_url
from ..websocket_manager import manager

router = APIRouter(prefix="/issues/{issue_id}/attachments", tags=["attachments"])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
}

MAX_SIZE = 10 * 1024 * 1024


def get_issue_or_404(issue_id: uuid.UUID, db: Session) -> Issue:
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.post("/", response_model=AttachmentResponse, status_code=201)
async def upload_attachment(
    issue_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_issue_or_404(issue_id, db)
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type {file.content_type} not allowed",
        )
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File exceeds 10MB"
        )

    object_key = f"issues/{issue_id}/{uuid.uuid4()}/{file.filename}"

    upload_file(file_bytes, object_key, file.content_type)
    attachment = Attachment(
        issue_id=issue_id,
        uploader_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        size=len(file_bytes),
        object_key=object_key,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    attachment = (
        db.query(Attachment)
        .options(joinedload(Attachment.uploader))
        .filter(Attachment.id == attachment.id)
        .first()
    )

    await manager.broadcast(
        "dashboard", {"type": "issue_updated", "issue_id": str(issue_id)}
    )
    response = AttachmentResponse.model_validate(attachment)
    response.url = get_presigned_url(object_key)
    return response


@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(
    issue_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = (
        db.query(Attachment)
        .filter(Attachment.id == attachment_id, Attachment.issue_id == issue_id)
        .first()
    )
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    issue = get_issue_or_404(issue_id, db)
    if current_user.id not in (attachment.uploader_id, issue.created_by):
        raise HTTPException(status_code=403, detail="Not allowed")
    delete_file(attachment.object_key)
    db.delete(attachment)
    db.commit()
