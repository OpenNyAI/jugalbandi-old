import logging
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from jiva.admin_api import admin_app
import io
from fastapi.testclient import TestClient


@pytest_asyncio.fixture()
async def jiva_client():
    async with AsyncClient(app=admin_app, base_url="http://testapp") as client:
        yield client


@pytest_asyncio.fixture()
async def jiva_test_client():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/skseth/a0ae7026506d.json"
    os.environ["JIVA_LIBRARY_BUCKET"] = "jugalbandi"
    os.environ["JIVA_LIBRARY_PATH"] = "testing/lib"
    client = TestClient(admin_app)
    yield client


@pytest_asyncio.fixture()
async def abcd_pdf():
    folder = os.path.dirname(__file__)

    with open(os.path.join(folder, "abcd.pdf"), "rb") as f:
        yield f


@pytest.mark.asyncio
async def test_upload_document(jiva_test_client: TestClient, caplog):
    caplog.set_level(level=logging.DEBUG)
    folder = os.path.dirname(__file__)
    file_path = os.path.join(folder, "abcd.pdf")
    logging.info(file_path)

    with open(file_path, "rb") as f:
        content = f.read()

    data = {"title": "abcd"}
    file = {"file": ("abcd.pdf", io.BytesIO(content))}

    jiva_test_client.post("/documents", data=data, files=file)
