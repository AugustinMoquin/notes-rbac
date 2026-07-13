from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DB
from app.models import Role, Tenant, User
from app.schemas import LoginRequest, SignupRequest, Token, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: DB):
    """Create a new tenant and its first (admin) user."""
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")

    tenant = Tenant(name=body.org_name)
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=body.email,
        password_hash=hash_password(body.password),
        role=Role.admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.tenant_id, user.role.value)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: DB):
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")

    token = create_access_token(user.id, user.tenant_id, user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user
