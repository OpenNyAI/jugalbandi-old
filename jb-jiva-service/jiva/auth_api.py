from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from auth_service.password import get_hashed_password, verify_password
from jugalbandi.auth_token import create_access_token, create_refresh_token
from .helper import get_jiva_repo, send_email, verify_refresh_token
from jugalbandi.jiva_repository import JivaRepository
from .model import (
    SignupRequest,
    UpdatePasswordRequest,
    TokenRequest,
    TokenResponse,
)
import time
import random
import datetime
from pytz import utc

auth_app = FastAPI()


@auth_app.post(
    "/signup",
    summary="Create new user",
    tags=["Authentication"],
    # include_in_schema=False
)
async def signup(
    signup_request: SignupRequest,
    jiva_repo: Annotated[JivaRepository, Depends(get_jiva_repo)],
):
    email_id = signup_request.email_id
    user_row = await jiva_repo.get_user(email_id=email_id)
    if user_row is not None:
        raise HTTPException(
            status_code=422, detail="User with this Email ID already exists"
        )

    password_hash = get_hashed_password(password=signup_request.password)
    await jiva_repo.insert_user(
        name=signup_request.name, email_id=email_id, password_hash=password_hash
    )
    return JSONResponse(
        content={"detail": "User Successfully signed up"}, status_code=200
    )


@auth_app.post(
    "/login",
    summary="Create access and refresh tokens for user after login",
    tags=["Authentication"],
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    jiva_repo: Annotated[JivaRepository, Depends(get_jiva_repo)],
):
    user_details = await jiva_repo.get_user(email_id=form_data.username)
    if user_details is None:
        raise HTTPException(status_code=422, detail="Incorrect email")

    password_hash = user_details.get("password_hash")
    if not verify_password(password=form_data.password, hashed_pass=password_hash):
        raise HTTPException(status_code=422, detail="Incorrect password")
    return TokenResponse(
        access_token=create_access_token(data={"sub": form_data.username}),
        token_type="bearer",
        refresh_token=create_refresh_token(data={"sub": form_data.username}),
    )


@auth_app.post(
    "/reset-password",
    summary="Reset user password",
    tags=["Authentication"],
    include_in_schema=False,
)
async def reset_password(
    email_id: str,
    jiva_repo: Annotated[JivaRepository, Depends(get_jiva_repo)],
):
    user_details = await jiva_repo.get_user(email_id=email_id)
    if user_details is None:
        raise HTTPException(status_code=422, detail="Incorrect email")

    current_timestamp = int(time.time())
    random_part = random.randint(0, 99999)
    verification_code = str(
        ((current_timestamp * 100000) + random_part) % 1000000
    ).zfill(6)

    current_datetimestamp = datetime.datetime.now()
    expiry_timestamp = current_datetimestamp + datetime.timedelta(minutes=15)
    reset_id = await jiva_repo.insert_reset_password(
        email_id=email_id,
        verification_code=verification_code,
        expiry_time=expiry_timestamp,
    )

    await send_email(
        recepient_email_id=email_id,
        recepient_name=user_details.get("name"),
        reset_id=reset_id,
        verification_code=verification_code,
    )
    return JSONResponse(
        content={"detail": "Verification code sent successfully."}, status_code=200
    )


@auth_app.post(
    "/update-password",
    summary="Update user password",
    tags=["Authentication"],
    include_in_schema=False,
)
async def update_password(
    update_password_request: UpdatePasswordRequest,
    jiva_repo: Annotated[JivaRepository, Depends(get_jiva_repo)],
):
    reset_password_details = await jiva_repo.get_reset_password_details(
        reset_id=update_password_request.reset_id,
        verification_code=update_password_request.verification_code,
    )
    expiry_timestamp = reset_password_details.get("expiry_time")
    current_timestamp = datetime.datetime.now().astimezone(utc)
    if current_timestamp > expiry_timestamp:
        raise HTTPException(
            status_code=401,
            detail="Time expired for the verification code. Please try again.",
        )

    password_hash = get_hashed_password(password=update_password_request.new_password)
    await jiva_repo.update_user_password(
        email_id=reset_password_details.get("email_id"), password_hash=password_hash
    )
    return JSONResponse(
        content={"detail": "Successfully updated password"}, status_code=200
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
    jiva_repo: Annotated[JivaRepository, Depends(get_jiva_repo)],
):
    user_details = await jiva_repo.get_user(email_id=token_request.email_id)
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
