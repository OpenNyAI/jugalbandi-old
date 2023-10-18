from typing import Annotated
from cachetools import cached
from pydantic import BaseSettings, Field


class JivaServiceSettings(BaseSettings):
    jiva_database_ip: Annotated[str, Field(..., env="JIVA_DATABASE_IP")] = ""
    jiva_database_port: Annotated[str, Field(..., env="JIVA_DATABASE_PORT")] = ""
    jiva_database_username: Annotated[
        str, Field(..., env="JIVA_DATABASE_USERNAME")
    ] = ""
    jiva_database_password: Annotated[
        str, Field(..., env="JIVA_DATABASE_PASSWORD")
    ] = ""
    jiva_database_name: Annotated[str, Field(..., env="JIVA_DATABASE_NAME")] = ""


@cached(cache={})
def get_jiva_service_settings():
    return JivaServiceSettings()
