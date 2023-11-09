import os
from typing import Annotated
from .server_env import init_env
from jose import JWTError
from fastapi import HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from jugalbandi.core.caching import aiocached
from jugalbandi.core.errors import QuotaExceededException, UnAuthorisedException
from jugalbandi.document_collection import (
    DocumentRepository,
    DocumentCollection,
    LocalStorage,
    GoogleStorage,
)
from jugalbandi.qa import (
    GPTIndexQAEngine,
    LangchainQAEngine,
    TextConverter,
    LangchainQAModel,
)
from jugalbandi.speech_processor import (
    CompositeSpeechProcessor,
    DhruvaSpeechProcessor,
    GoogleSpeechProcessor,
    AzureSpeechProcessor,
)
from jugalbandi.translator import (
    CompositeTranslator,
    GoogleTranslator,
    DhruvaTranslator,
    Translator,
)
from jugalbandi.auth_token.token import decode_token
from jugalbandi.feedback import QAFeedbackRepository, FeedbackRepository
from jugalbandi.tenant import TenantRepository


init_env()
reusable_oauth = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def verify_access_token(token: Annotated[str, Depends(reusable_oauth)]):
    if os.environ["ALLOW_AUTH_ACCESS"] == "true" and token is None:
        return None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return User(username=username, email=username)


@aiocached(cache={})
async def get_document_repository() -> DocumentRepository:
    # TODO: Rename the env variable
    return DocumentRepository(LocalStorage(os.environ["DOCUMENT_LOCAL_STORAGE_PATH"]),
                              GoogleStorage(os.environ["GCP_BUCKET_NAME"],
                              os.environ["GCP_BUCKET_FOLDER_NAME"]))


async def get_document_collection(
    uuid_number: str,
    document_repository: Annotated[
        DocumentRepository, Depends(get_document_repository)
    ],
) -> DocumentCollection:
    return document_repository.get_collection(uuid_number)


async def get_speech_processor():
    return CompositeSpeechProcessor(AzureSpeechProcessor(),
                                    DhruvaSpeechProcessor(),
                                    GoogleSpeechProcessor())


async def get_translator():
    return CompositeTranslator(GoogleTranslator(), DhruvaTranslator())


async def get_gpt_index_qa_engine(
    document_collection: Annotated[
        DocumentCollection, Depends(get_document_collection)
    ],
    speech_processor: Annotated[DocumentCollection, Depends(get_speech_processor)],
    translator: Annotated[Translator, Depends(get_translator)],
):
    return GPTIndexQAEngine(document_collection, speech_processor, translator)


async def get_langchain_gpt3_qa_engine(
    document_collection: Annotated[
        DocumentCollection, Depends(get_document_collection)
    ],
    speech_processor: Annotated[DocumentCollection, Depends(get_speech_processor)],
    translator: Annotated[Translator, Depends(get_translator)],
):
    return LangchainQAEngine(
        document_collection, speech_processor, translator, LangchainQAModel.GPT3
    )


async def get_langchain_gpt35_turbo_qa_engine(
    document_collection: Annotated[
        DocumentCollection, Depends(get_document_collection)
    ],
    speech_processor: Annotated[DocumentCollection, Depends(get_speech_processor)],
    translator: Annotated[Translator, Depends(get_translator)],
):
    return LangchainQAEngine(
        document_collection, speech_processor, translator, LangchainQAModel.GPT35_TURBO
    )


async def get_langchain_gpt4_qa_engine(
    document_collection: Annotated[
        DocumentCollection, Depends(get_document_collection)
    ],
    speech_processor: Annotated[DocumentCollection, Depends(get_speech_processor)],
    translator: Annotated[Translator, Depends(get_translator)],
):
    return LangchainQAEngine(
        document_collection, speech_processor, translator, LangchainQAModel.GPT4
    )


@aiocached(cache={})
async def get_feedback_repository() -> FeedbackRepository:
    return QAFeedbackRepository()


@aiocached(cache={})
async def get_tenant_repository() -> TenantRepository:
    return TenantRepository()


@aiocached(cache={})
async def get_text_converter() -> TextConverter:
    return TextConverter()


class User(BaseModel):
    username: str
    email: str | None = None


api_key_header = APIKeyHeader(name="api_key", auto_error=False)


async def get_api_key(tenant_repository: Annotated[TenantRepository,
                                                   Depends(get_tenant_repository)],
                      api_key_header: str = Security(api_key_header)):
    if os.environ["ALLOW_INVALID_API_KEY"] != "true":
        if api_key_header:
            balance_quota = await tenant_repository.get_balance_quota_from_api_key(api_key_header)
            if balance_quota is None:
                raise UnAuthorisedException("API key is invalid")
            else:
                if balance_quota > 0:
                    await tenant_repository.update_balance_quota(api_key_header, balance_quota)
                else:
                    raise QuotaExceededException("You have exceeded the Quota limit")
        else:
            raise UnAuthorisedException("API Key is missing")
