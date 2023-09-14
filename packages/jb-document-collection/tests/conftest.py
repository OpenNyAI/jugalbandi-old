import inspect
from io import BytesIO
from typing import Dict
from zipfile import ZipFile
from jugalbandi.document_collection.repository import DocumentSourceFile, WrapSyncReader
import pytest
import asyncio
import pytest_asyncio
import tempfile

from jugalbandi.storage import (
    LocalStorage,
    NullStorage,
    GoogleStorage,
)

from jugalbandi.document_collection import (
    DocumentRepository,
)


from faker import Faker


fake: Faker = Faker()


class FakeIndexer:
    def __init__(self):
        self.index_files: Dict[str, str] = {}

    def add_file(self, file_name: str, content: str):
        self.index_files[file_name] = content

    async def index(self, path: str) -> Dict[str, str]:
        return self.index_files


@pytest_asyncio.fixture()
async def doc_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = "testing/doc_repo"
        local_store = LocalStorage(temp_dir)
        remote_store = GoogleStorage("jugalbandi", base_path)
        repo = DocumentRepository(local_store, remote_store)
        yield repo

    async with asyncio.TaskGroup() as task_group:
        async for f in remote_store.list_all_files(""):
            task_group.create_task(remote_store.remove_file(f))

    await repo.shutdown()


@pytest_asyncio.fixture()
async def local_only_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield DocumentRepository(
            local_store=LocalStorage(temp_dir), remote_store=NullStorage()
        )


@pytest_asyncio.fixture()
async def zip_source_random():
    zip_contents = fake.zip(num_files=fake.pyint(min_value=1, max_value=5))
    exp_values: Dict[str, bytes] = {}
    with ZipFile(BytesIO(zip_contents), "r") as zf:
        for fileinfo in zf.infolist():
            exp_values[fileinfo.filename] = zf.read(fileinfo)

    yield (
        exp_values,
        DocumentSourceFile("somefile.zip", WrapSyncReader(BytesIO(zip_contents))),
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
