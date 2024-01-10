from typing import Annotated, Optional
from cachetools import cached
from pydantic import BaseSettings, Field


class LoggingSettings(BaseSettings):
    logging_database_ip: Annotated[
        Optional[str], Field(..., env="LOGGING_DATABASE_IP")
    ] = None
    logging_database_port: Annotated[
        Optional[str], Field(..., env="LOGGING_DATABASE_PORT")
    ] = None
    logging_database_username: Annotated[
        Optional[str], Field(..., env="LOGGING_DATABASE_USERNAME")
    ] = None
    logging_database_password: Annotated[
        Optional[str], Field(..., env="LOGGING_DATABASE_PASSWORD")
    ] = None
    logging_database_name: Annotated[
        Optional[str], Field(..., env="LOGGING_DATABASE_NAME")
    ] = None


@cached(cache={})
def get_logging_settings():
    return LoggingSettings()
