import asyncio
import inspect
import logging
import pytest
import os
import tempfile
import shutil
import pytest_asyncio
from jugalbandi.storage import (
    GoogleStorage,
)
from jugalbandi.library import Library
from faker import Faker
from jugalbandi.library import initialize_pipeline_manager


fake: Faker = Faker()


@pytest_asyncio.fixture()
async def pipeline_manager():
    yield initialize_pipeline_manager()


@pytest_asyncio.fixture()
async def jiva_library():
    base_path = "testing/jiva_repo"
    remote_store = GoogleStorage("jugalbandi", base_path)
    library = Library("lib", remote_store)
    yield library

    async with asyncio.TaskGroup() as task_group:
        async for f in remote_store.list_all_files(""):
            task_group.create_task(remote_store.remove_file(f))

    await library.shutdown()


@pytest_asyncio.fixture()
async def import_lib():
    folder = os.path.dirname(__file__)
    pdf_file_path = f"{folder}/abcd.pdf"
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(pdf_file_path, temp_dir)
        yield temp_dir


def pytest_collection_modifyitems(config, items):
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
