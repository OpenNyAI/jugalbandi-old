from typing import Annotated
from cachetools import cached
from pydantic import BaseSettings, Field


class TenantDBSettings(BaseSettings):
    tenant_database_ip: Annotated[str, Field(..., env="TENANT_DATABASE_IP")]
    tenant_database_port: Annotated[str, Field(..., env="TENANT_DATABASE_PORT")]
    tenant_database_username: Annotated[str, Field(..., env="TENANT_DATABASE_USERNAME")]
    tenant_database_password: Annotated[str, Field(..., env="TENANT_DATABASE_PASSWORD")]
    tenant_database_name: Annotated[str, Field(..., env="TENANT_DATABASE_NAME")]


@cached(cache={})
def get_tenant_db_settings():
    return TenantDBSettings()
