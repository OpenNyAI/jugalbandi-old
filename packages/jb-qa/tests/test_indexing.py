import pytest
import pytest_asyncio
import os
import aiofiles
import asyncio
import tempfile
from jugalbandi.document_collection import (
    DocumentRepository,
    DocumentSourceFile,
    LocalStorage,
    GoogleStorage
)
from jugalbandi.qa import GPTIndexer, LangchainIndexer, TextConverter
from dotenv import load_dotenv

load_dotenv()
test_dir = os.path.dirname(__file__)


@pytest_asyncio.fixture()
async def doc_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = "testing/doc_repo"
        local_store = LocalStorage(temp_dir)
        remote_store = GoogleStorage(os.environ["GCP_BUCKET_NAME"], base_path)
        repo = DocumentRepository(local_store, remote_store)
        yield repo

    async with asyncio.TaskGroup() as task_group:
        async for f in remote_store.list_all_files(""):
            task_group.create_task(remote_store.remove_file(f))

    await repo.shutdown()


@pytest.fixture()
def gpt_indexer():
    return GPTIndexer()


@pytest.fixture()
def langchain_indexer():
    return LangchainIndexer()


@pytest.fixture()
def text_converter():
    return TextConverter()


@pytest.mark.asyncio
async def test_gpt_index_indexing(doc_repo: DocumentRepository,
                                  gpt_indexer: GPTIndexer):
    file_path = os.path.join(test_dir, "test_mockups/indexing/testing.pdf")
    doc_collection = doc_repo.new_collection()
    async with aiofiles.open(file_path, "rb") as file:
        await doc_collection.init_from_files([DocumentSourceFile("testing.pdf", file)])
    try:
        await gpt_indexer.index(doc_collection)
    except Exception as e:
        pytest.fail(f"Indexing failed due to {e}")


@pytest.mark.asyncio
async def test_langchain_indexing(doc_repo: DocumentRepository,
                                  langchain_indexer: LangchainIndexer,
                                  text_converter: TextConverter):
    file_path = os.path.join(test_dir, "test_mockups/indexing/testing.pdf")
    doc_collection = doc_repo.new_collection()
    async with aiofiles.open(file_path, "rb") as file:
        await doc_collection.init_from_files([DocumentSourceFile("testing.pdf", file)])
    async for filename in doc_collection.list_files():
        await text_converter.textify(filename, doc_collection)
    try:
        await langchain_indexer.index(doc_collection)
    except Exception as e:
        pytest.fail(f"Indexing failed due to {e}")
