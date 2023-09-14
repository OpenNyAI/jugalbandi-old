import operator
from typing import Dict
import asyncpg
from datetime import datetime
from zoneinfo import ZoneInfo
from jugalbandi.core.caching import aiocachedmethod
from .qa_db_settings import get_qa_db_settings


class QARepository:
    def __init__(self) -> None:
        self.qa_db_settings = get_qa_db_settings()
        self.engine_cache: Dict[str, asyncpg.Pool] = {}

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.qa_db_settings.qa_database_ip,
            port=self.qa_db_settings.qa_database_port,
            user=self.qa_db_settings.qa_database_username,
            password=self.qa_db_settings.qa_database_password,
            database=self.qa_db_settings.qa_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_logs (
                    id SERIAL PRIMARY KEY,
                    model_name TEXT DEFAULT 'langchain',
                    uuid_number TEXT,
                    query TEXT,
                    paraphrased_query TEXT,
                    response TEXT,
                    source_text TEXT,
                    error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS qa_voice_logs (
                    id SERIAL PRIMARY KEY,
                    uuid_number TEXT,
                    input_language TEXT DEFAULT 'en',
                    output_format TEXT DEFAULT 'TEXT',
                    query TEXT,
                    query_in_english TEXT,
                    paraphrased_query TEXT,
                    response TEXT,
                    response_in_english TEXT,
                    audio_output_link TEXT,
                    source_text TEXT,
                    error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS document_store_logs (
                    id SERIAL PRIMARY KEY,
                    description TEXT,
                    uuid_number TEXT,
                    documents_list TEXT[],
                    error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """
            )

    async def insert_qa_logs(
        self,
        model_name,
        uuid_number,
        query,
        paraphrased_query,
        response,
        source_text,
        error_message,
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO qa_logs
                (model_name, uuid_number, query, paraphrased_query,
                response, source_text, error_message, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                model_name,
                uuid_number,
                query,
                paraphrased_query,
                response,
                source_text,
                error_message,
                datetime.now(ZoneInfo("UTC")),
            )

    async def insert_document_store_logs(
        self, description, uuid_number, documents_list, error_message
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                f"""
                INSERT INTO document_store_logs
                (description, uuid_number, documents_list, error_message, created_at)
                VALUES ($1, $2, ARRAY {documents_list}, $3, $4)
                """,
                description,
                uuid_number,
                error_message,
                datetime.now(ZoneInfo("UTC")),
            )

    async def insert_qa_voice_logs(
        self,
        uuid_number,
        input_language,
        output_format,
        query,
        query_in_english,
        paraphrased_query,
        response,
        response_in_english,
        audio_output_link,
        source_text,
        error_message,
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO qa_voice_logs
                (uuid_number, input_language, output_format, query, query_in_english,
                paraphrased_query, response,
                response_in_english, audio_output_link,
                source_text, error_message, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                uuid_number,
                input_language,
                output_format,
                query,
                query_in_english,
                paraphrased_query,
                response,
                response_in_english,
                audio_output_link,
                source_text,
                error_message,
                datetime.now(ZoneInfo("UTC")),
            )
