from typing import Annotated
from asyncpg import Pool
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .db import AuthRepository
from .password import get_hashed_password, verify_password
from jugalbandi.core.caching import aiocached
from jugalbandi.auth_token import create_access_token, create_refresh_token

auth_app = FastAPI()


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


@aiocached(cache={})
async def get_auth_repo() -> AuthRepository:
    auth = AuthRepository()
    return auth


@auth_app.post("/signup", summary="Create new user", tags=["Authentication"])
async def signup(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth: Annotated[AuthRepository, Depends(get_auth_repo)],
):
    user_row = await auth.get_user(form_data.username)
    if user_row is not None:
        raise HTTPException(
            status_code=422, detail="User with this email already exist"
        )
    password_hash = get_hashed_password(form_data.password)
    await auth.insert_user(form_data.username, password_hash)
    return JSONResponse(content={}, status_code=200)


@auth_app.post(
    "/login",
    summary="Create access and refresh tokens for user",
    tags=["Authentication"],
    response_model=LoginResponse,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth: Annotated[Pool, Depends(get_auth_repo)],
):
    user_row = await auth.get_user(form_data.username)
    if user_row is None:
        raise HTTPException(status_code=422, detail="Incorrect email")
    password_hash = user_row.get("password_hash")
    if not verify_password(form_data.password, password_hash):
        raise HTTPException(status_code=422, detail="Incorrect password")
    return LoginResponse(
        access_token=create_access_token(data={"sub": form_data.username}),
        token_type="bearer",
        refresh_token=create_refresh_token(data={"sub": form_data.username}),
    )
