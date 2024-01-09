from datetime import datetime
import operator
from typing import Dict
import asyncpg
import pytz
from jugalbandi.core.caching import aiocachedmethod
from .logging_settings import get_logging_feedback_settings


class LoggingRepository():
    def __init__(self) -> None:
        self.engine_cache: Dict[str, asyncpg.Pool] = {}
        self.logging_feedback_settings = get_logging_feedback_settings()

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.logging_feedback_settings.logging_feedback_database_ip,
            port=self.logging_feedback_settings.logging_feedback_database_port,
            user=self.logging_feedback_settings.logging_feedback_database_username,
            password=self.logging_feedback_settings.logging_feedback_database_password,
            database=self.logging_feedback_settings.logging_feedback_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    phone_number BIGINT UNIQUE,
                    telegram_username TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS app(
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    phone_number BIGINT UNIQUE,
                    telegram_username TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS document_store_logs(
                    user_id INTEGER FOREIGN KEY REFERENCES users(id),
                    app_id INTEGER FOREIGN KEY REFERENCES app(id),
                    uuid TEXT PRIMARY KEY,
                    documents_list TEXT[],
                    total_file_size FLOAT,
                    error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS qa_logs(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER FOREIGN KEY REFERENCES users(id),
                    app_id INTEGER FOREIGN KEY REFERENCES app(id),
                    document_uuid TEXT FOREIGN KEY REFERENCES document_store_logs(uuid),
                    input_language TEXT DEFAULT 'en',
                    output_format TEXT DEFAULT 'TEXT',
                    audio_input_link TEXT,
                    stt_model_name TEXT,
                    query TEXT,
                    query_translation_model_name TEXT,
                    query_in_english TEXT,
                    retrieval_k_value INTEGER,
                    retrieved_chunks TEXT[],
                    prompt TEXT,
                    gpt_model_name TEXT,
                    response_in_english TEXT,
                    response_translation_model_name TEXT,
                    response TEXT,
                    tts_model_name TEXT,
                    audio_output_link TEXT,
                    error_message TEXT,
                    status_code INTEGER,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS chat_history(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER FOREIGN KEY REFERENCES users(id),
                    app_id INTEGER FOREIGN KEY REFERENCES app(id),
                    document_uuid TEXT FOREIGN KEY REFERENCES document_store_logs(uuid),
                    message_owner TEXT NOT NULL,
                    preferred_language TEXT NOT NULL,
                    audio_url TEXT,
                    message TEXT,
                    message_in_english TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                );
            """
            )

    async def insert_users(self, first_name: str, last_name: str,
                           phone_number: int, telegram_username: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO users
                (first_name, last_name, phone_number,
                telegram_username, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                first_name,
                last_name,
                phone_number,
                telegram_username,
                datetime.now(pytz.UTC),
            )

    async def insert_app_information(self, name: str,
                                     phone_number: int, telegram_username: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO app
                (name, phone_number,
                telegram_username, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                name,
                phone_number,
                telegram_username,
                datetime.now(pytz.UTC),
            )

    async def insert_document_store_logs(self, user_id: int, app_id: int, uuid: str,
                                         documents_list: list, total_file_size: int,
                                         error_message: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO document_store_logs
                (user_id, app_id, uuid, documents_list,
                total_file_size, error_message, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                user_id,
                app_id,
                uuid,
                documents_list,
                total_file_size,
                error_message,
                datetime.now(pytz.UTC),
            )

    async def insert_qa_logs(self, user_id: int, app_id: int, document_uuid: str, input_language: str,
                             output_format: str, audio_input_link: str, stt_model_name: str,
                             query: str, query_translation_model_name: str, query_in_english: str,
                             retrieval_k_value: int, retrieved_chunks: list, prompt: str, gpt_model_name: str,
                             response_in_english: str, response_translation_model_name: str, response: str,
                             tts_model_name: str, audio_output_link: str, error_message: str, status_code: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO qa_logs
                (user_id, app_id, document_uuid, input_language,
                output_format, audio_input_link, stt_model_name,
                query, query_translation_model_name, query_in_english,
                retrieval_k_value, retrieved_chunks, prompt, gpt_model_name,
                response_in_english, response_translation_model_name, response,
                tts_model_name, audio_output_link, error_message, status_code created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14,
                $15, $16, $17, $18, $19, $20, $21, $22)
                """,
                user_id,
                app_id,
                document_uuid,
                input_language,
                output_format,
                audio_input_link,
                stt_model_name,
                query,
                query_translation_model_name,
                query_in_english,
                retrieval_k_value,
                retrieved_chunks,
                prompt,
                gpt_model_name,
                response_in_english,
                response_translation_model_name,
                response,
                tts_model_name,
                audio_output_link,
                error_message,
                status_code,
                datetime.now(pytz.UTC),
            )

    async def insert_chat_history(self, user_id: int, app_id: int, document_uuid: str,
                                  message_owner: str, preferred_language: str, audio_url: str,
                                  message: str, message_in_english: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO document_store_logs
                (user_id, app_id, document_uuid,
                message_owner, preferred_language, audio_url,
                message, message_in_english, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                user_id,
                app_id,
                document_uuid,
                message_owner,
                preferred_language,
                audio_url,
                message,
                message_in_english,
                datetime.now(pytz.UTC),
            )
