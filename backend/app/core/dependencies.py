from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from ..database import get_db
from ..models import User
from .security import decode_token

bearer_scheme = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
        db: Session = Depends(get_db)
) -> User:
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},)
    try:
        token= credentials.credentials
        payload=decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
        user = db.query(User).filter(User.id==user_id).first()
        if user is None:
            raise credential_exception
        return user
    except JWTError:
        raise credential_exception
    
