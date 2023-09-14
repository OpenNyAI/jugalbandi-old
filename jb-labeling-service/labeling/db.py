import operator
from typing import Dict, List
import asyncpg
from jugalbandi.core.caching import aiocachedmethod
from .model import Case
from .db_settings import get_labeling_service_settings


class LabelingRepository:
    def __init__(self) -> None:
        self.labeling_settings = get_labeling_service_settings()
        self.engine_cache: Dict[str, asyncpg.Pool] = {}

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        await self._create_schema(engine)
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=self.labeling_settings.labeling_database_ip,
            port=self.labeling_settings.labeling_database_port,
            user=self.labeling_settings.labeling_database_username,
            password=self.labeling_settings.labeling_database_password,
            database=self.labeling_settings.labeling_database_name,
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def _create_schema(self, engine: asyncpg.Pool):
        async with engine.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS case_table (
                    id TEXT PRIMARY KEY,
                    case_name TEXT,
                    court_name TEXT,
                    doc_url TEXT,
                    raw_text TEXT,
                    doc_size INTEGER,
                    case_type TEXT,
                    court_type TEXT,
                    facts TEXT,
                    facts_edited BOOL DEFAULT FALSE,
                    facts_last_updated_at TIMESTAMPTZ[] DEFAULT ARRAY[]::timestamp[],
                    facts_cumulative_time INTEGER DEFAULT 0,
                    facts_reviewed BOOL DEFAULT FALSE,
                    issues TEXT[],
                    issues_edited BOOL DEFAULT FALSE,
                    issues_last_updated_at TIMESTAMPTZ[] DEFAULT ARRAY[]::timestamp[],
                    issues_cumulative_time INTEGER DEFAULT 0,
                    issues_reviewed BOOL DEFAULT FALSE,
                    generated_issues TEXT,
                    sections_edited bool DEFAULT FALSE,
                    sections_last_updated_at TIMESTAMPTZ[] DEFAULT ARRAY[]::timestamp[],
                    sections_cumulative_time INTEGER DEFAULT 0,
                    sections_reviewed BOOL DEFAULT FALSE,
                    precedents_edited bool DEFAULT FALSE,
                    precedents_last_updated_at TIMESTAMPTZ[] DEFAULT ARRAY[]::timestamp[],
                    precedents_cumulative_time INTEGER DEFAULT 0,
                    precedents_reviewed BOOL DEFAULT FALSE,
                    petitioner_arguments TEXT[],
                    petitioner_arguments_edited bool DEFAULT FALSE,
                    petitioner_arguments_last_updated_at TIMESTAMPTZ[] DEFAULT ARRAY[]::timestamp[],
                    petitioner_arguments_cumulative_time INTEGER DEFAULT 0,
                    petitioner_arguments_reviewed BOOL DEFAULT FALSE,
                    generated_petitioner_arguments TEXT,
                    is_completed BOOL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    respondent_arguments TEXT[],
                    respondent_arguments_edited bool DEFAULT FALSE,
                    respondent_arguments_last_updated_at TIMESTAMPTZ[] DEFAULT ARRAY[]::timestamp[],
                    respondent_arguments_cumulative_time INTEGER DEFAULT 0,
                    respondent_arguments_reviewed BOOL DEFAULT FALSE,
                    generated_respondent_arguments TEXT,
                    petitioner_name TEXT,
                    respondent_name TEXT,
                    facts_token_length INTEGER DEFAULT 0,
                    issues_token_length INTEGER DEFAULT 0,
                    cumulative_final_token_length INTEGER DEFAULT 0,
                    facts_change_percentage REAL DEFAULT 0.0,
                    issues_change_percentage REAL DEFAULT 0.0,
                    precedent_para_count INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS case_section (
                    section_number TEXT,
                    case_id TEXT,
                    act_title TEXT,
                    reason TEXT,
                    description TEXT,
                    is_applicable BOOL DEFAULT TRUE,
                    PRIMARY KEY (section_number, case_id, act_title),
                    FOREIGN KEY (case_id) REFERENCES case_table (id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS case_precedent (
                    case_id TEXT,
                    precedent_name TEXT,
                    precedent_url TEXT,
                    paragraphs TEXT[],
                    PRIMARY KEY (case_id, precedent_name),
                    FOREIGN KEY (case_id) REFERENCES case_table (id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS users(
                    name TEXT,
                    email TEXT PRIMARY KEY,
                    affliation TEXT,
                    password_hash TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                create TABLE IF NOT EXISTS users_case_mapping (
                    user_email TEXT,
                    case_id TEXT,
                    FOREIGN KEY (user_email) REFERENCES users (email),
                    FOREIGN KEY (case_id) REFERENCES case_table (id)
                )
                """
            )

    async def insert_into_case_section(
        self,
        section_number: str,
        case_id: str,
        act_title: str,
        reason: str,
        description: str,
        is_applicable: bool
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO case_section
                (section_number, case_id, act_title, reason, description, is_applicable)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                section_number,
                case_id,
                act_title,
                reason,
                description,
                is_applicable
            )

    async def insert_into_case_precedent(
        self,
        case_id: str,
        precedent_name: str,
        precedent_url: str,
        paragraphs: List[str]
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO case_precedent
                (case_id, precedent_name, precedent_url, paragraphs)
                VALUES ($1, $2, $3, $4)
                """,
                case_id,
                precedent_name,
                precedent_url,
                paragraphs
            )

    async def insert_into_case_table(
        self,
        case_id: str,
        case_name: str,
        case_type: str,
        court_name: str,
        court_type: str,
        doc_url: str,
        raw_text: str,
        doc_size: int,
        facts: str,
        issues: List[str],
        petitioner_arguments: List[str],
        respodent_arguments: List[str]
    ):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO case_table
                (id, case_name, case_type, court_name, court_type,
                doc_url, raw_text, doc_size, facts, issues,
                petitioner_arguments, respodent_arguments)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                case_id,
                case_name,
                case_type,
                court_name,
                court_type,
                doc_url,
                raw_text,
                doc_size,
                facts,
                issues,
                petitioner_arguments,
                respodent_arguments
            )

    async def insert_user(self,
                          name: str,
                          email: str,
                          affliation: str,
                          password_hash: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO users
                (name, email, affliation, password_hash)
                VALUES ($1, $2, $3, $4)
                """,
                name,
                email,
                affliation,
                password_hash,
            )

    async def insert_into_users_case_mapping(self, user_email: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            case_id_list = await connection.fetch(
                """
                SELECT id FROM case_table
                WHERE id not in (SELECT case_id FROM users_case_mapping)
                LIMIT 5;
                """
            )

            for case_id in case_id_list:
                await connection.execute(
                    """
                    INSERT INTO users_case_mapping
                    (user_email, case_id)
                    VALUES ($1, $2)
                    """,
                    user_email,
                    case_id.get("id")
                )

    async def is_given_case_completed(self, case_id: str) -> bool:
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            time_details = await connection.fetchrow(
                """
                SELECT facts_cumulative_time, issues_cumulative_time,
                sections_cumulative_time, precedents_cumulative_time,
                petitioner_arguments_cumulative_time,
                respondent_arguments_cumulative_time FROM case_table
                where id = $1
                """,
                case_id
            )
            print(time_details)
            if (time_details.get("facts_cumulative_time") > 100 and time_details.get("issues_cumulative_time") > 100 and
                time_details.get("sections_cumulative_time") > 100 and time_details.get("precedents_cumulative_time") > 100 and
                    time_details.get("petitioner_arguments_cumulative_time") > 200 and time_details.get("respondent_arguments_cumulative_time") > 100):
                await connection.execute(
                    """
                    UPDATE case_table
                    SET is_completed = true
                    WHERE id = $1
                    """,
                    case_id
                )
                return True

        return False

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

    async def get_cases_from_user_email(self, user_email: str | None):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            if user_email:
                return await connection.fetch(
                    """
                    SELECT * FROM case_table
                    WHERE id in (SELECT case_id FROM users_case_mapping
                    WHERE user_email = $1)
                    """,
                    user_email
                )
            else:
                return await connection.fetch(
                    """
                    SELECT * FROM case_table
                    """
                )

    async def get_case_from_case_id(self, case_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT * FROM case_table
                WHERE id = $1
                """,
                case_id
            )

    async def get_token_length_from_case_id(self, case_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            response = await connection.fetchrow(
                """
                SELECT facts_token_length, issues_token_length FROM case_table
                WHERE id = $1
                """,
                case_id
            )
            return response.get("facts_token_length") + response.get("issues_token_length")

    async def get_sections_from_case_id(self, case_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetch(
                """
                SELECT section_number, act_title, reason, description, is_applicable
                FROM case_section
                WHERE case_id = $1
                """,
                case_id,
            )

    async def get_precedents_from_case_id(self, case_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetch(
                """
                SELECT precedent_name, precedent_url, paragraphs FROM case_precedent
                WHERE case_id = $1
                """,
                case_id
            )

    async def update_case_facts(self, case_id: str, case: Case, facts_token_length: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE case_table
                SET facts = $2, facts_edited = $3,
                facts_last_updated_at = array_append(facts_last_updated_at, $4),
                facts_cumulative_time = facts_cumulative_time + $5,
                facts_reviewed = $6, facts_token_length = $7
                WHERE id = $1
                """,
                case_id,
                case.facts,
                case.facts_edited,
                case.facts_last_updated_at[0],
                case.facts_cumulative_time,
                case.facts_reviewed,
                facts_token_length
            )

    async def update_case_issues(self, case_id: str, case: Case, issues_token_length: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE case_table
                SET issues = $2, issues_edited = $3,
                issues_last_updated_at = array_append(issues_last_updated_at, $4),
                issues_cumulative_time = issues_cumulative_time + $5,
                issues_reviewed = $6, issues_token_length = $7
                WHERE id = $1
                """,
                case_id,
                case.issues,
                case.issues_edited,
                case.issues_last_updated_at[0],
                case.issues_cumulative_time,
                case.issues_reviewed,
                issues_token_length
            )

    async def update_case_sections(self, case_id: str, case: Case):
        engine = await self._get_engine()
        async with engine.acquire() as connection:

            await connection.execute(
                """
                DELETE FROM case_section
                WHERE case_id = $1
                """,
                case_id
            )

            for case_section in case.sections:
                await self.insert_into_case_section(section_number=case_section.section_number,
                                                    case_id=case_id,
                                                    act_title=case_section.act_title,
                                                    reason=case_section.reason,
                                                    description=case_section.description,
                                                    is_applicable=case_section.is_applicable)

            await connection.execute(
                """
                UPDATE case_table
                SET sections_edited = $2,
                sections_last_updated_at = array_append(sections_last_updated_at, $3),
                sections_cumulative_time = sections_cumulative_time + $4,
                sections_reviewed = $5
                WHERE id = $1
                """,
                case_id,
                case.sections_edited,
                case.sections_last_updated_at[0],
                case.sections_cumulative_time,
                case.sections_reviewed
            )

    async def update_case_precedents(self, case_id: str, case: Case, cumulative_token_length: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:

            await connection.execute(
                """
                DELETE FROM case_precedent
                WHERE case_id = $1
                """,
                case_id
            )

            for case_precedent in case.precedents:
                await self.insert_into_case_precedent(case_id=case_id,
                                                      precedent_name=case_precedent.precedent_name,
                                                      precedent_url=case_precedent.precedent_url,
                                                      paragraphs=case_precedent.paragraphs)

            await connection.execute(
                """
                UPDATE case_table
                SET precedents_edited = $2,
                precedents_last_updated_at = array_append(precedents_last_updated_at, $3),
                precedents_cumulative_time = precedents_cumulative_time + $4,
                precedents_reviewed = $5, cumulative_final_token_length = $6
                WHERE id = $1
                """,
                case_id,
                case.precedents_edited,
                case.precedents_last_updated_at[0],
                case.precedents_cumulative_time,
                case.precedents_reviewed,
                cumulative_token_length
            )

    async def update_case_arguments(self, case_id: str, case: Case):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE case_table
                SET petitioner_arguments = $2,
                petitioner_arguments_edited = $3,
                petitioner_arguments_last_updated_at = array_append(petitioner_arguments_last_updated_at, $4),
                petitioner_arguments_cumulative_time = petitioner_arguments_cumulative_time + $5,
                petitioner_arguments_reviewed = $6,
                respondent_arguments = $7,
                respondent_arguments_edited = $8,
                respondent_arguments_last_updated_at = array_append(respondent_arguments_last_updated_at, $9),
                respondent_arguments_cumulative_time = respondent_arguments_cumulative_time + $10,
                respondent_arguments_reviewed = $11
                WHERE id = $1
                """,
                case_id,
                case.petitioner_arguments,
                case.petitioner_arguments_edited,
                case.petitioner_arguments_last_updated_at[0],
                case.petitioner_arguments_cumulative_time,
                case.petitioner_arguments_reviewed,
                case.respondent_arguments,
                case.respondent_arguments_edited,
                case.respondent_arguments_last_updated_at[0],
                case.respondent_arguments_cumulative_time,
                case.respondent_arguments_reviewed
            )

    async def update_change_percentages(self,
                                        case_id: str,
                                        facts_change_percentage: float,
                                        issues_change_percentage: float,
                                        precedents_para_count: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                UPDATE case_table
                SET facts_change_percentage = $2,
                issues_change_percentage = $3,
                precedents_para_count = $4
                WHERE id = $1
                """,
                case_id,
                facts_change_percentage,
                issues_change_percentage,
                precedents_para_count
            )
