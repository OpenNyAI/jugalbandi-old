from typing import Annotated, Optional
from cachetools import cached
from pydantic import BaseSettings, Field


class TokenSettings(BaseSettings):
    token_access_token_expire_minutes: Annotated[
        int, Field(..., env="TOKEN_ACCESS_TOKEN_EXPIRE_MINUTES")
    ] = 60
    token_refresh_token_expire_minutes: Annotated[
        int, Field(..., env="TOKEN_REFRESH_TOKEN_EXPIRE_MINUTES")
    ] = (60 * 24 * 7)
    token_algorithm: Annotated[str, Field(..., env="TOKEN_ALGORITHM")] = "HS256"
    token_jwt_secret_key: Annotated[
        Optional[str], Field(..., env="TOKEN_JWT_SECRET_KEY")
    ] = None
    token_jwt_secret_refresh_key: Annotated[
        Optional[str], Field(..., env="TOKEN_JWT_SECRET_REFRESH_KEY")
    ] = None


@cached(cache={})
def get_token_settings():
    return TokenSettings()
