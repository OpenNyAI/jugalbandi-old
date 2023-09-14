from typing import Annotated
from cachetools import cached
from pydantic import BaseSettings, Field


class AuthServiceSettings(BaseSettings):
    auth_database_ip: Annotated[
        str, Field(..., env="AUTH_DATABASE_IP")
    ] = ""
    auth_database_port: Annotated[
        str, Field(..., env="AUTH_DATABASE_PORT")
    ] = ""
    auth_database_username: Annotated[
        str, Field(..., env="AUTH_DATABASE_USERNAME")
    ] = ""
    auth_database_password: Annotated[
        str, Field(..., env="AUTH_DATABASE_PASSWORD")
    ] = ""
    auth_database_name: Annotated[
        str, Field(..., env="AUTH_DATABASE_NAME")
    ] = ""


@cached(cache={})
def get_auth_service_settings():
    return AuthServiceSettings()
