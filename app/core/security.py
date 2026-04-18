"""Security utilities for JWT authentication and password hashing"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import get_db as get_async_db
from app.models.user import User

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

# Password hashing context using Argon2id
# Argon2id parameters:
# - memory_cost=65536: 64 MB memory usage (OWASP recommended minimum)
# - time_cost=3: 3 iterations (balance between security and performance)
# - parallelism=4: Use 4 parallel threads (optimal for multi-core systems)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2id

    Args:
        password: Plain text password

    Returns:
        Argon2id hash of the password ($argon2id$ prefix)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an Argon2id hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Argon2id hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token

    Args:
        data: Dictionary containing claims to encode in the token.
              Must include "sub" (user_id) and "email".
        expires_delta: Optional custom expiration time.
                      Defaults to ACCESS_TOKEN_EXPIRE_HOURS from config.

    Returns:
        Encoded JWT token string

    Token Structure:
        {
            "sub": "user_uuid",     # User ID
            "email": "user@example.com",
            "exp": 1699564800,      # Expiration timestamp
            "iat": 1699561200       # Issued at timestamp
        }
    """
    to_encode = data.copy()

    # Set issued at time
    now = datetime.now(UTC)
    to_encode["iat"] = now

    # Set expiration time
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode["exp"] = expire

    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary containing the decoded token payload

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        if "expired" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token",
                headers={"WWW-Authenticate": "Bearer"},
            )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """Get the current authenticated user from JWT token

    This is a FastAPI dependency that:
    1. Extracts the JWT token from the Authorization header
    2. Validates and decodes the token
    3. Retrieves the user from the database
    4. Returns the User object for use in endpoints

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object of the authenticated user

    Raises:
        HTTPException: 401 Unauthorized if:
            - Token is invalid or expired
            - User ID not in token claims
            - User not found in database
    """
    token = credentials.credentials

    # Decode and validate token
    try:
        payload = decode_access_token(token)
    except HTTPException:
        raise

    # Extract user ID from token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate UUID format
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from database
    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def validate_calculation_ownership(
    calculation_id: uuid.UUID, current_user: User, db: AsyncSession
) -> None:
    """Validate that a user owns a calculation

    Args:
        calculation_id: UUID of the calculation to check
        current_user: The authenticated user
        db: Database session

    Raises:
        HTTPException: 403 Forbidden if user doesn't own the calculation
        HTTPException: 404 Not Found if calculation doesn't exist
    """
    from app.models.calculation import Calculation

    stmt = select(Calculation).where(Calculation.id == calculation_id)
    result = await db.execute(stmt)
    calculation = result.scalar_one_or_none()

    if calculation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")

    if calculation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - you don't own this calculation",
        )
