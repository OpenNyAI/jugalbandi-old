import base64
import os
from typing import Annotated, List

import httpx
from auth_service import auth_app
from fastapi import Depends, FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security.api_key import APIKey
from jugalbandi.audio_converter import convert_to_wav_with_ffmpeg
from jugalbandi.core import IncorrectInputException, Language, MediaFormat
from jugalbandi.core import SpeechProcessor as SpeechProcessorEnum
from jugalbandi.document_collection import DocumentRepository, DocumentSourceFile
from jugalbandi.feedback import FeedbackRepository
from jugalbandi.logging import Logger, LoggingRepository
from jugalbandi.qa import (
    LangchainIndexer,
    QAEngine,
    QueryResponse,
    TextConverter,
    rephrased_question,
)
from jugalbandi.speech_processor import (
    AzureSpeechProcessor,
    DhruvaSpeechProcessor,
    GoogleSpeechProcessor,
    SpeechProcessor,
)
from jugalbandi.tenant import TenantRepository
from jugalbandi.translator import Translator
from opentelemetry.propagate import inject

from .query_with_tfidf import querying_with_tfidf
from .server_env import init_env
from .server_helper import (
    User,
    get_api_key,
    get_document_repository,
    get_feedback_repository,
    get_langchain_qa_engine,
    get_logging_repository,
    get_speech_processor,
    get_tenant_repository,
    get_text_converter,
    get_translator,
    verify_access_token,
)

# from tools.utils import PrometheusMiddleware, metrics, setting_otlp


init_env()

APP_NAME = os.environ.get("APP_NAME", "generic_qa")
EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8080)
OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "http://tempo:4317")

logger = Logger("generic_qa")

api_description = """
Jugalbandi.ai has a vector datastore that allows you to get factual Q&A over
a document set.

API is currently available in it's alpha version. We are currently gaining test
data to improve our systems and predictions. 🚀

## Factual Q&A over large documents

You will be able to:

* **Upload documents** (_implemented_).
Allows you to upload documents and create a vector space for semantic similarity search.
Basically a better search than Ctrl+F

* **Factual Q&A** (_implemented_).
Allows you to pass uuid for a document set and ask a question for factual
response over it.
"""


app = FastAPI(
    title="Jugalbandi.ai",
    description=api_description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    license_info={
        "name": "MIT License",
        "url": "https://www.jugalbandi.ai/",
    },
)


# # Setting metrics middleware
# app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
# app.add_route("/metrics", metrics)

# # Setting OpenTelemetry exporter
# setting_otlp(app, APP_NAME, OTLP_GRPC_ENDPOINT)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def custom_exception_handler(request, exception):
    if hasattr(exception, "status_code"):
        status_code = exception.status_code
    else:
        status_code = 500
    logger.exception(str(exception))
    return JSONResponse(
        status_code=status_code, content={"error_message": str(exception)}
    )


@app.get("/")
async def root():
    return {"message": "Welcome to Jugalbandi API"}


@app.get("/chain")
async def chain(response: Response):
    headers = {}
    inject(headers)  # inject trace info to header
    await logger.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8080/",
            headers=headers,
        )
    await logger.info("Chain Finished")
    return {"path": "/chain"}


@app.get(
    "/user-logged-in", summary="Check if the user is logged in", tags=["Authentication"]
)
async def get_me(authorization: Annotated[User, Depends(verify_access_token)]):
    return {}


@app.post(
    "/upload-files",
    summary="Upload files to store the document set for querying",
    tags=["Document Store"],
)
async def upload_files(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    files: List[UploadFile],
    document_repository: Annotated[
        DocumentRepository, Depends(get_document_repository)
    ],
    text_converter: Annotated[TextConverter, Depends(get_text_converter)],
):
    document_collection = document_repository.new_collection()
    uuid_number = document_collection.id
    source_files = [DocumentSourceFile(file.filename, file) for file in files]
    await logger.info(f"UUID number: {uuid_number}")
    for file in source_files:
        await logger.info(f"File name: {file.filename}")
    await document_collection.init_from_files(source_files)

    async for filename in document_collection.list_files():
        await text_converter.textify(filename, document_collection)
    await logger.info("Textification is successful")

    langchain_indexer = LangchainIndexer()
    await langchain_indexer.index(document_collection)
    await logger.info("Langchain Indexing is successful")

    return {
        "uuid_number": uuid_number,
        "message": "Files uploading is successful",
    }


@app.get(
    "/query",
    summary="Query using langchain models with custom prompt",
    tags=["Q&A over Document Store"],
)
async def query(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    langchain_qa_engine: Annotated[QAEngine, Depends(get_langchain_qa_engine)],
    input_language: Language,
    output_format: MediaFormat,
    query_text: str = "",
    audio_url: str = "",
    prompt: str = Query(
        default="",
        description=(
            "Give prompts in this format. "
            "The first sentence of the prompt is necessary. "
            "The second sentence can be customized. \n\n"
            "You are a helpful assistant who helps with answering "
            "questions based on the provided information. If the "
            "information cannot be found in the text provided, "
            "you admit that you don't know"
        ),
    ),
) -> QueryResponse:
    return await langchain_qa_engine.query(
        query=query_text,
        speech_query_url=audio_url,
        prompt=prompt,
        input_language=input_language,
        output_format=output_format,
    )


