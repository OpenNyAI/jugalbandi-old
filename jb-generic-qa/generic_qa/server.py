from .server_env import init_env
from typing import Annotated, List
from fastapi import FastAPI, UploadFile, Depends, Query, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKey
from jugalbandi.core import (
  Language,
  MediaFormat,
  IncorrectInputException,
  SpeechProcessor as SpeechProcessorEnum
)
from jugalbandi.translator import (
  Translator,
  AzureTranslator
)
from jugalbandi.speech_processor import (
  SpeechProcessor,
  AzureSpeechProcessor,
  GoogleSpeechProcessor,
  DhruvaSpeechProcessor
)
from jugalbandi.audio_converter import convert_to_wav_with_ffmpeg
from jugalbandi.tenant import TenantRepository
from jugalbandi.document_collection import (
    DocumentRepository,
    DocumentSourceFile,
)
from jugalbandi.qa import (
    QAEngine,
    QueryResponse,
    GPTIndexer,
    LangchainIndexer,
    TextConverter,
    rephrased_question,
)
from auth_service import auth_app
from jugalbandi.feedback import FeedbackRepository
from .query_with_tfidf import querying_with_tfidf
from .server_helper import (
    get_api_key,
    get_tenant_repository,
    get_feedback_repository,
    get_gpt_index_qa_engine,
    get_langchain_gpt3_qa_engine,
    get_langchain_gpt35_turbo_qa_engine,
    get_langchain_gpt4_qa_engine,
    get_text_converter,
    verify_access_token,
    get_document_repository,
    get_speech_processor,
    get_translator,
    User,
)
from prometheus_fastapi_instrumentator import Instrumentator
import base64
# from .server_middleware import ApiKeyMiddleware

