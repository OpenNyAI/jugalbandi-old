from typing import Annotated, Optional
from cachetools import cached
from pydantic import BaseSettings, Field


class LoggingSettings(BaseSettings):
    logging_feedback_database_ip: Annotated[
        Optional[str], Field(..., env="LOGGING_FEEDBACK_DATABASE_IP")
    ] = None
    logging_feedback_database_port: Annotated[
        Optional[str], Field(..., env="LOGGING_FEEDBACK_DATABASE_PORT")
    ] = None
    logging_feedback_database_username: Annotated[
        Optional[str], Field(..., env="LOGGING_FEEDBACK_DATABASE_USERNAME")
    ] = None
    logging_feedback_database_password: Annotated[
        Optional[str], Field(..., env="LOGGING_FEEDBACK_DATABASE_PASSWORD")
    ] = None
    logging_feedback_database_name: Annotated[
        Optional[str], Field(..., env="LOGGING_FEEDBACK_DATABASE_NAME")
    ] = None


@cached(cache={})
def get_logging_feedback_settings():
    return LoggingSettings()
