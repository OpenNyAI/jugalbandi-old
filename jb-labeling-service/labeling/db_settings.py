from typing import Annotated
from cachetools import cached
from pydantic import BaseSettings, Field


class LabelingServiceSettings(BaseSettings):
    labeling_database_ip: Annotated[str, Field(..., env="LABELING_DATABASE_IP")] = ""
    labeling_database_port: Annotated[str, Field(..., env="LABELING_DATABASE_PORT")] = ""
    labeling_database_username: Annotated[
        str, Field(..., env="LABELING_DATABASE_USERNAME")
    ] = ""
    labeling_database_password: Annotated[
        str, Field(..., env="LABELING_DATABASE_PASSWORD")
    ] = ""
    labeling_database_name: Annotated[str, Field(..., env="LABELING_DATABASE_NAME")] = ""


@cached(cache={})
def get_labeling_service_settings():
    return LabelingServiceSettings()