init_env()

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
    contact={
        "name": "Saurabh - Major contributor in Jugalbandi.ai",
        "email": "saurabh@opennyai.org",
    },
    license_info={
        "name": "MIT License",
        "url": "https://www.jugalbandi.ai/",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
# app.add_middleware(ApiKeyMiddleware, tenant_repository=get_tenant_repository())


@app.exception_handler(Exception)
async def custom_exception_handler(request, exception):
    if hasattr(exception, 'status_code'):
        status_code = exception.status_code
    else:
        status_code = 500
    return JSONResponse(
        status_code=status_code,
        content={"error_message": str(exception)}
    )


@app.get("/")
async def root():
    return {"message": "Welcome to Jugalbandi API"}


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
    source_files = [DocumentSourceFile(file.filename, file) for file in files]
    await document_collection.init_from_files(source_files)

    async for filename in document_collection.list_files():
        await text_converter.textify(filename, document_collection)

    gpt_indexer = GPTIndexer()
    langchain_indexer = LangchainIndexer()

    await gpt_indexer.index(document_collection)
    await langchain_indexer.index(document_collection)
    return {
        "uuid_number": document_collection.id,
        "message": "Files uploading is successful",
    }


@app.get(
    "/query-with-gptindex",
    summary="Query using gpt-index model",
    tags=["Q&A over Document Store"],
)
async def query_using_gptindex(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
    gpt_index_qa_engine: Annotated[QAEngine, Depends(get_gpt_index_qa_engine)],
) -> QueryResponse:
    response = await gpt_index_qa_engine.query(query=query_string)
    return {
        "query": query_string,
        "answer": response.answer,
        "source_text": response.source_text,
    }


@app.get(
    "/query-with-langchain",
    summary="Query using langchain (GPT-3)",
    tags=["Q&A over Document Store"],
)
async def query_using_langchain(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
    langchain_qa_engine: Annotated[QAEngine, Depends(get_langchain_gpt3_qa_engine)],
) -> QueryResponse:
    response = await langchain_qa_engine.query(query=query_string)
    return {
        "query": query_string,
        "answer": response.answer,
        "source_text": response.source_text,
    }


@app.get(
    "/query-with-langchain-gpt3-5",
    summary="Query using langchain (GPT-3.5)",
    tags=["Q&A over Document Store"],
)
async def query_using_langchain_with_gpt3_5(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
    langchain_qa_engine: Annotated[
        QAEngine, Depends(get_langchain_gpt35_turbo_qa_engine)
    ],
):
    response = await langchain_qa_engine.query(query=query_string)
    return {
        "query": query_string,
        "answer": response.answer,
        "source_text": response.source_text,
    }


@app.get(
    "/query-with-langchain-gpt3-5-custom-prompt",
    summary="Query using langchain (GPT-3.5) with custom prompt",
    tags=["Q&A over Document Store"],
)
async def query_using_langchain_with_gpt3_5_and_custom_prompt(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
    langchain_qa_engine: Annotated[
        QAEngine, Depends(get_langchain_gpt35_turbo_qa_engine)
    ],
    prompt: str = Query(default="",
                        description=(
                            "Give prompts in this format. "
                            "The first sentence of the prompt is necessary. "
                            "The second sentence can be customized. \n\n"
                            "You are a helpful assistant who helps with answering "
                            "questions based on the provided information. If the "
                            "information cannot be found in the text provided, "
                            "you admit that you don't know"))
):
    response = await langchain_qa_engine.query(query=query_string,
                                               prompt=prompt,
                                               source_text_filtering=False)
    return {
        "query": query_string,
        "answer": response.answer,
        "source_text": response.source_text,
    }


@app.get(
    "/query-with-langchain-gpt4",
    summary="Query using langchain (GPT-4)",
    tags=["Q&A over Document Store"],
)
async def query_using_langchain_with_gpt4(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
    langchain_qa_engine: Annotated[QAEngine, Depends(get_langchain_gpt4_qa_engine)],
):
    response = await langchain_qa_engine.query(query=query_string)
    return {
        "query": query_string,
        "answer": response.answer,
    }


@app.get(
    "/query-with-langchain-gpt4-custom-prompt",
    summary="Query using langchain (GPT-4) with custom prompt",
    tags=["Q&A over Document Store"],
)
async def query_using_langchain_with_gpt4_and_custom_prompt(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
    langchain_qa_engine: Annotated[QAEngine, Depends(get_langchain_gpt4_qa_engine)],
    prompt: str = "",
):
    response = await langchain_qa_engine.query(query=query_string, prompt=prompt)
    return {
        "query": query_string,
        "answer": response.answer,
    }


@app.get(
    "/query-using-voice",
    summary="Query using voice with langchain (GPT-3.5) with custom prompt",
    tags=["Q&A over Document Store"],
)
async def query_with_voice_input_gpt3_5(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    langchain_qa_engine: Annotated[QAEngine,
                                   Depends(get_langchain_gpt35_turbo_qa_engine)],
    input_language: Language,
    output_format: MediaFormat,
    query_text: str = "",
    audio_url: str = "",
    prompt: str = "",
) -> QueryResponse:
    return await langchain_qa_engine.query(
        query=query_text,
        speech_query_url=audio_url,
        input_language=input_language,
        output_format=output_format,
        prompt=prompt,
        source_text_filtering=False,
    )


@app.get(
    "/query-using-voice-gpt4",
    summary="Query using voice with langchain (GPT-4) with custom prompt",
    tags=["Q&A over Document Store"],
)
async def query_with_voice_input_gpt4(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    langchain_qa_engine: Annotated[QAEngine, Depends(get_langchain_gpt4_qa_engine)],
    input_language: Language,
    output_format: MediaFormat,
    query_text: str = "",
    audio_url: str = "",
    prompt: str = "",
) -> QueryResponse:
    return await langchain_qa_engine.query(
        query=query_text,
        speech_query_url=audio_url,
        input_language=input_language,
        output_format=output_format,
        prompt=prompt,
    )


@app.get("/rephrased-query")
async def get_rephrased_query(
    authorization: Annotated[User, Depends(verify_access_token)],
    api_key: Annotated[APIKey, Depends(get_api_key)],
    query_string: str,
):
    answer = await rephrased_question(query_string)
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
    speech_processor_enum: SpeechProcessorEnum
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
    speech_processor_enum: SpeechProcessorEnum
):
    if speech_processor_enum.value == "Azure":
        speech_processor = AzureSpeechProcessor()
    elif speech_processor_enum.value == "Google":
        speech_processor = GoogleSpeechProcessor()
    else:
        speech_processor = DhruvaSpeechProcessor()

    print(text_query)
    audio_bytes = await speech_processor.text_to_speech(text_query, language)
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    return {"audio_bytes": audio_base64}


# Testing Azure Translator endpoint
@app.get(
    "/azure-translator",
    summary="Testing Azure Translator endpoint",
    tags=["Language Processing"],
)
async def get_azure_translator(
    authorization: Annotated[User, Depends(verify_access_token)],
    text_query: str,
    source_language: Language,
    destination_language: Language,
):
    translator = AzureTranslator()
    print(text_query)
    translated_text = await translator.translate_text(text_query,
                                                      source_language=source_language,
                                                      destination_language=destination_language)
    transliterated_text = await translator.transliterate_text(text_query,
                                                              source_language=source_language)
    return {"translated_text": translated_text,
            "transliterated_text": transliterated_text}


app.mount("/auth", auth_app)
