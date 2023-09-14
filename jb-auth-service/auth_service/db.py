import operator
from typing import Dict
import asyncpg
from auth_service.auth_service_settings import get_auth_service_settings
from jugalbandi.core.caching import aiocachedmethod


class AuthRepository:
    def __init__(self) -> None:
        self.auth_settings = get_auth_service_settings()
        self.engine_cache: Dict[str, asyncpg.Pool] = {}

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.auth_settings.auth_database_ip,
            port=self.auth_settings.auth_database_port,
            user=self.auth_settings.auth_database_username,
            password=self.auth_settings.auth_database_password,
            database=self.auth_settings.auth_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    email TEXT PRIMARY KEY,
                    password_hash TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """
            )

    async def insert_user(self, email, password_hash):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO users
                (email, password_hash)
                VALUES ($1, $2)
                """,
                email,
                password_hash,
            )

    async def get_user(self, email):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT * FROM users
                WHERE email=$1
                """,
                email,
            )
