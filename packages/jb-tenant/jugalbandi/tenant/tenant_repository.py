import operator
from typing import Dict
import asyncpg
from jugalbandi.core.caching import aiocachedmethod
from .tenant_db_settings import get_tenant_db_settings


class TenantRepository:
    def __init__(self) -> None:
        self.tenant_db_settings = get_tenant_db_settings()
        self.engine_cache: Dict[str, asyncpg.Pool] = {}

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.tenant_db_settings.tenant_database_ip,
            port=self.tenant_db_settings.tenant_database_port,
            user=self.tenant_db_settings.tenant_database_username,
            password=self.tenant_db_settings.tenant_database_password,
            database=self.tenant_db_settings.tenant_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant(
                    name TEXT,
                    email_id TEXT,
                    api_key TEXT PRIMARY KEY,
                    weekly_quota INTEGER DEFAULT 125,
                    balance_quota INTEGER DEFAULT 125
                );
            """
            )

    async def insert_into_tenant(
        self,
        name,
        email_id,
        api_key,
        weekly_quota
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO tenant
                (name, email_id, api_key, weekly_quota, balance_quota)
                VALUES ($1, $2, $3, $4, $5)
                """,
                name,
                email_id,
                api_key,
                weekly_quota,
                weekly_quota
            )

    async def get_balance_quota_from_api_key(
        self,
        api_key
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                SELECT balance_quota FROM tenant
                WHERE api_key = $1
                """,
                api_key
            )

    async def update_balance_quota(
        self,
        api_key,
        balance_quota
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE tenant
                SET balance_quota = $3
                WHERE api_key = $1 and balance_quota = $2
                """,
                api_key,
                balance_quota,
                balance_quota - 1
            )

    async def update_tenant_information(
        self,
        name,
        email_id,
        api_key,
        weekly_quota
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE tenant
                SET name = $1, email_id = $2, weekly_quota = $4, balance_quota = $4
                WHERE api_key = $3
                """,
                name,
                email_id,
                api_key,
                weekly_quota
            )

    async def reset_balance_quota_for_tenant(
        self,
        api_key
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE tenant
                SET balance_quota = weekly_quota
                WHERE api_key = $1
                """,
                api_key
            )