@app.get("/rephrased-query")
async def get_rephrased_query(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
):
    answer = await rephrased_question(query_string)
    await logger.info(f"Query: {query_string}")
    await logger.info(f"Answer: {answer}")
    return {"given_query": query_string, "rephrased_query": answer}


@app.get(
    "/get-balance-quota",
    summary="Get balance quota using api key",
    tags=["Tenant Quota"],
)
async def get_balance_quota(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: str,
    tenant_repository: Annotated[TenantRepository, Depends(get_tenant_repository)],
):
    response = await tenant_repository.get_balance_quota_from_api_key(api_key)
    if response is None:
        raise IncorrectInputException("Invalid API key")
    return {"balance_quota": response}


@app.post("/response-feedback", include_in_schema=False)
async def response_feedback(
    authorization: Annotated[User, Depends(verify_access_token)],
    feedback_repository: Annotated[
        FeedbackRepository, Depends(get_feedback_repository)
    ],
    uuid_number: str,
    query: str,
    response: str,
    feedback: bool,
):
    await feedback_repository.insert_response_feedback(
        uuid_number=uuid_number,
        query=query,
        response=response,
        feedback=feedback,
    )
    return "Feedback update is successful"


@app.post(
    "/source-document",
    summary="Get source document using keyword",
    tags=["Source Document over Document Store"],
)
async def get_source_document(
    authorization: Annotated[User, Depends(verify_access_token)],
    translator: Annotated[Translator, Depends(get_translator)],
    speech_processor: Annotated[SpeechProcessor, Depends(get_speech_processor)],
    query_string: str = "",
    input_language: Language = Language.EN,
    audio_file: UploadFile = File(None),
):
    answer = await querying_with_tfidf(
        translator, speech_processor, query_string, input_language, audio_file
    )
    return answer


# Testing STT endpoint
@app.get(
    "/speech-to-text",
    summary="Testing STT endpoint",
    tags=["Language Processing"],
)
async def get_speech_to_text(
    authorization: Annotated[User, Depends(verify_access_token)],
    speech_query_url: str,
    language: Language,
    speech_processor_enum: SpeechProcessorEnum,
):
    if speech_processor_enum.value == "Azure":
        speech_processor = AzureSpeechProcessor()
    elif speech_processor_enum.value == "Google":
        speech_processor = GoogleSpeechProcessor()
    else:
        speech_processor = DhruvaSpeechProcessor()

    wav_data = await convert_to_wav_with_ffmpeg(speech_query_url)
    text = await speech_processor.speech_to_text(wav_data, language)
    return {"text": text}


# Testing TTS endpoint
@app.get(
    "/text-to-speech",
    summary="Testing TTS endpoint",
    tags=["Language Processing"],
)
async def get_text_to_speech(
    authorization: Annotated[User, Depends(verify_access_token)],
    text_query: str,
    language: Language,
    speech_processor_enum: SpeechProcessorEnum,
):
    if speech_processor_enum.value == "Azure":
        speech_processor = AzureSpeechProcessor()
    elif speech_processor_enum.value == "Google":
        speech_processor = GoogleSpeechProcessor()
    else:
        speech_processor = DhruvaSpeechProcessor()

    print(text_query)
    audio_bytes = await speech_processor.text_to_speech(text_query, language)
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    return {"audio_bytes": audio_base64}


# Temporary data addition
@app.post("/logging-repo")
async def logging_repo(
    authorization: Annotated[User, Depends(verify_access_token)],
    logging_repository: Annotated[LoggingRepository, Depends(get_logging_repository)],
):
    # await logging_repository.insert_users_information("Hello", "Bye", 91234567890)
    # await logging_repository.insert_app_information("App1", 62846563489)
    # await logging_repository.insert_document_store_log(1, 1, "545634353434", ["Hello", "Bye"],
    #                                                    40, 200, "Successful upload")
    await logging_repository.insert_qa_log(
        1,
        1,
        "545634353434",
        "en",
        "How are you",
        "some-link",
        "I'm fine",
        "some-link",
        5,
        ["1", "2", "3", "4"],
        "some-prompt",
        "gpt-4",
        200,
        "Success",
        10,
    )
    await logging_repository.insert_stt_log(
        1, "some-link", "bhashini", "somshsdjf", 200, "success", 5
    )
    await logging_repository.insert_tts_log(
        1, "some-text", "bhashini", "some-link", 200, "success", 5
    )
    await logging_repository.insert_translator_log(
        1, "some-text", "hi", "en", "bhashini", "translated-text", 200, "success", 5
    )
    await logging_repository.insert_chat_history(
        1, 1, "545634353434", "user", "en", "some-link", "hello", "bye"
    )

    return "Logging is successful"


app.mount("/auth", auth_app)
