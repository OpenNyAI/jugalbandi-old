import pytest
import os
import tempfile
from jugalbandi.document_collection import (
    DocumentRepository,
    DocumentCollection,
    LocalStorage,
    GoogleStorage,
)
from jugalbandi.qa import (
    LangchainQAEngine,
    GPTIndexQAEngine,
    LangchainQAModel,
)
from jugalbandi.speech_processor import (
    CompositeSpeechProcessor,
    DhruvaSpeechProcessor,
    GoogleSpeechProcessor,
)
from jugalbandi.translator import (
    CompositeTranslator,
    GoogleTranslator,
    DhruvaTranslator
)
from dotenv import load_dotenv

load_dotenv()
test_dir = os.path.dirname(__file__)


@pytest.fixture()
def doc_collection(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setenv("DOCUMENT_LOCAL_STORAGE_PATH", temp_dir)
        doc_repo = DocumentRepository(LocalStorage(temp_dir),
                                      GoogleStorage(os.environ["GCP_BUCKET_NAME"],
                                                    os.environ["GCP_BUCKET_FOLDER_NAME"]
                                                    ))
        doc_collection = doc_repo.get_collection("a959a476-fdef-11ed-a270-3e85235234ab")
        yield doc_collection


@pytest.fixture()
def get_speech_processor():
    return CompositeSpeechProcessor(DhruvaSpeechProcessor(), GoogleSpeechProcessor())


@pytest.fixture()
def get_translator():
    return CompositeTranslator(GoogleTranslator(), DhruvaTranslator())


@pytest.fixture()
def gpt_index_qa_engine(doc_collection: DocumentCollection):
    return GPTIndexQAEngine(
        doc_collection, get_speech_processor, get_translator
    )


@pytest.fixture()
def langchain_gpt4_qa_engine(doc_collection: DocumentCollection, monkeypatch):
    return LangchainQAEngine(
        doc_collection, get_speech_processor, get_translator,
        LangchainQAModel.GPT4
    )


@pytest.mark.asyncio
async def test_gpt_index_querying(gpt_index_qa_engine: GPTIndexQAEngine):
    try:
        query_response = await gpt_index_qa_engine.query(
            "Give me definition of civil servant",
        )
        assert query_response.answer != "" and len(query_response.source_text) > 0
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


@pytest.mark.asyncio
async def test_langchain_querying(langchain_gpt4_qa_engine: LangchainQAEngine):
    try:
        query_response = await langchain_gpt4_qa_engine.query(
            "Give me definition of civil servant",
        )
        assert query_response.answer != "" and len(query_response.source_text) == 0
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")
