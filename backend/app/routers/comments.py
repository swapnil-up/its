from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
import uuid

from ..database import get_db
from ..models import Comment, Issue, User
from ..schemas import CommentCreate, CommentUpdate, CommentResponse, PaginatedComments
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/issues/{issue_id}/comments", tags=["comments"])

def get_issue_or_404(issue_id: uuid.UUID, db: Session)->Issue: 
    issue = db.query(Issue).filter(Issue.id==issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.get("/", response_model=PaginatedComments)
def list_comments(issue_id: uuid.UUID, limit: int=Query(20, ge=1, le=100), offset: int=Query(0, ge=0), db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    get_issue_or_404(issue_id, db)
    comments = db.query(Comment).options(joinedload(Comment.commenter), joinedload(Comment.issue))
    items = (comments.filter(Comment.issue_id==issue_id).order_by(Comment.created_at.asc()).offset(offset).limit(limit).all())
    total= comments.filter(Comment.issue_id==issue_id).count()
    return{
        "items": items, "total": total, "limit": limit, "offset": offset
    }

@router.post("/", response_model = CommentResponse, status_code=201)
def create_comment(issue_id: uuid.UUID, payload: CommentCreate, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    get_issue_or_404(issue_id, db)
    comment = Comment(**payload.model_dump(), author_id=current_user.id, issue_id=issue_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment( issue_id: uuid.UUID, comment_id: uuid.UUID, payload: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id==comment_id).filter(Issue.id==issue_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found."
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return(db.query(Comment).options(joinedload(Comment.commenter), joinedload(Comment.issue)).filter(Comment.id==comment_id).first())

@router.delete("/{comment_id}", status_code=204)
def delete_comment( issue_id: uuid.UUID, comment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    issue = db.query(Issue).filter(Issue.id==issue_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found."
        )
    if current_user.id != comment.author_id and current_user.id != issue.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You aren't allowed to delete if you didn't create",
        )
    db.delete(comment)
    db.commit()
    return None
