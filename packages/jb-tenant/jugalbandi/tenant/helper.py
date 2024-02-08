import hashlib
import random
import re
import string
import time

import jwt
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_api_key(length=32):
    timestamp = str(time.time()).encode("utf-8")
    random_data = "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(length)
    ).encode("utf-8")
    combined_data = timestamp + random_data
    api_key = hashlib.sha256(combined_data).hexdigest()[:length]
    return api_key


class InputValidator:
    def validate_input_for_length(self, input: str) -> bool:
        return 1 < len(input) < 100

    def validate_email(self, email: str) -> bool:
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        return "@" in email and 2 < len(email) < 320 and bool(re.match(pattern, email))


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def token_encode(expiry_date, email) -> str:
    return jwt.encode(
        {"email": email, "exp_date": expiry_date},
        "some_signature_key",
        algorithm="HS256",
    )


def token_decode(token) -> str:
    try:
        return jwt.decode(token, "some_signature_key", algorithms=["HS256"])
    except Exception:
        return False
