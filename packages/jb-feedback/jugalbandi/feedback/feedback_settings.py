from typing import Annotated, Optional
from cachetools import cached
from pydantic import BaseSettings, Field


class FeedbackSettings(BaseSettings):
    pass


class SchemeFeedbackSettings(FeedbackSettings):
    scheme_feedback_database_ip: Annotated[
        Optional[str], Field(..., env="SCHEME_FEEDBACK_DATABASE_IP")
    ] = None
    scheme_feedback_database_port: Annotated[
        Optional[str], Field(..., env="SCHEME_FEEDBACK_DATABASE_PORT")
    ] = None
    scheme_feedback_database_username: Annotated[
        Optional[str], Field(..., env="SCHEME_FEEDBACK_DATABASE_USERNAME")
    ] = None
    scheme_feedback_database_password: Annotated[
        Optional[str], Field(..., env="SCHEME_FEEDBACK_DATABASE_PASSWORD")
    ] = None
    scheme_feedback_database_name: Annotated[
        Optional[str], Field(..., env="SCHEME_FEEDBACK_DATABASE_NAME")
    ] = None


class QAFeedbackSettings(FeedbackSettings):
    qa_feedback_database_ip: Annotated[
        Optional[str], Field(..., env="QA_FEEDBACK_DATABASE_IP")
    ] = None
    qa_feedback_database_port: Annotated[
        Optional[str], Field(..., env="QA_FEEDBACK_DATABASE_PORT")
    ] = None
    qa_feedback_database_username: Annotated[
        Optional[str], Field(..., env="QA_FEEDBACK_DATABASE_USERNAME")
    ] = None
    qa_feedback_database_password: Annotated[
        Optional[str], Field(..., env="QA_FEEDBACK_DATABASE_PASSWORD")
    ] = None
    qa_feedback_database_name: Annotated[
        Optional[str], Field(..., env="QA_FEEDBACK_DATABASE_NAME")
    ] = None


@cached(cache={})
def get_scheme_feedback_settings():
    return SchemeFeedbackSettings()


@cached(cache={})
def get_qa_feedback_settings():
    return QAFeedbackSettings()
