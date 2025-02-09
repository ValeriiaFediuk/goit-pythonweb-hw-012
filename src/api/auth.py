import json
import redis.asyncio as redis
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import (
    RequestEmail,
    Token, 
    User, 
    UserCreate, 
    UserLogin, 
    PasswordResetRequest, 
    PasswordResetConfirm
) 

from src.database.db import get_db
from src.services.auth import Hash, create_access_token, get_email_from_token, verify_reset_token
from src.services.email import send_email, send_reset_email
from src.services.users import UserService
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_cached_user(email: str):
    user_data = await redis_client.get(f"user:{email}")
    return json.loads(user_data) if user_data else None

async def cache_user(email: str, user_data: dict):
    await redis_client.setex(f"user:{email}", 3600, json.dumps(user_data))

# Реєстрація користувача
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.API_ERROR_USER_ALREADY_EXIST,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    cached_user = await get_cached_user(body.email)

    if cached_user:
        if not Hash().verify_password(body.password, cached_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.API_ERROR_WRONG_PASSWORD,
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = await create_access_token(data={"sub": cached_user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.API_ERROR_USER_NOT_AUTHORIZED,
        )

    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.API_ERROR_WRONG_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Кешуємо користувача після успішної автентифікації
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
    }
    await cache_user(user.email, user_data)

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}

@router.post("/forgot_password")
async def forgot_password(
    request: Request,
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    background_tasks.add_task(
        send_reset_email, user.email, user.username, request.base_url
    )
    return {"message": "Password reset email sent. Please check your inbox."}

@router.post("/reset_password")
async def reset_password(
    body: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    email = verify_reset_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hashed_password = Hash().get_password_hash(body.new_password)
    await user_service.update_password(email, hashed_password)
    return {"message": "Password successfully reset"}
