from datetime import datetime
import operator
from typing import Dict
import asyncpg
import pytz

from jugalbandi.core.caching import aiocachedmethod
from .feedback_settings import (
    get_qa_feedback_settings,
    get_scheme_feedback_settings,
)


class FeedbackRepository:
    def __init__(self) -> None:
        pass

    async def _get_engine(self) -> asyncpg.Pool:
        pass

    async def _create_engine(self, timeout=5):
        pass

    async def _create_schema(self, engine):
        pass

    async def insert_response_feedback(self, uuid_number, query, response, feedback):
        pass


class QAFeedbackRepository(FeedbackRepository):
    def __init__(self) -> None:
        self.engine_cache: Dict[str, asyncpg.Pool] = {}
        self.qa_feedback_settings = get_qa_feedback_settings()

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.qa_feedback_settings.qa_feedback_database_ip,
            port=self.qa_feedback_settings.qa_feedback_database_port,
            user=self.qa_feedback_settings.qa_feedback_database_username,
            password=self.qa_feedback_settings.qa_feedback_database_password,
            database=self.qa_feedback_settings.qa_feedback_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS response_feedback (
                    id SERIAL PRIMARY KEY,
                    uuid_number TEXT,
                    query TEXT,
                    response TEXT,
                    feedback BOOLEAN,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """
            )

    async def insert_response_feedback(self, uuid_number, query, response, feedback):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO response_feedback
                (uuid_number, query, response, feedback, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                uuid_number,
                query,
                response,
                feedback,
                datetime.now(pytz.UTC),
            )


class SchemeFeedbackRepository(FeedbackRepository):
    def __init__(self) -> None:
        self.engine_cache: Dict[str, asyncpg.Pool] = {}
        self.scheme_feedback_settings = get_scheme_feedback_settings()

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.scheme_feedback_settings.scheme_feedback_database_ip,
            port=self.scheme_feedback_settings.scheme_feedback_database_port,
            user=self.scheme_feedback_settings.scheme_feedback_database_username,
            password=self.scheme_feedback_settings.scheme_feedback_database_password,
            database=self.scheme_feedback_settings.scheme_feedback_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jugalbandi_users_conversation_history (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    FOREIGN KEY (chat_id) REFERENCES jugalbandi_users(chat_id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    language_preference TEXT DEFAULT 'hi',
                    user_audio_file_link TEXT,
                    bot_audio_file_link TEXT,
                    conversation_chunk_id TEXT,
                    FOREIGN KEY (conversation_chunk_id) REFERENCES jugalbandi_user_prompts(conversation_chunk_id),
                    bot_preference TEXT,
                    scheme_name TEXT,
                    user_message TEXT,
                    bot_response TEXT,
                    user_message_translated TEXT,
                    bot_response_translated TEXT,
                    current_prompt TEXT,
                    next_prompt_name TEXT,
                    next_prompt TEXT,
                    llm_output TEXT,
                    feedback TEXT
                );
                CREATE INDEX IF NOT EXISTS chat_id_idx ON jugalbandi_users_conversation_history(chat_id);
            """
            )

    async def insert_response_feedback(self, chat_id, feedback):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                "update public.jugalbandi_users_conversation_history set feedback=$1 where chat_id=$2 and id=(select id from public.jugalbandi_users_conversation_history where chat_id=$2 order by created_at desc limit 1)",
                feedback,
                chat_id,
            )
