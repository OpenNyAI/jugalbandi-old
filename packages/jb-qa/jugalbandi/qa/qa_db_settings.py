from typing import Annotated
from cachetools import cached
from pydantic import BaseSettings, Field


class QaDbSettings(BaseSettings):
    qa_database_ip: Annotated[str, Field(..., env="QA_DATABASE_IP")]
    qa_database_port: Annotated[str, Field(..., env="QA_DATABASE_PORT")]
    qa_database_username: Annotated[str, Field(..., env="QA_DATABASE_USERNAME")]
    qa_database_password: Annotated[str, Field(..., env="QA_DATABASE_PASSWORD")]
    qa_database_name: Annotated[str, Field(..., env="QA_DATABASE_NAME")]


@cached(cache={})
def get_qa_db_settings():
    return QaDbSettings()
