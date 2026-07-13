from fastapi import APIRouter, HTTPException, status

from app.deps import DB, AdminUser
from app.models import User
from app.schemas import UserCreate, UserOut
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, admin: AdminUser, db: DB):
    """Admins add users to their own tenant."""
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")

    user = User(
        tenant_id=admin.tenant_id,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserOut])
def list_users(admin: AdminUser, db: DB):
    return db.query(User).filter(User.tenant_id == admin.tenant_id).all()
