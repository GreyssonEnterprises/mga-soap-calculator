"""Authentication endpoints for user registration and login"""
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.base import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserInfo,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
)


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserRegisterResponse:
    """Register a new user

    Args:
        request: Registration data containing email and password
        db: Database session

    Returns:
        UserRegisterResponse with user ID and success message

    Raises:
        HTTPException 400: If email is already registered
        HTTPException 422: If email format is invalid or password is too weak
    """
    # Check if user already exists
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(request.password)

    # Create new user
    new_user = User(
        email=request.email,
        hashed_password=hashed_password
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return UserRegisterResponse(
        id=new_user.id,
        email=new_user.email,
        message="User registered successfully"
    )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="Login user",
    description="Authenticate user with email and password to receive JWT token"
)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> UserLoginResponse:
    """Authenticate user and return JWT token

    Args:
        request: Login credentials (email and password)
        db: Database session

    Returns:
        UserLoginResponse with JWT access token and user info

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 422: If email format is invalid
    """
    # Find user by email
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            email=user.email
        )
    )