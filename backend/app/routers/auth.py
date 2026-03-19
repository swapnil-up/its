from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token, LoginRequest
from ..core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == user_data.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists", headers={"WWW-Authenticate": "Bearer"})
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, response: Response, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == credentials.email).first()
    if not exists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized", headers={"WWW-Authenticate": "Bearer"})
    password = verify_password(credentials.password, exists.hashed_password)
    if not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized", headers={"WWW-Authenticate": "Bearer"})
    access = create_access_token({"sub": str(exists.id)})
    refresh = create_refresh_token({"sub": str(exists.id)})
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=60*60*24*7)
    return Token(access_token=access, token_type="bearer")


@router.post("/refresh", response_model=Token)
def refresh(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email Not Found", headers={"WWW-Authenticate": "Bearer"})
    user_id=decode_token(token).get("sub")
    user = db.query(User).filter(User.id==user_id).first()
    if user:
        access = create_access_token({"sub": str(user.id)})
        return Token(access_token=access, token_type="bearer")

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "logged out"}

