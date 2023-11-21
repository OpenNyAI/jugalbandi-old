from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jugalbandi.core.caching import aiocached
from jugalbandi.auth_token.token import decode_token, decode_refresh_token
from jugalbandi.legal_library import LegalLibrary
from jugalbandi.storage import GoogleStorage
from jugalbandi.translator import (
    CompositeTranslator,
    GoogleTranslator,
    DhruvaTranslator,
)
from jugalbandi.jiva_repository import JivaRepository
from .model import User
from typing import Annotated
import os
import openai
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

jiva_email_api_key = os.environ["JIVA_EMAIL_API_KEY"]
jiva_base_url = os.environ["JIVA_BASE_URL"]
jiva_sub_url = os.environ["JIVA_SUB_URL"]

reusable_oauth = OAuth2PasswordBearer(tokenUrl="/library/auth/login", auto_error=False)


@aiocached(cache={})
async def get_jiva_repo() -> JivaRepository:
    jiva_repo = JivaRepository()
    return jiva_repo


@aiocached(cache={})
async def get_library() -> LegalLibrary:
    bucket_name = os.environ["JIVA_LIBRARY_BUCKET"]
    library_path = os.environ["JIVA_LIBRARY_PATH"]
    google_storage = GoogleStorage(bucket_name, library_path)
    return LegalLibrary(id="jiva", store=google_storage)


async def get_translator():
    return CompositeTranslator(GoogleTranslator(), DhruvaTranslator())


async def verify_access_token(
    jiva_repo: Annotated[JivaRepository, Depends(get_jiva_repo)],
    token: Annotated[str, Depends(reusable_oauth)],
):
    if os.environ["ALLOW_AUTH_ACCESS"] == "true" and token is None:
        return None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_details = await jiva_repo.get_user(email_id=username)
    return User(name=user_details.get("name"), email_id=user_details.get("email_id"))


async def verify_refresh_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_refresh_token(token)
        username: str = payload
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username


async def send_email(
    recepient_email_id: str, recepient_name: str, reset_id: str, verification_code: str
):
    verification_link = (
        f"{jiva_base_url}/{jiva_sub_url}?reset_id={reset_id}"
        f"&verification_code={verification_code}"
    )

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
        }
        .container {
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0px 0px 5px 2px gray;
        }
        .header {
            color: #333;
            font-size: 24px;
            text-align: center;
        }
        .content {
            color: #1c1c1c;
            font-size: 18px;
            margin-top: 20px;
            text-align: center;
        }
        .verification-link {
            color: black;
            font-family: Roboto-Regular, Helvetica, Arial, sans-serif;
            font-size: 24px;
            text-align: center;
        }
        .signature {
            font-size: 17px;
            margin-top: 40px;
            text-align: center;
        }
        .do-not-reply {
            color: red;
            font-style: italic;
            font-size: 12px;
            margin-top: 30px;
            text-align: center;
        }
        a:link {
            color: blue;
        }
        a:visited {
            color: purple;
        }
        </style>
    </head>
    <body>
        <div class="container">
        <div class="header">Hi {{recepient_name}}!</div>
        <div class="content">
            <p>
            Forgot your password?<br />We received a request to reset the password
            for your account.<br /><br />To reset your password, please click on
            the link given below:
            </p>
        </div>
        <div class="verification-link">
            <a href={{verification_link}}>Password Reset</a>
        </div>
        <div class="content">
            <p>This password reset link is only valid for the next 15 minutes.</p>
            <p>If you didn't make this request, please ignore this email.</p>
        </div>
        <div class="signature">Thanks,<br />Jiva team.</div>
        <div class="do-not-reply">Note: Please do not reply to this mail.</div>
        </div>
    </body>
    </html>
    """
    html_template = html_template.replace('{{recepient_name}}', recepient_name)
    html_template = html_template.replace('{{verification_link}}', verification_link)

    sg = SendGridAPIClient(jiva_email_api_key)
    from_email = Email("support@opennyai.org")
    to_email = To(recepient_email_id)
    subject = "JIVA: Password Reset"
    content = Content("text/html", html_template)
    mail = Mail(from_email, to_email, subject, content)

    mail_json = mail.get()

    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)


async def classify_query(query: str) -> str:
    system_rules = (
        """
        Given a query, classify it as either a descriptive search (questions) or a non-descriptive search (commands).
        The Descriptive searches typically are questions whereas the non descriptive searches are often commands or statements.
        Return only either Descriptive Search or Non Descriptive Search for the given query as the output.
        """
    )
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_rules},
            {"role": "user", "content": query},
        ],
    )
    return res["choices"][0]["message"]["content"]
