from dotenv import load_dotenv
import pytest
from auth_service.password import get_hashed_password, verify_password

load_dotenv()


@pytest.mark.asyncio
async def test_hashing_and_verification_of_password():
    password_hash = get_hashed_password("password")
    is_real_password = verify_password("password", password_hash)
    assert is_real_password is True
