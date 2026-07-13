from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Role, User
from app.security import decode_access_token

bearer = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or expired token")

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user no longer exists")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


def require_admin(user: CurrentUser) -> User:
    if user.role != Role.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admin role required")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
