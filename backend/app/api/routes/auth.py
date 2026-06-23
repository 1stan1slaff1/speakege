from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.guest import GUEST_ID_COOKIE_NAME
from app.database import get_db
from app.models.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from app.models.tables import User
from app.services.auth import create_token, decode_token, hash_password, verify_password
from app.submissions import attach_guest_attempts_to_user

router = APIRouter(prefix="/auth", tags=["auth"])


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email(email: str) -> str:
    normalized = normalize_email(email)
    if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=400, detail="Введите корректный email.")
    return normalized


def user_to_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, created_at=user.created_at)


def get_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    return token


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = get_bearer_token(authorization)
    user_id = decode_token(token)
    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_optional_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization:
        return None
    return get_current_user(authorization=authorization, db=db)


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    email = validate_email(payload.email)

    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    guest_id = request.cookies.get(GUEST_ID_COOKIE_NAME)
    if guest_id:
        attach_guest_attempts_to_user(db, guest_id=guest_id, user_id=user.id)

    return TokenResponse(access_token=create_token(user.id))


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    user = db.scalar(select(User).where(User.email == email))

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт отключён.")

    return TokenResponse(access_token=create_token(user.id))


@router.get("/user", response_model=UserResponse)
async def get_user(current_user: User = Depends(get_current_user)):
    return user_to_response(current_user)
