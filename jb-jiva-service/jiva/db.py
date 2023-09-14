import operator
from typing import Dict
import asyncpg
from jugalbandi.core.caching import aiocachedmethod
from .db_settings import get_jiva_service_settings
from datetime import datetime


class JivaRepository:
    def __init__(self) -> None:
        self.jiva_settings = get_jiva_service_settings()
        self.engine_cache: Dict[str, asyncpg.Pool] = {}

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.jiva_settings.jiva_database_ip,
            port=self.jiva_settings.jiva_database_port,
            user=self.jiva_settings.jiva_database_username,
            password=self.jiva_settings.jiva_database_password,
            database=self.jiva_settings.jiva_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    name TEXT,
                    email_id TEXT PRIMARY KEY,
                    password_hash TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                CREATE TABLE IF NOT EXISTS conversation_history (
                    email_id TEXT,
                    message_id UUID DEFAULT uuid_generate_v4() NOT NULL,
                    message TEXT,
                    sender TEXT CHECK (sender = 'user' OR sender = 'bot'),
                    query TEXT,
                    feedback BOOL,
                    message_date DATE DEFAULT CURRENT_DATE,
                    message_time TIME DEFAULT CURRENT_TIME,
                    PRIMARY KEY (email_id, message_id),
                    FOREIGN KEY (email_id) REFERENCES users (email_id)
                );
                CREATE TABLE IF NOT EXISTS reset_password (
                    id SERIAL PRIMARY KEY,
                    email_id TEXT,
                    verification_code TEXT,
                    expiry_time TIMESTAMPTZ NOT NULL,
                    FOREIGN KEY (email_id) REFERENCES users (email_id)
                );
                CREATE TABLE IF NOT EXISTS opened_documents (
                    email_id TEXT,
                    document_title TEXT,
                    document_id TEXT,
                    PRIMARY KEY (email_id, document_id),
                    FOREIGN KEY (email_id) REFERENCES users (email_id)
                );
                CREATE TABLE IF NOT EXISTS bookmark (
                    email_id TEXT,
                    bookmark_id UUID DEFAULT uuid_generate_v4() NOT NULL,
                    document_id TEXT,
                    document_title TEXT,
                    section_name TEXT,
                    bookmark_name TEXT,
                    bookmark_note TEXT,
                    bookmark_page INTEGER,
                    bookmark_date DATE DEFAULT CURRENT_DATE,
                    bookmark_time TIME DEFAULT CURRENT_TIME,
                    PRIMARY KEY (email_id, bookmark_id),
                    FOREIGN KEY (email_id) REFERENCES users (email_id)
                );
                CREATE TABLE IF NOT EXISTS query_response_feeback (
                    id SERIAL PRIMARY KEY,
                    query TEXT,
                    document_title TEXT,
                    section_name TEXT,
                    section_page_number TEXT,
                    feedback BOOLEAN
                )
            """
            )

    async def get_user(self, email_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT * FROM users
                WHERE email_id=$1
                """,
                email_id,
            )

    async def get_reset_password_details(self,
                                         reset_id: int,
                                         verification_code: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT * FROM reset_password
                where id = $1 and verification_code = $2
                """,
                reset_id,
                verification_code,
            )

    async def get_daily_activities(self, email_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetch(
                """
                SELECT message_id, query, message_date, message_time FROM conversation_history
                WHERE email_id = $1 AND sender = 'user'
                ORDER BY message_date DESC, message_time DESC;
                """,
                email_id,
            )

    async def get_conversation_history(self, email_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetch(
                """
                SELECT * FROM conversation_history
                WHERE email_id = $1 ORDER BY message_date ASC, message_time ASC;;
                """,
                email_id,
            )

    async def get_bookmarks(self, email_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetch(
                """
                SELECT * FROM bookmark
                WHERE email_id = $1;
                """,
                email_id,
            )

    async def get_opened_documents(self, email_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetch(
                """
                SELECT * FROM opened_documents
                WHERE email_id = $1;
                """,
                email_id,
            )

    async def insert_user(self,
                          name: str,
                          email_id: str,
                          password_hash: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO users
                (name, email_id, password_hash)
                VALUES ($1, $2, $3)
                """,
                name,
                email_id,
                password_hash,
            )

    async def insert_reset_password(self,
                                    email_id: str,
                                    verification_code: str,
                                    expiry_time: datetime):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                INSERT INTO reset_password
                (email_id, verification_code, expiry_time)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                email_id,
                verification_code,
                expiry_time
            )

    async def update_user_password(self,
                                   email_id: str,
                                   password_hash: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE users
                SET password_hash = $2
                WHERE email_id = $1
                """,
                email_id,
                password_hash,
            )

    async def insert_conversation_history(self,
                                          email_id: str,
                                          message: str,
                                          sender: str,
                                          query: str,
                                          feedback: bool | None):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                INSERT INTO conversation_history
                (email_id, message, sender, query, feedback)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING message_id
                """,
                email_id,
                message,
                sender,
                query,
                feedback
            )

    async def insert_bookmark(self,
                              email_id: str,
                              document_id: str,
                              document_title: str,
                              section_name: str,
                              bookmark_name: str,
                              bookmark_note: str,
                              bookmark_page: int):
        engine = await self._get_engine()
        # pass
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                INSERT INTO bookmark
                (email_id, document_id, document_title,
                section_name, bookmark_name, bookmark_note,
                bookmark_page)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING bookmark_id
                """,
                email_id,
                document_id,
                document_title,
                section_name,
                bookmark_name,
                bookmark_note,
                bookmark_page
            )

    async def put_feedback_into_conversation(self,
                                             email_id: str,
                                             message_id: str,
                                             feedback: bool):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.execute(
                """
                UPDATE conversation_history
                SET feedback = $3
                WHERE email_id = $1 AND message_id = $2
                """,
                email_id,
                message_id,
                feedback
            )

    async def update_bookmark(self,
                              email_id: str,
                              bookmark_id: str,
                              document_id: str,
                              document_title: str,
                              section_name: str,
                              bookmark_name: str,
                              bookmark_note: str,
                              bookmark_page: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.execute(
                """
                UPDATE bookmark
                SET document_id = $3, document_title = $4, section_name = $5, bookmark_name = $6, bookmark_note = $7, bookmark_page = $8
                WHERE email_id = $1 AND bookmark_id = $2
                """,
                email_id,
                bookmark_id,
                document_id,
                document_title,
                section_name,
                bookmark_name,
                bookmark_note,
                bookmark_page
            )

    async def delete_conversation_history(self, email_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                DELETE FROM conversation_history
                WHERE email_id = $1
                """,
                email_id,
            )

    async def delete_bookmark(self, email_id: str, bookmark_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                DELETE FROM bookmark
                WHERE email_id = $1 and bookmark_id = $2
                """,
                email_id,
                bookmark_id,
            )

    async def delete_activity(self, email_id: str, message_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            conversation_list = await connection.fetch(
                """
                SELECT message_id, sender, query, message_date, message_time
                FROM conversation_history
                WHERE email_id=$1 and message_id=$2
                UNION ALL
                SELECT message_id, sender, query, message_date, message_time
                FROM conversation_history
                WHERE (message_date, message_time) > (
                    SELECT message_date, message_time
                    FROM conversation_history
                    WHERE email_id=$1 and message_id=$2
                ) AND email_id=$1
                ORDER BY message_date, message_time
                limit 10;
                """,
                email_id,
                message_id,
            )
            message_id_list = ["'" + str(conversation_list[0].get("message_id")) + "'"]
            for i in range(1, len(conversation_list)):
                if conversation_list[i].get("sender") == "user":
                    break
                else:
                    message_id_list.append("'" + str(conversation_list[i].get("message_id")) + "'")

            await connection.execute(
                """
                DELETE FROM conversation_history
                WHERE email_id = $1 and message_id in ({})
                """.format(','.join(message_id_list)),
                email_id,
            )

    async def insert_opened_documents(self,
                                      email_id: str,
                                      document_title: str,
                                      document_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO opened_documents
                (email_id, document_title, document_id)
                VALUES ($1, $2, $3)
                """,
                email_id,
                document_title,
                document_id
            )

    async def delete_opened_documents(self,
                                      email_id: str,
                                      document_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                DELETE FROM opened_documents
                WHERE email_id = $1 AND document_id = $2
                """,
                email_id,
                document_id
            )

    async def insert_query_response_feedback(self, query: str,
                                             document_title: str,
                                             section_name: str,
                                             section_page_number: str,
                                             feedback: bool):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO query_response_feeback
                (query, document_title, section_name,
                section_page_number, feedback)
                VALUES ($1, $2, $3, $4, $5)
                """,
                query,
                document_title,
                section_name,
                section_page_number,
                feedback
            )
