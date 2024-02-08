# import asyncpg
import psycopg2
from tenant_db_settings import get_tenant_db_settings


class TenantRepository:
    def __init__(self) -> None:
        self.tenant_db_settings = get_tenant_db_settings()

    def _get_engine(self) -> psycopg2:
        engine = self._create_engine()
        self._create_schema(engine)
        return engine

    def _create_engine(self):
        engine = psycopg2.connect(
            host=self.tenant_db_settings.tenant_database_ip,
            port=self.tenant_db_settings.tenant_database_port,
            user=self.tenant_db_settings.tenant_database_username,
            password=self.tenant_db_settings.tenant_database_password,
            database=self.tenant_db_settings.tenant_database_name,
        )
        # engine = asyncpg.create_pool(
        #     host=self.tenant_db_settings.tenant_database_ip,
        #     port=self.tenant_db_settings.tenant_database_port,
        #     user=self.tenant_db_settings.tenant_database_username,
        #     password=self.tenant_db_settings.tenant_database_password,
        #     database=self.tenant_db_settings.tenant_database_name,
        #     max_inactive_connection_lifetime=timeout,
        # )
        return engine

    def _create_schema(self, engine: psycopg2):
        with engine.cursor() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant(
                    name TEXT,
                    email_id TEXT,
                    api_key TEXT PRIMARY KEY,
                    password TEXT,
                    weekly_quota INTEGER DEFAULT 125,
                    balance_quota INTEGER DEFAULT 125
                );
                CREATE TABLE IF NOT EXISTS tenant_bot(
                    tenant_api_key TEXT,
                    document_uuid TEXT,
                    phone_number TEXT PRIMARY KEY,
                    FOREIGN KEY (tenant_api_key) REFERENCES tenant (api_key)
                )
            """
            )

    def insert_into_tenant(
        self,
        name: str,
        email_id: str,
        api_key: str,
        password: str,
        weekly_quota: int = 125,
    ):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                INSERT INTO tenant
                (name, email_id, api_key, password, weekly_quota, balance_quota)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    email_id,
                    api_key,
                    password,
                    weekly_quota,
                    weekly_quota,
                ),
            )
            engine.commit()

    def get_balance_quota_from_api_key(self, api_key: str):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                SELECT balance_quota FROM tenant
                WHERE api_key = %s
                """,
                (api_key,),
            )
            return connection.fetchone()

    def get_tenant_details(self, email_id: str):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                SELECT * FROM tenant
                WHERE email_id = %s
                """,
                (email_id,),
            )
            return connection.fetchone()

    def get_all_tenant_emails(self):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                SELECT email_id FROM tenant
                """,
            )
            email_records = connection.fetchall()
            registered_emails = [email_record[0] for email_record in email_records]
            return registered_emails

    def update_balance_quota(self, api_key: str, balance_quota: str):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                UPDATE tenant
                SET balance_quota = %s
                WHERE api_key = %s and balance_quota = %s
                """,
                (
                    balance_quota - 1,
                    api_key,
                    balance_quota,
                ),
            )
            engine.commit()

    def update_tenant_information(
        self, name: str, email_id: str, api_key: str, weekly_quota: int
    ):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                UPDATE tenant
                SET name = %s, email_id = %s, weekly_quota = %s, balance_quota = %s
                WHERE api_key = %s
                """,
                (
                    name,
                    email_id,
                    weekly_quota,
                    weekly_quota,
                    api_key,
                ),
            )
            engine.commit()

    def reset_balance_quota_for_tenant(self, api_key: str):
        engine = self._get_engine()
        with engine.cursor() as connection:
            connection.execute(
                """
                UPDATE tenant
                SET balance_quota = weekly_quota
                WHERE api_key = %s
                """,
                (api_key,),
            )
            engine.commit()
