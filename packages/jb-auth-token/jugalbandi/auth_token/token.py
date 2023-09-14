from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, ValidationError
from jose import JWTError, jwt
from .token_settings import get_token_settings

# from jugalbandi.core import BusinessException


class TokenData(BaseModel):
    username: str | None = None


class AuthTokenExpired(Exception):
    pass


class AuthTokenDecodeError(Exception):
    pass


def create_access_token(data: dict, expires_delta: Optional[float] = None) -> str:
    to_encode = data.copy()
    settings = get_token_settings()
    if expires_delta is not None:
        expires_delta = float(datetime.utcnow().timestamp()) + expires_delta
    else:
        expires_delta = (
            datetime.utcnow().timestamp()
            + timedelta(
                minutes=settings.token_refresh_token_expire_minutes
            ).total_seconds()
        )
    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(
        to_encode, settings.token_jwt_secret_key, settings.token_algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[float] = None) -> str:
    to_encode = data.copy()
    settings = get_token_settings()
    if expires_delta is not None:
        expires_delta = float(datetime.utcnow().timestamp()) + expires_delta
    else:
        expires_delta = (
            datetime.utcnow().timestamp()
            + timedelta(
                minutes=settings.token_refresh_token_expire_minutes
            ).total_seconds()
        )

    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(
        to_encode, settings.token_jwt_secret_refresh_key, settings.token_algorithm
    )
    return encoded_jwt


def decode_token(token: str):
    try:
        settings = get_token_settings()
        payload = jwt.decode(
            token, settings.token_jwt_secret_key, algorithms=[settings.token_algorithm]
        )
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise AuthTokenExpired()
            # TODO: handle in service
            # raise HTTPException(
            #     status_code=status.HTTP_401_UNAUTHORIZED,
            #     detail="Token expired",
            #     headers={"WWW-Authenticate": "Bearer"},
            # )
        return payload["sub"]
    except (JWTError, ValidationError) as exc:
        raise AuthTokenDecodeError from exc
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Could not validate credentials",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )


def decode_refresh_token(token: str):
    try:
        settings = get_token_settings()
        payload = jwt.decode(
            token,
            settings.token_jwt_secret_refresh_key,
            algorithms=[settings.token_algorithm],
        )
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise AuthTokenExpired()
            # TODO: handle in service
            # raise HTTPException(
            #     status_code=status.HTTP_401_UNAUTHORIZED,
            #     detail="Token expired",
            #     headers={"WWW-Authenticate": "Bearer"},
            # )
        return payload["sub"]
    except (JWTError, ValidationError) as exc:
        raise AuthTokenDecodeError from exc
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Could not validate credentials",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
