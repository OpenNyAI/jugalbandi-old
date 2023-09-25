from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .db import LabelingRepository
from .model import TokenResponse, TokenRequest, User
from .helper import get_labeling_repo, verify_refresh_token
from auth_service.password import get_hashed_password, verify_password
from jugalbandi.auth_token import create_access_token, create_refresh_token

auth_app = FastAPI()


@auth_app.post("/signup", summary="Create new user", tags=["Authentication"])
async def signup(
    user: User,
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
):
    user_row = await labeling_repo.get_user(user.email)
    if user_row is not None:
        raise HTTPException(
            status_code=422, detail="User with this email already exist"
        )
    password_hash = get_hashed_password(user.password)
    await labeling_repo.insert_user(user.name, user.email, user.affliation, password_hash)
    await labeling_repo.insert_into_users_case_mapping(user.email)  # Automically assign cases to the user when they sign up
    return JSONResponse(content={"detail": "Successfully signed up"}, status_code=200)


@auth_app.post(
    "/login",
    summary="Create access and refresh tokens for user",
    tags=["Authentication"],
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
):
    user_row = await labeling_repo.get_user(form_data.username)
    if user_row is None:
        raise HTTPException(status_code=422, detail="Incorrect email")
    password_hash = user_row.get("password_hash")
    if not verify_password(form_data.password, password_hash):
        raise HTTPException(status_code=422, detail="Incorrect password")
    return TokenResponse(
        access_token=create_access_token(data={"sub": form_data.username}),
        token_type="bearer",
        refresh_token=create_refresh_token(data={"sub": form_data.username}),
    )


@auth_app.post(
    "/new-auth-tokens",
    summary="Create new access and refresh tokens for user after verification",
    tags=["Authentication"],
    response_model=TokenResponse,
    include_in_schema=False,
)
async def new_auth_tokens(
    token_request: TokenRequest,
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
):
    user_details = await labeling_repo.get_user(email_id=token_request.email_id)
    if user_details is None:
        raise HTTPException(status_code=422, detail="Incorrect email")
    email_id = await verify_refresh_token(token=token_request.refresh_token)
    if email_id != token_request.email_id:
        raise HTTPException(status_code=422, detail="Incorrect refresh token")
    return TokenResponse(
        access_token=create_access_token(data={"sub": email_id}),
        token_type="bearer",
        refresh_token=create_refresh_token(data={"sub": email_id}),
    )
